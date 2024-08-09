import re
import random
from utils import connect_to_collection, format_list_strings, is_taint_source, GITHUB_TAINT_LIST, GITHUB_TAINT_CI_OBJECT_LIST, reusable_wf_direct_taint, reusable_wf_indirect_taint, composite_action_direct_taint, composite_action_indirect_taint
"""
RQ2-2:
prompt_1: Is there any code injection vulnerability in the following GitHub Workflow?

prompt_2: 
-- X type a: Is there any input flow action vulnerability (i.e., Where the taint originates in the workflow and flows in a sink inside the action) in the following GitHub Workflow?
-- X type b: Is there any direct flow action vulnerability (i.e., Where the taint originates inside the action and flows into a sink inside the action itself) in the following GitHub Workflow?
-- type c: Is there any output flow action vulnerability (i.e., Where the taint originates inside the action and flows in a sink outside the action) in the following GitHub Workflow?
-- X type d: Is there any input reusable flow vulnerability (i.e., Where the taint originates in the workflow and flows in a sink inside the reusable workflow) in the following GitHub Workflow?
-- X type e: Is there any direct reusable flow vulnerability (i.e., Where the taint originates inside the reusable workflow and flows in a sink inside the reusable workflow itself) in the following GitHub Workflow?
-- type f: Is there any output reusable flow vulnerability (i.e., Where the taint originates inside the reusable workflow and flows in a sink outside the reusable workflow) in the following GitHub Workflow?
-- type g: Is there any direct code injection vulnerability (i.e., Where the taint originates in the workflow and flows into a sink in the same workflow. The taint can also pass through actions and reusable workflows) in the following GitHub Workflow?

prompt_3: Is there any code injection vulnerability in the following GitHub Workflow? Hint 1: Here is the list of taint sources for GitHub Workflows: [all taint sources]. Hint 2: action/reusable workflow info.
"""
def contains_taint_variable(string):
    pattern = r".*\$\{\{.*\}\}.*"
    match = re.search(pattern, string)
    if match is None:
        return False
    for taint in GITHUB_TAINT_CI_OBJECT_LIST + GITHUB_TAINT_LIST:
        if taint in string:
            return True
    return False

def get_action(action_collection, action_name, action_version):
    if action_collection == False:
        raise Exception("No connection to MongoDB...")
    return action_collection.find_one({"name": action_name, "version": action_version})

def get_action_default_inputs(action_info):
    default_inputs = []
    for input in action_info["defaults"].get("inputs", []):                                                
        input_val = input['value']
        if isinstance(input_val, str) and contains_taint_variable(input_val):
            default_inputs.append(f"{input['name']}={input_val}")
    if default_inputs == []:
        return None
    return format_list_strings(default_inputs)
    
def get_action_arg_to_sink(action_info):
    arg_to_sink = set()
    if action['name'] == "actions/github-script": # special case 
        arg_to_sink.add("`script`")        
    for arg in action_info["ql_results"].get("ArgToSink", []):
        arg_to_sink.add("`" + arg['name'] + "`")
    for arg in action_info["ql_results"].get("ArgToLSink", []):
        arg_to_sink.add("`" + arg['name'] + "`")

    if action['name'] == "actions/checkout" and "ref" in arg_to_sink:
        arg_to_sink.remove("`ref`")
    elif action['name'] == "peaceiris/actions-gh-pages" and "commit-message" in arg_to_sink:
        arg_to_sink.remove("`commit-message`")
    elif action['name'] == "peter-evans/create-pull-request" and "ref" in arg_to_sink:
        arg_to_sink.remove("`ref`")
    
    if len(arg_to_sink) == 0:
        return None
    return arg_to_sink

def get_action_env_to_sink(action_info):
    env_to_sink = set()
    for env in action_info["ql_results"].get("EnvtoSink", []):
        env_to_sink.add("`" + env['name'] + "`")
    for env in action_info["ql_results"].get("EnvtoLSink", []):
        env_to_sink.add("`" + env['name'] + "`")
    
    if len(env_to_sink) == 0:
        return None
    return env_to_sink

def action_has_context_to_sink(action_info):
    if action_info["ql_results"].get("ContextToSink", []) != []:
        return True
    if action_info["ql_results"].get("ContextToLSink", []) != []:
        return True
    return False

def get_action_context_to_output(action_info):
    context_to_output = set()
    for context in action_info["ql_results"].get("ContextToOutput", []):
        for output in context['output']:
            if output["function"] == "setOutput":
                context_to_output.add("`" + output["name"] + "`")
    if len(context_to_output) == 0:
        return None
    return context_to_output

def get_action_arg_to_output(action_info):
    arg_to_output = set()
    for arg in action_info["ql_results"].get("ArgToOutput", []):
        for output in arg['output']:
            if output["function"] == "setOutput":
                arg_to_output.add(("`" + arg['name'] + "`", "`" + output["name"] + "`"))
    if len(arg_to_output) == 0:
        return None
    return arg_to_output

def get_action_env_to_output(action_info):
    env_to_output = set()
    for env in action_info["ql_results"].get("EnvtoOutput", []):
        for output in env['output']:
            if output["function"] == "setOutput":
                env_to_output.add(("`" + env['name'] + "`", "`" + output["name"] + "`"))
    if len(env_to_output) == 0:
        return None
    return env_to_output

def handle_docker_action(action_info):
    action_default_inputs = get_action_default_inputs(action_info)
    text = ""
    if action_default_inputs:
        text = f"{action_info['name']}@{action_info['version']} is a vulnerable docker action. "
    else:
        text = f"{action_info['name']}@{action_info['version']} is a docker action and it is vulnerable only if any one of the inputs is tainted by taint sources. "
    return text

def handle_node1216_action(action_info):
    text = ""
    if 'ql_results' not in action_info:
        action_default_inputs = get_action_default_inputs(action_info)
        if action_default_inputs:
            text = f"{action_info['name']}@{action_info['version']} is a vulnerable javascript action. "
        else:
            text = f"{action_info['name']}@{action_info['version']} is a javascript action and it is vulnerable only if any one of the inputs is tainted by taint sources. "
        return text

    has_context_to_sink = action_has_context_to_sink(action_info)
    action_default_inputs = get_action_default_inputs(action_info)
    if has_context_to_sink:
        text += f"{action_info['name']}@{action_info['version']} is a vulnerable javascript action because it directly uses taint sources inside itself. "
    
    arg_to_sink = get_action_arg_to_sink(action_info)
    env_to_sink = get_action_env_to_sink(action_info)
    text1 = f"{action_info['name']}@{action_info['version']} is a javascript action. "
    if arg_to_sink or env_to_sink:
        if action_default_inputs:
            text1 += f"Its default input is " + action_default_inputs + ". "
    if arg_to_sink and env_to_sink:
        text1 += f"If "  
        text1 += f"the input {arg_to_sink.pop()} " if len(arg_to_sink) == 1 else f"any one of inputs({', '.join(arg_to_sink)}) "
        text1 += "or "
        text1 += f"the environment variable {env_to_sink.pop()} " if len(env_to_sink) == 1 else f"any one of the environment variables({', '.join(env_to_sink)}) "
        text1 += f"is tainted by taint sources, there will be a code injection vulnerability inside the {action_info['name']}@{action_info['version']}. "
    elif arg_to_sink:
        text1 += f"If "  
        text1 += f"the input {arg_to_sink.pop()} " if len(arg_to_sink) == 1 else f"any one of inputs({', '.join(arg_to_sink)}) "
        text1 += f"is tainted by taint sources, there will be a code injection vulnerability inside the {action_info['name']}@{action_info['version']}. "
    elif env_to_sink:
        text1 += f"If "  
        text1 += f"the environment variable {env_to_sink.pop()} " if len(env_to_sink) == 1 else f"any one of the environment variables({', '.join(env_to_sink)}) "
        text1 += f"is tainted by taint sources, there will be a code injection vulnerability inside the {action_info['name']}@{action_info['version']}. "

    context_to_output = get_action_context_to_output(action_info)
    arg_to_output = get_action_arg_to_output(action_info)
    env_to_output = get_action_env_to_output(action_info)
    if context_to_output:
        if len(context_to_output) == 1:
            text1 += f"The output {context_to_output.pop()} of {action_info['name']}@{action_info['version']} is tainted by taint sources. "  
        else:
            text1 += f"The outputs({', '.join(context_to_output)}) of {action_info['name']}@{action_info['version']} are tainted by taint sources. "
    if arg_to_output or env_to_output:
        text1 += f"Here are data flows in {action_info['name']}@{action_info['version']}: "
        text_list = []
        if arg_to_output:
            for arg, output in arg_to_output:
                text_list.append(f"input {arg} flows to output {output}")
        if env_to_output:
            for env, output in env_to_output:
                text_list.append(f"environment variable {env} flows to output {output}")
        if len(text_list) == 1:
            text1 += text_list[0] + ". "
        else:
            text1 += ", ".join(text_list[0:-1]) + " and " + text_list[-1] + ". "
    if text1 == f"{action_info['name']}@{action_info['version']} is a javascript action. ":
        text1 = ""
    res = text + text1
    if res == "":
        res = f"{action_info['name']}@{action_info['version']} is a non-vulnerable javascript action. "
    return res

def handle_composite_action(action_info):
    text = ""
    action_full_name = f"{action_info['name']}@{action_info['version']}"
    if action_full_name in composite_action_direct_taint:
        text += f"{action_full_name} is a vulnerable composite action because it directly uses taint sources inside itself. "
    else:
        text += f"{action_full_name} is a composite action. "
    if action_full_name in composite_action_indirect_taint:
        action_default_inputs = get_action_default_inputs(action_info)
        if action_default_inputs:
            text += f"Its default input is " + action_default_inputs + ". "

        tainted_args = composite_action_indirect_taint[action_full_name]
        if len(tainted_args) == 1:
            text += f"If the input `{tainted_args[0]}` is tainted by taint sources, there will be a code injection vulnerability inside the {action_full_name}. "
        elif len(tainted_args) == 2:
            text += f"If the inputs `{tainted_args[0]}` or `{tainted_args[1]}` are tainted by taint sources, there will be a code injection vulnerability inside the {action_full_name}. "

    if text == f"{action_full_name} is a composite action. ":
        text = f"{action_full_name} is a non-vulnerable composite action. "

    return text

def handle_reusable_wf(wf):
    text = ""
    if wf in reusable_wf_direct_taint:
        text += f"{wf} is a vulnerable reusable workflow because it directly uses taint sources inside itself. "
    elif wf in reusable_wf_indirect_taint:
        if text == "":
            text += f"{wf} is a reusable workflow. "
        tainted_args = reusable_wf_indirect_taint[wf]
        if len(tainted_args) == 1:
            text += f"If the input `{tainted_args[0]}` is tainted by taint sources, there will be a code injection vulnerability inside the {wf}. "
        elif len(tainted_args) == 2:
            text += f"If the inputs `{tainted_args[0]}` or `{tainted_args[1]}` are tainted by taint sources, there will be a code injection vulnerability inside the {wf}. "
        elif len(tainted_args) == 3:
            text += f"If the inputs `{tainted_args[0]}`, `{tainted_args[1]}` or `{tainted_args[2]}` are tainted by taint sources, there will be a code injection vulnerability inside the {wf}. "
    else:
        text += f"{wf} is a non-vulnerable reusable workflow. "
    return text


taint_sources = "Here is the list of taint sources for GitHub Workflows: [" 
taint_sources += ", ".join(GITHUB_TAINT_LIST)
taint_sources += ", "
taint_sources += ", ".join(GITHUB_TAINT_CI_OBJECT_LIST)
taint_sources += "]. "
prompt_1 = "Is there any code injection vulnerability in the following GitHub Workflow? "
prompt_2 = {
    "a": "input flow action vulnerability (i.e., Where the taint originates in the workflow and flows in a sink inside the action)",
    "b": "direct flow action vulnerability (i.e., Where the taint originates inside the action and flows into a sink inside the action itself)",
    "c": "output flow action vulnerability (i.e., Where the taint originates inside the action and flows in a sink outside the action)",
    "d": "input reusable flow vulnerability (i.e., Where the taint originates in the workflow and flows in a sink inside the reusable workflow)",
    "e": "direct reusable flow vulnerability (i.e., Where the taint originates inside the reusable workflow and flows in a sink inside the reusable workflow itself)",
    # "f": "output reusable flow vulnerability (i.e., Where the taint originates inside the reusable workflow and flows in a sink outside the reusable workflow)",
    "g": "direct code injection vulnerability (i.e., Where the taint originates in the workflow and flows into a sink in the same workflow. The taint can also pass through actions and reusable workflows)"
}
prompt_3 = "Is there any code injection vulnerability in the following GitHub Workflow? Hint 1: " + taint_sources

source = connect_to_collection('LLM4wf','DatasetIII')
action_collection = connect_to_collection("git-reactions", "actions_col")
cursor = source.find()
docs = [doc for doc in cursor]
for doc in docs:
    action_hint_message = ""
    # Get action data flow information
    for action in doc["ir"]["dependencies"]["actions"]:
        if action["type"] == "gh_local_action":
            action_hint_message += f"{action['name']} is a local action and it is vulnerable if any one of the inputs is tainted by taint sources. "
            continue
        elif action["type"] == "gh_docker_action":
            action_hint_message += f"{action['name']} is a docker action and it is vulnerable if any one of the inputs is tainted by taint sources. "
            continue

        action_info = get_action(action_collection, action["name"], action["version"])
        if action_info['type'] == "docker":
            action_hint_message += handle_docker_action(action_info)
        elif action_info['type'] == "node12" or action_info['type'] == "node16":
            action_hint_message += handle_node1216_action(action_info)
        elif action_info['type'] == "composite":   
            action_hint_message += handle_composite_action(action_info)
        else:
            action_hint_message += f"{action['name']} is an unknown action and it is vulnerable if any one of the inputs is tainted by taint sources. "

    reusable_wf_hint_message = ""
    for wf in doc["ir"]["dependencies"]["workflows"]:
        reusable_wf_hint_message += handle_reusable_wf(wf)        
    
    hintmessage = action_hint_message + reusable_wf_hint_message
    
    prompts = {}
    prompts["prompt1"] = prompt_1
    prompts["prompt3"] = prompt_3 if hintmessage == "" else prompt_3 + f"Hint 2: {hintmessage}"

    if "updated_alerts" not in doc:
        random_type = random.choice(["a", "b", "c", "d", "e", "g"])
        prompts["prompt2"] = f"Is there any {prompt_2[random_type]} in the following GitHub Workflow? "
    else:
        alert_types = set()
        for alert in doc["updated_alerts"]:
            alert_types.add(alert["type"])
        if len(alert_types) == 1:
            prompts["prompt2"] = f"Is there any {prompt_2[alert_types.pop()]} in the following GitHub Workflow? " 
        elif len(alert_types) == 2:
            prompts["prompt2"] = f"Is there any {prompt_2[alert_types.pop()]} or {prompt_2[alert_types.pop()]} in the following GitHub Workflow? "
        elif len(alert_types) == 3:
            prompts["prompt2"] = f"Is there any {prompt_2[alert_types.pop()]}, {prompt_2[alert_types.pop()]} or {prompt_2[alert_types.pop()]} in the following GitHub Workflow? "
        else:
            print(doc["_id"])      

    source.update_one({"_id": doc["_id"]}, {"$set": {"vul_detection_prompts": prompts}})

    


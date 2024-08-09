from bson import ObjectId
from utils import is_taint_source, connect_to_collection, hardcoded_wrong_type_4, hardcoded_wrong_type_400, hardcoded_wrong_type_14

"""
type 100 : sinks in composite action, orginates from workflow or composite action itself

type:   
    a : the taint originates in the workflow and flows in a sink inside the action, taint may be an argument or env
        <== type 5 : sink inside local action
        <== type 7 : sink inside docker action
        <== type 8 : sink inside js action def docker
        <== type 9 : sink inside unknown action
        <== type 1/11 : sink inside js action node12/16
        <== type 2/12 : sink inside js action node12/16
        <== some of type 400 : sinks in composite action, orginates from workflow or composite action itself

    b : the taint originates inside the action and flows in a sink inside the action itself
        <== type 14 : js action node12/16
        <== some of type 400 : sinks in composite action, orginates from workflow or composite action itself
    
    c : the taint originates inside the action and flows in a sink outside the action
        <== some of type 4 : sinks in the workflow, maybe originate from taint sources, step output, env

    d : the taint originates in the workflow and flows in a sink inside the reusable workflow
        <== type 10: sinks in reusable workflow, orginates from workflow
        <== some of type 40 : sinks in reusable workflow, orginates from workflow or reusable workflow itself
        <== type 80 : sinks in reusable workflow, orginates from workflow

    e : the taint originates inside the reusable workflow and flows in a sink inside the reusable workflow itself
        <== some of type 40 : sinks in reusable workflow, orginates from workflow or reusable workflow itself

    f : the taint originates inside the reusable workflow and flows in a sink outside the reusable workflow

    g : the taint originates in the workflow and flows into a sink in the workflow after passthrough action or reusable workflow
        <== some of type 4 : sinks in the workflow, maybe originate from taint sources, step output, env
"""

wrong_type_4 = set()
wrong_type_400 = set()
wrong_type_40 = set()
wrong_type_14 = set()
wrong_type_100 = set()
wrong_type_others = set()
test = set()

def check_taint_arg_root(tainted_arg_root):
    # check if tainted_arg_root is a correct taint source
    if "||" in tainted_arg_root: 
        # print("tainted_arg_root: " + str(tainted_arg_root))
        roots = tainted_arg_root.split("||")
        tainted_arg_root = None
        for root in roots:
            root = root.strip()
            if is_taint_source(root):
                if not tainted_arg_root:
                    tainted_arg_root = root
                else:
                    tainted_arg_root += ", " + root
        # print("tainted_arg_root: " + str(tainted_arg_root))
        if not tainted_arg_root: # false positive case: github.event.issue != null && github.event.issue.user.login || github.event.pull_request.user.login 
            return None
    elif "==" in tainted_arg_root: # false positive case: github.event.comment.body == '/approve'
        return None
    elif not is_taint_source(tainted_arg_root):
        return None
    return tainted_arg_root

def add_line_numbers(input_string):
    lines = input_string.split('\n')
    max_width = len(str(len(lines)))

    formatted_lines = []
    for i, line in enumerate(lines, start=1):
        line_number = str(i).rjust(max_width)
        formatted_lines.append(f"{line_number}: {line}")

    result_string = '\n'.join(formatted_lines)
    return result_string

def find_run_line_number(yaml, job_id, run_num):
    found_job = False
    workflow_yaml = yaml.split('\n')
    jobs_line = 0
    while not workflow_yaml[jobs_line].startswith('jobs:'):
        jobs_line += 1
    for i in range(jobs_line, len(workflow_yaml)):
        line = workflow_yaml[i].strip()
        if line.startswith('-'):
            line = line[1:].strip()
        if line.startswith('#'):
            continue
        if not found_job and line.startswith(job_id + ':'):
            found_job = True
        elif found_job and (line.startswith('run:') or line.startswith('run :') or line.startswith('run  :')):
            if run_num == 1:
                return i + 1
            else:
                run_num -= 1
    return 0
    
def find_uses_line_number(yaml, job_id, uses_num, action_name):
    found_job = False
    workflow_yaml = yaml.split('\n')
    jobs_line = 0
    while not workflow_yaml[jobs_line].startswith('jobs:'):
        jobs_line += 1
    for i in range(jobs_line, len(workflow_yaml)):
        line = workflow_yaml[i].strip()
        if line.startswith('-'):
            line = line[1:].strip()
        if line.startswith('#'):
            continue
        if not found_job and line.startswith(job_id + ':'):
            found_job = True
        elif found_job and (line.startswith('uses:') or line.startswith('uses :')):
            if uses_num == 1 and action_name in line:
                return i + 1
            else:
                uses_num -= 1
    return 0

def find_job_uses_line_number(yaml, job_id, workflow_name):
    found_job = False
    workflow_yaml = yaml.split('\n')
    jobs_line = 0
    while not workflow_yaml[jobs_line].startswith('jobs:'):
        jobs_line += 1
    for i in range(jobs_line, len(workflow_yaml)):
        line = workflow_yaml[i].strip()
        if line.startswith('-'):
            line = line[1:].strip()
        if line.startswith('#'):
            continue
        if not found_job and line.startswith(job_id + ':'):
            found_job = True
        elif found_job and (line.startswith('uses:') or line.startswith('uses :')):
            if workflow_name in line:
                return i + 1
            else:
                return 0
    return 0

def convert_to_hashable(obj):
    if isinstance(obj, list):
        return tuple(obj)
    elif isinstance(obj, dict):
        return frozenset((key, convert_to_hashable(value)) for key, value in obj.items())
    else:
        return obj

def remove_duplicates(lst):
    seen = set()
    result = []

    for d in lst:
        hashable_dict = convert_to_hashable(d)

        if hashable_dict not in seen:
            seen.add(hashable_dict)
            result.append(d)

    return result

def handle_type_4(id, details, ir, yaml):
    shell_cmd = details['shell_cmd']
    flag = 0
    job_ids = []
    run_nums = []
    for taskgroup_name, taskgroup in ir['taskgroups'].items():
        run_num = 0
        if not taskgroup['workflow_step']:
            for task_name, task in taskgroup['tasks'].items():
                if task['exec']['type'] == "shell_cmd":
                    run_num += 1
                    if shell_cmd == task['exec']['command']:
                        flag += 1
                        job_ids.append(taskgroup_name)
                        run_nums.append(run_num)
                        
    if not flag:
        wrong_type_4.add(id)
        return None
    
    line_nums = [find_run_line_number(yaml, job_ids[i], run_nums[i]) for i in range(flag)] 
    
    taint_result = details['TaintRes'][0] # confirmed that only one taint result
    type = "g"
    tainted_arg = details['tainted_var']
    tainted_arg_full = None
    tainted_arg_type = None
    tainted_arg_root = taint_result['path'][0][0]

    tainted_arg_root = check_taint_arg_root(tainted_arg_root)
    if not tainted_arg_root and taint_result['path'][0][1] != "jscontext_output":
        wrong_type_4.add(id)
        return None

    # # check if tainted_arg_root is a correct taint source
    # if "||" in tainted_arg_root: 
    #     # print("tainted_arg_root: " + str(tainted_arg_root))
    #     roots = tainted_arg_root.split("||")
    #     tainted_arg_root = None
    #     for root in roots:
    #         root = root.strip()
    #         if is_taint_source(root):
    #             if not tainted_arg_root:
    #                 tainted_arg_root = root
    #             else:
    #                 tainted_arg_root += ", " + root
    #     # print("tainted_arg_root: " + str(tainted_arg_root))
    #     if not tainted_arg_root: # false positive case: github.event.issue != null && github.event.issue.user.login || github.event.pull_request.user.login
    #         wrong_type_4.add(id) 
    #         return None
    # elif "==" in tainted_arg_root: # false positive case: github.event.comment.body == '/approve'
    #     wrong_type_4.add(id) 
    #     return None
    # elif not is_taint_source(tainted_arg_root):
    #     if taint_result['path'][0][1] != "jscontext_output":
    #         wrong_type_4.add(id) 
    #         return None

    # get tainted_arg_type    
    if len(taint_result['path'][-1]) != 2:
        if "env." + taint_result['path'][-1] in shell_cmd:
            tainted_arg_type = "env"
        elif "outputs." + taint_result['path'][-1] in shell_cmd:
            tainted_arg_type = "shell_output"
        else:
            return "missing"
    else:
        tainted_arg_type = taint_result['path'][-1][1]

    if tainted_arg_type == "env" or tainted_arg_type == "shell_env":
        tainted_arg_full = "env." + tainted_arg
    elif tainted_arg_type == "shell_output":
        tainted_arg_full = "steps." + tainted_arg
        tainted_arg = taint_result['name']
    elif tainted_arg_type == "jsaction_output" or tainted_arg_type == "jscontext_output":
        type = "c"
        tainted_arg_full = "steps." + tainted_arg
        tainted_arg = taint_result['name']
        tainted_arg_root = None
    elif tainted_arg_type == "context":
        tainted_arg = "github." + tainted_arg
        tainted_arg_full = taint_result['name']
        if tainted_arg != tainted_arg_root:
            tainted_arg = tainted_arg_root
    else:
        return "missing"

    taint_summary = []
    for line_num in line_nums:
        taint_summary.append(
        {
            "type" : type,
            "shell_cmd(action)" : shell_cmd,
            "line_num" : line_num,
            "tainted_var" : tainted_arg,
            "tainted_var_full" : tainted_arg_full,
            "tainted_var_root" : tainted_arg_root,
            "tainted_var_type" : tainted_arg_type
        })
    return taint_summary

def handle_type_400(id, details, ir, yaml):
    vul_action = details['composite_action']
    flag = 0
    job_ids = []
    uses_nums = []
    step_ids = []
    for taskgroup_name, taskgroup in ir['taskgroups'].items():
        uses_num = 0
        if not taskgroup['workflow_step']:
            for task_name, task in taskgroup['tasks'].items():
                if task['exec']['type'] != "shell_cmd":
                    uses_num += 1
                    if vul_action == task['exec']['command']:
                        flag += 1
                        job_ids.append(taskgroup_name)
                        step_ids.append(task_name)
                        uses_nums.append(uses_num)
    if not flag:
        wrong_type_400.add(id)
        return None
    
    taint_result = details['TaintRes'][0] # confirmed that there is only one taint result
    taint_summary = []
    if len(taint_result['path'][-1]) == 2:
        tainted_arg_type = taint_result['path'][-1][1]
        if tainted_arg_type == "context" or tainted_arg_type == "shell_env" or tainted_arg_type == "default_input": # type b
            line_nums = [find_uses_line_number(yaml, job_ids[i], uses_nums[i], vul_action) for i in range(flag)]
            for line_num in line_nums:
                taint_summary.append({
                    "type" : "b",
                    "shell_cmd(action)" : vul_action,
                    "line_num" : line_num
                })
        elif tainted_arg_type == "arg": # type a
            line_nums = [find_uses_line_number(yaml, job_ids[i], uses_nums[i], vul_action) for i in range(flag)]
            if len(line_nums) > 1:
                valid_line_nums = []
                # validate arg
                for i in range(len(line_nums)):
                    arg_match = False
                    task = ir['taskgroups'][job_ids[i]]['tasks'][step_ids[i]]
                    for arg in task['args']:
                        if arg['name'] == taint_result['path'][-1][0] and taint_result['path'][-2][0] in arg['value']:
                            arg_match = True
                            break
                    if arg_match:
                        valid_line_nums.append(line_nums[i])
                line_nums = valid_line_nums
            
            tainted_arg = taint_result['name']
            tainted_arg_full = taint_result['name']
            tainted_arg_root = taint_result['path'][0][0]
            
            tainted_arg_root = check_taint_arg_root(tainted_arg_root)
            if not tainted_arg_root:
                wrong_type_400.add(id) 
                return None
                
            for line_num in line_nums:
                taint_summary.append({
                    "type" : "a",
                    "shell_cmd(action)" : vul_action,
                    "line_num" : line_num,
                    "tainted_var" : tainted_arg,
                    "tainted_var_full" : tainted_arg_full,
                    "tainted_var_root" : tainted_arg_root,
                    "tainted_var_type" : tainted_arg_type
                })         
    else: # special case: 9sako6/imgcmp@master action --> direct taint
          # special case: davoudarsalani/action-notify@master --> direct taint
        line_nums = [find_uses_line_number(yaml, job_ids[i], uses_nums[i], vul_action) for i in range(flag)]
        if vul_action == "9sako6/imgcmp@master" or vul_action == "davoudarsalani/action-notify@master":
            for line_num in line_nums:
                taint_summary.append({
                    "type" : "b",
                    "shell_cmd(action)" : vul_action,
                    "line_num" : line_num
                })
        else:
            return "missing"
    return taint_summary    
    
def handle_type_40(id, details, ir, yaml):
    vul_resuable_workflow = details['reusable_workflow'].replace('@', '/')
    flag = 0
    job_ids = []
    for taskgroup_name, taskgroup in ir['taskgroups'].items():
        if taskgroup['workflow_step']:
            task = taskgroup['tasks']['workflow']
            if vul_resuable_workflow == task['name'].split('@')[0]:
                vul_resuable_workflow = task['name']
                flag += 1
                job_ids.append(taskgroup_name)
    if not flag:
        wrong_type_40.add(id)
        return None
    
    line_nums = [find_job_uses_line_number(yaml, job_ids[i], vul_resuable_workflow) for i in range(flag)] # len(line_nums) == 1
    taint_summary = []
    taint_result = details['TaintRes'][0] # confirmed that there is only one taint result
    if len(taint_result['path'][-1]) == 2 and taint_result['path'][-1][1] == "wf_input":
        tainted_arg_root = taint_result['path'][0][0] 
        tainted_arg_root = check_taint_arg_root(tainted_arg_root)
        if not tainted_arg_root:
            wrong_type_40.add(id) 
            return None
        for line_num in line_nums:          
            taint_summary.append({
            "type" : "d",
            "reusable_workflow" : vul_resuable_workflow,
            "line_num" : line_num,
            "tainted_var" : taint_result['name'],
            "tainted_var_full" : taint_result['name'],
            "tainted_var_root" : tainted_arg_root,
            "tainted_var_type" : taint_result['path'][-1][1]})
        return taint_summary
    else:
        return "missing"
    
def handle_type_14(id, details, ir, yaml):
    vul_action = details['action']
    flag = 0
    job_ids = []
    uses_nums = []
    for taskgroup_name, taskgroup in ir['taskgroups'].items():
        uses_num = 0
        if not taskgroup['workflow_step']:
            for task_name, task in taskgroup['tasks'].items():
                if task['exec']['type'] != "shell_cmd":
                    uses_num += 1
                    if vul_action == task['exec']['command']:
                        flag += 1
                        job_ids.append(taskgroup_name)
                        uses_nums.append(uses_num)
    if not flag:
        wrong_type_14.add(id)
        return None
    
    line_nums = [find_uses_line_number(yaml, job_ids[i], uses_nums[i], vul_action) for i in range(flag)]
    taint_summary = []
    for line_num in line_nums:
        taint_summary.append({
            "type" : "b",
            "shell_cmd(action)" : vul_action,
            "line_num" : line_num
        })
    return taint_summary
    
def handle_type_100(id, details, ir, yaml):
    vul_action = details['composite_action']
    flag = 0
    job_ids = []
    uses_nums = []
    for taskgroup_name, taskgroup in ir['taskgroups'].items():
        uses_num = 0
        if not taskgroup['workflow_step']:
            for task_name, task in taskgroup['tasks'].items():
                if task['exec']['type'] != "shell_cmd":
                    uses_num += 1
                    if vul_action == task['exec']['command']:
                        flag += 1
                        job_ids.append(taskgroup_name)
                        uses_nums.append(uses_num)
    if not flag:
        wrong_type_100.add(id)
        return None
    
    line_nums = [find_uses_line_number(yaml, job_ids[i], uses_nums[i], vul_action) for i in range(flag)]
    taint_summary = []
    for line_num in line_nums:
        taint_summary.append({
            "type" : "b",
            "shell_cmd(action)" : vul_action,
            "line_num" : line_num
        })
    return taint_summary

def handle_type_others(id, details, ir, yaml):
    vul_action = None
    action_indices = ['action', 'def_docker_action', 'local_action', 'docker_action', 'unknown_action']
    for action in action_indices:
        if action in details:
            vul_action = details[action]
            break
    
    flag = 0
    job_ids = []
    uses_nums = []
    step_ids = []
    for taskgroup_name, taskgroup in ir['taskgroups'].items():
        uses_num = 0
        if not taskgroup['workflow_step']:
            for task_name, task in taskgroup['tasks'].items():
                if task['exec']['type'] != "shell_cmd":
                    uses_num += 1
                    if vul_action == task['exec']['command']:
                        flag += 1
                        job_ids.append(taskgroup_name)
                        step_ids.append(task_name)
                        uses_nums.append(uses_num)
    if not flag:
        wrong_type_others.add(id)
        return None
    
    line_nums = [find_uses_line_number(yaml, job_ids[i], uses_nums[i], vul_action) for i in range(flag)]
    taint_summary = []
    taint_result = details['TaintRes'][0] # confirmed that there is only one taint result
    tainted_arg = taint_result['name']
    tainted_arg_full = taint_result['name']
    tainted_arg_root = taint_result['path'][0][0]

    tainted_arg_root = check_taint_arg_root(tainted_arg_root)
    if not tainted_arg_root and taint_result['path'][0][1] != "jscontext_output":
        wrong_type_others.add(id)
        return None
    
    if len(line_nums) > 1:
        valid_line_nums = []
        # validate arg
        for i in range(len(line_nums)):
            arg_match = False
            task = ir['taskgroups'][job_ids[i]]['tasks'][step_ids[i]]
            for arg in task['args']:
                if arg['name'] == tainted_arg and taint_result['path'][-2][0] in arg['value']:
                    arg_match = True
                    break
            if arg_match:
                valid_line_nums.append(line_nums[i])
        line_nums = valid_line_nums

    for line_num in line_nums:
        taint_summary.append({
            "type" : "a",
            "shell_cmd(action)" : vul_action,
            "line_num" : line_num,
            "tainted_var" : tainted_arg,
            "tainted_var_full" : tainted_arg_full,
            "tainted_var_root" : tainted_arg_root,
            "tainted_var_type" : "arg"
        }) 
    return taint_summary

def handle_hardcoded_type(id, details, ir, yaml):
    summary_list = []
    if id in hardcoded_wrong_type_4:
        summary_list += hardcoded_wrong_type_4[id]
    if id in hardcoded_wrong_type_400:
        summary_list += hardcoded_wrong_type_400[id]
    if id in hardcoded_wrong_type_14:
        summary_list += hardcoded_wrong_type_14[id]
    
    if summary_list == []:
        return []
    
    # print(summary_list)
    res = []
    for summary in summary_list:
        if summary['type'] == "e":
            vul_resuable_workflow = summary['reusable_workflow']
            flag = 0
            job_ids = []
            for taskgroup_name, taskgroup in ir['taskgroups'].items():
                if taskgroup['workflow_step']:
                    task = taskgroup['tasks']['workflow']
                    if vul_resuable_workflow == task['name']:
                        flag += 1
                        job_ids.append(taskgroup_name)
            if not flag:
                print("Cannot find workflow in " + str(id))
                continue
            line_nums = [find_job_uses_line_number(yaml, job_ids[i], vul_resuable_workflow) for i in range(flag)] 
            for line_num in line_nums:
                res.append({
                    "type" : "e",
                    "reusable_workflow" : vul_resuable_workflow,
                    "line_num" : line_num
                })
        else:
            vul_action = summary['action']
            flag = 0
            job_ids = []
            uses_nums = []
            for taskgroup_name, taskgroup in ir['taskgroups'].items():
                uses_num = 0
                if not taskgroup['workflow_step']:
                    for task_name, task in taskgroup['tasks'].items():
                        if task['exec']['type'] != "shell_cmd":
                            uses_num += 1
                            if vul_action == task['exec']['command']:
                                flag += 1
                                job_ids.append(taskgroup_name)
                                uses_nums.append(uses_num)
            if not flag:
                print("Cannot find action in " + str(id))
                continue
            line_nums = [find_uses_line_number(yaml, job_ids[i], uses_nums[i], vul_action) for i in range(flag)]
            for line_num in line_nums:
                res.append({
                    "type" : "b",
                    "shell_cmd(action)" : vul_action,
                    "line_num" : line_num
                })
    return res
       
def main():
    source =  connect_to_collection('LLM4wf', 'VerifiedArgusResults-deduplicate')
    dest = connect_to_collection('LLM4wf', 'VerifiedArgusResults-update-taint-summary')
    cursor = source.find()
    for doc in cursor:
        id = doc['_id']
        yaml = add_line_numbers(doc['yaml'])
        ir = doc['ir']

        updated_alerts = []

        for alert in doc['alerts']:
            details= alert['details']
            if alert['type'] == 4:
                taint_summary_type_4 = handle_type_4(id, details, ir, doc['yaml'])
                if taint_summary_type_4 == "missing": 
                    print("missing:" + str(id))
                elif taint_summary_type_4:
                    updated_alerts += taint_summary_type_4

            elif alert['type'] == 400:
                taint_summary_type_400 = handle_type_400(id, details, ir, doc['yaml'])
                if taint_summary_type_400 == "missing": 
                    print("missing:" + str(id))
                elif taint_summary_type_400:
                    updated_alerts += taint_summary_type_400

            elif alert['type'] == 40:
                taint_summary_type_40 = handle_type_40(id, details, ir, doc['yaml'])
                if taint_summary_type_40 == "missing": 
                    print("missing:" + str(id))
                elif taint_summary_type_40:
                    updated_alerts += taint_summary_type_40

            elif alert['type'] == 14:
                taint_summary_type_14 = handle_type_14(id, details, ir, doc['yaml'])
                if taint_summary_type_14:
                    updated_alerts += taint_summary_type_14

            elif alert['type'] == 100:
                taint_summary_type_100 = handle_type_100(id, details, ir, doc['yaml'])
                if taint_summary_type_100:
                    updated_alerts += taint_summary_type_100

            else:
                taint_summary_type_others = handle_type_others(id, details, ir, doc['yaml'])
                if taint_summary_type_others:
                    updated_alerts += taint_summary_type_others

        updated_alerts += handle_hardcoded_type(id, details, ir, doc['yaml'])
        deduplicate_alerts = remove_duplicates(updated_alerts)
        if len(deduplicate_alerts) > 0 and str(id) != "63dd966380aa29a6fd488bfa" and str(id) != "63dd94a880aa29a6fd486c40" and str(id) != "63dd9511045fe2c0b7162fff":
            # add taint summary to doc
            doc["updated_alerts"] = deduplicate_alerts
            doc["updated_yaml"] = yaml
            dest.insert_one(doc)

    print(len(wrong_type_4)) # 24
    print(len(wrong_type_400)) # 110
    print(len(wrong_type_40)) # 0
    print(len(wrong_type_14)) # 2
    print(len(wrong_type_100)) # 0

if __name__ == "__main__":
    main()
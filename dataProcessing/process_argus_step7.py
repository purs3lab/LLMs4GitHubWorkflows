from utils import connect_to_collection, format_list_strings

prompt_1 = "Please repair code injection vulnerabilities in the following GitHub Workflow. "
prompt_2 = "Please repair code injection vulnerabilities in the following GitHub Workflow. The vulnerability exists in the shell script starting from line "
Hint = "Hint: Avoid string interpolation by using an intermediate environment variable using a `env` tag to store the sensitive data, and then use the environment variable in the command under the `run` keyword by accessing it without the `${{ ... }}`. "

source = connect_to_collection('LLM4wf','DatasetIII')
cursor = source.find({'updated_alerts':{"$exists":True}})
docs = list(cursor)
print(len(docs))
for doc in docs:
    alerts = doc['updated_alerts']
    lines = set()
    for alert in alerts:
        type_ = alert['type']
        if type_ == 'g' or type_ == 'c':
            lines.add(str(alert['line_num']))
    if len(lines) == 0:
        continue
    sorted_lines = sorted(list(lines))
    prompts = {}
    prompts['prompt1'] = prompt_1
    prompts['prompt2'] = prompt_2 + format_list_strings(sorted_lines) + '. '
    prompts['prompt3'] = prompts['prompt2'] + Hint
    source.update_one({'_id': doc['_id']}, {"$set": {'vuln_fix_prompts': prompts}})
        
cursor = source.find()
docs = list(cursor)
print(len(docs))
for doc in docs:
    if 'updated_alerts' not in doc:
        source.update_one({'_id': doc['_id']}, {"$set": {'response_template': 'No\n'}})
    else:
        response_template = 'Yes\n'
        alerts = doc['updated_alerts']
        for alert in alerts:
            line_num = alert['line_num']
            if ('tainted_var_full' not in alert) or (alert['tainted_var_full'] is None):
                tainted_var = 'N/A'
            else:
                tainted_var = alert['tainted_var_full']  
            if ('tainted_var_root' not in alert) or (alert['tainted_var_root'] is None):
                taint_souce = 'N/A'
            else:
                taint_souce = alert['tainted_var_root'] 
            response_template += f"line number: {line_num} | tainted variable: {tainted_var} | taint source: {taint_souce}\n"
        source.update_one({'_id': doc['_id']}, {"$set": {'response_template': response_template}})
            
    
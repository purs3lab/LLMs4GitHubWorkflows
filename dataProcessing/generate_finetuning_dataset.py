import json
import random
import re

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON file: {e}")
        return None
    
def remove_comments(yaml_content):
    comment_pattern = re.compile(r'^\s*#.*$', re.MULTILINE)    
    yaml_content_without_comments = re.sub(comment_pattern, '', yaml_content)
    lines = yaml_content_without_comments.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)


# res = []

# wfgen = read_json_file('wfsgen-finetune.json')
# for item in wfgen:
#     random_number = random.randint(1, 5)
#     inp = item['prompt' + str(random_number)]
#     out = "```yaml\n" + remove_comments(item['yaml']) + "\n```" 
    
#     res.append({
#         "Instruction" : "You are a software engineer. Please generate a YAML file based on the user's input below. No additional explanation is needed. The output format should be ```yaml <Workflow>```. ",
#         "Input" : inp,
#         "Output" : out
#     })
    
# syntaxbug = read_json_file('wfsbugfinding-finetune.json')
# for item in syntaxbug:
#     random_number = random.randint(1, 2)
#     prpt = item['error_detection_prompts']['prompt'+str(random_number)] + '\n'
#     inp = '```yaml\n' + item['yaml'] + '\n```'
#     out = item['response_template']
#     res.append({
#         "Instruction" : 'You are a software engineer and help the user identify whether a GitHub Workflow has syntax errors or not. Output format should be: <Yes or No>| line number: <line num>. If the error is in the shell script, output the line number of the run key. If no syntax errors exist, line number is N/A. ',
#         "Input" : prpt + inp,
#         "Output" : out
#     })
    
# codeinjection = read_json_file('wfsvulfingding-finetune.json')

# for item in codeinjection:
#     random_number = random.randint(1, 3)
#     prpt = item['vul_detection_prompts']['prompt'+str(random_number)] + '\n'
#     inp = '```yaml\n' + item['yaml'] + '\n```'
#     out = item['response_template']
#     res.append({
#         "Instruction" : "You are a security engineer and help the user detect code injection vulnerabilities in the GitHub Workflow. If no vulnerabilities are detected, print No. Otherwise, print Yes followed by the line number of the run key(sink in the shell script) or the line number of the uses key(sink in the GitHub Action or Reusable Workflow), tainted variable, and the corresponding taint source. The output format should be: Yes | line number: <line number> | tainted variable: <tainted variable> | taint source: <taint source>. If vulnerabilities happen inside the GitHub Action or Reusable Workflow, both the tainted variable and the taint source are N/A. ",
#         "Input" : prpt + inp,
#         "Output" : out
#     })
    
# print(len(res))
# random.shuffle(res)

# with open('finetuning-dataset.json', 'w') as json_file:
#     json.dump(res, json_file)
    

res = []

wfgen = read_json_file('wfsgen-eval-large.json')
wfgen = wfgen[:800]
for item in wfgen:
    random_number = random.randint(1, 5)
    inp = item['prompt' + str(random_number)]
    out = "```yaml\n" + remove_comments(item['yaml']) + "\n```" 
    
    res.append({
        "Instruction" : "You are a software engineer. Please generate a YAML file based on the user's input below. No additional explanation is needed. The output format should be ```yaml <Workflow>```. ",
        "Input" : inp,
        "Output" : out
    })
print(len(wfgen))
    
syntaxbug = read_json_file('wfsbugfinding-eval.json')
syntaxbug = syntaxbug[:800]
for item in syntaxbug:
    random_number = random.randint(1, 2)
    prpt = item['error_detection_prompts']['prompt'+str(random_number)] + '\n'
    inp = '```yaml\n' + item['yaml'] + '\n```'
    out = item['response_template']
    res.append({
        "Instruction" : 'You are a software engineer and help the user identify whether a GitHub Workflow has syntax errors or not. Output format should be: <Yes or No>| line number: <line num>. If the error is in the shell script, output the line number of the run key. If no syntax errors exist, line number is N/A. ',
        "Input" : prpt + inp,
        "Output" : out
    })
print(len(syntaxbug))
    
codeinjection = read_json_file('wfsvulfingding-eval.json')
codeinjection = codeinjection[:800]
for item in codeinjection:
    random_number = random.randint(1, 3)
    prpt = item['vul_detection_prompts']['prompt'+str(random_number)] + '\n'
    inp = '```yaml\n' + item['yaml'] + '\n```'
    out = item['response_template']
    res.append({
        "Instruction" : "You are a security engineer and help the user detect code injection vulnerabilities in the GitHub Workflow. If no vulnerabilities are detected, print No. Otherwise, print Yes followed by the line number of the run key(sink in the shell script) or the line number of the uses key(sink in the GitHub Action or Reusable Workflow), tainted variable, and the corresponding taint source. The output format should be: Yes | line number: <line number> | tainted variable: <tainted variable> | taint source: <taint source>. If vulnerabilities happen inside the GitHub Action or Reusable Workflow, both the tainted variable and the taint source are N/A. ",
        "Input" : prpt + inp,
        "Output" : out
    })
print(len(codeinjection))

print(len(res))
random.shuffle(res)

with open('finetuning-testset.json', 'w') as json_file:
    json.dump(res, json_file)
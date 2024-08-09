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
 
# syntaxbug = read_json_file('./data/wfsbugfinding-eval.json')
# random.shuffle(syntaxbug)
# bug_sample = []
# no_bug_sample = []
# for item in syntaxbug:
#     new_item = {}
#     new_item['id'] = item['id']
#     new_item['yaml'] = item['yaml']
#     new_item['response_template'] = item['response_template']
#     for j in range(1, 3):
#         prompt = item['error_detection_prompts']['prompt'+str(j)] + '\n```yaml\n' + item['yaml'] + '\n```'
#         new_item['prompt'+str(j)] = prompt
#     if len(item['bug_info']) == 0:
#         no_bug_sample.append(new_item)
#     else:
#         new_item['bug_info'] = item['bug_info']
#         bug_sample.append(new_item)
    
# wfsbugfinding_eval_small = bug_sample[:100] + no_bug_sample[:100]
# random.shuffle(wfsbugfinding_eval_small)
# print(len(wfsbugfinding_eval_small)) # 200
# with open('./data/wfsbugfinding-eval-small.json', 'w') as file:
#     json.dump(wfsbugfinding_eval_small, file)

# wfsbugfinding_eval_large = bug_sample[100:2600] + no_bug_sample[100:2600]
# random.shuffle(wfsbugfinding_eval_large)
# print(len(wfsbugfinding_eval_large)) # 5000
# with open('./data/wfsbugfinding-eval-large.json', 'w') as file:
#     json.dump(wfsbugfinding_eval_large, file)
 
# syntaxbug = read_json_file('./data/wfsbugfinding-eval.json')
# random.shuffle(syntaxbug)
# bug_sample = []
# for item in syntaxbug:
#     if len(item['error_fix_prompts']) > 0:
#         new_item = {}
#         new_item['id'] = item['id']
#         new_item['yaml'] = item['yaml']
#         for j in range(1, 4):
#             prompt = item['error_fix_prompts']['prompt'+str(j)] + '\n```yaml\n' + item['yaml'] + '\n```'
#             new_item['prompt'+str(j)] = prompt
#         bug_sample.append(new_item)

# wfsbugfixing_eval_small = bug_sample[:200]
# random.shuffle(wfsbugfixing_eval_small)
# print(len(wfsbugfixing_eval_small)) # 200
# with open('./data/wfsbugfixing-eval-small.json', 'w') as file:
#     json.dump(wfsbugfixing_eval_small, file)

# wfsbugfixing_eval_large = bug_sample[200:2700]
# random.shuffle(wfsbugfixing_eval_large)
# print(len(wfsbugfixing_eval_large)) # 2500
# with open('./data/wfsbugfixing-eval-large.json', 'w') as file:
#     json.dump(wfsbugfixing_eval_large, file)
    

# codeinjection = read_json_file('./data/wfsvulfingding-eval.json')
# random.shuffle(codeinjection)
# print(len(codeinjection)) # 3800 
# vul = []
# not_vul = []
# for item in codeinjection:
#     new_item = {}
#     new_item['id'] = item['id']
#     new_item['yaml'] = item['yaml']
#     new_item['response_template'] = item['response_template']
#     for j in range(1, 4):
#         prompt = item['vul_detection_prompts']['prompt'+str(j)] + '\n```yaml\n' + item['yaml'] + '\n```'
#         new_item['prompt'+str(j)] = prompt
#     if len(item['alerts']) == 0:
#         not_vul.append(new_item)
#     else:
#         new_item['alerts'] = item['alerts']
#         vul.append(new_item)
    
# vul_num = 0
# wfsvulfingding_eval_small = vul[:80]
# wfsvulfingding_eval_small += not_vul[:80]
# random.shuffle(wfsvulfingding_eval_small)
# print(len(wfsvulfingding_eval_small)) # 160
# with open('./data/wfsvulfinding-eval-small.json', 'w') as file:
#     json.dump(wfsvulfingding_eval_small, file)

# vul_num_large = 0
# wfsvulfingding_eval_large = vul[80:] # 923
# wfsvulfingding_eval_large += not_vul[80:1003] # 923
# random.shuffle(wfsvulfingding_eval_large)
# print(len(wfsvulfingding_eval_large)) # 1846
# with open('./data/wfsvulfinding-eval-large.json', 'w') as file:
#     json.dump(wfsvulfingding_eval_large, file)
    
codeinjection = read_json_file('./data/wfsvulfingding-eval.json')
random.shuffle(codeinjection)
sample = []
for item in codeinjection:
    if len(item['vuln_fix_prompts']) > 0:
        new_item = {}
        new_item['id'] = item['id']
        new_item['yaml'] = item['yaml']
        for j in range(1, 4):
            prompt = item['vuln_fix_prompts']['prompt'+str(j)] + '\n```yaml\n' + item['yaml'] + '\n```'
            new_item['prompt'+str(j)] = prompt
        sample.append(new_item)
print(len(sample)) # 475
wfsvulfixing_eval_small = sample[:100]
random.shuffle(wfsvulfixing_eval_small)
print(len(wfsvulfixing_eval_small)) # 100
with open('./data/wfsvulfixing-eval-small.json', 'w') as file:
    json.dump(wfsvulfixing_eval_small, file)

wfsvulfixing_eval_large = sample[100:]
random.shuffle(wfsvulfixing_eval_large)
print(len(wfsvulfixing_eval_large)) # 375
with open('./data/wfsvulfixing-eval-large.json', 'w') as file:
    json.dump(wfsvulfixing_eval_large, file)
    

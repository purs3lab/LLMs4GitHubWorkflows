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

def write_json_file(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file)

# ref_dataset = read_json_file('./data/wfsbugfinding-eval.json')
# print(ref_dataset[0].keys()) # ['id', 'yaml', 'bug_info', 'error_detection_prompts', 'response_template', 'error_fix_prompts']

# # update wfsbugfixing-eval-small.json and wfsbugfixing-eval-large.json
# wfsbugfixing_eval = read_json_file('./data/wfsbugfixing-eval-large.json')
# for sample in wfsbugfixing_eval:
#     # print(sample.keys()) # (['id', 'yaml', 'prompt1', 'prompt2', 'prompt3'])
#     _id = sample['id']
#     ref_sample = next((s for s in ref_dataset if s['id'] == _id), None)
#     group = ref_sample['bug_info']['type']
#     sample['group'] = group
# write_json_file(wfsbugfixing_eval, './data/wfsbugfixing-eval-large.json')


ref_dataset2 = read_json_file('./data/wfsvulfingding-eval.json')
print(ref_dataset2[0].keys()) # ['id', 'yaml', 'alerts', 'vul_detection_prompts', 'response_template', 'vuln_fix_prompts']

# update wfsvulfixing-eval-small.json and wfsvulfixing-eval-large.json
wfsvulfixing_eval = read_json_file('./data/wfsvulfixing-eval-large.json')
for sample in wfsvulfixing_eval:
    # print(sample.keys()) # (['id', 'yaml', 'prompt1', 'prompt2', 'prompt3'])
    _id = sample['id']
    ref_sample = next((s for s in ref_dataset2 if s['id'] == _id), None)
    group = set()
    for alert in ref_sample['alerts']:
        if alert['type'] == 'c' or alert['type'] == 'g':
            group.add(alert['type'])
    group = tuple(sorted(list(group)))
    sample['group'] = group
write_json_file(wfsvulfixing_eval, './data/wfsvulfixing-eval-large.json')
import json
import random
def read_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)
    
def write_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def remove_line_numbers(input_string):
    lines = input_string.split('\n')
    max_width = len(str(len(lines)))

    format_lines = []
    for line in lines:
        format_lines.append(line[max_width + 1:])

    result_string = '\n'.join(format_lines)
    return result_string
    
# def pick_samples():
#     dataset = read_json('./data/wfsbugfinding-finetune.json')
#     samples = {}
#     for data in dataset:
#         if data['bug_info'] == {}:
#             continue
#         if data['bug_info']['type'] not in samples:
#             samples[data['bug_info']['type']] = []
#         samples[data['bug_info']['type']].append(data['id'])
#     sample_ids = []
#     for bug_type in samples:
#         sample_ids.extend(random.sample(samples[bug_type], 2))
#     res = []
#     for data in dataset:
#         if data['id'] in sample_ids:
#             yaml = remove_line_numbers(data['yaml'])
#             with open(f"./{data['id']}.yaml", "w") as f:
#                 f.write(yaml)
#             res.append(data)
#     write_json('./data/wfsbugfixing-examples.json', res)

# def pick_samples():
#     dataset = read_json('./data/wfsvulfingding-finetune.json')   

#     samples = {}
#     for data in dataset:
#         if data['alerts'] == {} or data['vuln_fix_prompts'] == {}:
#             continue
#         groups = set()
#         for alert in data['alerts']:
#             if alert['type'] == 'c' or alert['type'] == 'g':
#                 groups.add(alert['type'])
#         groups = tuple(sorted(list(groups)))
#         if groups not in samples:
#             samples[groups] = []
#         samples[groups].append(data['id'])
#     sample_ids = []
#     for group in samples:
#         sample_ids.extend(random.sample(samples[group], 3))
#     res = []
#     for data in dataset:
#         if data['id'] in sample_ids:
#             yaml = remove_line_numbers(data['yaml'])
#             with open(f"./{data['id']}.yaml", "w") as f:
#                 f.write(yaml)
#             res.append(data)
#     write_json('./data/wfsvulfixing-examples.json', res)

# if __name__ == '__main__':
#     pick_samples()
    
# dataset = read_json('./data/wfsbugfixing-examples.json')
# for data in dataset:
#     id = data['id']
#     with open(f"./data/{id}.yaml", "r") as workflow_file:
#         fixed = workflow_file.read()
#         data['fixed_yaml'] = fixed
# write_json('./data/wfsbugfixing-examples.json', dataset)

dataset = read_json('./data/wfsvulfixing-examples.json')
for data in dataset:
    id = data['id']
    with open(f"./data/{id}.yaml", "r") as workflow_file:
        fixed = workflow_file.read()
        data['fixed_yaml'] = fixed
write_json('./data/wfsvulfixing-examples.json', dataset)
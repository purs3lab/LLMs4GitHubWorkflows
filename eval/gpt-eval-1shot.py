from openai import OpenAI
from datasets import load_dataset
import time
import csv
import json
import argparse
import re
import random
client = OpenAI()

def remove_comments(yaml_content):
    comment_pattern = re.compile(r'^\s*#.*$', re.MULTILINE)    
    yaml_content_without_comments = re.sub(comment_pattern, '', yaml_content)
    lines = yaml_content_without_comments.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def process_example_data(example_data_path, task):
    data_examples = {}
    if task == "wfsgen":
        dataset = load_dataset("json", data_files=example_data_path, split="train", cache_dir='./huggingface_cache')
        for data in dataset:
            group = data['group']
            if group not in data_examples:
                data_examples[group] = data
    elif task == "wfsbugfind":
        dataset = load_dataset("json", data_files=example_data_path, split="train", cache_dir='./huggingface_cache')
        for data in dataset:
            group = data['bug_info']['type']
            if group not in data_examples:
                data_examples[group] = data
    elif task == "wfsvulfind":
        with open(example_data_path, 'r') as file:
            dataset = json.load(file)
        for data in dataset:
            group = set()
            for alert in data['alerts']:
                group.add(alert['type'])
            group = tuple(sorted(list(group)))
            if group not in data_examples:
                data_examples[group] = data
    elif task == "wfsbugfix":
        dataset = load_dataset("json", data_files=example_data_path, split="train", cache_dir='./huggingface_cache')
        for data in dataset:
            group = data['bug_info']['type']
            if group not in data_examples:
                data_examples[group] = []
            data_examples[group].append(data)
        for group in data_examples:
            data_examples[group] = random.choice(data_examples[group])
    elif task == "wfsvulfix":
        with open(example_data_path, 'r') as file:
            dataset = json.load(file)
        for data in dataset:
            group = set()
            for alert in data['alerts']:
                if alert['type'] == "c" or alert['type'] == "g":
                    group.add(alert['type'])
            group = tuple(sorted(list(group)))
            if group not in data_examples:
                data_examples[group] = []
            data_examples[group].append(data)
        for group in data_examples:
            data_examples[group] = random.choice(data_examples[group])
    else:
        print("Error: task name is not valid.")
        exit()
    return data_examples

def get_example(data, examples, level, task):
    eg_inp = ""
    eg_out = ""
    if task == "wfsgen":
        group = data['group']
        example = examples[group]
        eg_inp = example['prompt' + str(level)]
        eg_out = "```yaml\n" + remove_comments(example['yaml']) + "\n```"
    elif task == "wfsbugfind":
        group = data['bug_info']['type'] if data['bug_info'] else None
        if group in examples:
            example = examples[group]
        else:
            group = random.choice(list(examples.keys()))
            example = examples[group]
        eg_inp = example['error_detection_prompts']['prompt' + str(level)] + '\n```yaml\n' + example['yaml'] + '\n```'
        eg_out = example['response_template']
    elif task == "wfsvulfind":
        group = set()
        if data['alerts']:
            for alert in data['alerts']:
                group.add(alert['type'])
        group = tuple(sorted(list(group)))
        example = examples[group]
        eg_inp = example['vul_detection_prompts']['prompt' + str(level)] + '\n```yaml\n' + example['yaml'] + '\n```'
        eg_out = example['response_template']
    elif task == "wfsbugfix":        
        group = data['group']
        example = examples[group]
        eg_inp = example['error_fix_prompts']['prompt' + str(level)] + '\n```yaml\n' + example['yaml'] + '\n```'
        eg_out = '```yaml\n' + example['fixed_yaml'] + '\n```'
    elif task == "wfsvulfix":
        group = data['group']
        example = examples[tuple(group)]
        eg_inp = example['vuln_fix_prompts']['prompt' + str(level)] + '\n```yaml\n' + example['yaml'] + '\n```'
        eg_out = '```yaml\n' + example['fixed_yaml'] + '\n```'
    else:
        print("Error: task name is not valid.")
        exit()
    return eg_inp, eg_out

def get_num_prompts(task):
    num_prompts = 0
    if task == "wfsgen":
        num_prompts = 5
    elif task == "wfsbugfind":
        num_prompts = 2
    elif task == "wfsvulfind" or task == "wfsbugfix" or task == "wfsvulfix":
        num_prompts = 3
    else:
        print("Error: task name is not valid.")
        exit()
    return num_prompts

def get_system_content(task_name):
    res = None
    max_tokens = 0
    if task_name == "wfsgen":
        res = "You are a software engineer. Please generate a YAML file based on the user's input below. No additional explanation is needed. The output format should be ```yaml <Workflow>```. "
        max_tokens = 1024
    elif task_name == "wfsbugfind":
        res = "You are a software engineer and help the user identify whether a GitHub Workflow has syntax errors or not. Output format should be: <Yes or No>| line number: <line num>. If the error is in the shell script, output the line number of the run key. If no syntax errors exist, line number is N/A. "
        max_tokens = 30
    elif task_name == "wfsvulfind":
        res = "You are a security engineer and help the user detect code injection vulnerabilities in the GitHub Workflow. If no vulnerabilities are detected, print No. Otherwise, print Yes followed by the line number of the run key(sink in the shell script) or the line number of the uses key(sink in the GitHub Action or Reusable Workflow), tainted variable, and the corresponding taint source. The output format should be: Yes | line number: <line number> | tainted variable: <tainted variable> | taint source: <taint source>. If vulnerabilities happen inside the GitHub Action or Reusable Workflow, both the tainted variable and the taint source are N/A. "
        max_tokens = 100
    elif task_name == "wfsbugfix":
        res = "You are a software engineer. Please help the user fix syntax errors in the GitHub Workflow. Output format should be: ```yaml <Workflow>```. If the input workflow contains line numbers, please remove them from the output. "
        max_tokens = 2048
    elif task_name == "wfsvulfix":
        res = "You are a security engineer. Please help the user repair code injection vulnerabilities in the GitHub Workflow. Output format should be: ```yaml <Workflow>```. If the input workflow contains line numbers, please remove them from the output. "
        max_tokens = 2048
    else:
        print("Error: task name is not valid.")
        exit()
    return max_tokens, res
            
def call_gpt(instr, eg_inp, eg_out, inp, temperature, max_tokens, model):
    # ref: https://platform.openai.com/docs/api-reference/chat
    res = []
    retries = 3
    while retries > 0:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": instr}, 
                    {"role": "user", "content": eg_inp},
                    {"role": "assistant", "content": eg_out},
                    {"role": "user", "content": inp},
                ],
                # What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
                temperature=temperature, 
                # An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.
                top_p=1.0,
                # How many chat completion choices to generate for each input message.
                n=5, 
                # Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.
                frequency_penalty=0.0, 
                #Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.
                presence_penalty=0.0,
                max_tokens=max_tokens,
            )
            for i in range(len(response.choices)):
                res.append(response.choices[i].message.content)
            return res
        except Exception as e:
            print(f"Error: {e}")
            retries -= 1
            time.sleep(1)
    return []
    
def add_result_to_csv(data_row, file_path):
    with open(file_path, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(data_row)

def generate_wfs(csv_file_name, dataset, temperature, level, model_name, task, examples):
    if model_name == "gpt-3.5":
        model = "gpt-3.5-turbo"
    else:
        model = "FINETUNED_GPT_3.5_KEY"
    for data in dataset:
        max_tokens, instr = get_system_content(task)
        eg_inp, eg_out = get_example(data, examples, level, task)
        id = data["id"]
        inp = data["prompt" + str(level)]
        datarow = [id]
        results = call_gpt(instr, eg_inp, eg_out, inp, temperature, max_tokens, model)
        if len(results) == 5:
            for res in results:
                datarow.append(res)
            add_result_to_csv(datarow, "./results/" + csv_file_name)
        else:
            print(f"Error: id = {id}, the number of chat completion choices to generate is {len(results)}.")

def main(data_path, model_name, task, example_data_path, specified_temperature, specified_prompt_level):
    dataset_name = data_path.split("/")[-1].rstrip(".json")
    print(f"dataset_name: {dataset_name}")
    dataset = load_dataset("json", data_files=data_path, split="train", cache_dir='./huggingface_cache')
    examples = process_example_data(example_data_path, task)
    num_prompts = get_num_prompts(task)
    if specified_temperature:
        temperatures = [specified_temperature]
    else:
        temperatures =  [0.1, 0.3, 0.5, 0.7, 0.9]
    if specified_prompt_level:
        prompt_levels = [specified_prompt_level]
    else:
        prompt_levels = [i for i in range(1, num_prompts + 1)]
    
    for temperature in temperatures:
        for level in prompt_levels:
            csv_file_name = f"{dataset_name}_{model_name}_1shot_{temperature}_prompt{level}.csv"
            print(f"{csv_file_name} begins ......")
            header = ["_id", "gen_text_1", "gen_text_2", "gen_text_3", "gen_text_4", "gen_text_5"]
            add_result_to_csv(header, "./results/" + csv_file_name)
            generate_wfs(csv_file_name, dataset, temperature, level, model_name, task, examples)
            print(f"{csv_file_name} is finished......")
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, required=True)
    parser.add_argument("--example_data_path", type=str, required=True)
    parser.add_argument("--model", type=str, required=True, choices=["gpt-3.5", "finetuned-gpt-3.5"])
    parser.add_argument('--task', type=str, required=True, default="wfsgen", choices=["wfsgen", "wfsbugfind", "wfsvulfind", "wfsbugfix", "wfsvulfix"], help="task name")
    parser.add_argument('--specified_temperature', type=float, required=False, help="temperature value")
    parser.add_argument('--specified_prompt_level', type=int, required=False, help="prompt level")

    args = parser.parse_args()
    print(args)
    main(args.data_path, args.model, args.task, args.example_data_path, args.specified_temperature, args.specified_prompt_level)

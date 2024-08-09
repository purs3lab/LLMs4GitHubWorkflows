import re
import argparse
from datasets import load_dataset
from typing import List
import os
import csv
import ast
import random
import yaml

system_content = [
    "You are a software engineer. Please generate a YAML file based on the user's input below. No additional explanation is needed. The output format should be ```yaml <Workflow>```. ",
    "You are a software engineer. Please help the user fix syntax errors in the GitHub Workflow. Output format should be: ```yaml <Workflow>```. If the input workflow contains line numbers, please remove them from the output. ",
    "You are a security engineer. Please help the user repair code injection vulnerabilities in the GitHub Workflow. Output format should be: ```yaml <Workflow>```. If the input workflow contains line numbers, please remove them from the output. ",
]  

def remove_vulfix_info(s):
    s = s.replace(system_content[2], "")
    pattern1 = r"Please repair code injection vulnerabilities in the following GitHub Workflow. \n```yaml.*?```"
    pattern2 = r"Please repair code injection vulnerabilities in the following GitHub Workflow. The vulnerability exists in the shell script starting from line \d+(, \d+)*( and \d+)?. \n```yaml.*?```"
    pattern3 = r"Please repair code injection vulnerabilities in the following GitHub Workflow. The vulnerability exists in the shell script starting from line \d+(, \d+)*( and \d+)?. Hint: Avoid string interpolation by using an intermediate environment variable using a `env` tag to store the sensitive data, and then use the environment variable in the command under the `run` keyword by accessing it without the `\$\{\{\s?... \}\}`. \n```yaml.*?```"
    s = re.sub(pattern1, '', s, flags=re.DOTALL)
    s = re.sub(pattern2, '', s, flags=re.DOTALL)
    s = re.sub(pattern3, '', s, flags=re.DOTALL)
    result = re.sub('\n\s*\n', '\n', s)
    return result

def remove_vulfix_1shot_info(model, s):
    s = s.replace(system_content[2], "")
    if model == "starchat":
        pattern = r"Please repair code injection vulnerabilities in the following GitHub Workflow.[^\n]*\n```yaml.*?```\n+```yaml.*?```\n+Please repair code injection vulnerabilities in the following GitHub Workflow.[^\n]*\n```yaml.*?```"
    else:
        pattern = r"Please repair code injection vulnerabilities in the following GitHub Workflow.[^\n]*\n```yaml.*?```[^\n]*?```yaml.*?```[^\n]*?Please repair code injection vulnerabilities in the following GitHub Workflow.[^\n]*\n```yaml.*?```"
    s = re.sub(pattern, '', s, flags=re.DOTALL)
    result = re.sub('\n\s*\n', '\n', s)
    return result
    
def remove_bugfix_info(s):
    s = s.replace(system_content[1], "")
    pattern = r"Please fix syntax errors in the following GitHub Workflow.[^\n]*\n```yaml.*?```"
    s = re.sub(pattern, '', s, flags=re.DOTALL)
    result = re.sub('\n\s*\n', '\n', s)
    return result

def remove_bugfix_1shot_info(model, s):
    s = s.replace(system_content[1], "")
    if model == "starchat":
        pattern = r"Please fix syntax errors in the following GitHub Workflow.[^\n]*\n```yaml.*?```\n+```yaml.*?```\n+Please fix syntax errors in the following GitHub Workflow.[^\n]*\n```yaml.*?```"
    else:
        pattern = r"Please fix syntax errors in the following GitHub Workflow.[^\n]*\n```yaml.*?```[^\n]*?```yaml.*?```[^\n]*?Please fix syntax errors in the following GitHub Workflow.[^\n]*\n```yaml.*?```"
    s = re.sub(pattern, '', s, flags=re.DOTALL)
    result = re.sub('\n\s*\n', '\n', s)
    return result

def remove_wfsgen_info(s):
    result = s.replace(system_content[0], "")
    return result

def remove_wfsgen_1shot_info(model, s):
    s = s.replace(system_content[0], "")
    if model == "starchat":
        pattern = r"Generate a GitHub Workflow named .*?```yaml.*?```\n+Generate a GitHub Workflow named [^\n]*\n"
    else:
        pattern = r"Generate a GitHub Workflow named .*?```yaml.*?```.*?Generate a GitHub Workflow named [^\n]*\n"
    s = re.sub(pattern, '', s, flags=re.DOTALL)
    result = re.sub('\n\s*\n', '\n', s)
    return result


def remove_line_number(text):
    lines = text.split('\n')
    pattern = r"^\d+:"
    if not re.match(pattern, lines[0]):
        return text
    
    formatted_lines = []
    for line in lines:
        start = line.find(":")
        if start != -1:
            line = line[start+1:]
        formatted_lines.append(line)
    result_string = '\n'.join(formatted_lines)

    return result_string

def add_result_to_csv(data_row, file_path):
    with open(file_path, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(data_row)

def pattern_match(text):
    pattern = r'```(yaml|YAML|yml|YML)\s*([\s\S]*?)```'
    
    code_blocks = re.findall(pattern, text, re.MULTILINE)
    
    if len(code_blocks) == 1:
        block = code_blocks[0] 
        return block[1] 
    elif len(code_blocks) > 1:
        block = max(code_blocks, key=len)
        return block[1]
    return None

def remove_notes(text):
    lines = text.split('\n')
    start_index = 0
    end_index = len(lines)

    for i, line in enumerate(lines):
        if line.startswith("name:") or line.startswith("on:"):
            start_index = i
            break

    for i in range(start_index, len(lines)):
        if lines[i] == '' or lines[i].startswith(" ") or lines[i].startswith("#"):
            continue
        elif ":" not in lines[i] or lines[i].count(":") > 1:
            end_index = i
            break
        else:
            groups = lines[i].split(":")
            if ' ' in groups[0].strip():
                end_index = i
                break
        
    cleaned_text = '\n'.join(lines[start_index:end_index])

    return cleaned_text

def extract_workflow(text):
    extracted_wf = pattern_match(text)
    if extracted_wf:
        return extracted_wf
    cleaned_text = remove_notes(text)
    return cleaned_text
    
def find_csv_file(path: str) -> List[str]:
    csv_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))
    return csv_files

def main(model, task, data_source_path, data_save_path, remove_line_numbers):
    files_path = find_csv_file(data_source_path)
    for file_path in files_path:
        print(file_path)
        dataset = load_dataset("csv", data_files=file_path, split="train")
        res_path = data_save_path + '/' + file_path.split('/')[-1]
        print(res_path)
        add_result_to_csv(["_id", "wf_1", "wf_2", "wf_3", "wf_4", "wf_5"], res_path)
        for item in dataset:
            if model == "gpt":
                wf_id = str(item['_id'])
                data_row = [wf_id]
                indices = ['gen_text_1', 'gen_text_2', 'gen_text_3', 'gen_text_4', 'gen_text_5']         
                for index in indices:
                    gen_text = item[index]
                    if gen_text: # gen_text may be None
                        yaml_file = extract_workflow(gen_text)
                        if remove_line_numbers:
                            yaml_file = remove_line_number(yaml_file)
                    else:
                        yaml_file = ""
                    data_row.append(yaml_file)
                add_result_to_csv(data_row, res_path)
            elif model == "starchat" or model == "codellama":
                wf_id = ast.literal_eval(item['_id']).decode('utf-8')
                data_row = [wf_id]
                indices = ['gen_text_1', 'gen_text_2', 'gen_text_3', 'gen_text_4', 'gen_text_5']
                for index in indices:
                    gen_text = ast.literal_eval(item[index]).decode('utf-8')
                    if task == "wfsvulfix":
                        gen_text = remove_vulfix_info(gen_text)
                    elif task == "bugfix":
                        gen_text = remove_bugfix_info(gen_text)
                    elif task == "wfsgen":
                        gen_text = remove_wfsgen_info(gen_text)
                    elif task == "wfsgen-1shot":
                        gen_text = remove_wfsgen_1shot_info(model, gen_text)
                    elif task == "bugfix-1shot":
                        gen_text = remove_bugfix_1shot_info(model, gen_text)
                    elif task == "wfsvulfix-1shot":
                        gen_text = remove_vulfix_1shot_info(model, gen_text)
                    
                    if gen_text:
                        yaml_file = extract_workflow(gen_text)
                        if remove_line_numbers:
                            yaml_file = remove_line_number(yaml_file)
                    else:
                        yaml_file = ""
                    data_row.append(yaml_file)
                add_result_to_csv(data_row, res_path)
           

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True, choices=["gpt", "starchat", "codellama"])
    parser.add_argument("--task", type=str, required=True, choices=["wfsgen", "bugfix", "wfsvulfix", "wfsgen-1shot", "bugfix-1shot", "wfsvulfix-1shot"])
    parser.add_argument("--data_source_path", type=str)
    parser.add_argument("--data_save_path", type=str)
    parser.add_argument("--remove_line_numbers", action="store_true")
    args = parser.parse_args()
    print(args)
    main(args.model, args.task, args.data_source_path, args.data_save_path, args.remove_line_numbers)

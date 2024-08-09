import re
import argparse
from datasets import load_dataset
from typing import List
import os
import csv
import ast
import random
import yaml

system_content = "You are a security engineer and help the user detect code injection vulnerabilities in the GitHub Workflow. If no vulnerabilities are detected, print No. Otherwise, print Yes followed by the line number of the run key(sink in the shell script) or the line number of the uses key(sink in the GitHub Action or Reusable Workflow), tainted variable, and the corresponding taint source. The output format should be: Yes | line number: <line number> | tainted variable: <tainted variable> | taint source: <taint source>. If vulnerabilities happen inside the GitHub Action or Reusable Workflow, both the tainted variable and the taint source are N/A."

def add_result_to_csv(data_row, file_path):
    with open(file_path, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(data_row)

def process_0shot(s):
    s = s.replace(system_content, "")
    pattern = r"Is there [^\n]*? in the following GitHub Workflow\?[^\n]*\n```yaml.*?```"
    s = re.sub(pattern, '', s, flags=re.DOTALL)
    result = re.sub('\n\s*\n', '\n', s)
    res1 = re.search(r"(Yes|No)", result)
    if res1:
        text = res1.group(1) 
        if text == "No":
            return "No"
        else:
            vul_info = []
            pattern = r"line number:\s+(\d+)\s+\|\s+tainted variable:(.+?)\|\s+taint source:([^|\n]+)"
            blocks = re.findall(pattern, result)
            if blocks:
                for block in blocks:
                    vul_info.append(
                        {
                            "line number": block[0],
                            "tainted variable": block[1].strip(),
                            "taint source": block[2].strip()
                        }
                    )
            return vul_info
    else:
        return "not found"


def process_1shot(model, s):
    s = s.replace(system_content, "")
    if model == "starchat_1shot":
        pattern = r"Is there [^\n]*? in the following GitHub Workflow\?[^\n]*\n```yaml.*?```\n+(Yes|No).+?Is there [^\n]*? in the following GitHub Workflow\?[^\n]*\n```yaml.*?```"
    else:
        pattern = r"Is there [^\n]*? in the following GitHub Workflow\?[^\n]*\n```yaml.*?```.+?Is there [^\n]*? in the following GitHub Workflow\?[^\n]*\n```yaml.*?```"
    s = re.sub(pattern, '', s, flags=re.DOTALL)
    result = re.sub('\n\s*\n', '\n', s)
    res1 = re.search(r"(Yes|No)", result)
    if res1:
        text = res1.group(1) 
        if text == "No":
            return "No"
        else:
            vul_info = []
            pattern = r"line number:\s+(\d+)\s+\|\s+tainted variable:(.+?)\|\s+taint source:([^|\n]+)"
            blocks = re.findall(pattern, result)
            if blocks:
                for block in blocks:
                    vul_info.append(
                        {
                            "line number": block[0],
                            "tainted variable": block[1].strip(),
                            "taint source": block[2].strip()
                        }
                    )
            return vul_info
    else:
        return "not found"


def extract_answer(text):  
    if text.startswith("No"):
        return "No"
    elif text.startswith("Yes"):
        vul_info = []
        pattern = r"line number:\s+(\d+)\s+\|\s+tainted variable:([^\|]+)\|\s+taint source:([^|\n]+)"
        blocks = re.findall(pattern, text)
        if blocks:
            for block in blocks:
                vul_info.append(
                    {
                        "line number": block[0],
                        "tainted variable": block[1].strip(),
                        "taint source": block[2].strip()
                    }
                )
        return vul_info
    else:
        return "not found"
    
def find_csv_file(path: str) -> List[str]:
    csv_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))
    return csv_files

def main(model, data_source_path, data_save_path):
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
                    answer = extract_answer(gen_text)
                    data_row.append(answer)
                add_result_to_csv(data_row, res_path)
            else:
                wf_id = ast.literal_eval(item['_id']).decode('utf-8')
                data_row = [wf_id]
                indices = ['gen_text_1', 'gen_text_2', 'gen_text_3', 'gen_text_4', 'gen_text_5']
                for index in indices:
                    gen_text = ast.literal_eval(item[index]).decode('utf-8')
                    if model == "starchat_0shot":
                        text = process_0shot(gen_text)
                    elif model == "starchat_1shot":
                        text = process_1shot(model, gen_text)
                    elif model == "codellama_0shot":
                        text = process_0shot(gen_text)
                    elif model == "codellama_1shot":
                        text = process_1shot(model, gen_text)
                    data_row.append(text)
                add_result_to_csv(data_row, res_path)
           

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, choices=["gpt", "starchat_0shot", "starchat_1shot", "codellama_0shot", "codellama_1shot"], required=True)
    parser.add_argument("--data_source_path", type=str)
    parser.add_argument("--data_save_path", type=str)
    args = parser.parse_args()
    print(args)
    main(args.model, args.data_source_path, args.data_save_path)

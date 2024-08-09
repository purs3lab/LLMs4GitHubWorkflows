import re
import os
import csv
from typing import List
import argparse
from datasets import load_dataset
from nltk.translate.bleu_score import sentence_bleu

def remove_comments(yaml_content):
    comment_pattern = re.compile(r'^\s*#.*$', re.MULTILINE)    
    yaml_content_without_comments = re.sub(comment_pattern, '', yaml_content)
    lines = yaml_content_without_comments.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def add_result_to_csv(data_row, file_path):
    with open(file_path, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(data_row)

def find_csv_file(path: str) -> List[str]:
    csv_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))
    return csv_files

def fetch_data(data, wf_id):
    for item in data:
        if item['id'] == wf_id:
            return remove_comments(item['yaml'])
    return None

def main(data_path, ground_truth_path, target_path):
    ground_truth = load_dataset("json", data_files=ground_truth_path, split="train")
    csv_file_paths = find_csv_file(data_path)
    for csv_file_path in csv_file_paths:
        csv_file = load_dataset("csv", data_files=csv_file_path, split="train")
        res_path = target_path + '/' + csv_file_path.split('/')[-1]
        print(res_path)
        header = ["_id", "bleu_1", "bleu_2", "bleu_3", "bleu_4", "bleu_5"]
        add_result_to_csv(header, res_path)
        for item in csv_file:
            wf_id = str(item['_id'])
            reference = fetch_data(ground_truth, wf_id)
            if reference is not None:
                references = [reference.split()]
            else:
                print(f"Reference not found for {wf_id}")
                continue
            data_row = [wf_id]
            indices = ["wf_1", "wf_2", "wf_3", "wf_4", "wf_5"]
            for index in indices:
                candidate = item[index]
                if candidate is None:
                    bleu = 0
                else:
                    candidate = remove_comments(candidate)
                    candidate = candidate.split()
                    bleu = sentence_bleu(references,candidate)
                data_row.append(bleu)
            add_result_to_csv(data_row, res_path)
                

if __name__ == '__main__':
    # python analyze/wfsgen/calculate_bleu.py --data_path="result/extracted_yaml" --ground_truth_path="/data/wfsgen-eval-small.json" --target_path="analyze/wfsgen/bleu"
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str)
    parser.add_argument("--ground_truth_path", type=str)
    parser.add_argument("--target_path", type=str)
    args = parser.parse_args()
    main(args.data_path, args.ground_truth_path, args.target_path)
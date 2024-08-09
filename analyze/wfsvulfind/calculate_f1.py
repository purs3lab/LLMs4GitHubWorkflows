import re
import os
import csv
from typing import List
import argparse
from datasets import load_dataset
from sklearn.metrics import f1_score

def find_csv_file(path: str) -> List[str]:
    csv_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))
    return csv_files

def extract_name(name):
    name = name.split('/')[-1]
    name = name.replace('.csv', '')
    p = name.split('_')[0]
    name = name.replace(p, '')
    return name.lstrip('_')

def extract_details(name):
    name = name.split('_')
    return name[0] + '_' + name[1], float(name[2]), int(name[3].replace('prompt', ''))

def calculate_f1_score(csv_filename, labels):
    y_pred = []
    y_true = []
    with open(csv_filename, 'r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)  # Skip the header

        for row in csv_reader:
            y_true.append(labels[row[0]])
            yes_count = 0
            no_count = 0
            for item in row[1:]:
                if item == "not found":
                    continue
                elif item == "No":
                    no_count += 1
                else:
                    yes_count += 1
            if yes_count > no_count:
                y_pred.append(1)
            else:
                y_pred.append(0)
            
    f1 = f1_score(y_true, y_pred, pos_label=1, average='binary')
    return f1

def fetch_labels(ground_truth):
    labels = {}
    for item in ground_truth:
        if item['response_template'].startswith('Yes'):
            labels[item['id']] = 1
        else:
            labels[item['id']] = 0
    return labels

def print_results(results):
    for model_name in results:
        print("\n")
        print(f"Model: {model_name}")
        num_temp = 5
        num_prompt = len(results[model_name]) // num_temp
        header = f"    "
        for i in range(num_prompt):
            header += f"prompt{i + 1} "
        print(header)
        for i in range(num_temp):
            temp = round(i * 0.2 + 0.1, 1)
            text = f"{temp} "
            for j in range(num_prompt):
                t = results[model_name][i * num_prompt + j]
                text += f"{t[2]}   "
            print(text)

def main(data_path, ground_truth_path):
    ground_truth = load_dataset("json", data_files=ground_truth_path, split="train")
    labels = fetch_labels(ground_truth)
    results = {}
    csv_file_paths = find_csv_file(data_path)
    for csv_file_path in csv_file_paths:
        csv_file_name = extract_name(csv_file_path)
        model_name, temperature, prompt = extract_details(csv_file_name)
        if model_name not in results:
            results[model_name] = []
        f1_score = calculate_f1_score(csv_file_path, labels)
        f1_score = round(f1_score * 100, 2) 
        f1 = str(f1_score).ljust(5, '0')
        results[model_name].append((temperature, prompt, f1))

    for model_name in results:
        results[model_name] = sorted(results[model_name], key=lambda x: (x[0], x[1]))
        print(results[model_name])
    
    print_results(results)
                

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str)
    parser.add_argument("--ground_truth_path", type=str)
    args = parser.parse_args()
    main(args.data_path, args.ground_truth_path)
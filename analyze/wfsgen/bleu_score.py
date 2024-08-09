import csv
import os
import argparse
def find_csv_file(path: str) -> list[str]:
    csv_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))
    return csv_files

def calculate_avg_scores(csv_filename):
    total_bleu_score = 0
    total_count = 0
    with open(csv_filename, 'r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)  # Skip the header

        for row in csv_reader:
            best_bleu_score = 0
            total_count += 1
            for score in row[1:]:
                if float(score) > best_bleu_score:
                    best_bleu_score = float(score)
            total_bleu_score += best_bleu_score
                
    return total_bleu_score, total_count

def extract_name(name):
    name = name.split('/')[-1]
    name = name.replace('.csv', '')
    p = name.split('_')[0]
    name = name.replace(p, '')
    return name.lstrip('_')

def extract_details(name):
    name = name.split('_')
    return name[0] + '_' + name[1], float(name[2]), int(name[3].replace('prompt', ''))

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
        

def main(dir):
    csv_files = find_csv_file(dir)
    results = {}
    for csv_filename in csv_files:
        name = extract_name(csv_filename)
        model_name, temperature, prompt = extract_details(name)
        if model_name not in results:
            results[model_name] = []
        total_bleu_score, total_count = calculate_avg_scores(csv_filename)
        avg_bleu = round(total_bleu_score / total_count * 100, 2) 
        avg_bleu = str(avg_bleu).ljust(5, '0')
        results[model_name].append((temperature, prompt, avg_bleu))
        
    for model_name in results:
        results[model_name] = sorted(results[model_name], key=lambda x: (x[0], x[1]))
        print(model_name)
        print(results[model_name])
    
    # print_results(results)
        
              
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str)
    args = parser.parse_args()
    print(args)
    main(args.dir)
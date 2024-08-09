import subprocess
import os
import csv
from typing import List
import argparse
from datasets import load_dataset

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

def main(data_path, target_path):
    csv_file_paths = find_csv_file(data_path)
    for csv_file_path in csv_file_paths:
        csv_file = load_dataset("csv", data_files=csv_file_path, split="train")
        res_path = target_path + '/' + csv_file_path.split('/')[-1]
        print(res_path)
        header = ["_id", "static_check_1", "static_check_2", "static_check_3", "static_check_4", "static_check_5"]
        add_result_to_csv(header, res_path)
        for item in csv_file:
            wf_id = str(item['_id'])
            data_row = [wf_id]
            indices = ["wf_1", "wf_2", "wf_3", "wf_4", "wf_5"]
            for index in indices:
                new_id = wf_id + '-' + index
                yaml_file = item[index]
                if yaml_file is None:
                    data_row.append("not found")
                    continue
                yaml_file_path = target_path + '/' + new_id + '.yaml'
                with open(yaml_file_path, "w") as f:
                    f.write(yaml_file)
                command = ["./actionlint", "-ignore", "shellcheck reported issue in this script:.*:warning:", "-ignore", "shellcheck reported issue in this script:.*:info:", "-ignore", "shellcheck reported issue in this script:.*:style:", "-ignore", 'workflow command "set-output" was deprecated', "-ignore", 'workflow command "save-state" was deprecated', "-ignore", "is potentially untrusted", "-ignore", "label .* is unknown", "-format", "{{json .}}", yaml_file_path]
                try:
                    saved_output = ""
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    while True:
                        output = process.stdout.readline()
                        saved_output += output.decode('utf-8')
                        if (not output):
                            break
                    process.wait()
                    return_code = process.returncode
                    # actionlint command exits with one of the following exit statuses.
                    # 0: It ran successfully and no problem was found.
                    # 1: It ran successfully and some problem was found.
                    # 2: It failed due to invalid command line option.
                    # 3: It failed due to some fatal error.
                    if (return_code == 0):
                        data_row.append("passed")
                    elif (return_code == 1):
                        data_row.append(saved_output)
                    else:
                        print("Error...")
                        data_row.append("run error")
                except subprocess.TimeoutExpired:
                    print("Timeout Error...")
                    data_row.append("run error")
                    pass
                except subprocess.CalledProcessError as e:
                    print("Call Process Error...")
                    data_row.append("run error")
                    pass
                finally:
                    # Delete wf_file whether an exception occurred or not
                    if os.path.exists(yaml_file_path):
                        os.remove(yaml_file_path)
            add_result_to_csv(data_row, res_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str)
    parser.add_argument("--target_path", type=str)
    args = parser.parse_args()
    main(args.data_path, args.target_path)

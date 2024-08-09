import json
import random

LENGTH = 1600

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

def handle_datasetII(data):
    random.shuffle(data)
    no_bug = []
    bug = []
    for item in data:
        if len(item['bug_info']) == 0:
            no_bug.append(item)
        else:
            bug.append(item)
    length = LENGTH
    trainset = bug[:length]
    testset = bug[length:]
    print(f"Buggy Workflows in trainset: {len(trainset)}")
    print(f"Buggy Workflows in testset: {len(testset)}")

    trainset.extend(no_bug[:length])
    testset.extend(no_bug[length:])

    print(f"Total Workflows in trainset: {len(trainset)}")
    print(f"Total Workflows in testset: {len(testset)}")

    random.shuffle(trainset)
    random.shuffle(testset)

    return trainset, testset
    

def handle_datasetIII(data):
    random.shuffle(data)
    not_vul = []
    vul = []
    for item in data:
        if len(item['alerts']) == 0:
            not_vul.append(item)
        else:
            vul.append(item)

    length = LENGTH
    trainset = vul[:length]
    testset = vul[length:]
    print(f"Vulnerable Workflows in trainset: {len(trainset)}")
    print(f"Vulnerable Workflows in testset: {len(testset)}")

    train_vul = 0
    test_vul = 0
    for item in trainset:
        train_vul += len(item['alerts'])
    for item in testset:
        test_vul += len(item['alerts'])
    print(f"Vulnerabilities in trainset: {train_vul}")
    print(f"Vulnerabilities in testset: {test_vul}")

    trainset.extend(not_vul[:length])
    testset.extend(not_vul[length:])

    print(f"Total Workflows in trainset: {len(trainset)}")
    print(f"Total Workflows in testset: {len(testset)}")

    random.shuffle(trainset)
    random.shuffle(testset)

    return trainset, testset
    

if __name__ == "__main__":
    datasetII = read_json_file('./gen_dataset/DatasetII.json')
    trainset2, testset2 = handle_datasetII(datasetII)
    with open('wfsbugfinding-finetune.json', 'w') as file:
        json.dump(trainset2, file)
    with open('wfsbugfinding-eval.json', 'w') as file:
        json.dump(testset2, file)

    datasetIII = read_json_file('DatasetIII.json')
    trainset3, testset3 = handle_datasetIII(datasetIII)
    with open('wfsvulfingding-finetune.json', 'w') as file:
        json.dump(trainset3, file)
    with open('wfsvulfingding-eval.json', 'w') as file:
        json.dump(testset3, file)
    

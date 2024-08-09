from utils import connect_to_collection
import random
import json
source = connect_to_collection('LLM4wf','DatasetII')

"""
    Type: unexpected mapping value, Count: 1617
    Type: deprecated command usage, Count: 1642
    Type: invalid Webhook event configuration, Count: 31953
    Type: invalid action usage, Count: 3152
    Type: invalid shell command, Count: 1402
    Type: unexpected/invalid identifier, Count: 5550
    Type: None, Count: 62920
    Type: invalid glob pattern, Count: 343
    Type: invalid reusable workflow call, Count: 11
    Type: invalid permissions configuration, Count: 11
    Type: invalid matrix configuration, Count: 280
    Type: invalid job dependency, Count: 2
    Type: invalid expression embedded with ${{ }} syntax, Count: 16953
    Type: invalid credential usage, Count: 3
    """
def type_distribution():
    bug_types = {}
    pipeline = [
        {"$group": {"_id": "$bug_info.type", "count": {"$sum": 1}}}
    ]
    result = list(source.aggregate(pipeline))
    for entry in result:
        print(f"Type: {entry['_id']}, Count: {entry['count']}")
        bug_types[entry['_id']] = entry['count']
    return bug_types

def generate_prompts(bug_types):
    cursor = source.find()
    docs = list(cursor)
    for doc in docs:
        if doc['syntax_error']:
            error_detection_prompts = {
                "prompt1": "Is there a syntax error in the following GitHub Workflow? ",
                "prompt2": f"Is there a/an {doc['bug_info']['type']} in the following GitHub Workflow? "
            }
            error_fix_prompts =  {
                "prompt1": "Please fix syntax errors in the following GitHub Workflow.", 
                "prompt2": f"Please fix syntax errors in the following GitHub Workflow. The syntax error exists in line {doc['bug_info']['line_num']}. ",
                "prompt3": f"Please fix syntax errors in the following GitHub Workflow. The syntax error exists in line {doc['bug_info']['line_num']}. Hint: {doc['bug_info']['message']}. "
            }
            response_template = f"Yes | line number: {doc['bug_info']['line_num']}"
            source.update_one({'_id': doc['_id']}, {"$set": {'error_detection_prompts': error_detection_prompts, 'error_fix_prompts': error_fix_prompts, 'response_template': response_template}})
        else:
            random_bug = random.choice(list(bug_types.keys()))
            error_detection_prompts = {
                "prompt1": "Is there a syntax error in the following GitHub Workflow? ",
                "prompt2": f"Is there a/an {random_bug} in the following GitHub Workflow? "
            }
            response_template = "No | line number: N/A"
            source.update_one({'_id': doc['_id']}, {"$set": {'error_detection_prompts': error_detection_prompts, 'response_template': response_template}})
        
def generate_dataset():
    cursor = source.find()
    docs = list(cursor)
    print(len(docs))
    data = []
    for doc in docs:
        data.append({
            "id": str(doc["_id"]),
            "yaml": doc['yaml'],
            "bug_info": doc['bug_info'] if 'bug_info' in doc else {},
            "error_detection_prompts": doc['error_detection_prompts'],
            "response_template": doc['response_template'],
            "error_fix_prompts": doc['error_fix_prompts'] if 'error_fix_prompts' in doc else {}
        })

    with open('DatasetII.json', 'w') as json_file:
        json.dump(data, json_file)


def main():
    bug_types = type_distribution()
    bug_types.pop(None)
    generate_prompts(bug_types)
    generate_dataset()
    
if __name__ == "__main__":
    main()
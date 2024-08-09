from utils import connect_to_collection
import json
source = connect_to_collection('LLM4wf','DatasetIII')
cursor = source.find()
docs = list(cursor)
print(len(docs))
data = []
for doc in docs:
    data.append({
        "id": str(doc["_id"]),
        "yaml": doc['updated_yaml'],
        "alerts": doc['updated_alerts'] if 'updated_alerts' in doc else {},
        "vul_detection_prompts": doc['vul_detection_prompts'],
        "response_template": doc['response_template'],
        "vuln_fix_prompts": doc['vuln_fix_prompts'] if 'vuln_fix_prompts' in doc else {}
    })

with open('DatasetIII.json', 'w') as json_file:
    json.dump(data, json_file)


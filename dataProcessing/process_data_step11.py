from utils import connect_to_collection
import json

source = connect_to_collection("LLM4wf", "DatasetI")
comb_groups = source.aggregate([{ '$group' : { '_id' : '$combination_group', 'count': { '$sum' : 1 } } }, { '$sort' : { 'count' : 1 } }])
comb_dict = {}
comb_great_than_100 = []
for doc in comb_groups:
    comb_dict[doc['_id']] = doc['count']
    if doc['count'] > 100:
        comb_great_than_100.append(doc['_id'])
print(len(comb_great_than_100)) # 133

data_small = []
data_large = []

for comb in comb_great_than_100:
    docs = source.find({'combination_group' : comb}).limit(22)
    flag = 0
    for doc in docs:
        flag+=1
        if flag <= 2:
            data_small.append({
                'id': str(doc['_id']),
                'yaml': doc['workflow_yaml'],
                'prompt1': doc['info']['level1'],
                'prompt2': doc['info']['level2'],
                'prompt3': doc['info']['level3'],
                'prompt4': doc['info']['level4'],
                'prompt5': doc['info']['level5'],
                'group': doc['combination_group']
            })
        else:
            data_large.append({
                'id': str(doc['_id']),
                'yaml': doc['workflow_yaml'],
                'prompt1': doc['info']['level1'],
                'prompt2': doc['info']['level2'],
                'prompt3': doc['info']['level3'],
                'prompt4': doc['info']['level4'],
                'prompt5': doc['info']['level5'],
                'group': doc['combination_group']
            })

print(len(data_small))
print(len(data_large))
with open('wfsgen-eval-small.json', 'w') as f:
    json.dump(data_small, f)
with open('wfsgen-eval-large.json', 'w') as f:
    json.dump(data_large, f)

data_finetune = []
source = connect_to_collection("LLM4wf", "DatasetI-finetune")
cursor = source.find()
docs = list(cursor)
for doc in docs:
    data_finetune.append({
                'id': str(doc['_id']),
                'yaml': doc['workflow_yaml'],
                'prompt1': doc['info']['level1'],
                'prompt2': doc['info']['level2'],
                'prompt3': doc['info']['level3'],
                'prompt4': doc['info']['level4'],
                'prompt5': doc['info']['level5'],
                'group': doc['combination_group']
            })
print(len(data_finetune))
with open('wfsgen-finetune.json', 'w') as f:
    json.dump(data_finetune, f)
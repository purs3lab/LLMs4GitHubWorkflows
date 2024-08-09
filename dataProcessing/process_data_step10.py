from utils import connect_to_collection    
    
NumofTriggers_group= [0.5410, 0.3194, 0.1396]
NumofActions_group = [0.2005, 0.3040, 0.2469, 0.1610, 0.0876]
NumofReusableWfs_group = [0.9534, 0.0466]
NumofJobs_group = [0.8812, 0.1085, 0.0103]
NumofSteps_group = [0.0406, 0.1631, 0.5743, 0.1722, 0.0498]
cc_group = [0.9338, 0.0483, 0.0179]

source = connect_to_collection("LLM4wf", "DatasetI")
dest = connect_to_collection("LLM4wf", "DatasetI-finetune")
comb_groups = source.aggregate([{ '$group' : { '_id' : '$combination_group', 'count': { '$sum' : 1 } } }])
comb_dict = {}
for doc in comb_groups:
    comb_dict[doc['_id']] = doc['count']
   
sum = 0
actual_sum = 0
for i in range(len(NumofTriggers_group)):
    for j in range(len(NumofActions_group)):
        for k in range(len(NumofReusableWfs_group)):
            for p in range(len(NumofJobs_group)):
                for m in range(len(NumofSteps_group)):
                    for n in range(len(cc_group)):
                        comb = chr(ord('a') + i) + chr(ord('a') + j) + chr(ord('a') + k) + chr(ord('a') + p) + chr(ord('a') + m) + chr(ord('a') + n)
                        prob = NumofTriggers_group[i] * NumofActions_group[j] * NumofReusableWfs_group[k] * NumofJobs_group[p] * NumofSteps_group[m] * cc_group[n]
                        num = int(prob * 4210) # adjust this number to make actual_num = 3200
                        if num > 1:
                            actual_num = comb_dict[comb] if comb in comb_dict else 0
                            actual_num = num if actual_num > num else actual_num
                            print(f"comb = {comb}, num = {num}, actual_num = {actual_num}")
                            if actual_num > 0:
                                docs = source.find({'combination_group' : comb}).limit(actual_num)
                                for doc in docs:
                                    dest.insert_one(doc)
                                    source.delete_one({'_id': doc['_id']})
                            sum += num
                            actual_sum += actual_num

print(f"sum = {sum}")
print(f"actual_sum = {actual_sum}")

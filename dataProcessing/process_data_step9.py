from utils import connect_to_collection

NumofTriggers_group_a = 0
NumofTriggers_group_b = 0
NumofTriggers_group_c = 0

NumofActions_group_a = 0
NumofActions_group_b = 0
NumofActions_group_c = 0
NumofActions_group_d = 0
NumofActions_group_e = 0

NumofReusableWfs_a = 0
NumofReusableWfs_b = 0

NumofJobs_a = 0
NumofJobs_b = 0
NumofJobs_c = 0

NumofSteps_a = 0
NumofSteps_b = 0
NumofSteps_c = 0
NumofSteps_d = 0
NumofSteps_e = 0

cc_a = 0
cc_b = 0
cc_c = 0

source = connect_to_collection("LLM4wf", "workflows-nl")
dest = connect_to_collection("LLM4wf", "DatasetI")
cursor = source.find(no_cursor_timeout=True)
docs = [doc for doc in cursor]
for doc in docs:
    stats = doc['stats']
    if stats['NumofTriggers'] > 6 or stats['NumofActions'] > 10 or stats['NumofReusableWfs'] > 4 or stats['NumofJobs'] > 8 or stats['NumofSteps'] > 21  or stats['CyclomaticComplexity'] > 8:
        continue

    combination = ""
    if stats['NumofTriggers'] == 1:
        combination += 'a'
        NumofTriggers_group_a += 1
    elif stats['NumofTriggers'] == 2:
        combination += 'b'
        NumofTriggers_group_b += 1
    else:
        combination += 'c'
        NumofTriggers_group_c += 1

    if stats['NumofActions'] <= 1:
        combination += 'a'
        NumofActions_group_a += 1
    elif stats['NumofActions'] == 2:
        combination += 'b'
        NumofActions_group_b += 1
    elif stats['NumofActions'] == 3:
        combination += 'c'
        NumofActions_group_c += 1
    elif stats['NumofActions'] == 4:
        combination += 'd'
        NumofActions_group_d += 1
    else:
        combination += 'e'
        NumofActions_group_e += 1

    if stats['NumofReusableWfs'] == 0:
        combination += 'a'
        NumofReusableWfs_a += 1
    else:
        combination += 'b'
        NumofReusableWfs_b += 1

    if stats['NumofJobs'] == 1:
        combination += 'a'
        NumofJobs_a += 1
    elif stats['NumofJobs'] == 2 or stats['NumofJobs'] == 3:
        combination += 'b'
        NumofJobs_b += 1
    else:
        combination += 'c'
        NumofJobs_c += 1

    if stats['NumofSteps'] == 0:
        combination += 'a'
        NumofSteps_a += 1
    elif stats['NumofSteps'] <= 2:
        combination += 'b'
        NumofSteps_b += 1
    elif stats['NumofSteps'] <= 6:
        combination += 'c'
        NumofSteps_c += 1
    elif stats['NumofSteps'] <= 10:
        combination += 'd'
        NumofSteps_d += 1
    else:
        combination += 'e'
        NumofSteps_e += 1

    if stats['CyclomaticComplexity'] == 1:
        combination += 'a'
        cc_a += 1
    elif stats['CyclomaticComplexity'] == 2:
        combination += 'b'
        cc_b += 1
    else:
        combination += 'c'
        cc_c += 1

    doc['combination_group'] = combination
    dest.insert_one(doc)

sum = NumofTriggers_group_a + NumofTriggers_group_b + NumofTriggers_group_c
print(f"NumofTriggers_group_a = {NumofTriggers_group_a}, proportion = {(NumofTriggers_group_a / sum): .4f}")
print(f"NumofTriggers_group_b = {NumofTriggers_group_b}, proportion = {(NumofTriggers_group_b / sum): .4f}") 
print(f"NumofTriggers_group_c = {NumofTriggers_group_c}, proportion = {(NumofTriggers_group_c / sum): .4f}")

print(f"NumofActions_group_a = {NumofActions_group_a}, proportion = {(NumofActions_group_a / sum): .4f}")
print(f"NumofActions_group_b = {NumofActions_group_b}, proportion = {(NumofActions_group_b / sum): .4f}")
print(f"NumofActions_group_c = {NumofActions_group_c}, proportion = {(NumofActions_group_c / sum): .4f}")
print(f"NumofActions_group_d = {NumofActions_group_d}, proportion = {(NumofActions_group_d / sum): .4f}")
print(f"NumofActions_group_e = {NumofActions_group_e}, proportion = {(NumofActions_group_e / sum): .4f}")

print(f"NumofReusableWfs_a = {NumofReusableWfs_a}, proportion = {(NumofReusableWfs_a / sum): .4f}")
print(f"NumofReusableWfs_b = {NumofReusableWfs_b}, proportion = {(NumofReusableWfs_b / sum): .4f}")

print(f"NumofJobs_a = {NumofJobs_a}, proportion = {(NumofJobs_a / sum): .4f}")
print(f"NumofJobs_b = {NumofJobs_b}, proportion = {(NumofJobs_b / sum): .4f}")
print(f"NumofJobs_c = {NumofJobs_c}, proportion = {(NumofJobs_c / sum): .4f}")

print(f"NumofSteps_a = {NumofSteps_a}, proportion = {(NumofSteps_a / sum): .4f}")
print(f"NumofSteps_b = {NumofSteps_b}, proportion = {(NumofSteps_b / sum): .4f}")
print(f"NumofSteps_c = {NumofSteps_c}, proportion = {(NumofSteps_c / sum): .4f}")
print(f"NumofSteps_d = {NumofSteps_d}, proportion = {(NumofSteps_d / sum): .4f}")
print(f"NumofSteps_e = {NumofSteps_e}, proportion = {(NumofSteps_e / sum): .4f}")

print(f"cc_a = {cc_a}, proportion = {(cc_a / sum): .4f}")
print(f"cc_b = {cc_b}, proportion = {(cc_b / sum): .4f}")
print(f"cc_c = {cc_c}, proportion = {(cc_c / sum): .4f}")

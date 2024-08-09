from utils import connect_to_collection, add_line_numbers
import random
dest = connect_to_collection('LLM4wf','DatasetIII')

source_errors = connect_to_collection('LLM4wf','VerifiedArgusResults-update-taint-summary')
cursor_errors = source_errors.find()
docs_errors = list(cursor_errors)
vul_num = 0
for doc in docs_errors:
    vul_num += len(doc['updated_alerts'])
print(f"Workflows with code injection vulnerabilities: {len(docs_errors)}.") # Workflows with code injection vulnerabilities: 2603.
print(f"Number of code injection vulnerabilities: {vul_num}.") # Number of code injection vulnerabilities: 4397.

source_correct = connect_to_collection('LLM4wf','workflows-without-errors')
cursor_correct = source_correct.aggregate([{ '$sample': { 'size': vul_num } }])
docs_correct = list(cursor_correct)
for doc in docs_correct:
    doc["updated_yaml"] = add_line_numbers(doc['workflow_yaml'])
print(f"Workflows without vulnerabilities: {len(docs_correct)}.") # Workflows without vulnerabilities: 4397.
source_correct.delete_many({'_id': {'$in': [doc['_id'] for doc in docs_correct]}})

docs = docs_errors + docs_correct
random.shuffle(docs)
dest.insert_many(docs)
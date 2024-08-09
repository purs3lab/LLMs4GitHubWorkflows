import yaml
import random
from pymongo import MongoClient
import logging
import os

def connect_to_collection(db_name, collection_name):
    try:
        client = MongoClient('Your_URL')
        _db = client[db_name]
        _collection = _db[collection_name]
        return _collection
    except Exception as exc:
        logging.error({
            "message": "Failed to connect to the collection",
            "erro": exc
        })
        raise Exception
    
def add_line_numbers(input_string):
    lines = input_string.split('\n')
    max_width = len(str(len(lines)))

    formatted_lines = []
    for i, line in enumerate(lines, start=1):
        line_number = str(i).rjust(max_width)
        formatted_lines.append(f"{line_number}: {line}")

    result_string = '\n'.join(formatted_lines)
    return result_string

dest = connect_to_collection('LLM4wf','DatasetII')

source_errors = connect_to_collection('LLM4wf','workflows-with-errors')
cursor_errors = source_errors.find({'bug':{'$size':1}})
docs_errors = list(cursor_errors)
for doc in docs_errors:
    doc['yaml'] = add_line_numbers(doc['workflow_yaml'])
syntax_error_wf_num = len(docs_errors)
print(f"Workflows with only one syntax error: {syntax_error_wf_num}.") # Workflows with only one syntax error: 62920.

source_correct = connect_to_collection('LLM4wf','workflows-without-errors')
cursor_correct = source_correct.aggregate([{ '$sample': { 'size': syntax_error_wf_num } }])
docs_correct = list(cursor_correct)
for doc in docs_correct:
    doc['yaml'] = add_line_numbers(doc['workflow_yaml'])
syntax_correct_wf_num = len(docs_correct)
print(f"Workflows without syntax errors: {syntax_correct_wf_num}.") # Workflows without syntax errors: 62920.
source_correct.delete_many({'_id': {'$in': [doc['_id'] for doc in docs_correct]}})

docs = docs_errors + docs_correct
random.shuffle(docs)
dest.insert_many(docs)
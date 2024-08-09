from pymongo import MongoClient
import logging
from transformers import AutoTokenizer, CodeLlamaTokenizer
import tiktoken
starcoder_tokenizer = AutoTokenizer.from_pretrained("HuggingFaceH4/starchat-beta")
gpt_encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
codellama_tokenizer = CodeLlamaTokenizer.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")

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
    
def count_tokens(tokenizer, text):
    inputs = tokenizer.encode(text)
    num = len(inputs) 
    return num

count_in_argus = 0
count_length_limit = 0

# Step 2: limit length to 1024 and remove workflows that have command injection vulnerabilities
source = connect_to_collection('LLM4wf','workflows-ir-deduplicate')
argus_data = connect_to_collection('LLM4wf', 'ArgusResults')
cursor = source.find(no_cursor_timeout=True)
docs = [doc for doc in cursor]
for doc in docs:
    _id = doc['_id']
    doc_in_argus = argus_data.find_one({"wf_id": _id})
    if doc_in_argus:
        source.delete_one({"_id": _id})
        count_in_argus += 1
    yaml = doc['workflow_yaml']
    if count_tokens(gpt_encoding, yaml) > 1024 or count_tokens(starcoder_tokenizer, yaml) > 1024 or count_tokens(codellama_tokenizer, yaml) > 1024:
        source.delete_one({"_id": _id})
        count_length_limit += 1

print(f"count_in_argus = {count_in_argus}") # 5378
print(f"count_length_limit = {count_length_limit}") # 163612
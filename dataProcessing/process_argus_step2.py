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

source = connect_to_collection('LLM4wf', 'VerifiedArgusResults')
dest = connect_to_collection('LLM4wf', 'VerifiedArgusResults-deduplicate')
pipeline = [
    {"$group": {"_id": "$yaml", "count": {"$sum": 1}, "docs": {"$push": "$_id"}}}
]
duplicate_results = list(source.aggregate(pipeline))
print(f"We have {len(duplicate_results)} unique workflows.") # We have 3186 unique workflows.

for duplicate_result in duplicate_results:
    duplicate_id = duplicate_result['docs'][0]  
    document = source.find_one({"_id": duplicate_id})
    dest.insert_one(document)
print(f"After removing duplicates, we have {dest.count_documents({})} documents.") # After removing duplicates, we have 3186 documents.

count = 0
cursor = dest.find(no_cursor_timeout=True)
docs = [doc for doc in cursor]
for doc in docs:
    _id = doc['_id']
    yaml = doc['yaml']
    if count_tokens(gpt_encoding, yaml) > 2048 or count_tokens(starcoder_tokenizer, yaml) > 2048 or count_tokens(codellama_tokenizer, yaml) > 2048:
        dest.delete_one({"_id": _id})
        count += 1
print(f"We remove {count} long documents. Now we have {dest.count_documents({})} documents.") # We remove 580 long documents. Now we have 2606 documents.

    


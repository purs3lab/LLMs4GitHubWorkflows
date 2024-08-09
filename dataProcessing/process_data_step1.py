from pymongo import MongoClient
import logging
import json
import random
from bson import ObjectId
import re
import csv

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
    
# Step 1: Remove duplicates
pipeline = [
    {"$group": {"_id": "$workflow_yaml", "count": {"$sum": 1}, "docs": {"$push": "$_id"}}}
]
source = connect_to_collection('git-reactions', 'workflows-ir')
duplicate_results = list(source.aggregate(pipeline))
print(f"We have {len(duplicate_results)} unique workflows.") # 1186175

dest = connect_to_collection('LLM4wf','workflows-ir-deduplicate')
for duplicate_result in duplicate_results:
    _id = duplicate_result['docs'][0]
    document = source.find_one({"_id": _id})
    dest.insert_one(document)

print("Finish...")
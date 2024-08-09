from pymongo import MongoClient
import logging

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
    
argus_data = connect_to_collection('LLM4wf', 'ArgusResults')
docs = list(argus_data.find({'vuln':True})) # get 7640 confirmed wfs
dest = connect_to_collection('LLM4wf', 'VerifiedArgusResults')
dest.insert_many(docs)
print('Finish...')


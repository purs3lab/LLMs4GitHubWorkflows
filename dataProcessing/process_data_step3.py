import os
from pymongo import MongoClient
import logging
import pathlib
import os
import time
from bson import ObjectId
import subprocess
import json

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

wfs = pathlib.Path("./wfs")

source = connect_to_collection('LLM4wf','workflows-ir-deduplicate') # 1017185
dest1 = connect_to_collection('LLM4wf','workflows-with-errors') # 78068
dest2 = connect_to_collection('LLM4wf','workflows-without-errors') # 939117
cursor = source.find(no_cursor_timeout=True)
# cursor = source.find().limit(100)
counter = 0
docs = [doc for doc in cursor]
for doc in docs:
    counter += 1
    if counter % 1000 == 0:
        print(counter)
    yaml_file = doc['workflow_yaml']
    wf_file = wfs / os.path.basename(doc["workflow_path"])
    with open(wf_file, "w") as f:
        f.write(yaml_file)
    command = ["./actionlint", "-ignore", "shellcheck reported issue in this script:.*:warning:", "-ignore", "shellcheck reported issue in this script:.*:info:", "-ignore", "shellcheck reported issue in this script:.*:style:", "-ignore", 'workflow command "set-output" was deprecated', "-ignore", 'workflow command "save-state" was deprecated', "-ignore", "is potentially untrusted", "-ignore", "label .* is unknown", "-format", "{{json .}}", wf_file]
    saved_output = ""
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            saved_output += output.decode('utf-8')
            if (not output):
                break
        process.wait()
        return_code = process.returncode
        # actionlint command exits with one of the following exit statuses.
        # 0: It ran successfully and no problem was found.
        # 1: It ran successfully and some problem was found.
        # 2: It failed due to invalid command line option.
        # 3: It failed due to some fatal error.
        if (return_code == 0):
            source.update_one({"_id": doc["_id"]}, {"$set": {"syntax_error": False}})
            dest2.insert_one(doc)
        elif (return_code == 1):
            res = saved_output + str(process.stderr.read().decode('utf-8'))
            doc['bug'] = json.loads(res)
            source.update_one({"_id": doc["_id"]}, {"$set": {"syntax_error": True}})
            dest1.insert_one(doc)
        else:
            source.update_one({"_id": doc["_id"]}, {"$set": {"syntax_error": "syntax check failed"}})
    except subprocess.TimeoutExpired:
        source.update_one({"_id": doc["_id"]}, {"$set": {"syntax_error": "syntax check failed"}})
    except subprocess.CalledProcessError as e:
        source.update_one({"_id": doc["_id"]}, {"$set": {"syntax_error": "syntax check failed"}})
    finally:
        if os.path.exists(wf_file):
            os.remove(wf_file)


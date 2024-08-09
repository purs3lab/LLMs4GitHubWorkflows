from pymongo import MongoClient
import logging
import os
import pathlib
import json

wfs = pathlib.Path("./wfs")
res = pathlib.Path("./results")

def connect_to_collection(collection_name):
    try:
        client = MongoClient('Your_URL')
        _db = client["LLM4wf"]
        _collection = _db[collection_name]
        return _collection
    except Exception as exc:
        logging.error({
            "message": "Failed to connect to the collection",
            "erro": exc
        })
        raise Exception

source = connect_to_collection("workflows-step_name")
dest = connect_to_collection("workflows-nl")

cursor = source.find(no_cursor_timeout=True)
docs = list(cursor)
counter = 0
for document in docs:
    if counter % 1000 == 0:
        print(counter)
    try:
        repo_lang = document['repo_metadata']['language']
        repo_lang = "none" if not repo_lang else repo_lang
            
        ir = document['ir']
        yaml_file = document['workflow_yaml']
        dependencies = {}
        dependencies['actions'] = ir['dependencies']['actions']
        dependencies['workflows'] = ir['dependencies']['workflows']        
        dependencies['vars'] = ir['CIvars_set']
        dependencies_str = json.dumps(dependencies)

        wf_file = wfs / os.path.basename(document["workflow_path"])
        res_file = res / os.path.basename(document["workflow_path"])
    
        # Write the workflow to a file so argus can use it
        with open(wf_file, "w") as f:
            f.write(yaml_file)

        command = f"python main.py --yaml_file '{wf_file}' --repo_lang '{repo_lang}' --dependencies '{dependencies_str}'"
        os.system(command)

        with open(f"{res_file}.json", "r") as f:
            data = json.load(f)

        # Modify the document to add the stats json
        document['info'] = data
        dest.insert_one(document)
        counter += 1
    except:
        pass
    finally:
        # Delete wf_file and res_file, whether an exception occurred or not
        if os.path.exists(wf_file):
            os.remove(wf_file)
        if os.path.exists(f"{res_file}.json"):
            os.remove(f"{res_file}.json")

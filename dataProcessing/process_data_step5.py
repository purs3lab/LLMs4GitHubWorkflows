import yaml
from utils import connect_to_collection

def has_step_name(content):
    wf_name = content.get("name", "")
    if wf_name == "":
        return False

    jobs = content.get("jobs", {})
    for job_id, job_body in jobs.items():
        if "steps" in job_body:
            for step in job_body["steps"]:
                if "name" not in step or step["name"] == "":
                    return False
    return True
                 
source = connect_to_collection('LLM4wf','workflows-without-errors')
cursor = source.find(no_cursor_timeout=True)
docs = [doc for doc in cursor]
dest = connect_to_collection('LLM4wf','workflows-step_name') # 292919

num = 0
for doc in docs:
    num += 1
    if num % 1000 == 0:
        print(num)
    try:
        content = yaml.safe_load(doc['workflow_yaml'])
        if has_step_name(content):
            dest.insert_one(doc)
    except:
        # If anything results in error, we ignore
        pass

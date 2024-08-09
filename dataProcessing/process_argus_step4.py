from utils import connect_to_collection
import csv

source =  connect_to_collection('LLM4wf', 'VerifiedArgusResults-update-taint-summary')
action_collection = connect_to_collection("git-reactions", "actions_col")
cursor = source.find()
direct_taint_composite_action = set()
indirect_taint_composite_action = {}

direct_taint_reusable_workflow = set()
indirect_taint_reusable_workflow = {}

for doc in cursor:
    for alert in doc['updated_alerts']:
        if alert["type"] == "b":
            action = alert['shell_cmd(action)']
            action_name = action.split("@")[0]
            action_version = action.split("@")[1]
            doc = action_collection.find_one({"name": action_name, "version": action_version})
            if doc['type'] == "composite":
                direct_taint_composite_action.add(action)
        elif alert["type"] == "a":
            action = alert['shell_cmd(action)']
            if "@" not in action:
                continue
            action_name = action.split("@")[0]
            action_version = action.split("@")[1]
            doc = action_collection.find_one({"name": action_name, "version": action_version})
            if doc['type'] == "composite":
                if action not in indirect_taint_composite_action:
                    indirect_taint_composite_action[action] = []
                if alert['tainted_var'] not in indirect_taint_composite_action[action]:
                    indirect_taint_composite_action[action].append(alert['tainted_var'])
        elif alert["type"] == "d":
            rw = alert['reusable_workflow']
            if rw not in indirect_taint_reusable_workflow:
                indirect_taint_reusable_workflow[rw] = []
            if alert['tainted_var'] not in indirect_taint_reusable_workflow[rw]:
                indirect_taint_reusable_workflow[rw].append(alert['tainted_var'])
        elif alert["type"] == "e":
            rw = alert['reusable_workflow']
            direct_taint_reusable_workflow.add(rw)
            

print("direct taint composite action: ", len(direct_taint_composite_action))
for action in direct_taint_composite_action:
    print(f"\"{action}\",")

print("indirect taint composite action: ", len(indirect_taint_composite_action))
for action in indirect_taint_composite_action:
    print(f"\"{action}\": {indirect_taint_composite_action[action]},")

print("indirect taint reusable workflow: ", len(indirect_taint_reusable_workflow))
for rw in indirect_taint_reusable_workflow:
    print(f"\"{rw}\": {indirect_taint_reusable_workflow[rw]},")

print("direct taint reusable workflow: ", len(direct_taint_reusable_workflow))
for rw in direct_taint_reusable_workflow:
    print(f"\"{rw}\",")
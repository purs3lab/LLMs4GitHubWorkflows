from utils import connect_to_collection
import json
    
pipeline_NumofTriggers = [
    { '$group' : { '_id' : '$stats.NumofTriggers', 'count': { '$sum' : 1 } } }, 
    { '$sort' : { '_id' : 1 } }
]

pipeline_Triggers = [
    { '$unwind' : { 'path' : '$stats.Triggers' } },
    { '$group' : { '_id' : '$stats.Triggers', 'count' : { '$sum' : 1 } } },
    { '$sort' : { 'count' : -1 } }
]

pipeline_TriggerCombs = [
    { '$group' : { '_id' : '$stats.Triggers', 'count' : { '$sum' : 1 } } },
    { '$sort' : { 'count' : -1 } }
]

pipeline_NumofActions = [
    { '$group' : { '_id' : '$stats.NumofActions', 'count': { '$sum' : 1 } } }, 
    { '$sort' : { '_id' : 1 } }
]

pipeline_Actions = [
    { '$unwind' : { 'path' : '$stats.Actions' } },
    { '$group' : { '_id' : '$stats.Actions', 'count' : { '$sum' : 1 } } },
    { '$sort' : { 'count' : -1 } }
]

pipeline_ActionCombs = [
    { '$group' : { '_id' : '$stats.Actions', 'count' : { '$sum' : 1 } } },
    { '$sort' : { 'count' : -1 } }
]

pipeline_NumofReusableWfs = [
    { '$group' : { '_id' : '$stats.NumofReusableWfs', 'count': { '$sum' : 1 } } }, 
    { '$sort' : { '_id' : 1 } }
]

pipeline_ReusableWfs = [
    { '$unwind' : { 'path' : '$stats.ReusableWfs' } },
    { '$group' : { '_id' : '$stats.ReusableWfs', 'count' : { '$sum' : 1 } } },
    { '$sort' : { 'count' : -1 } }
]

pipeline_ReusableWfsCombs = [
    { '$group' : { '_id' : '$stats.ReusableWfs', 'count' : { '$sum' : 1 } } },
    { '$sort' : { 'count' : -1 } }
]

pipeline_NumofJobs = [
    { '$group' : { '_id' : '$stats.NumofJobs', 'count': { '$sum' : 1 } } }, 
    { '$sort' : { '_id' : 1 } }
]

pipeline_NumofSteps = [
    { '$group' : { '_id' : '$stats.NumofSteps', 'count': { '$sum' : 1 } } }, 
    { '$sort' : { '_id' : 1 } }
]

pipeline_CyclomaticComplexity = [
    { '$group' : { '_id' : '$stats.CyclomaticComplexity', 'count': { '$sum' : 1 } } }, 
    { '$sort' : { '_id' : 1 } }
]

def DataDistribution(source, pipeline):
    distribution_data = {}
    for doc in source.aggregate(pipeline):
        key = doc["_id"]
        count = doc["count"]
        if isinstance(key, list):
            distribution_data[str(key)] = count
        else:
            distribution_data[key] = count
    return distribution_data

if __name__ == "__main__":
    source = connect_to_collection("LLM4wf", "workflows-nl")
    data = {}
    data['NumofTriggers'] =  DataDistribution(source, pipeline_NumofTriggers)
    data['Triggers'] = DataDistribution(source, pipeline_Triggers)
    data['Trigger Combinations'] = DataDistribution(source, pipeline_TriggerCombs)

    data['NumofActions'] = DataDistribution(source, pipeline_NumofActions)
    data['Actions'] = DataDistribution(source, pipeline_Actions)
    data['Action Combinations'] = DataDistribution(source, pipeline_ActionCombs)

    data['NumofReusableWfs'] = DataDistribution(source, pipeline_NumofReusableWfs)
    data['Reusable Workflows'] = DataDistribution(source, pipeline_ReusableWfs)
    data['Reusable Workflow Combinations'] = DataDistribution(source, pipeline_ReusableWfsCombs)

    data['NumofJobs'] = DataDistribution(source, pipeline_NumofJobs)
    data['NumofSteps'] = DataDistribution(source, pipeline_NumofSteps)
    data['Cyclomatic Complexity'] = DataDistribution(source, pipeline_CyclomaticComplexity)

    with open('ComplexityMetricDistribution.json', 'w') as json_file:
        json.dump(data, json_file)

    print(f'Data has been written to json file ...')


from utils import connect_to_collection

class CyclomaticComplexityCalculator:
    def __init__(self, jobs):
        self.nodes = len(jobs) + 2
        self.edges = 0

        self.graph = {}
        for job_dict in jobs:
            self.graph[job_dict['id']] = []
        # The <job_id> must start with a letter or _ and contain only alphanumeric characters, -, or _. #start#node# will not conflict with job ids.
        self.graph['#start#node#'] = []
        self.graph['#end#node#'] = []
        self.add_edge(jobs)

    def add_edge(self, jobs):
        for job_dict in jobs:
            if len(job_dict['needs']) == 0:
                self.graph['#start#node#'].append(job_dict['id'])
                self.edges += 1
            else:
                for pre_job in job_dict['needs']:
                    self.graph[pre_job].append(job_dict['id'])
                    self.edges += 1
        
        for node in self.graph:
            if node != '#start#node#' and node != '#end#node#' and len(self.graph[node]) == 0:
                self.graph[node].append('#end#node#')
                self.edges += 1

    def calculate_cyclomatic_complexity(self):
        # Calculate the cyclomatic complexity using the formula: M = E - N + 2R
        complexity = self.edges - self.nodes + 2
        return complexity
    
    def get_graph(self):
        return self.graph

def upgrade_info(info):
    # Create a CyclomaticComplexityCalculator object
    calculator = CyclomaticComplexityCalculator(info['stats']['jobs'])
    # Calculate the cyclomatic complexity
    complexity = calculator.calculate_cyclomatic_complexity()
    graph = calculator.get_graph()

    new_info = {
        'NumofTriggers' : len(info['stats']['Triggers']), 
        'Triggers' : sorted(info['stats']['Triggers']),
        'NumofJobs' : info['stats']['NumOfJobs'],
        'NumofActions' : len(info['stats']['Actions']),
        'Actions' : sorted([action['name'] for action in info['stats']['Actions']]),
        'Actions_details' : info['stats']['Actions'],
        'NumofReusableWfs' : len(info['stats']['ReusableWfs']),
        'ReusableWfs' : sorted(info['stats']['ReusableWfs']),
        'NumofSteps' : info['stats']['TotalNumOfSteps'],
        'CyclomaticComplexity' : complexity,
        'CFG' : graph
    }

    return new_info

if __name__ == "__main__":
    source = connect_to_collection("LLM4wf", "workflows-nl")
    cursor = source.find(no_cursor_timeout=True)
    docs = [doc for doc in cursor]
    for doc in docs:
        info = doc['info']
        new_info = upgrade_info(info)
        source.update_one({'_id': doc['_id']}, {'$set': {'stats': new_info}})
        







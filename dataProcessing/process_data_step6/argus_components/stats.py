import json
import os
import pathlib
from collections import defaultdict

from argus_components.workflow.ghworkflow import GHWorkflow
from argus_components.utils.nl_utils import NLUtils

class Stats:
    def __init__(self, yaml_file, repo_lang, dependencies):
        self.yaml_file = yaml_file
        self.workflow = GHWorkflow(self.yaml_file)
        self.repo_language = repo_lang
        self.dependencies = json.loads(dependencies)
        self._parse()
        self._stats()

    def _stats(self):
        self.stats_dict = defaultdict(dict)
        self.stats_dict["Triggers"] = self.workflow.get_triggers()
        self.stats_dict["NumOfJobs"] = len(self.workflow.jobs)
        self.stats_dict["Actions"] = self.dependencies["actions"]
        self.stats_dict["ReusableWfs"] = self.dependencies["workflows"]
        self.stats_dict["jobs"] = []
        TotalNumOfSteps = 0

        for job in self.workflow.jobs:
            job_dic = defaultdict(dict)
            job_dic["id"] = job.id
            job_dic["needs"] = job.needs
            job_dic["NumOfSteps"] = len(job.steps)
            self.stats_dict["jobs"].append(job_dic)
            TotalNumOfSteps += job_dic["NumOfSteps"]

        self.stats_dict["TotalNumOfSteps"] = TotalNumOfSteps

    def _parse(self):
        self.descriptions = defaultdict(dict)
        self.descriptions["workflow_name"] = NLUtils.workflow_name(self.repo_language, self.workflow.name)
        self.descriptions["workflow_run_name"] = NLUtils.workflow_run_name(self.workflow.run_name)
        self.descriptions["triggers"] = NLUtils.triggers(self.workflow.triggers)
        self.descriptions["workflow_permissions"] = NLUtils.permissions(self.workflow.permissions, None)
        self.descriptions["workflow_env"] = NLUtils.env(self.workflow.env, "workflow")
        self.descriptions["workflow_defaults"] = NLUtils.defaults(self.workflow.defaults, "workflow")
        self.descriptions["workflow_concurrency"] = NLUtils.concurrency(self.workflow.concurrency, "workflow")
        self.descriptions["all_job_name"] = NLUtils.job_step_name(self.workflow.jobs, False)
        self.descriptions["all_job_step_name"] = NLUtils.job_step_name(self.workflow.jobs, True)
        self.descriptions["detailed_job"] = NLUtils.jobs(self.workflow.jobs, True)
        self.descriptions["not_detailed_job"] = NLUtils.jobs(self.workflow.jobs, False)

    def _get_wf_level5(self):
        # include all details, in other words, translate wf into nl line by line
        nl_level5 = self.descriptions["workflow_name"] + \
                    self.descriptions["workflow_run_name"] + \
                    self.descriptions["triggers"] + \
                    self.descriptions["workflow_permissions"] + \
                    self.descriptions["workflow_env"] + \
                    self.descriptions["workflow_defaults"] + \
                    self.descriptions["workflow_concurrency"] + \
                    self.descriptions["detailed_job"]
        return nl_level5

    def _get_wf_level4(self):
        # compared to level5, level4 only keeps step name and removes other step details for each step
        nl_level4 = self.descriptions["workflow_name"] + \
                    self.descriptions["workflow_run_name"] + \
                    self.descriptions["triggers"] + \
                    self.descriptions["workflow_permissions"] + \
                    self.descriptions["workflow_env"] + \
                    self.descriptions["workflow_defaults"] + \
                    self.descriptions["workflow_concurrency"] + \
                    self.descriptions["not_detailed_job"]
        return nl_level4

    def _get_wf_level3(self):
        # include workflow-level information (workflow_name, run_name(optional), triggers, workflow_permissions(optional), workflow_env(optional), workflow_defaults(optional), workflow_concurrency(optional)), all job names and step names
        # provide with actions, reusable workflows and variables that can be used
        nl_level3 = self.descriptions["workflow_name"] + \
                    self.descriptions["workflow_run_name"] + \
                    self.descriptions["triggers"] + \
                    self.descriptions["workflow_permissions"] + \
                    self.descriptions["workflow_defaults"] + \
                    self.descriptions["workflow_concurrency"] + \
                    self.descriptions["all_job_step_name"] + \
                    NLUtils.dependency(self.dependencies)
        return nl_level3

    def _get_wf_level2(self):
        # include workflow-level information (workflow_name, run_name(optional), triggers, workflow_permissions(optional), workflow_env(optional), workflow_defaults(optional), workflow_concurrency(optional)), all job names and step names
        nl_level2 = self.descriptions["workflow_name"] + \
                    self.descriptions["workflow_run_name"] + \
                    self.descriptions["triggers"] + \
                    self.descriptions["workflow_permissions"] + \
                    self.descriptions["workflow_env"] + \
                    self.descriptions["workflow_defaults"] + \
                    self.descriptions["workflow_concurrency"] + \
                    self.descriptions["all_job_step_name"]
        return nl_level2
    
    def _get_wf_level1(self):
        # include workflow-level information (workflow_name, run_name(optional), triggers, workflow_permissions(optional), workflow_env(optional), workflow_defaults(optional), workflow_concurrency(optional)) and all job names
        nl_level1 = self.descriptions["workflow_name"] + \
                    self.descriptions["workflow_run_name"] + \
                    self.descriptions["triggers"] + \
                    self.descriptions["workflow_permissions"] + \
                    self.descriptions["workflow_env"] + \
                    self.descriptions["workflow_defaults"] + \
                    self.descriptions["workflow_concurrency"] + \
                    self.descriptions["all_job_name"]
        return nl_level1

    def translate_nl(self):
        self.wf_dict = defaultdict(dict)
        # collect data at different levels of granularity
        self.wf_dict["level1"] = self._get_wf_level1() 
        self.wf_dict["level2"] = self._get_wf_level2()
        self.wf_dict["level3"] = self._get_wf_level3()
        self.wf_dict["level4"] = self._get_wf_level4()
        self.wf_dict["level5"] = self._get_wf_level5()
        self.wf_dict["stats"] = self.stats_dict
        data = json.dumps(self.wf_dict)
        res_folder = pathlib.Path(os.getcwd()) / "results"
        with open(res_folder / f"{os.path.basename(self.workflow.workflow_full_path)}.json", "w") as f:
            f.write(data)



    

     

#    _____ __________  ________ ____ ___  _________
#   /  _  \\______   \/  _____/|    |   \/   _____/
#  /  /_\  \|       _/   \  ___|    |   /\_____  \ 
# /    |    \    |   \    \_\  \    |  / /        \
# \____|__  /____|_  /\______  /______/ /_______  /
#         \/       \/        \/                 \/ 
# 
# Copyright (C) 2023 Siddharth Muralee

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from __future__ import annotations

import glob
import os
import yaml
import json
from typing import Dict, List, Tuple, Union
from uuid import uuid4
from hashlib import sha256

from .workflow import Workflow

from argus_components.ci import GithubCI

NO_ACTION = 0
GITHUB_ACTION = 1
THIRD_PARTY_ACTION = 2
DOCKER_ACTION = 3
LOCAL_ACTION = 4

COMMIT_REF = 0
TAG_REF = 1
BRANCH_REF = 2
NON_THIRD_PARTY_REF = 3
NO_VERSION = 4
DOCKER_TAG_REF = 5
DOCKER_COMMIT_REF = 6
DOCKER_NO_REF = 7
NON_FIRST_PARTY_REF = 8

class GHWorkflow(Workflow):

    def read_workflow(self):
        try:
            with open(self.workflow_full_path, "r") as workflow_file:
               self.content = yaml.safe_load(workflow_file)
        except FileNotFoundError:
            raise FileNotFoundError("Workflow file not found")

    def __init__(self, workflow_path):
        self.uid = str(uuid4())
        self.workflow_full_path = workflow_path
        self.read_workflow()

        # Triggers that are defined in the workflow
        self.triggers : List[Dict] = []
        # Permissions of token that is defined in the workflow
        self.permissions : List[Dict] = []

        self.jobs = []
        self.parse_workflow()
        
    def parse_workflow(self):
        """ Parses the workflow file """
        self.name = self.get_name()

        self.run_name = self.get_run_name()
        
        # Triggers have on -> which is a special case in yaml, gets loaded to True
        # We automatically append to the triggers list (self.triggers)
        self.parse_triggers("on")
        self.parse_triggers(True)    

        # We parse the permissions of the workflow
        self.parse_workflow_permissions()

        self.env = self.parse_workflow_env()

        self.defaults = self.get_defaults()
        
        self.concurrency = self.get_concurrency()

        ctr = 0
        for job_id, body in self.get_jobs().items():
            self.jobs.append(GHWorkflowJob(job_id, body, ctr))
            ctr += 1

        
    def parse_triggers(self, filter):
        """ Parses the triggers """
        trigger = self.content.get(filter, None)
        if trigger is None:
            return []
        if isinstance(trigger, dict):
            for keyword, config in trigger.items():
                if config == None:
                    self.triggers.append({
                        "type" : keyword,
                        "condition" : ""
                    })
                else: 
                    self.triggers.append({
                        "type" : keyword,
                        "condition" : config
                    })
        elif isinstance(trigger, list):
            for item in trigger:
                self.triggers.append({
                        "type" : item,
                        "condition" : ""
                })
        elif isinstance(trigger, str):
            self.triggers.append({
                "type" : trigger,
                "condition" : ""
            })
        else:
            logger.error(f"[Error] Wrong type for trigger : {type(trigger), trigger}")
    
    # https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#env    
    def parse_workflow_env(self):
        return GithubCI.pack_to_dict_format(self.get_env(), "env")

    def parse_workflow_permissions(self) -> None:
        """Parses the permissions of the workflow"""
        permissions = self.get_permissions()
            
        if permissions == None:
            return

        if isinstance(permissions, str):
            if permissions == "read-all|write-all" or permissions == "write-all|read-all":
                permissions = "read and write"
            elif permissions.endswith('-all'):
                permissions = permissions.rstrip("-all")
            else:
                logger.debug("permissions: ", permissions)

            self.permissions.append(
                {
                    "scope" : "across all scopes",
                    "access" : permissions
                } 
            )
        elif isinstance(permissions, dict):
            if len(permissions) == 0:
                self.permissions.append(
                    {
                        "scope" : "across all scopes",
                        "access" : None
                    } 
                )

            for permission_name, permission_value in permissions.items():
                self.permissions.append(
                    {
                        "scope" : "in the `" + permission_name + "` scope",
                        "access" : permission_value
                    } 
                )
                
        return   


    #
    # Getters
    #  

    @property
    def is_self_hosted(self):
        for job in self.jobs:
            if job.is_self_hosted:
                return True
        
    def get_name(self):
        """Returns the name of the workflow"""
        return self.content.get("name", "")
    
    def get_run_name(self):
        """Returns the name of workflow runs"""
        return self.content.get("run-name", "")

    def get_jobs(self):
        """Returns the jobs in the workflow"""
        return self.content.get("jobs", {})
    
    def get_env(self):
        """Returns the global environment variables in the workflow"""
        return self.content.get("env", None)

    def get_permissions(self):
        """Returns the permissions of the workflow"""
        return self.content.get("permissions", None)

    def get_triggers(self):
        """Returns the triggers type of the workflow"""
        triggers = []
        for trigger in self.triggers:
            triggers.append(trigger["type"])
        return triggers
    
    def get_defaults(self):
        return self.content.get("defaults", None)
    
    def get_concurrency(self):
        return self.content.get("concurrency", None)
        
    #
    # Debugging
    # 

    def __str__(self):
        ret = f"Workflow : {self.name}\n"
        ret += f"Triggers : {self.triggers}\n"
        ret += f"Jobs : {self.jobs}\n"
        ret += f"Env : {self.env}\n"
        return ret

class GHWorkflowJob:

    def __init__(self, job_id, body : dict, job_num = 0):
        self.id = job_id
        self.job_num = job_num
        self.body = body
        self.steps : List[GHWorkflowStep] = []
        self.permissions : List[Dict] = []
        self.root_parser()

    def root_parser(self):    
        self.name = self.body.get("name", None)
        self.parse_permissions()
        self.needs = self.parse_needs()
        self.runs_on = self.body.get("runs-on", None)
        self.condition = self.body.get("if", "")
        self.environment = self.body.get("environment", None)
        self.concurrency = self.body.get("concurrency", None)
        for step_num, step in enumerate(self.body.get("steps", [])):
            self.steps.append(GHWorkflowStep(step, (self.job_num * 100) +  step_num))
        self.outputs = self.body.get("outputs", None)
        self.env = self.parse_job_env()
        self.defaults = self.body.get("defaults", None)
        self.continueonerror = self.body.get("continue-on-error", None)
        self.timeout = self.body.get("timeout-minutes", None)
        self.strategy = self.body.get("strategy", None)
        self.container = self.body.get("container", None)
        self.services = self.body.get("services", None)
        self.reusable_wfl = self.body.get("uses", None)
        self.args = self.parse_wfl_args()
        self.secrets = self.parse_secrets()

    def parse_job_env(self):
        return GithubCI.pack_to_dict_format(self.body.get("env", None), "env")
    
    def parse_wfl_args(self):
        return GithubCI.pack_to_dict_format(self.body.get("with", None), "arg")
    
    def parse_secrets(self):
        return GithubCI.pack_to_dict_format(self.body.get("secrets", None), "secrets")

    def parse_needs(self) -> List:
        needs = self.body.get("needs", [])
        if isinstance(needs, str):
            return [needs]
        elif isinstance(needs, list):
            return needs
        else:
            raise Exception(f"Unknown needs type : {type(needs)}")
        return []
    
    def parse_permissions(self) -> None:
        """Parses the permissions of the job"""
        permissions = self.body.get("permissions", None)
            
        if permissions == None:
            return

        if isinstance(permissions, str):
            if permissions == "read-all|write-all" or permissions == "write-all|read-all":
                permissions = "read and write"
            elif permissions.endswith('-all'):
                permissions = permissions.rstrip("-all")
            else:
                logger.debug("permissions: ", permissions)

            self.permissions.append(
                {
                    "scope" : "across all scopes",
                    "access" : permissions
                } 
            )
        elif isinstance(permissions, dict):
            if len(permissions) == 0:
                self.permissions.append(
                    {
                        "scope" : "across all scopes",
                        "access" : None
                    } 
                )

            for permission_name, permission_value in permissions.items():
                self.permissions.append(
                    {
                        "scope" : "in the `" + permission_name + "` scope",
                        "access" : permission_value
                    } 
                )
                
        return    

                    
class GHWorkflowStep:
    
    def __init__(self, step_config : dict, step_num = 0):
        self.step_config = step_config
        self.id = step_config.get("id", "")
        self.name = step_config.get("name", "")
        self.step_num = step_num

        self.run = {
            "type" : "Unknown",
            "cmd" : "",
            "name" : "",
            "version" : "",
            "shell" : "bash", # Default shell is bash
        }

        # Make sure the step has a run or uses command
        assert "run" in step_config or "uses" in step_config, f"Step {self.id} [{step_config}] has no run or uses command"
        # Make sure the step doesn't have both a run and uses command
        assert not ("run" in step_config and "uses" in step_config), f"Step [{self.id}] has both run and uses commands"

        # Parse the commands
        if "run" in step_config:
            self.run["type"] = "shell_cmd"
            self.run["cmd"] = step_config["run"]
            self.run["shell"] = step_config.get("shell", "default")
        elif "uses" in step_config:
            self.run["type"] = "gh_action"
            self.run["name"] = GHWorkflowStep.get_action_name(step_config["uses"])
            self.run["version"] = GHWorkflowStep.get_action_version(step_config["uses"])
    
        # Parse Arguments      
        self.condition = step_config.get("if", "") 
        self.args = self.prepare_args()
        self.env = self.prepare_env()
        self.continueonerror = step_config.get("continue-on-error", None)
        self.timeout = step_config.get("timeout-minutes", None)


    def prepare_args(self):
        return GithubCI.pack_to_dict_format(self.step_config.get("with", None), "arg")

    def prepare_env(self):
        return GithubCI.pack_to_dict_format(self.step_config.get("env", None), "env")

    def prepare_cmd_ci_vars(self):
        return GithubCI.get_github_variables_from_string(self.run["cmd"])

    @staticmethod
    def get_action_name(action_name):
        try:
            return action_name.split("@")[0]
        except IndexError:
            return action_name
    
    @staticmethod
    def get_action_version(action_name):
        try:
            return action_name.split("@")[1]
        except IndexError:
            return None

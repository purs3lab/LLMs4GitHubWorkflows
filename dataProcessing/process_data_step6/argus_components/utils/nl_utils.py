"""
reference: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
"""
from typing import Dict, List, Tuple, Union
from argus_components.ci import GithubCI
from cron_descriptor import get_description, Options
import json
import os
import re


class NLUtils:
    json_file = open(os.path.join(os.getcwd(), "argus_components/utils/trigger_nl_mapping.json"), 'r')
    TRIGGER_NL = json.load(json_file)

    # name of workflow
    @staticmethod
    def workflow_name(lang : str, name : str) -> str:
        if lang == "none":
            return f"Generate a GitHub Workflow named `{name}`. "
        else:
            return f"Generate a GitHub Workflow named `{name}` for a GitHub repository whose primary programming language is {lang}. "

    # name for workflow runs
    @staticmethod
    def workflow_run_name(name : str) -> str: 
        if name == "":
            return ""
        
        return f"The name for workflow runs is set to `{name}`. "
    
    @staticmethod
    def make_ordinal(n) -> str:
    # Convert an integer into its ordinal representation::
        n = int(n)
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        else:
            suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        return str(n) + suffix
    
    @staticmethod
    def helper_func(sentences : List) -> str:
        if len(sentences) == 0:
            return ""
        
        input_list = [str(sentence) for sentence in sentences]

        if len(input_list) == 1:
            return input_list[0]
        
        result = ", ".join(input_list[:-1])
        result += f" or {input_list[-1]}"
        return result
    
    @staticmethod
    def helper_func_2(sentences : List) -> str:
        if len(sentences) == 0:
            return ""
        
        input_list = [str(sentence) for sentence in sentences]

        if len(input_list) == 1:
            return input_list[0]
        
        result = ", ".join(input_list[:-1])
        result += f" and {input_list[-1]}"
        return result
    
    @staticmethod
    def get_port_description(port_mapping):
        port_mapping = str(port_mapping)
        parts = port_mapping.split('/')
        if len(parts) == 2:
            port, protocol = parts
            return f"the {protocol} port {port} on Docker host is mapped to a random free port on the service container"
        elif len(parts) == 1:
            parts = port_mapping.split(':')
            if len(parts) == 2:
                host_port, container_port = parts
                return f"the port {host_port} on the Docker host is mapped to port {container_port} on the service container"
        return ""

    @staticmethod
    def trigger_helper(event_name : str, activity_types : List) -> str:
        sentences = []
        if event_name in NLUtils.TRIGGER_NL:
            for type in activity_types:
                if type in NLUtils.TRIGGER_NL[event_name]:
                    sentences.append(NLUtils.TRIGGER_NL[event_name][type])
        return NLUtils.helper_func(sentences)
    
    @staticmethod
    def posix_to_nl(cons):
        descriptions = []
        options = Options()
        for con in cons:
            description = get_description(con["cron"], options)
            descriptions.append(description.lower())
        return NLUtils.helper_func(descriptions)
    
    # events that trigger a workflow
    @staticmethod
    def triggers(triggers_list : List[Dict]) -> str:
        length = len(triggers_list)
        if length == 0:
            return ""
        elif length == 1:
            trigger_text = "This workflow will be triggered by an event: "
        else:
            trigger_text = "This workflow will be triggered by multiple events: "

        for i in range(length):
            event_name = triggers_list[i]["type"]
            cons = triggers_list[i]["condition"]
            if length != 1:
                trigger_text += str(i + 1) + ") "

            if cons== "":
                trigger_text += NLUtils.trigger_helper(event_name, ["default"]) + ". "
            elif event_name == "schedule":
                trigger_text += NLUtils.trigger_helper(event_name, ["default"]) +  NLUtils.posix_to_nl(cons) + ". "
            elif event_name == "workflow_call" or event_name == "workflow_dispatch":
                trigger_text += "this workflow is called by another workflow. " if event_name == "workflow_call" else "someone manually triggers the workflow. "
                if "inputs" in cons:
                    num = len(cons["inputs"])
                    if num == 1:
                        trigger_text += "This workflow receives an input: "
                    else:
                        trigger_text += f"This workflow receives {str(num)} inputs: "
                    for input_id in cons["inputs"]:
                        input_text = input_id + '-'
                        input_list = []
                        for item in cons["inputs"][input_id]:
                            if item == "description":
                                input_list.append("this input represents " + cons["inputs"][input_id]["description"].lower())
                            elif item == "default":
                                if not isinstance(cons["inputs"][input_id]["default"], str):
                                    input_list.append("its default value is " + str(cons["inputs"][input_id]["default"]))
                                else:
                                    input_list.append("its default value is " + cons["inputs"][input_id]["default"])
                            elif item == "required":
                                if cons["inputs"][input_id]["required"]:
                                    input_list.append("it must be supplied")
                                else:
                                    input_list.append("it is optional")
                            elif item == "type":
                                input_list.append("the data type is " + str(cons["inputs"][input_id]["type"]))
                            elif item == "options":
                                opt_txt = "it has options including " + NLUtils.helper_func_2(cons["inputs"][input_id]["options"])
                                input_list.append(opt_txt)

                        input_text += NLUtils.helper_func_2(input_list) + '; '
                        trigger_text += input_text
                    trigger_text = trigger_text.rstrip("; ") + ". "

                if "outputs" in cons:
                    num = len(cons["outputs"])
                    if num == 1:
                        trigger_text += "This workflow has an output: "
                    else:
                        trigger_text += f"This workflow has {str(num)} outputs: "
                    for output_id in cons["outputs"]:
                        output_text = output_id +'-'
                        output_list = []
                        for item in cons["outputs"][output_id]:
                            if item == "description":
                                output_list.append("it represents " + cons["outputs"][output_id]["description"].lower())
                            elif item == "value":
                                output_list.append("its value is " + cons["outputs"][output_id]["value"])
                        output_text += NLUtils.helper_func_2(output_list) + '; '
                        trigger_text += output_text
                    trigger_text = trigger_text.rstrip("; ") + ". "

                if "secrets" in cons:
                    num = len(cons["secrets"])
                    if num == 1:
                        trigger_text += "It receives a secret: "
                    else:
                        trigger_text += f"It receives {str(num)} secrets: "
                    for secret_id in cons["secrets"]:
                        secret_text = secret_id +'-'
                        secret_list = []
                        for item in cons["secrets"][secret_id]:
                            if item == "description":
                                secret_list.append("it represents " + cons["secrets"][secret_id]["description"].lower())
                            elif item == "required":
                                if cons["secrets"][secret_id]["required"]:
                                    secret_list.append("it must be supplied")
                                else:
                                    secret_list.append("it is optional")
                        secret_text += NLUtils.helper_func_2(secret_list) + '; '
                        trigger_text += secret_text
                    trigger_text = trigger_text.rstrip("; ") + ". "

            elif event_name == "workflow_run":
                wfs = cons["workflows"]
                types = cons["types"] if "types" in cons else []
                branch_catagory = "branches" if "branches" in cons else None
                branch_catagory = "branches-ignore" if "branches-ignore" in cons else branch_catagory
                 
                if len(wfs) == 1:
                    wf_name = "the workflow named " + cons["workflows"][0]
                else:
                    wf_name = "one of the workflows(" + NLUtils.helper_func_2(cons["workflows"]) + ")"

                activity_type_text = " is " + ("requested, in progress or completed" if len(types) == 0 else NLUtils.helper_func(types))
                
                branch_text = ""
                if branch_catagory == "branches":
                    branch_text = " on a branch whose name matches " + NLUtils.helper_func(cons["branches"])
                elif branch_catagory == "branches-ignore": 
                    branch_text += " on a branch whose name does not match " + NLUtils.helper_func(cons["branches-ignore"])

                trigger_text += wf_name + activity_type_text + branch_text + ". "
                
            elif event_name == "repository_dispatch":
                trigger_text += NLUtils.trigger_helper(event_name, ["default"])
                if "types" in cons:
                    if isinstance(cons["types"], str):
                        trigger_text += " and its event type is " + cons["types"]
                    else:
                        trigger_text += " and its event type includes " + NLUtils.helper_func_2(cons["types"])
                trigger_text += ". "

            else:
                if "types" in cons:
                    activity_types = cons["types"]
                    if isinstance(activity_types, str):
                        activity_types = [activity_types]
                    trigger_text += NLUtils.trigger_helper(event_name, activity_types) + ". "

                if event_name == "pull_request" or event_name == "pull_request_target" or event_name == "push":
                    branches_list = []
                    tags_list = []
                    paths_list = []

                    branch_catagory = "branches" if "branches" in cons else None
                    branch_catagory = "branches-ignore" if "branches-ignore" in cons else branch_catagory
                    if branch_catagory:
                        for item in cons[branch_catagory]:
                            if not isinstance(item, str):
                                item = str(item)
                            if re.search(r"[*!+?\[\]]+", item):
                                branches_list.append("a branch whose name matches " + item)
                            else:
                                branches_list.append("a branch named " + item)
                
                    tags_catagory = "tags" if "tags" in cons else None
                    tags_catagory = "tags-ignore" if "tags-ignore" in cons else tags_catagory
                    if tags_catagory:
                        for item in cons[tags_catagory]:
                            if not isinstance(item, str):
                                item = str(item)
                            if re.search(r"[*!+?\[\]]+", item):
                                tags_list.append("a tag whose name matches " + item)
                            else:
                                tags_list.append("a tag named " + item)

                    if branch_catagory == "branches" and tags_catagory == "tags":
                        trigger_text += "The workflow would run whenever there is a push event to: "
                        trigger_text += NLUtils.helper_func(branches_list + tags_list) + ". "
                    elif branch_catagory == "branches-ignore" and tags_catagory == "tags-ignore":
                        trigger_text += "The workflow would run whenever there is a push event unless the push event is to: "
                        trigger_text += NLUtils.helper_func(branches_list + tags_list) + ". "
                    else:
                        if branch_catagory == "branches":
                            trigger_text += "The workflow would run whenever there is a push event to: " if event_name == "push" else "The workflow would run whenever there is a pull_request event targeting: "
                            trigger_text += NLUtils.helper_func(branches_list) + ". "
                        elif branch_catagory == "branches-ignore": 
                            trigger_text += "The workflow would run whenever there is a push event unless the push event is to: " if event_name == "push" else "The workflow would run whenever there is a pull_request event unless the pull request is targeting: "
                            trigger_text += NLUtils.helper_func(branches_list) + ". "
                        if tags_catagory == "tags":
                            trigger_text += "The workflow would run whenever there is a push event to: " if event_name == "push" else "The workflow would run whenever there is a pull_request event targeting: "
                            trigger_text += NLUtils.helper_func(tags_list) + ". "
                        elif tags_catagory == "tags-ignore": 
                            trigger_text += "The workflow would run whenever there is a push event unless the push event is to: " if event_name == "push" else "The workflow would run whenever there is a pull_request event unless the pull request is targeting: "
                            trigger_text += NLUtils.helper_func(tags_list) + ". "

                    paths_catagory = "paths" if "paths" in cons else None
                    paths_catagory = "paths-ignore" if "paths-ignore" in cons else paths_catagory
                    if paths_catagory:
                        for item in cons[paths_catagory]:
                            if not isinstance(item, str):
                                item = str(item)
                            paths_list.append(item)
                        if paths_catagory == "paths":
                            trigger_text += f"Only if at least one path of {event_name} event matches a pattern in the paths filter({NLUtils.helper_func(paths_list)}), the workflow runs. "
                        else:
                            trigger_text += f"When all the path names of {event_name} event match patterns in the paths-ignore filter({NLUtils.helper_func(paths_list)}), the workflow will not run. "           

        return trigger_text

    @staticmethod
    def permissions(permissions_list : List[Dict], job_specific : str) -> str: 
        if len(permissions_list) == 0:
            return ""
        if job_specific:
            permission_text = f"The job `{job_specific}` modifies the default permissions for the GITHUB_TOKEN: "
        else:
            permission_text = "The workflow modifies the default permissions for the GITHUB_TOKEN: "

        temp_list = []
        for item in permissions_list:
            permission_name = item["scope"]
            permission_value = item["access"]
            if permission_value:
                temp_list.append(permission_value + " access is granted to the GITHUB_TOKEN " + permission_name)
            else:
                if job_specific:
                    temp_list.append("the job disables permissions for the GITHUB_TOKEN " + permission_name)
                else:
                    temp_list.append("the workflow disables permissions for the GITHUB_TOKEN " + permission_name)
        permission_text += NLUtils.helper_func_2(temp_list) + ". "

        if job_specific:
            permission_text += f"This permission setting only applies to the job `{job_specific}`. "
        else:
            permission_text += "This permission setting applies to all jobs in the workflow. "
        return permission_text
    
    @staticmethod
    def env(env_list : List[Dict], scope : str) -> str: 
        if len(env_list) == 0:
            return ""
        
        if len(env_list) == 1:
            text = f"The {scope} sets an environment variable to use: "
        else:
            text = f"The {scope} sets {str(len(env_list))} environment variables to use: "
        res = []
        for var in env_list:
            res.append("`" + str(var["name"]) + "` is set to `" + str(var["value"]) + "`")
        text += NLUtils.helper_func_2(res) + ". "
        return text

    @staticmethod
    def concurrency(con, scope : str) -> str:
        if con == None:
            return ""
        text = ""
        if isinstance(con, str):
            text += "Only a single {} using the {} concurrency group will run at a time. ".format(scope, con)
        elif isinstance(con, dict):
            if "group" in con:
                text += "Only a single {} using the {} concurrency group will run at a time. ".format(scope, con["group"])
            if "cancel-in-progress" in con and con["cancel-in-progress"]:
                text += "When this {} is queued, any currently running {} in the same concurrency group will be canceled. ".format(scope, scope)
        return text
    
    @staticmethod
    def defaults(default, scope : str) -> str:
        if default == None:
            return ""
        text = ""
        if isinstance(default, dict) and "run" in default:
            text += "For all run steps in the {}, ".format(scope)
            text_list = []
            if "shell" in default["run"]:
                text_list.append("default shell is set to {}".format(default["run"]["shell"]))
            if "working-directory" in default["run"]:
                text_list.append("default working directory is set to {}".format(default["run"]["working-directory"]))
            text += NLUtils.helper_func_2(text_list) + ". "
        return text
    
    @staticmethod
    def job_step_name(jobs_list : List, add_step : bool) -> str:
        jobs_count = len(jobs_list)
        jobs_text = "The workflow has one job. " if jobs_count == 1 else "The workflow has {} jobs. ".format(str(jobs_count))

        for i in range(jobs_count):
            job = jobs_list[i]
            # id, name
            if job.name:
                jobs_text += "The {} job is named `{}` and its job id is `{}`. ".format(NLUtils.make_ordinal(i + 1), job.name, job.id)
            else:
                jobs_text += "The job id of the {} job is `{}`. ".format(NLUtils.make_ordinal(i + 1), job.id)
            
            if not add_step:
                continue

            # steps
            jobs_text += NLUtils.steps(job.id, job.steps, False)

        return jobs_text
    
    @staticmethod
    def jobs(jobs_list : List, step_detailed : bool) -> str: 
        jobs_count = len(jobs_list)
        jobs_text = "The workflow has one job. " if jobs_count == 1 else "The workflow has {} jobs. ".format(str(jobs_count))

        for i in range(jobs_count):
            job = jobs_list[i]
            # id, name
            if job.name:
                jobs_text += "The {} job is named `{}` and its job id is `{}`. ".format(NLUtils.make_ordinal(i + 1), job.name, job.id)
            else:
                jobs_text += "The job id of the {} job is `{}`. ".format(NLUtils.make_ordinal(i + 1), job.id)

            # needs
            if len(job.needs) > 0:
                jobs_need = []
                for j in job.needs:
                    jobs_need.append("`" + j + "`")
                jobs_text += "Before this job runs, " + NLUtils.helper_func_2(jobs_need) + " must complete successfully. "
            
            # if
            if job.condition != "":
                jobs_text += "This job will run only if the condition({}) is met. ".format(job.condition)

            # runs-on
            if job.runs_on != None:
                if isinstance(job.runs_on, str):
                    jobs_text += "This job will run on " + job.runs_on + " runner. "
                elif isinstance(job.runs_on, list):
                    jobs_text += "This job will execute on any runner that has the labels " + NLUtils.helper_func_2(job.runs_on) + ". "
                elif isinstance(job.runs_on, dict):
                    if "group" in job.runs_on:
                        if isinstance(job.runs_on["group"], str):
                            job.runs_on["group"] = [job.runs_on["group"]]
                        if "labels" in job.runs_on:
                            if isinstance(job.runs_on["labels"], str):
                                job.runs_on["labels"] = [job.runs_on["labels"]]
                            jobs_text += "This job will execute on any runner that is a member of {} and also has labels {}. ".format(NLUtils.helper_func(job.runs_on["group"]), NLUtils.helper_func_2(job.runs_on["labels"]))
                        else:
                            jobs_text += "This job will execute on any runner that is a member of {}. ".format(NLUtils.helper_func(job.runs_on["group"]))
                    else:
                        print("Wrong key of runs-on!!!!")

            # strategy
            if job.strategy != None:
                if "matrix" in job.strategy:
                    jobs_text += "The job uses a matrix strategy to automatically create multiple job runs that are based on the combinations of the variables. "
                    if isinstance(job.strategy["matrix"], str):
                        jobs_text += "The matrix is {}. ".format(job.strategy["matrix"])
                    elif isinstance(job.strategy["matrix"], dict):
                        include_var_list = None
                        exclude_var_list = None

                        for matrix_var, matrix_var_values in job.strategy["matrix"].items():
                            if matrix_var == "include":
                                include_var_list = matrix_var_values
                            elif matrix_var == "exclude":
                                exclude_var_list = matrix_var_values
                            else:
                                if len(matrix_var_values) == 1:
                                    jobs_text += "The variable `{}` has one value: {}. ".format(matrix_var, matrix_var_values[0])
                                else:
                                    jobs_text += "The variable `{}` has {} values: {}. ".format(matrix_var, str(len(matrix_var_values)), NLUtils.helper_func_2(matrix_var_values))
                        
                        if exclude_var_list != None:
                            jobs_text += "If combinations of variables partially match one of the objects {}, combinations should be excluded from the matrix. ".format(exclude_var_list)

                        if include_var_list != None:
                            jobs_text += "For each object in the {} list, the key:value pairs in the object will be added to each of the matrix combinations if none of the key:value pairs overwrite any of the original matrix values. If the object cannot be added to any of the matrix combinations, a new matrix combination will be created instead. ".format(include_var_list)

                    
                if "fail-fast" in job.strategy and job.strategy["fail-fast"]:
                    jobs_text += "If any job run in the matrix fails, all in-progress and queued jobs in the matrix will be canceled. "

                if "max-parallel" in job.strategy:
                    jobs_text += "The maximum number of job runs in parallel is set to {}. ".format(str(job.strategy["max-parallel"]))

            # container
            if job.container != None:
                if isinstance(job.container, str):
                    jobs_text += "The job creates a Docker container that uses `{}` image. ".format(str(job.container))
                elif isinstance(job.container, dict):
                    jobs_text += "The job creates a Docker container"
                    if "image" in job.container:
                        jobs_text += " that uses `{}` image. ".format(job.container["image"])
                    else:
                        jobs_text += ". "
                    if "credentials" in job.container:
                        jobs_text += "The credentials for the container registry are that `username` is {} and `password` is {}. ".format(job.container["credentials"]["username"], job.container["credentials"]["password"])
                    if "env" in job.container:
                        if len(job.container["env"]) == 1:
                            jobs_text += "The container sets an environment variable to use: "
                        else:
                            jobs_text += "The container sets {} environment variables to use: ".format(str(len(job.container["env"]))) 
                        container_var = []
                        for key, value in job.container["env"].items():
                            container_var.append("`" + str(key) + "` is set to `" + str(value) + "`")
                        jobs_text += NLUtils.helper_func_2(container_var) + ". "
                    if "ports" in job.container:
                        ports_str = []
                        for port in job.container["ports"]:
                            ports_str.append(str(port))
                        jobs_text += "The container maps port {} to the host machine. ".format(NLUtils.helper_func_2(ports_str))
                    if "volumes" in job.container:
                        if len(job.container["volumes"]) == 1:
                            jobs_text += "The container also sets a volume to use: `{}`. ".format(job.container["volumes"][0])
                        else:
                            jobs_text += "The container also sets an array of volumes to use: {}. ".format(NLUtils.helper_func_2(job.container["volumes"]))
                    if "options" in job.container:
                        jobs_text += "It configures additional container resource options: {}. ".format(job.container["options"])
                    

            # services
            if job.services != None and isinstance(job.services, dict):
                for service_id, service_body in job.services.items():
                    jobs_text += "The job defines a service called {}".format(service_id)
                    if "image" in service_body:
                        jobs_text += " which will be created using the Docker image `{}`. ".format(service_body["image"])
                    else:
                        jobs_text += ". "
                    if "credentials" in service_body:
                        jobs_text += "The authentication credentials required to access the Docker image registry for {} are that `username` is {} and `password` is {}. ".format(service_id, service_body["credentials"]["username"], service_body["credentials"]["password"])
                    if "env" in service_body:
                        if len(service_body["env"]) == 1:
                            jobs_text += "The service container sets an environment variable to use: "
                        else:
                            jobs_text += "The service container sets {} environment variables to use: ".format(str(len(service_body["env"]))) 
                        service_container_var = []
                        for key, value in service_body["env"].items():
                            service_container_var.append("`" + str(key) + "` is set to `" + str(value) + "`")
                        jobs_text += NLUtils.helper_func_2(service_container_var) + ". "
                    if "ports" in service_body:
                        jobs_text += "For communication, "
                        port_list = []
                        for port_str in service_body["ports"]:
                            port_description = NLUtils.get_port_description(port_str)
                            if port_description == "":
                                print(f"[Error] Get port description error.")
                            else:
                                port_list.append(port_description)
                        jobs_text += NLUtils.helper_func_2(port_list) + ". "
                            
                    if "volumes" in service_body:
                        if len(service_body["volumes"]) == 1:
                            jobs_text += "The service container sets a volume to use: `{}`. ".format(service_body["volumes"][0])
                        else:
                            jobs_text += "The service container sets an array of volumes to use: {}. ".format(NLUtils.helper_func_2(service_body["volumes"]))

                    if "options" in service_body:
                        jobs_text += "It configures additional Docker container resource options: {}. ".format(service_body["options"])
                    
            # permissions
            jobs_text += NLUtils.permissions(job.permissions, job.id)

            # env
            jobs_text += NLUtils.env(job.env, "job")

            # environment
            if job.environment != None:
                if isinstance(job.environment, str):
                    jobs_text += "This job references {} environment. ".format(job.environment)
                elif isinstance(job.environment, dict):
                    if "name" in job.environment:
                        jobs_text += "This job references {} environment".format(job.environment["name"])
                    else:
                        jobs_text += "This job references an environment"

                    if "url" in job.environment:
                        jobs_text += " whose url is {}. ".format(job.environment["url"])
                    else:
                        jobs_text += ". "
                else:
                    print("Wrong type of job.environment!")

            # concurrency
            jobs_text += NLUtils.concurrency(job.concurrency, "job")

            # defaults
            jobs_text += NLUtils.defaults(job.defaults, "job")

            # continue-on-error 
            if job.continueonerror:
                jobs_text += "When the job run fails, the workflow run will not fail. "
            
            # timeout-minutes
            if job.timeout:
                jobs_text += "The maximum number of minutes to run the job is {}. ".format(str(job.timeout))

            # steps
            jobs_text += NLUtils.steps(job.id, job.steps, step_detailed)
            
            # uses, with, secrets: when a job is used to call a reusable workflow
            if job.reusable_wfl != None:
                jobs_text += "This job will call a reusable workflow located at `{}`. ".format(job.reusable_wfl)
            
            if len(job.args) > 0:
                jobs_text += "The job will pass an input to the called workflow: " if len(job.args) == 1 else "The job will pass {} inputs to the called workflow: ".format(str(len(job.args)))
                args_list = []
                for arg in job.args:
                    args_list.append("the input `{}` is `{}`".format(arg["name"], arg["value"]))
                jobs_text += NLUtils.helper_func_2(args_list) + ". "

            if len(job.secrets) > 0:
                jobs_text += "The job will pass a secret to the called workflow: " if len(job.secrets) == 1 else "The job will pass {} secrets to the called workflow: ".format(str(len(job.secrets)))
                secrets_list = []
                for secret in job.secrets:
                    secrets_list.append("the secret `{}` is `{}`".format(secret["name"], secret["value"]))
                jobs_text += NLUtils.helper_func_2(secrets_list) + ". "

            # outputs
            if job.outputs != None:
                jobs_text += "This job has an output: " if len(job.outputs) == 1 else "This job has {} outputs: ".format(str(len(job.outputs)))
                outputs_list = []
                for key,value in job.outputs.items():
                    outputs_list.append("`{}` is defined as {}".format(key, value))
                jobs_text += NLUtils.helper_func_2(outputs_list) + ". "
            
        return jobs_text
            
    @staticmethod
    def steps(job_id : str, steps_list : List, detailed : bool) -> str:
        steps_count = len(steps_list)
        if steps_count == 0:
            return ""
        steps_text = "The job `{}` has ".format(job_id)
        steps_text += "one step. " if steps_count == 1 else "{} steps. ".format(str(steps_count))

        for i in range(steps_count):
            step = steps_list[i]
            # name, id
            if step.id != "":
                steps_text += "The {} step is named `{}` and its id is `{}`. ".format(NLUtils.make_ordinal(i + 1), step.name, step.id)
            else:
                steps_text += "The {} step is named `{}`. ".format(NLUtils.make_ordinal(i + 1), step.name)

            if not detailed:
                continue

            # if
            if step.condition != "":
                steps_text += "This step will run only if the condition({}) is met. ".format(step.condition)
            
            # env
            steps_text += NLUtils.env(step.env, "step")
            
            # uses, run and shell
            if step.run["type"] == "gh_action":
                if step.run["version"]:
                    action_type = GithubCI.get_option_dict_from_sting(step.run["version"])["type"]
                    if action_type == "tag":
                        steps_text += "This step runs action `{}` tagged as {}. ".format(step.run["name"], step.run["version"])
                    elif action_type == "commit":
                        steps_text += "This step runs action `{}` whose commit is {}. ".format(step.run["name"], step.run["version"])
                    elif action_type == "branch":
                        steps_text += "This step runs action `{}` from the {} branch. ".format(step.run["name"], step.run["version"])
                else:
                    steps_text += "This step runs action `{}`.".format(step.run["name"])
            elif step.run["type"] == "shell_cmd":
                shell_description = {
                    "bash" : "uses bash to run a script",
                    "pwsh" : "uses PowerShell Core to run a script",
                    "python" : "runs a python script",
                    "sh" : "uses sh to run a script",
                    "cmd" : "uses Windows cmd to run a script",
                    "powershell" : "uses PowerShell Desktop to run a script",
                    "default" : "runs a script",
                }
                if step.run["shell"] in shell_description:
                    steps_text += "This step {}: `{}`. ".format(shell_description[step.run["shell"]], step.run["cmd"])
                else:
                    steps_text += "This step uses a custom shell {} to run a script: `{}`. ".format(step.run["shell"], step.run["cmd"])
            else:
                print("Step has no run or uses command!!!!!!!!!!")
            
            # with
            if len(step.args) > 0:
                steps_text += "The step defines an input parameter for the action: " if len(step.args) == 1 else "The step defines {} input parameters for the action: ".format(str(len(step.args))) 
                step_args = []
                for arg in step.args:
                    step_args.append("`" + str(arg["name"]) + "` is set to `" + str(arg["value"]) + "`")
                steps_text += NLUtils.helper_func_2(step_args) + ". "
            
            # continue-on-error
            if step.continueonerror:
                steps_text += "When this step fails, the job will move on to the next step. "
            
            # timeout-minutes
            if step.timeout:
                steps_text += "The maximum number of minutes to run the step is {}. ".format(str(step.timeout))

        return steps_text
    
    @staticmethod
    def dependency(dependencies : Dict) -> str:
        text = ""
        if len(dependencies['actions']) > 0:
            text += "Here are some Github Actions that might be used in the workflow: "
            actions_list = []
            for item in dependencies['actions']:
                if item['version'] is None:
                    actions_list.append(item['name'])
                else:
                    actions_list.append(item['version'] + " version of " + item['name'])
            text += NLUtils.helper_func_2(actions_list) + ". "

        if len(dependencies['workflows']) > 0:
            text += "Here are some reusable workflows that might be used in the workflow: "
            wf_list = []
            for item in dependencies['workflows']:
                wf_list.append(item)
            text += NLUtils.helper_func_2(wf_list) + ". "

        if len(dependencies['vars']) > 0:
            text += "Here are some variables that might be used in the workflow: "
            var_list = []
            for item in dependencies["vars"]:
                var_list.append(item['expression'])
            text += NLUtils.helper_func_2(var_list) + ". "
        
        return text

            
            
            

            
        

"""
Type: invalid expression embedded with ${{ }} syntax         
Ref: https://docs.github.com/en/actions/learn-github-actions/expressions
     An expression can be any combination of literal values, references to a context, or functions.
message: 1. "got unexpected %s while lexing %s, expecting %s%s"
         2. "unexpected %s while parsing %s. expecting %s"
         3. "unexpected EOF while lexing expression"
         4. "property %q is not defined in object type %s"
         5. "receiver of object dereference %q must be type of object but got %q"
         6. "property %q is not defined in object type %s as element of filtered array"
         7. "property filtered by %q at object filtering must be type of object but got %q" 
         8. "index access of array must be type of number but got %q"
         9. "property access of object must be type of string but got %q"
        10. "index access operand must be type of object or array but got %q"
        11. object, array, and null values should not be evaluated in template with ${{ }} but evaluating the value of type {string => string} [expression]
        12. type of expression at "env" must be object but found type string [expression]
        13. "undefined variable %q. available variables are %s"
        14. "property %q is not defined in object type %s"
        15. "undefined function %q. available functions are %s" 
        16. "number of arguments is wrong. function %q takes %s%d parameters but %d arguments are given"
        17. "%s argument of function call is not assignable. %q cannot be assigned to %q. called function type is %q"
        18. "format string %q does not contain placeholder {%d}. remove argument which is unused in the format string"
        19. "format string %q contains placeholder {%d} but only %d arguments are given to format"
        20. "context %q is not allowed here. available %s %s. see https://docs.github.com/en/actions/learn-github-actions/contexts#context-availability for more details"
        21. "calling function %q is not allowed here. %q is only available in %s. see https://docs.github.com/en/actions/learn-github-actions/contexts#context-availability for more details"
        22. "configuration variable name %q must not start with the GITHUB_ prefix (case insensitive). note: see the convention at https://docs.github.com/en/actions/learn-github-actions/variables#naming-conventions-for-configuration-variables"
        23. "configuration variable name %q can only contain alphabets, decimal numbers, and '_'. note: see the convention at https://docs.github.com/en/actions/learn-github-actions/variables#naming-conventions-for-configuration-variables"
        24. "no configuration variable is allowed since the variables list is empty in actionlint.yaml. you may forget adding the variable %q to the list"
        25. "undefined configuration variable %q. defined configuration variables in actionlint.yaml are %s"
        26. "elements of object at receiver of object filtering `.*` must be type of object but got %q. the type of receiver was %q"
        27. "object type %q cannot be filtered by object filtering `.*` since it has no object element"
        28. "receiver of object filtering `.*` must be type of array or object but got %q"
        29. "type of operand of ! operator %q is not assignable to type \"bool\""
        30. "type of input %q must be bool but found type %s"
        31. "type of input %q must be number but found type %s"
        32. "type of expression must be bool but found type %s"
        33. "type of expression at %q must be number but found type %s"
        34. "type of expression at %q must be array but found type %s"
        35. "type of expression at %q must be object but found type %s"
        36. "type of expression at \"runs-on\" must be string or array but found type %q"
        37. "one ${{ }} expression should be included in %q value but got %d expressions"
        38. "object, array, and null values should not be evaluated in template with ${{ }} but evaluating the value of type %s"
        39. "\"if\" condition should be type \"bool\" but got type %q"
        40. "input %q is typed as %s by reusable workflow %q. %s value cannot be assigned"    ???(reusable workflow)
        41. "invalid integer value: %q: %s"
        42. "invalid float value: %q: %s"
        43. "parsing invalid integer literal %q: %s"
        44. "parsing invalid float literal %q: %s"
        45. "parser did not reach end of input after parsing the expression. %d remaining token(s) in the input: %s"

# Type: invalid credential usage
# messages: 
# (kind: credentials)  1. "\"password\" section in %s should be specified via secrets. do not put password value directly"
(kind: syntax-check) 2. "both \"username\" and \"password\" must be specified in \"credentials\" section"

# Type: if condition always evaluated to be true(kind: if-cond)
# message: 1. "if: condition %q is always evaluated to true because extra characters are around ${{ }}"

"""

from utils import connect_to_collection
import re
     
"""
Type: Unexpected/Invalid Identifiers
message: 1. "expected %q key for %q section but got %q"
	    2. "unexpected key %q for %q section. expected one of %v"
	    3. "unexpected key %q for %q section"
         4. "element of \"schedule\" section must be mapping and must contain one key \"cron\""
         5. "%q is only available for a reusable workflow call with \"uses\" but \"uses\" is not found in job %q"
         6. "when a reusable workflow is called with \"uses\", %q is not available. only following keys are allowed: \"name\", \"uses\", \"with\", \"secrets\", \"needs\", \"if\", and \"permissions\" in job %q"
         7. "key %q is duplicated in %s. previously defined at %s%s"
         8. "\"working-directory\" is not available with \"uses\". it is only available with \"run\""
         9. "this step is for running shell command since it contains at least one of \"run\", \"shell\" keys, but also contains %q key which is used for running action"
         10. "this step is for running action since it contains at least one of \"uses\", \"with\" keys, but also contains %q key which is used for running shell command"
         16. "\"on\" section is missing in workflow"
         17. "\"jobs\" section is missing in workflow"
         18. "\"steps\" section is missing in job %q"
         19. "\"runs-on\" section is missing in job %q"
         20. "\"type\" is missing at %q input of workflow_call event"
         21. "\"value\" is missing at %q output of workflow_call event"
         22. "group name is missing in \"concurrency\" section"
         23. "name is missing in \"environment\" section"
         24. "\"run\" is required to run script in step"
         25. "\"uses\" is required to run action in step"
"""
unexpected_identifiers_patterns = [
     r"expected .+ key for .+ section but got .+",
     r"unexpected key .+",
     r"element of \"schedule\" section must be mapping and must contain one key \"cron\"",
     r".+ is only available for a reusable workflow call with \"uses\" but \"uses\" is not found in job .+",
     r"when a reusable workflow is called with \"uses\", .+",
     r"key .+ is duplicated in .+ previously defined at .+",
     r"\"working-directory\" is not available with \"uses\". it is only available with \"run\"",
     r"this step is for running shell command since it contains at least one of \"run\", \"shell\" keys, but also contains .+ key which is used for running action",
     r"this step is for running action since it contains at least one of \"uses\", \"with\" keys, but also contains .+ key which is used for running shell command",
     r"\"on\" section is missing in workflow",
     r"\"jobs\" section is missing in workflow",
     r"\"steps\" section is missing in job .+",
     r"\"runs-on\" section is missing in job .+",
     r"\"type\" is missing at .+ input of workflow\_call event",
     r"\"value\" is missing at .+ output of workflow\_call event",
     r"group name is missing in \"concurrency\" section",
     r"name is missing in \"environment\" section",
     r"\"run\" is required to run script in step",
     r"\"uses\" is required to run action in step"
]

"""
Type: Unexpected mapping values
message: 1. "%s should not be empty. please remove this section if it's unnecessary"
         2. "%q section should not be empty"
         3. "string should not be empty"
         4. "\"schedule\" section must be sequence node but got %s node with %q tag"
         5. "%q section must be sequence node but got %s node with %q tag"
         6. "expecting a single ${{...}} expression or %s, but found plain text node"
         7. "expected bool value but found %s node with %q tag"
         8. "expected scalar node for integer value but found %s node with %q tag"
         9. "expected scalar node for float value but found %s node with %q tag"
         10. "expected scalar node for string value but found %s node with %q tag"
         11. "%s is %s node but mapping node is expected"
         12. "value at \"max-parallel\" must be greater than zero: %v"
         13. "value at \"timeout-minutes\" must be greater than zero: %v"
"""

unexpected_mapping_values_patterns = [
     r".+ should not be empty",
     r"\"schedule\" section must be sequence node but got .+ node with .+ tag",
     r".+ section must be sequence node but got .+ node with .+ tag",
     r"expecting a single \$\{\{...\}\} expression or .+, but found plain text node",
     r"expected bool value but found .+ node with .+ tag",
     r"expected scalar node for .+ value but found .+ node with .+ tag",
     r".+ is .+ node but mapping node is expected",
     r"value at .+ must be greater than zero: .+"
]

"""
Type: invalid Webhook event configuration
messages: 
(kind: syntax-check) 20. `input type of workflow_dispatch event must be one of "string", "boolean", "choice", "environment" but got %q`
(kind: syntax-check) 21. "invalid value %q for input type of workflow_call event. it must be one of \"boolean\", \"number\", or \"string\""
(kind: syntax-check) 22. "%q event should not be listed in sequence. Use mapping for \"on\" section and configure the event as values of the mapping"
"""

unexpected_event_patterns = [
     r"input type of workflow\_dispatch event must be one of \"string\", \"boolean\", \"choice\", \"environment\" but got .+",
     r"invalid value .+ for input type of workflow\_call event. it must be one of \"boolean\", \"number\", or \"string\"",
     r".+ event should not be listed in sequence. Use mapping for \"on\" section and configure the event as values of the mapping"
]

def related_event(str):
     for pattern in unexpected_event_patterns:
          match = re.search(pattern, str)
          if match:
               return True
     return False

def related_Identifiers(str):
     for pattern in unexpected_identifiers_patterns:
          match = re.search(pattern, str)
          if match:
               return True
     return False

def related_mapping_values(str):
     for pattern in unexpected_mapping_values_patterns:
          match = re.search(pattern, str)
          if match:
               return True
     return False
aa = set()
source = connect_to_collection("LLM4wf", "DatasetII")
# cursor = source.find(no_cursor_timeout=True)
cursor = source.find({"syntax_error": True})
docs = [doc for doc in cursor]
for doc in docs:
     if str(doc["_id"]) == "63c49b301899db58864f21f5":
          source.delete_one({"_id": doc["_id"]})

     _type = None
     kind = doc["bug"][0]['kind']
     message = doc["bug"][0]['message']
     line_num = doc["bug"][0]['line']
     if kind == 'workflow-call':
          """
          Type: invalid reusable workflow call (kind: workflow-call)
          message: 1. "reusable workflow call %q at \"uses\" is not following the format \"owner/repo/path/to/workflow.yml@ref\" nor \"./path/to/workflow.yml\". see https://docs.github.com/en/actions/learn-github-actions/reusing-workflows for more details"
               2. "input %q is required by %q reusable workflow"
               3. "input %q is not defined in %q reusable workflow. %s"
               4. "secret %q is required by %q reusable workflow"
               5. "secret %q is not defined in %q reusable workflow. %s"
          """
          _type = "invalid reusable workflow call"

     elif kind == 'shellcheck' or kind == 'shell-name':
          """
          Type: invalid shell command
          message:
          (kind: shell-name)    1. "shell name %q is invalid%s. available names are %s"
          (kind: shell-check)   2. "shellcheck reported issue in this script: SC%d:%s:%d:%d: %s"
          """
          _type = "invalid shell command"
          
     elif kind == 'permissions':
          """
          Type: invalid permissions configuration (kind: permissions)
          message: 1. "%q is invalid for permission for all the scopes. available values are \"read-all\" and \"write-all\""
               2. "unknown permission scope %q. all available permission scopes are %s"
               3. "%q is invalid for permission of scope %q. available values are \"read\", \"write\" or \"none\""       
          """
          _type = "invalid permissions configuration"

     elif kind == 'matrix':
          """
          Type: invalid matrix configuration (kind: matrix)
          message: 1. "duplicate value %s is found in matrix %q. the same value is at %s"
               2. "\"exclude\" section exists but no matrix variation exists"
               3. "%q in \"exclude\" section does not exist in matrix. available matrix configurations are %s"
               4. "value %s in \"exclude\" does not match in matrix %q combinations. possible values are %s"   
          """
          _type = "invalid matrix configuration"

     elif kind == 'job-needs':
          pattern = r"job ID .+ duplicates\. previously defined at .+"
          match = re.search(pattern, message)
          if match:
               """
               Type: Unexpected/Invalid Identifiers
                    (kind: job-needs)    13. "job ID %q duplicates. previously defined at %s. note that job ID is case insensitive"
               """
               _type = "unexpected/invalid identifier"
          else:
               """
               Type: invalid job dependency (kind: job-needs)
               message: 1. "job ID %q duplicates in \"needs\" section. note that job ID is case insensitive"
                    2. "job %q needs job %q which does not exist in this workflow"
                    3. "cyclic dependencies in \"needs\" configurations of jobs are detected. detected cycle is %s"
               """
               _type = "invalid job dependency"

     elif kind == 'glob':
          """
          Type: invalid glob pattern (kind: glob)
          message: 1. "invalid glob pattern. %s%s. %s"
               2. "character " + cfmt + " is invalid for branch and tag names. %s. see `man git-check-ref-format` for more details. note that regular expression is unavailable"
               3. "glob pattern cannot be empty"
               4. "error while scanning glob pattern %q: %s"
               5. "path value must not start with spaces"
               6. "path value must not end with spaces"
          """
          _type = "invalid glob pattern"
          
     elif kind == 'events':
          """
          Type: invalid Webhook event configuration (kind: events)
          messages: 1. "invalid CRON format %q in schedule event: %s"
                    2. "scheduled job runs too frequently. it runs once per %g seconds. the shortest interval is once every 5 minutes"
                    3. "%q filter is not available for %s event. it is only for %s %s"
                    4. "both %q and %q filters cannot be used for the same event %q. note: use '!' to negate patterns"
                    5. "unknown Webhook event %q. see https://docs.github.com/en/actions/learn-github-actions/events-that-trigger-workflows#webhook-events for list of all Webhook event names"
                    6. "no workflow is configured for \"workflow_run\" event"
                    7. "\"workflows\" cannot be configured for %q event. it is only for workflow_run event"
                    8. "\"types\" cannot be specified for %q Webhook event"
                    9. "invalid activity type %q for %q Webhook event. available types are %s"
                    10. "input of workflow_call event %q is typed as number but its default value %q cannot be parsed as a float number: %s"
                    11. "input of workflow_call event %q is typed as boolean. its default value must be true or false but got %q"
                    12. "input %q of workflow_call event has the default value %q, but it is also required. if an input is marked as required, its default value will never be used"
                    13. "input type of %q is \"choice\" but \"options\" is not set"
                    14. "option %q is duplicated in options of %q input"
                    15. "default value %q of %q input is not included in its options %q"
                    16. "\"options\" can not be set to %q input because its input type is not \"choice\""
                    17. "type of %q input is \"number\" but its default value %q cannot be parsed as a float number: %s"
                    18. "type of %q input is \"boolean\". its default value %q must be \"true\" or \"false\""
                    19. "maximum number of inputs for \"workflow_dispatch\" event is 10 but %d inputs are provided. see https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#providing-inputs"
          """
          _type = "invalid Webhook event configuration"
     
     elif kind == 'deprecated-commands':
          """
          Type: deprecated command usage (kind: deprecated-commands)
          messages: 1. "workflow command %q was deprecated. use `%s` instead: https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions"
          """
          _type = "deprecated command usage"

     elif kind == 'action':
          """
          Type: invalid action usage (kind: action)
          messages: 1. "specifying action %q in invalid format because %s. available formats are \"{owner}/{repo}@{ref}\" or \"{owner}/{repo}/{path}@{ref}\""
                    2. "URI for Docker container %q is invalid: %s (tag=%s)"
                    3. "tag of Docker action should not be empty: %q"
                    4. "input %q is not defined in action %s. available inputs are %s"
                    5. "missing input %q which is required by action %s. all required inputs are %s"
          """
          _type = "invalid action usage"

     elif kind == 'runner-label' or kind == 'env-var' or kind == 'id':
          """
          Type: Unexpected/Invalid Identifiers
          message:
          (kind: id)           11. "step ID %q duplicates. previously defined at %s. step ID must be unique within a job. note that step ID is case insensitive"
          (kind: id)           12. "invalid %s ID %q. %s ID must start with a letter or _ and contain only alphanumeric characters, -, or _"
          (kind: runner-labl)  14. "label %q conflicts with label %q defined at %s. note: to run your job on each workers, use matrix"
          (kind: env-var)      15. "environment variable name %q is invalid. '&', '=' and spaces should not be contained"
          """
          _type = "unexpected/invalid identifier"
          
     elif kind == 'syntax-check':
          if related_Identifiers(message):
               _type = "unexpected/invalid identifier"
          elif related_mapping_values(message):
               _type = "unexpected mapping value"
          elif related_event(message):
               _type = "invalid Webhook event configuration"
          else:
               """
               Type: invalid credential usage
               messages: 
               (kind: syntax-check) 2. "both \"username\" and \"password\" must be specified in \"credentials\" section"
               """
               _type = "invalid credential usage"
     else:
          # kind == 'expression':
          _type = "invalid expression embedded with ${{ }} syntax"

     bug_info = {
          "type": _type,
          "message": message,
          "line_num": line_num
     }

     source.update_one({"_id": doc["_id"]}, {"$set": {"bug_info": bug_info}})
               
          
     
     
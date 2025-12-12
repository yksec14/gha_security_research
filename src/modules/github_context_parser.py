import re
from pathlib import Path

CONTEXT_SIGNATURE = "github.event."

def matrix_walk(node, path="", stop_at=set()):
    if path.startswith("matrix.include."):
        norm = path.replace("matrix.include.", "matrix.", 1)
    else:
        norm = path

    if norm in stop_at:
        yield norm, node

    if isinstance(node, dict):
        for k, v in node.items():
            new = f"{path}.{k}" if path else k
            yield from matrix_walk(v, new, stop_at)

    elif isinstance(node, list):
        for v in node:
            yield from matrix_walk(v, path, stop_at)


def analyze_matrix(matrix_text, job_data):
    matrix_pattern = re.compile(
        r'(?<![A-Za-z0-9_.])matrix\.[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*'
    )
    re_matrix = set(matrix_pattern.findall(matrix_text))

    matrix_list = []
    job_matrix_data = (job_data.get('strategy') or {})

    for p, v in matrix_walk(job_matrix_data, stop_at=re_matrix):
        matrix_list.append(
            {
                p : v 
            }
        )

    return matrix_list



def analyze_env(env_data, job_data):
    context_env =  {}
    if isinstance(env_data, dict):
        for env_key, env_value in env_data.items():
            if CONTEXT_SIGNATURE in str(env_value):
                context_env[env_key] = env_value 

        return context_env
    
    elif isinstance(env_data, str):
        if "matrix" not in env_data:
            if CONTEXT_SIGNATURE in env_data:
                print("string_env_data", env_data)
            return context_env

        else:
            matrix_env_list = analyze_matrix(env_data, job_data)
            for matrix_env in matrix_env_list:
                for matrix_key, matrix_data in matrix_env.items():
                    if isinstance(matrix_data, dict):
                        for key, value in matrix_data.items():
                            if CONTEXT_SIGNATURE in str(value):
                                context_env[key] = value

                    elif isinstance(matrix_data, list):
                        for matrix_data_item in matrix_data:
                            for matrix_data_item_key, matrix_data_item_value in matrix_data_item.items():
                                if CONTEXT_SIGNATURE in str(matrix_data_item_value):
                                    context_env[matrix_data_item_key] = matrix_data_item_value


                    else:
                        # print(env_data, type(matrix_data), matrix_data)
                        pass

        return context_env


def get_context_data(workflow_content):
    result = {
        "use_github_context": False,
        "job_result": {}
    }

    if CONTEXT_SIGNATURE in str(workflow_content):
        result["use_github_context"] = True
    else:
        result["use_github_context"] = False
        return result

  
    global_env = workflow_content.get("env", {}) or {}
    context_global_env = analyze_env(global_env, workflow_content) 
    result["context_global_env"] = context_global_env
    
    for job_name, job_data in (workflow_content.get("jobs") or {}).items():
        job_env = job_data.get("env", {}) or {}    
        context_job_env = analyze_env(job_env, job_data)    

        result["job_result"][job_name] = {
            "context_job_env": context_job_env,
            "step_result": {}
        }

        step_id = 0
        step_info = {}
        for step in job_data.get("steps", []) or []:
            step_id += 1

            step_env = step.get("env", {}) or {}
            context_step_env = analyze_env(step_env, job_data)
                
            step_info = {
                "type": "None",
                "label": [],
                "context_step_env": context_step_env,
                "used_env_key": []
            }

            run = step.get("run", None)
            if run != None:
                step_info["type"] = "run"

                if CONTEXT_SIGNATURE in str(run):
                    step_info["label"].append("injection_risk_basic")

                if "matrix." in str(run):
                    matrix_list = analyze_matrix(run, job_data)
                    if CONTEXT_SIGNATURE in str(matrix_list):
                        step_info["label"].append("injection_risk_matrix")

                for env_key, env_value in context_global_env.items() | context_job_env.items() | context_step_env.items():
                    if env_key in str(run):
                        step_info["label"].append("practice2")
                        step_info["used_env_key"].append(env_key)
                         
            uses = step.get("uses", None)
            if uses != None:
                step_info["type"] = "uses"
                step_info["action"] = uses

                uses_with = step.get("with", None)
                if uses_with != None:
                    step_info["with"] = True

                    if CONTEXT_SIGNATURE in str(uses_with):
                        step_info["label"].append("practice1_basic")

                    if "matrix." in str(uses_with):
                        matrix_list = analyze_matrix(str(uses_with), job_data)
                        if CONTEXT_SIGNATURE in str(matrix_list):
                            step_info["label"].append("practice1_matrix")

                    for env_key, env_value in context_global_env.items() | context_job_env.items() | context_step_env.items():
                        if env_key in str(uses_with):
                            step_info["label"].append("practice1_env")
                            step_info["used_env_key"].append(env_key)

                else:
                    step_info["with"] = False

            result["job_result"][job_name]["step_result"][str(step_id)] = step_info

    return result

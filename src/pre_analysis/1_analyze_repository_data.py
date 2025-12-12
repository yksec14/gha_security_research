
import os
import sys
import argparse
import json
from pathlib import Path
import yaml
import time
import tqdm
import pandas as pd
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

sys.path.append(str(Path(__file__).resolve().parent.parent))

import settings as st
from modules.github_context_parser import get_context_data

def get_actions_list(workflow_content):
    actions_list = []
    if "jobs" in workflow_content:
        for job_id, job in workflow_content["jobs"].items():
            if "steps" in job:
                for step in job["steps"]:
                    if "uses" in step:
                        action = step["uses"]
                        actions_list.append(action)

    return actions_list


def get_workflows_data(repo_dir):
    workflow_files = list(Path(os.path.join(repo_dir,".github/workflows")).rglob("*.y*ml"))
    
    workflows_data = {
        "workflows_num": len(workflow_files),
        "workflows":{}
    }

    for workflow_file in workflow_files:
        with open(workflow_file, "r") as f:
            try:
                workflow_content = yaml.safe_load(f)

                if workflow_content is None:
                    workflows_data["workflows"][workflow_file.name] = {
                        "is_valid": False,
                        "error": "Empty workflow file"
                    }
                    continue
                
                workflows_data["workflows"][workflow_file.name] = {
                    "is_valid": True,
                    "content": workflow_content,
                    "actions_list": get_actions_list(workflow_content),
                    "context_data": get_context_data(workflow_content),
                }

            except yaml.YAMLError as e:
                workflows_data["workflows"][workflow_file.name] = {
                    "is_valid": False,
                    "error": f"Error parsing YAML: {str(e)}"
                }

            except Exception as e:
                workflows_data["workflows"][workflow_file.name] = {
                    "is_valid": False,
                    "error": f"Unexpected error: {str(e)}"
                }

    return workflows_data



def process_month(year, month):
    output_path = os.path.join(st.REPOSITORY_DATA_DIR, f"repository_data_{year}_{month}.json")
    if st.ALLOW_OVERWRITE == False and os.path.exists(output_path) == True:
        print(f'Skip: {year}-{month}')
        return

    source_file1 = os.path.join(st.GHA_CHECK_DIR, f"gha_check_{year}_{month}.json")
    if os.path.exists(source_file1) == False:
        print(f"[Error] File not found: {source_file1}")
        return

    with open(source_file1, "r") as f:
        source_data1 = json.load(f)

    source_file2 = os.path.join(st.SEARTGHS_BY_MONTH_DIR, f"results_{year}_{month}.csv")
    if os.path.exists(source_file2) == False:
        print(f"[Error] File not found: {source_file2}")
        return
    
    with open(source_file2, "r") as f:
        source_data2 = pd.read_csv(f)


    results = {
        "SEARCH_DATE": f'{year}-{month}',
        "STARTED_AT": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
        "ENDED_AT": None,
        "SUCCESS": {},
        "ERROR": {}
    }

    count = 0
    for repository_name in tqdm.tqdm(source_data1["True"],desc=f"{year}-{month}"):
        count += 1
        if st.DEBUG == True and count > st.DEBUG_DATA_NUM:
            print("\nDebug Mode: Stop after limited data")
            break

        repo_dir = os.path.join(st.CLONED_DIR, repository_name)
        if not os.path.exists(repo_dir):
            # print(f"[Warning] Repository not found: {repository_name}")
            results["ERROR"][repository_name] = "Repository data not found"
            continue

        results["SUCCESS"][repository_name] = {}

        df_seartghs_repository = source_data2[source_data2["name"] == repository_name] 
        results["SUCCESS"][repository_name]["SEARTGHS_DATA"] = df_seartghs_repository.to_dict(orient="records")[0]

        results["SUCCESS"][repository_name]["WORKFLOWS_DATA"] = get_workflows_data(repo_dir)

        if st.LOOP_SLEEP_TIME > 0:
            time.sleep(st.LOOP_SLEEP_TIME)
    
    results["ENDED_AT"] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)



def generate_year_months(start, end):
    current = start
    while current <= end:
        yield current.year, current.month
        current += relativedelta(months=1)

def process_range(start_date, end_date):
    for year, month in generate_year_months(start_date, end_date):
        process_month(year, month)

def main():
    parser = argparse.ArgumentParser(
        description="Fetch workflow lists from GitHub for repositories by year-month range."
    )
    parser.add_argument(
        "--start", type=str, required=True, help="Start year-month in format YYYY-MM (e.g., 2025-01)"
    )
    parser.add_argument(
        "--end", type=str, required=True, help="End year-month in format YYYY-MM (e.g., 2025-10)"
    )
    args = parser.parse_args()

    start_date = datetime.strptime(args.start, "%Y-%m")
    end_date = datetime.strptime(args.end, "%Y-%m")

    process_range(start_date, end_date)


if __name__ == "__main__":
    main()
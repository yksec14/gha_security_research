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


def should_apply_practice(repo_dir, repository_data):
    return True

def is_practice_implemented(repo_dir, repository_data):
    use_scorecard = False
    for workflow_name, workflow_data in repository_data["WORKFLOWS_DATA"]["workflows"].items():
        if workflow_data["is_valid"] == True:
            actions_list = workflow_data["actions_list"]
            for actions in actions_list:
                actions_name = actions.split("@")[0]
                if "ossf/scorecard-action" == actions_name:
                    use_scorecard = True

    return use_scorecard


def analyze_practice(repo_dir, repository_data):
    is_target = should_apply_practice(repo_dir, repository_data)
    if is_target == True:
        is_implemented = is_practice_implemented(repo_dir, repository_data)
    else:
        is_implemented = None

    return {
        "is_target": is_target,
        "is_implemented": is_implemented
    }

def process_month(year, month):
    output_path = os.path.join(st.P3_ANALYZED_DATA_DIR, f"p3_analyzed_data_{year}_{month}.json")
    if st.ALLOW_OVERWRITE == False and os.path.exists(output_path):
        print(f"[Skip] File already exists: {output_path}")
        return
    

    source_file1 = os.path.join(st.GHA_CHECK_DIR, f"gha_check_{year}_{month}.json")
    if os.path.exists(source_file1) == False:
        print(f"[Error] File not found: {source_file1}")
        return

    with open(source_file1, "r") as f:
        source_data1 = json.load(f)


    source_file2 = os.path.join(st.REPOSITORY_DATA_DIR, f"repository_data_{year}_{month}.json")
    if os.path.exists(source_file2) == False:
        print(f"[Error] File not found: {source_file2}")
        return
    
    with open(source_file2, "r") as f:
        source_data2 = json.load(f)

    results = {
        "SEARCH_DATE": f'{year}-{month}',
        "SUCCESS": {},
        "ERROR": {}
    }

    count = 0
    for repository_name in tqdm.tqdm(source_data1["True"],desc=f"{year}-{month}"):
        repo_dir = os.path.join(st.CLONED_DIR, repository_name)
        if not os.path.exists(repo_dir):
            # print(f"[Warning] Repository not found: {repository_name}")
            results["ERROR"][repository_name] = "Repository data not found"
            continue

        repository_data = source_data2["SUCCESS"][repository_name]
        results["SUCCESS"][repository_name] = analyze_practice(repo_dir, repository_data)

        count += 1
        if st.DEBUG == True and count > st.DEBUG_DATA_NUM:
            print("\nDebug Mode: Stop after limited data")
            break


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
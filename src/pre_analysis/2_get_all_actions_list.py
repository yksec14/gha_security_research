
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


def get_actions_type_list(actions_list):
    actions_type_list = {
        "public": [],
        "local": [],
        "docker": []
    }

    for actions in actions_list:
        if actions.startswith("./"):
            actions_type_list["local"].append(actions)

        elif actions.startswith("docker://"):
            actions_type_list["docker"].append(actions)

        else:
            actions_type_list["public"].append(actions)


    return actions_type_list


def process_month(year, month):
    source_file = os.path.join(st.REPOSITORY_DATA_DIR, f"repository_data_{year}_{month}.json")
    if os.path.exists(source_file) == False:
        print(f"[Error] File not found: {source_file}")
        return

    with open(source_file, "r") as f:
        source_data = json.load(f)

    actions_list = []

    count = 0
    for repository_name, repository_data in tqdm.tqdm(source_data["SUCCESS"].items(),desc=f"{year}-{month}"):
        count += 1
        if st.DEBUG == True and count > st.DEBUG_DATA_NUM:
            print("\nDebug Mode: Stop after limited data")
            break
        
        for workflow_name, workflow_data in repository_data["WORKFLOWS_DATA"]["workflows"].items():
            if workflow_data["is_valid"] == False:
                continue

            actions_list.extend(workflow_data["actions_list"])

        if st.LOOP_SLEEP_TIME > 0:
            time.sleep(st.LOOP_SLEEP_TIME)

    return list(set(actions_list))



def generate_year_months(start, end):
    current = start
    while current <= end:
        yield current.year, current.month
        current += relativedelta(months=1)


def process_range(start_date, end_date):
    output_path = os.path.join(st.ACTIONS_DATA_DIR, "all_actions_list.json")
    if st.ALLOW_OVERWRITE == False and os.path.exists(output_path) == True:
        print('Skip: all_actions_list.json is already exists.')
        return


    actions_list = []
    for year, month in generate_year_months(start_date, end_date):
        actions_list.extend(process_month(year, month))


    actions_list = list(set(actions_list))
    actions_type_list = get_actions_type_list(actions_list)
    results = {
        "START_DATE": start_date.strftime("%Y-%m"),
        "END_DATE": end_date.strftime("%Y-%m"),
        "ACTIONS_LIST": actions_type_list
    }
    
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)

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
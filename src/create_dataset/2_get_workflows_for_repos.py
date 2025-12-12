import os
import sys
import argparse
import json
import pandas as pd
from pathlib import Path
import time
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

sys.path.append(str(Path(__file__).resolve().parent.parent))

import settings as st
from modules.github_api import get_access_token, get_rate_limit, call_workflows_api, call_get_repository_api

def get_repo_workflows(repository_name, access_token):
    is_success, result = call_workflows_api(repository_name, access_token)
    
    return is_success, result

def get_repository_data(repository_name, access_token):
    is_success, result = call_get_repository_api(repository_name, access_token)
    
    return is_success, result

def check_repository_active(row, access_token):
    is_active_repo = True
    
    
    ### check by SEART-GHS metadata
    if row["isFork"] == True or row["isArchived"] == True:
    ## if row["isFork"] == True or row["isArchived"] == True or row["isDisabled"] == True:
        ## print(f"Exclude: {repository_name}")
        is_active_repo = False

    ### check by GitHub API
    # is_success, result = get_repository_data(row["name"], access_token)
    # if is_success:
    #     result = result.json()
    #     if result["fork"] == True or result["archived"] == True:
    #     # if result["fork"] == True or result["archived"] == True or result["disabled"] == True:
    #         is_active_repo = False
    #     else:
    #         is_active_repo = True

    # else:
    #     is_active_repo = False

    return is_active_repo    


def process_month(year, month):
    output_path = os.path.join(st.REPO_WORKFLOWS_DIR, f'workflows_{year}_{month}.json')
    if st.ALLOW_OVERWRITE == False and os.path.exists(output_path) == True:
        print(f'Skip: {year}-{month}')
        return
    
    source_file = os.path.join(st.SEARTGHS_BY_MONTH_DIR, f"results_{year}_{month}.csv")
    if os.path.exists(source_file) == False:
        print(f"[Error] File not found: {source_file}")
        return

    df_seartghs = pd.read_csv(source_file)

    results = {
        "SEARCH_DATE": f'{year}-{month}',
        "STARTED_AT": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
        "ENDED_AT": None,
        "SUCCESS": {},
        "ERROR": {},
    }

    count = 0
    remaining = 5000
    data_num = df_seartghs.shape[0]
    access_token, expires_at = get_access_token()
    for _, row in df_seartghs.iterrows():
        is_active_repo = check_repository_active(row, access_token)
        if is_active_repo == False:
            continue
        
        count += 1
        if st.DEBUG == True and count > st.DEBUG_DATA_NUM:
            print("\nDebug Mode: Stop after limited data")
            break

        if count % 5000 == 0:
            access_token, expires_at = get_access_token()

        repository_name = row["name"]
        is_success, result = get_repo_workflows(repository_name, access_token)
        if is_success:
            results["SUCCESS"][repository_name] = result.json()
            limit_num, remaining, reset_time_utc = get_rate_limit(result)
        else:
            results["ERROR"][repository_name] = result

        if int(remaining) <= 100:
            sleep_seconds = (reset_time_utc - datetime.now(timezone.utc)).total_seconds() + 60
            print(f"[WARNING] API limit nearly reached. Sleeping for {int(sleep_seconds)} seconds until reset...")
            time.sleep(sleep_seconds)    

        sys.stdout.write(f"\r[{year}-{month}] Count: {count}/{data_num} RateLimit:{remaining}/{limit_num} ResetTime: {reset_time_utc.strftime('%Y-%m-%d %H:%M:%S')}")
        sys.stdout.flush()        

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

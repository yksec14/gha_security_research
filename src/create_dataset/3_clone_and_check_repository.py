import os
import sys
import argparse
import json
import subprocess
from pathlib import Path
import time
import tqdm
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

sys.path.append(str(Path(__file__).resolve().parent.parent))

import settings as st

def clone_repository(repository_name):
    owner, repo = repository_name.split("/")
    owner_dir = os.path.join(st.CLONED_DIR, owner)
    if not os.path.exists(owner_dir):
        os.makedirs(owner_dir)

    repo_dir = os.path.join(owner_dir, repo)
    if not os.path.exists(repo_dir):
        subprocess.run([
            "git", 
            "clone", 
            f"https://github.com/{repository_name}.git", 
            repo_dir
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
            )
        
    return repo_dir


def check_workflow_files(repo_dir):
    if not os.path.exists(repo_dir):
        print(f"[Error] Repository directory not found: {repo_dir}")
        return False

    workflow_files = list(Path(os.path.join(repo_dir,".github/workflows")).rglob("*.y*ml"))
    if workflow_files:
        return True
    else:
        # os.remove(repo_dir)
        return False

def process_month(year, month):
    output_path = os.path.join(st.GHA_CHECK_DIR, f"gha_check_{year}_{month}.json")
    if st.ALLOW_OVERWRITE == False and os.path.exists(output_path) == True:
        print(f'Skip: {year}-{month}')
        return

    source_file = os.path.join(st.REPO_WORKFLOWS_DIR, f"workflows_{year}_{month}.json")
    if os.path.exists(source_file) == False:
        print(f"[Error] File not found: {source_file}")
        return
    
    with open(source_file, "r") as f:
        source_data = json.load(f)

    results = {
        "SEARCH_DATE": f'{year}-{month}',
        "STARTED_AT": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
        "ENDED_AT": None,
        "True": [],
        "False": [],
    }

    count = 0
    for repository_name, workflows in tqdm.tqdm(source_data["SUCCESS"].items(),desc=f"{year}-{month}"):
        count += 1
        if st.DEBUG == True and count > st.DEBUG_DATA_NUM:
            print("\nDebug Mode: Stop after limited data")
            break

        if workflows["total_count"] >= 1:
            repo_dir = clone_repository(repository_name)
            has_workflow = check_workflow_files(repo_dir)

            results[str(has_workflow)].append(repository_name)

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
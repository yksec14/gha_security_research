import re
import os
import sys
import argparse
import json
from pathlib import Path
import requests
import yaml
import time
import tqdm
import pandas as pd
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

sys.path.append(str(Path(__file__).resolve().parent.parent))

import settings as st
from modules.github_api import get_access_token, get_rate_limit


with open(os.path.join(st.ACTIONS_DATA_DIR, "firstparty_users.json"), "r") as f:
    firstparty_users = json.load(f)["firstparty"]

def check_action_is_third_party(actions, repository_owner):
    if actions.startswith("./") or actions.startswith("docker://"):
        return False
    else:
        if actions.startswith("/"):
            actions_owner = actions.split("/")[1]
        else:
            actions_owner = actions.split("/")[0]

        if repository_owner != actions_owner and actions_owner not in firstparty_users:
            return True

    return False


def should_apply_practice(repo_dir, repository_data):
    use_third_party = False
    repository_owner = Path(repo_dir).parent.name
    
    for workflow_name, workflow_data in repository_data["WORKFLOWS_DATA"]["workflows"].items():
        if workflow_data["is_valid"] == True:
            actions_list = workflow_data["actions_list"]
            for actions in actions_list:
                if check_action_is_third_party(actions, repository_owner):
                    use_third_party = True

    return use_third_party



def check_short_sha1_commit(actions_repository_name, short_sha1):
    access_token, expires_at = get_access_token(st.config["1"])
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Mozilla/5.0 (compatible; GitHub Actions Third-Party Action Checker)" 
        }

        api_url = f"https://api.github.com/repos/{actions_repository_name}/commits/{short_sha1}"
        resonse = requests.get(api_url, headers=headers)
        if resonse.status_code == 200:
            return True
        elif resonse.status_code == 404:
            return False
        else:
            print(f"Error: {actions_repository_name} - {short_sha1} - {resonse.status_code}")
            return False
    except Exception as e:
        print(f"Exception: {actions_repository_name} - {short_sha1} - {str(e)}")
        return False

with open(os.path.join(st.ACTIONS_DATA_DIR, "public_actions_repository_data.json"), "r") as f:
    public_actions_repository_data = json.load(f)["DATA"]

def get_action_ref_type(actions):
    actions_name = actions.split("@")[0]
    ref_string = actions.split("@")[1]

    if actions_name.startswith("/"):
        repository_name = "/".join(actions_name.split("/")[1:3])
    else:
        repository_name = "/".join(actions_name.split("/")[0:2])

    repository_data = public_actions_repository_data[repository_name]
    if repository_data["tags"]["is_success"] == True:
        tag_list = [item["name"] for item in repository_data["tags"]["data"]]
    else:
        tag_list = []

    if repository_data["branches"]["is_success"] == True:
        branch_list = [item["name"] for item in repository_data["branches"]["data"]]
    else:
        branch_list = []


    SHA1_RE = re.compile(r'^[0-9a-f]{40}$', re.IGNORECASE)
    SHORT_SHA1_RE = re.compile(r'^[0-9a-f]{4,39}$', re.IGNORECASE)

    if SHA1_RE.fullmatch(ref_string):
        return "sha1"
    elif SHORT_SHA1_RE.fullmatch(ref_string):
        is_short_sha1 = check_short_sha1_commit(repository_name, ref_string)
        if is_short_sha1:
            return "short_sha1"
    elif ref_string in tag_list:
        return "tag"
    elif ref_string in branch_list and ref_string not in tag_list:
        return "branch"
    else:
        return "unknown_or_notfound"
    

with open(os.path.join(st.ACTIONS_DATA_DIR, "repository_marketplace_data.json"), "r") as f:
    repository_marketplace_data = json.load(f)["DATA"]


def check_action_is_verified(actions):
    actions_name = actions.split("@")[0]
    if actions_name.startswith("/"):
        repository_name = "/".join(actions_name.split("/")[1:3])
    else:
        repository_name = "/".join(actions_name.split("/")[0:2])

    if repository_marketplace_data[repository_name]["has_marketplace_url"] == True:
        is_verified = repository_marketplace_data[repository_name]["is_verified"]
        return is_verified
    else:
        return False

def analyze_pinning_pattern(actions):
    if "@" not in actions:
        ref_type = "default"
    else:
        ref_type =  get_action_ref_type(actions)

    if ref_type == "sha1":
        return True
    elif ref_type == "tag":
        if check_action_is_verified(actions) == True:
            return True
        else:
            return False
    else:
        return False

    

def is_practice_implemented(repo_dir, repository_data):
    repository_owner = Path(repo_dir).parent.name
    pinning_pattern = {}
    
    for workflow_name, workflow_data in repository_data["WORKFLOWS_DATA"]["workflows"].items():
        if workflow_data["is_valid"] == True:
            actions_list = workflow_data["actions_list"]
            for actions in actions_list:
                if check_action_is_third_party(actions, repository_owner):
                    result = analyze_pinning_pattern(actions)
                    pinning_pattern[actions] = result

    if False not in pinning_pattern.values() and len(pinning_pattern) > 0:
        return True
    else:
        return False


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
    output_path = os.path.join(st.P4_ANALYZED_DATA_DIR, f"p4_analyzed_data_{year}_{month}.json")
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
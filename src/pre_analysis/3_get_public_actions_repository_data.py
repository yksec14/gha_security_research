import os
import json
import sys
import time
import tqdm
from pathlib import Path
from datetime import datetime, timezone


sys.path.append(str(Path(__file__).resolve().parent.parent))

import settings as st
from modules.github_api import get_access_token, get_rate_limit, call_get_repository_tags_api, call_get_repository_branches_api


def get_pageinated_api_data(repository_name, api_caller):
    access_token, expires_at = get_access_token()
    page_id = 1
    data_list = []
    while True:
        is_success, result = api_caller(repository_name, access_token, page_id)
        if not is_success:
            return False, result

        data_list.extend(result.json())
        limit_num, remaining, reset_time_utc = get_rate_limit(result)
        if int(remaining) <= 100:
            sleep_seconds = (reset_time_utc - datetime.now(timezone.utc)).total_seconds() + 60
            print(f"[WARNING] API limit nearly reached. Sleeping for {int(sleep_seconds)} seconds until reset...")
            time.sleep(sleep_seconds)   

        if len(result.json()) < 100:
            return True, data_list
        
        page_id += 1

def get_repository_tags_list(repository_name):
    return get_pageinated_api_data(repository_name, call_get_repository_tags_api)

def get_repository_branches_list(repository_name):
    return get_pageinated_api_data(repository_name, call_get_repository_branches_api)



def main():
    output_path = os.path.join(st.ACTIONS_DATA_DIR, "public_actions_repository_data.json")
    if st.ALLOW_OVERWRITE == False and os.path.exists(output_path) == True:
        print('Skip: public_actions_repository_data.json is already exists.')
        return

    source_file = os.path.join(st.ACTIONS_DATA_DIR, "all_actions_list.json")
    if os.path.exists(source_file) == False:
        print(f"[Error] File not found: {source_file}")
        return
    
    with open(source_file, "r") as f:
        source_data = json.load(f)

    results = {
        "STARTED_AT": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
        "ENDED_AT": None,
        "DATA": {}
    }

    for actions in tqdm.tqdm(source_data["ACTIONS_LIST"]["public"]):
        if "@" in actions:
            actions_name = actions.split("@")[0]
        else:
            actions_name = actions

        if actions_name.startswith("/"):
            repository_name = "/".join(actions_name.split("/")[1:3])
        else:
            repository_name = "/".join(actions_name.split("/")[0:2])

        is_success_tags, result_tags = get_repository_tags_list(repository_name)
        # if is_success_tags == False:
        #     print(f"[Info] Failed to get tags for repository: {repository_name}")

        is_success_branches, result_branches = get_repository_branches_list(repository_name)
        # if is_success_branches == False:
        #     print(f"[Info] Failed to get branches for repository: {repository_name}")

        if repository_name in results["DATA"]:
            # print(f"Already processed: {repository_name}")
            continue

        results["DATA"][repository_name] = {
            "tags": {
                "is_success": is_success_tags,
                "data": result_tags
            },
            "branches": {
                "is_success": is_success_branches,
                "data": result_branches
            }
        }

        if st.LOOP_SLEEP_TIME > 0:
            time.sleep(st.LOOP_SLEEP_TIME)

    results["ENDED_AT"] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)


if __name__ == "__main__":
    main()
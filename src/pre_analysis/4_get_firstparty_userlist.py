import os
import json
import sys
import time
import tqdm
from bs4 import BeautifulSoup
import requests
from pathlib import Path
from datetime import datetime, timezone


sys.path.append(str(Path(__file__).resolve().parent.parent))

import settings as st


def get_html_page(owner_name):
    try:
        response = requests.get(f"https://github.com/{owner_name}")
        response.raise_for_status()

        return True, response.text

    except Exception as e:
        return False, str(e)


def controls_github_domain_from_file(owner_name):
    is_success, html_text = get_html_page(owner_name)
    if is_success == False:
        return False

    soup = BeautifulSoup(html_text, "html.parser")

    details_elements = soup.select('details[title="Label: Verified"], details.dropdown-signed-commit')
    for details in details_elements:
        text = details.get_text(separator=" ", strip=True)
        if "controls the domain" in text and "github.com" in text:
            return True

    return False


def main():
    output_path = os.path.join(st.ACTIONS_DATA_DIR, "firstparty_users.json")
    if st.ALLOW_OVERWRITE == False and os.path.exists(output_path) == True:
        print('Skip: firstparty_users.json is already exists.')
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
        "firstparty": [],
        "others": []
    }

    for actions in tqdm.tqdm(source_data["ACTIONS_LIST"]["public"]):
        if "@" in actions:
            actions_name = actions.split("@")[0]
        else:
            actions_name = actions

        if actions_name.startswith("/"):
            owner_name = actions_name.split("/")[1]
        else:
            owner_name = actions_name.split("/")[0]

        if owner_name in results["firstparty"] or owner_name in results["others"]:
            continue

        is_firstparty = controls_github_domain_from_file(owner_name)
        if is_firstparty == True:
            results["firstparty"].append(owner_name)
        else:
            results["others"].append(owner_name)

        if st.LOOP_SLEEP_TIME > 0:
            time.sleep(st.LOOP_SLEEP_TIME)

    results["ENDED_AT"] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)




    results["ENDED_AT"] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)


if __name__ == "__main__":
    main()
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

def get_marketplace_url(repository_name):
    repository_url = "https://github.com/" + repository_name
    try:
        response = requests.get(repository_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        button = soup.find("a", string="View on Marketplace")
        if button:
            link = button['href']
            marketplace_url = "https://github.com" + link
            return True, marketplace_url
        else:
            return False, "Not Found Marketplace URL"
    except Exception as e:
        return False, f"Error: {str(e)}"
    

def check_verified_badge(marketplace_url):
    try:
        response = requests.get(marketplace_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        verified_svg = soup.find("svg", {"aria-label": "Manually verified"})
        # verified_text = "Verified creator" in soup.text
        verified_text = "GitHub has manually verified the creator of the action as an official partner organization." in soup.text

        if verified_svg is not None and verified_text == True:
            return True, "Verified"
        
        # elif verified_svg is None and verified_text == True:
        #     print(marketplace_url, "Verified text found but no SVG")
        #     return False, "Verified by Text"
            
        # elif verified_svg is not None and verified_text == False:
        #     print(marketplace_url, "Verified SVG found but no text")
        #     return False, "Verified by SVG"

        else:
            return False, "Not Verified"

    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    output_path = os.path.join(st.ACTIONS_DATA_DIR, "repository_marketplace_data.json")
    if st.ALLOW_OVERWRITE == False and os.path.exists(output_path) == True:
        print('Skip: repository_marketplace_data.json is already exists.')
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

        if repository_name in results["DATA"]:
            continue
        
        has_marketplace_url, result = get_marketplace_url(repository_name)
        results["DATA"][repository_name] = {
                "has_marketplace_url": has_marketplace_url,
                "marketplace_url_or_error": result
            }
        
        if has_marketplace_url:
            marketplace_url = result
            is_verified, result = check_verified_badge(marketplace_url)
            results["DATA"][repository_name]["is_verified"] = is_verified
            results["DATA"][repository_name]["verified_status_or_error"] = result

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
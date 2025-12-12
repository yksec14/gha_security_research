import os
from pathlib import Path

### To enable debug mode, set DEBUG to True.
### When DEBUG is True, only a limited number of data entries (DEBUG_DATA_NUM) will be processed.
DEBUG = True
DEBUG_DATA_NUM = 50


### To allow overwriting existing files, set ALLOW_OVERWRITE to True.
### When set to False, existing files will be preserved and not overwritten.
ALLOW_OVERWRITE = True

### Options for controlling load and API request behavior.
LOOP_SLEEP_TIME = 0     ## Interval (seconds) between processing loops.
API_MAX_RETRIES = 3     ## Number of retry attempts for failed GitHub API requests.
API_RETRY_DELAY = 10    ## Waiting time (seconds) before retrying a failed request.


### If you use Personal Access Token, uncomment the following lines and set the value.
TOKEN_MODE="PERSONAL_ACCESS_TOKEN"
PERSONAL_ACCESS_TOKEN = "[GITHUB_PERSONAL_ACCESS_TOKEN]"

### If you use GitHub App, uncomment the following lines and set the values.
# TOKEN_MODE="GITHUB_APP_TOKEN"
# GITHUB_APP_CONFIG ={
#     "APP_ID": "[GITHUB_APP_ID]",
#     "INSTALLATION_ID": "[GITHUB_INSTALLATION_ID]",
#     "PRIVATE_KEY_PATH": "[GITHUB_APP_PRIVATE_KEY_PATH]",
# }


### Define directory paths (DO NOT MODIFY)
BASE_DIR = Path(__file__).resolve().parent.parent
SEARTGHS_FILEPATH = os.path.join(BASE_DIR,"data/raw/results.csv")
SEARTGHS_BY_MONTH_DIR = os.path.join(BASE_DIR, "data/dataset/seartghs_by_month")
REPO_WORKFLOWS_DIR = os.path.join(BASE_DIR, "data/dataset/repo_workflows")
GHA_CHECK_DIR = os.path.join(BASE_DIR, "data/dataset/gha_check")
CLONED_DIR = os.path.join(BASE_DIR, "data/dataset/cloned_repos")

REPOSITORY_DATA_DIR = os.path.join(BASE_DIR, "data/analyzed_data/repository_data")
ACTIONS_DATA_DIR = os.path.join(BASE_DIR, "data/analyzed_data/actions_data")
RESULTS_DIR = os.path.join(BASE_DIR, "data/analyzed_data/results")

P1_ANALYZED_DATA_DIR = os.path.join(BASE_DIR, "data/analyzed_data/practice1")
P2_ANALYZED_DATA_DIR = os.path.join(BASE_DIR, "data/analyzed_data/practice2")
P3_ANALYZED_DATA_DIR = os.path.join(BASE_DIR, "data/analyzed_data/practice3")
P4_ANALYZED_DATA_DIR = os.path.join(BASE_DIR, "data/analyzed_data/practice4")
P5_ANALYZED_DATA_DIR = os.path.join(BASE_DIR, "data/analyzed_data/practice5")
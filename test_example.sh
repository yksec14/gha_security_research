## This test_example is designed to run locally without any external network access.
## All required data are included in the `example_data` directory, so the script can be executed entirely offline.

echo "Running test with example data"

echo "Step 1: Copying example repositories to ./data/dataset/"
cp -r ./example_data/example_user ./data/dataset/cloned_repos

echo "Step 2: Copying example data for testing"
cp ./example_data/results_1000_1.csv ./data/dataset/seartghs_by_month/results_1000_1.csv
cp ./example_data/gha_check_1000_1.json ./data/dataset/gha_check/gha_check_1000_1.json
cp ./example_data/repository_data_1000_1.json ./data/analyzed_data/repository_data/repository_data_1000_1.json
cp ./example_data/all_actions_list.json ./data/analyzed_data/actions_data/all_actions_list.json
cp ./example_data/public_actions_repository_data.json ./data/analyzed_data/actions_data/public_actions_repository_data.json
cp ./example_data/firstparty_users.json ./data/analyzed_data/actions_data/firstparty_users.json
cp ./example_data/repository_marketplace_data.json ./data/analyzed_data/actions_data/repository_marketplace_data.json

## Pre-analysis data are already included in the `example-data` directory, so this step is skipped by default.
echo "[Skip] Step 3: Pre-analysis"

## If you want to re-run the pre-analysis, uncomment the following line.
## Note: This will access GitHub via the API and requires a valid Personal Access Token.
# echo "Step 3: Running pre-analysis..."
# ./pre_analysis.sh 1000-1 1000-1

echo "Step 4: Analyzing security practices (test mode)"
./analyze_security_practices.sh 1000-1 1000-1

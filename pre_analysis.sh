
echo "START: E2 - Pre analysis for analyzing security practices"
echo "  Start date: $1"
echo "  End date:   $2"

echo ""
echo "Step 1: Analyze repository data"
python src/pre_analysis/1_analyze_repository_data.py --start $1 --end $2

echo ""
echo "Step 2: Get all actions list"
python src/pre_analysis/2_get_all_actions_list.py --start $1 --end $2

echo ""
echo "Step 3: Get public actions repository data"
python src/pre_analysis/3_get_public_actions_repository_data.py

echo ""
echo "Step 4: Get first-party user list"
python src/pre_analysis/4_get_firstparty_userlist.py

echo ""
echo "Step 5: Get marketplace data"
python src/pre_analysis/5_get_marketplace_data.py

echo "FINISH: E2 - Pre analysis for analyzing security practices"

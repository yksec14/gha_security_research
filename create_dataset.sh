
echo "START: E1 - Create dataset"
echo "  Start date: $1"
echo "  End date:   $2"

echo ""
echo "Step 1: Split SEART-GHS datasetby month"
python src/create_dataset/1_split_seartghs_by_month.py --start $1 --end $2

echo ""
echo "Step 2: Get workflows for repositories"
python src/create_dataset/2_get_workflows_for_repos.py --start $1 --end $2

echo ""
echo "Step 3: Clone and check repositories"
python src/create_dataset/3_clone_and_check_repository.py --start $1 --end $2

echo ""
python src/create_dataset/show_result.py --start $1 --end $2

echo "FINISH: E1 - Create dataset"
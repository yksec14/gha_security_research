
import os
import sys
import argparse
import json
from pathlib import Path
import time
import tqdm
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

sys.path.append(str(Path(__file__).resolve().parent.parent))

import settings as st
from modules.github_context_parser import get_context_data

results = {
    "all_repositories": 0,
    "github_actions_used": 0,
}


def process_month(year, month):
    source_file1 = os.path.join(st.REPO_WORKFLOWS_DIR, f'workflows_{year}_{month}.json')
    if os.path.exists(source_file1) == False:
        print(f"[Error] File not found: {source_file1}")
        return

    with open(source_file1, "r") as f:
        source_data1 = json.load(f)


    source_file2 = os.path.join(st.GHA_CHECK_DIR, f"gha_check_{year}_{month}.json")
    if os.path.exists(source_file2) == False:
        print(f"[Error] File not found: {source_file2}")
        return

    with open(source_file2, "r") as f:
        source_data2 = json.load(f)

    results["all_repositories"] += len(source_data1["SUCCESS"])
    results["github_actions_used"] += len(source_data2["True"])


def show_results():
    print("=== GitHub Actions Usage Summary ===")
    print(f"Total Repositories: {results['all_repositories']}")
    print(f"Repositories Using GitHub Actions: {results['github_actions_used']}")
    if results['all_repositories'] > 0:
        usage_percentage = (results['github_actions_used'] / results['all_repositories']) * 100
    else:
        usage_percentage = 0
    print(f"GitHub Actions Usage Percentage: {usage_percentage:.2f}%")

def generate_year_months(start, end):
    current = start
    while current <= end:
        yield current.year, current.month
        current += relativedelta(months=1)

def process_range(start_date, end_date):
    for year, month in generate_year_months(start_date, end_date):
        process_month(year, month)

    show_results()

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
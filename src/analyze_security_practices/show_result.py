import os
import sys
import argparse
import json
from pathlib import Path
import yaml
import time
import tqdm
import pandas as pd
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from collections import defaultdict

sys.path.append(str(Path(__file__).resolve().parent.parent))

import settings as st

results = defaultdict(lambda: {"target_num": 0, "implemented_num": 0})
for i in range(1, 6):
    key = f"practice{i}"
    results[key]

def process_month(year, month):
    source_file = os.path.join(st.RESULTS_DIR, f"results_{year}_{month}.json")
    if os.path.exists(source_file) == False:
        print(f"[Error] File not found: {source_file}")
        return

    with open(source_file, "r") as f:
        source_data = json.load(f)
    
    # for repository_name, result in tqdm.tqdm(source_data.items(),desc=f"{year}-{month}"):
    for repository_name, result in source_data.items():
        for i in range(1, 6):
            key = f"practice{i}"
            practice_result = result.get(key, None)

            if practice_result is None:
                print(f"[Warning] No data for {repository_name} in {year}-{month} for {key}")

            if practice_result is not None:
                if practice_result["is_target"] == True:
                    results[key]["target_num"] += 1
                    if practice_result["is_implemented"] == True:
                        results[key]["implemented_num"] += 1

                if practice_result["is_target"] == False:
                    if practice_result["is_implemented"] == True:
                        print(f"[Warning] {repository_name} in {year}-{month} is not target but implemented for {key}")
                


def generate_year_months(start, end):
    current = start
    while current <= end:
        yield current.year, current.month
        current += relativedelta(months=1)


def show_results(results):
    print("=== Security Practice Implementation Results ===")
    for i in range(1, 6):
        key = f"practice{i}"
        target_num = results[key]["target_num"]
        implemented_num = results[key]["implemented_num"]
        implementation_rate = (implemented_num / target_num * 100) if target_num > 0 else 0.0
        print(f"{key}:")
        print(f"  Target Repositories: {target_num}")
        print(f"  Implemented Repositories: {implemented_num}")
        print(f"  Implementation Rate: {implementation_rate:.2f}%")
        print("")

def process_range(start_date, end_date):
    for year, month in generate_year_months(start_date, end_date):
        process_month(year, month)

    show_results(results)

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
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

sys.path.append(str(Path(__file__).resolve().parent.parent))

import settings as st



def process_month(year, month):
    results = {}
    output_path = os.path.join(st.RESULTS_DIR, f"results_{year}_{month}.json")
    if st.ALLOW_OVERWRITE == False and os.path.exists(output_path):
        print(f"[Skip] File already exists: {output_path}")
        return
    
    source_file = os.path.join(st.GHA_CHECK_DIR, f"gha_check_{year}_{month}.json")
    if os.path.exists(source_file) == False:
        print(f"[Error] File not found: {source_file}")
        return

    with open(source_file, "r") as f:
        source_data = json.load(f)
    
    p1_data_path = os.path.join(st.P1_ANALYZED_DATA_DIR, f"p1_analyzed_data_{year}_{month}.json")
    with open(p1_data_path, "r") as f:
        p1_data = json.load(f)["SUCCESS"]

    p2_data_path = os.path.join(st.P2_ANALYZED_DATA_DIR, f"p2_analyzed_data_{year}_{month}.json")
    with open(p2_data_path, "r") as f:
        p2_data = json.load(f)["SUCCESS"]

    p3_data_path = os.path.join(st.P3_ANALYZED_DATA_DIR, f"p3_analyzed_data_{year}_{month}.json")
    with open(p3_data_path, "r") as f:
        p3_data = json.load(f)["SUCCESS"]

    p4_data_path = os.path.join(st.P4_ANALYZED_DATA_DIR, f"p4_analyzed_data_{year}_{month}.json")
    with open(p4_data_path, "r") as f:
        p4_data = json.load(f)["SUCCESS"]

    p5_data_path = os.path.join(st.P5_ANALYZED_DATA_DIR, f"p5_analyzed_data_{year}_{month}.json")
    with open(p5_data_path, "r") as f:
        p5_data = json.load(f)["SUCCESS"]


    # for repository_name in tqdm.tqdm(source_data["True"],desc=f"{year}-{month}"):
    for repository_name in source_data["True"]:
        repo_result = {
            "practice1": p1_data.get(repository_name, None),
            "practice2": p2_data.get(repository_name, None),
            "practice3": p3_data.get(repository_name, None),
            "practice4": p4_data.get(repository_name, None),
            "practice5": p5_data.get(repository_name, None),
        }
        results[repository_name] = repo_result
        
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
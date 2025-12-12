import os
import sys
import pandas as pd
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import settings as st

def main():
    df = pd.read_csv(st.SEARTGHS_FILEPATH)

    df["createdAt"] = pd.to_datetime(df["createdAt"])

    df["year"] = df["createdAt"].dt.year
    df["month"] = df["createdAt"].dt.month

    for (year, month), group in df.groupby(["year", "month"]):
        output_path = os.path.join(st.SEARTGHS_BY_MONTH_DIR, f"results_{year}_{month}.csv")
        group.to_csv(output_path, index=False)


if __name__ == "__main__":
    main()
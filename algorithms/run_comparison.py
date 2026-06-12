import csv
import json
import os
import sys
from datetime import datetime, timezone

import pandas as pd


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from algorithms.a_star.runner import run as run_astar
from algorithms.simulated_annealing.runner import run as run_simulated_annealing
from algorithms.hill_climbing.runner import run as run_hill_climbing

DATASETS_DIR = os.path.join(PROJECT_ROOT, "datasets")
SPLIT_DIR = os.path.join(DATASETS_DIR, "splits")
RESULT_DIR = os.path.join(DATASETS_DIR, "results")
DASHBOARD_DIR = os.path.join(PROJECT_ROOT, "dashboard")

TRAIN_FILE = os.path.join(SPLIT_DIR, "bd_train.csv")
VAL_FILE = os.path.join(SPLIT_DIR, "bd_validation.csv")
TEST_FILE = os.path.join(SPLIT_DIR, "bd_test.csv")

RESULT_JSON = os.path.join(RESULT_DIR, "algorithm_comparison_results.json")
RESULT_CSV = os.path.join(RESULT_DIR, "algorithm_comparison_results.csv")
RESULT_JS = os.path.join(DASHBOARD_DIR, "algorithm_results.js")


def split_meta(df):
    timestamps = pd.to_datetime(df["timestamp"])
    return {
        "rows": len(df),
        "start": str(timestamps.min()),
        "end": str(timestamps.max()),
        "districts": sorted(df["district"].dropna().unique().tolist()) if "district" in df.columns else [],
    }


def evaluate_split(name, records):
    return [
        dict({"split": name}, **run_astar(records)),
        dict({"split": name}, **run_simulated_annealing(records)),
        dict({"split": name}, **run_hill_climbing(records)),
    ]


def main():
    os.makedirs(RESULT_DIR, exist_ok=True)

    train_df = pd.read_csv(TRAIN_FILE)
    val_df = pd.read_csv(VAL_FILE)
    test_df = pd.read_csv(TEST_FILE)

    train_records = train_df.to_dict(orient="records")
    val_records = val_df.to_dict(orient="records")
    test_records = test_df.to_dict(orient="records")

    all_results = []
    all_results.extend(evaluate_split("train", train_records))
    all_results.extend(evaluate_split("validation", val_records))
    all_results.extend(evaluate_split("test", test_records))

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "source_dataset": "bd_agrohome_hourly_90days.csv",
        "currency": "৳",
        "splits": {
            "train": split_meta(train_df),
            "validation": split_meta(val_df),
            "test": split_meta(test_df),
        },
        "results": all_results,
        "best_on_test": sorted(
            [r for r in all_results if r["split"] == "test"],
            key=lambda x: (x["objective_cost"], x["execution_time_ms"]),
        )[0],
    }

    with open(RESULT_JSON, "w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)

    with open(RESULT_CSV, "w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "split",
                "algorithm",
                "execution_time_ms",
                "objective_cost",
                "avg_hourly_cost",
                "avg_efficiency",
                "irrigation_on_hours",
                "unsafe_outdoor_hours",
                "convergence_iterations",
            ],
        )
        writer.writeheader()
        writer.writerows(all_results)

    with open(RESULT_JS, "w", encoding="utf-8") as fp:
        fp.write("window.AIRO_RESULTS = ")
        fp.write(json.dumps(payload, indent=2))
        fp.write(";\n")

    print("Algorithm comparison finished.")
    print(f"Results JSON: {RESULT_JSON}")
    print(f"Results CSV: {RESULT_CSV}")
    print(f"Dashboard JS: {RESULT_JS}")


if __name__ == "__main__":
    main()

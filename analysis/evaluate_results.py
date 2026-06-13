"""Compute aggregated evaluation metrics from algorithm comparison results.

Outputs:
 - datasets/results/algorithm_evaluation_summary.json
 - datasets/results/algorithm_evaluation_summary.csv
 - dashboard/algorithm_evaluation.js  (window.AIRO_EVAL)

Metrics computed per algorithm:
 - total_objective_cost (sum across splits)
 - avg_execution_time_ms
 - avg_convergence_iterations
 - avg_efficiency
 - avg_hourly_cost
 - avg_cost_reduction_percent (average percent reduction vs baseline per split)
 - overall_cost_reduction_percent (vs baseline total across all splits)

Baseline for each split is the sum of `hourly_cost_tk` in that split CSV.
"""
import json
import os
import csv
from collections import defaultdict

import pandas as pd


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(ROOT, "datasets", "results")
SPLIT_DIR = os.path.join(ROOT, "datasets", "splits")
DASHBOARD_DIR = os.path.join(ROOT, "dashboard")

RESULT_JSON = os.path.join(RESULTS_DIR, "algorithm_comparison_results.json")
OUT_JSON = os.path.join(RESULTS_DIR, "algorithm_evaluation_summary.json")
OUT_CSV = os.path.join(RESULTS_DIR, "algorithm_evaluation_summary.csv")
OUT_JS = os.path.join(DASHBOARD_DIR, "algorithm_evaluation.js")


def load_payload(path):
    with open(path, "r", encoding="utf-8") as fp:
        return json.load(fp)


def read_baseline_cost(split_name):
    filename = {
        "train": "bd_train.csv",
        "validation": "bd_validation.csv",
        "test": "bd_test.csv",
    }.get(split_name)
    if not filename:
        return 0.0
    path = os.path.join(SPLIT_DIR, filename)
    if not os.path.exists(path):
        return 0.0
    df = pd.read_csv(path)
    # Accept either hourly_cost_tk or hourly_cost column
    col = "hourly_cost_tk" if "hourly_cost_tk" in df.columns else ("hourly_cost" if "hourly_cost" in df.columns else None)
    if col is None:
        return 0.0
    return float(df[col].sum())


def compute_evaluation():
    payload = load_payload(RESULT_JSON)
    results = payload.get("results", [])

    # Gather baseline costs per split
    baseline = {}
    for s in ("train", "validation", "test"):
        baseline[s] = read_baseline_cost(s)

    # Aggregate metrics per algorithm
    alg_groups = defaultdict(list)
    per_split = defaultdict(lambda: defaultdict(dict))

    for r in results:
        alg = r.get("algorithm")
        split = r.get("split")
        alg_groups[alg].append(r)
        per_split[alg][split] = r

    summary = {}
    # total baseline across all splits (for overall reduction)
    total_baseline = sum(baseline.values())

    for alg, rows in alg_groups.items():
        total_obj = sum(r.get("objective_cost", 0.0) for r in rows)
        avg_time = sum(r.get("execution_time_ms", 0.0) for r in rows) / len(rows)
        avg_iters = sum(r.get("convergence_iterations", 0.0) for r in rows) / len(rows)
        avg_eff = sum(r.get("avg_efficiency", 0.0) for r in rows) / len(rows)
        avg_hourly = sum(r.get("avg_hourly_cost", 0.0) for r in rows) / len(rows)

        # compute per-split reduction percents, then average
        reduction_percents = []
        for s in ("train", "validation", "test"):
            r = per_split[alg].get(s)
            if not r:
                continue
            baseline_cost = baseline.get(s, 0.0)
            alg_cost = float(r.get("objective_cost", 0.0))
            if baseline_cost > 0:
                reduction = (baseline_cost - alg_cost) / baseline_cost * 100.0
            else:
                reduction = 0.0
            reduction_percents.append(reduction)

        avg_reduction = sum(reduction_percents) / len(reduction_percents) if reduction_percents else 0.0

        overall_reduction = ((total_baseline - total_obj) / total_baseline * 100.0) if total_baseline > 0 else 0.0

        summary[alg] = {
            "algorithm": alg,
            "total_objective_cost": round(total_obj, 2),
            "avg_execution_time_ms": round(avg_time, 2),
            "avg_convergence_iterations": round(avg_iters, 2),
            "avg_efficiency": round(avg_eff, 4),
            "avg_hourly_cost": round(avg_hourly, 4),
            "avg_cost_reduction_percent": round(avg_reduction, 3),
            "overall_cost_reduction_percent": round(overall_reduction, 3),
        }

    # Prepare CSV rows sorted by overall_reduction desc
    rows = sorted(summary.values(), key=lambda x: -x["overall_cost_reduction_percent"])

    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fp:
        json.dump({"generated_at": payload.get("generated_at"), "baseline": baseline, "summary": summary}, fp, indent=2)

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=[
            "algorithm",
            "total_objective_cost",
            "avg_execution_time_ms",
            "avg_convergence_iterations",
            "avg_efficiency",
            "avg_hourly_cost",
            "avg_cost_reduction_percent",
            "overall_cost_reduction_percent",
        ])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    # Export to dashboard JS for display
    eval_payload = {
        "generated_at": payload.get("generated_at"),
        "baseline": baseline,
        "summary": summary,
    }
    with open(OUT_JS, "w", encoding="utf-8") as fp:
        fp.write("window.AIRO_EVAL = ")
        fp.write(json.dumps(eval_payload, indent=2))
        fp.write(";\n")

    print("Evaluation complete:")
    print(" JSON:", OUT_JSON)
    print(" CSV:", OUT_CSV)
    print(" WEB JS:", OUT_JS)


if __name__ == "__main__":
    compute_evaluation()

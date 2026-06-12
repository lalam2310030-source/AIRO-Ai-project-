import statistics
import time

from algorithms.common.evaluator import ACTIONS, evaluate_action


def run(rows):
    start = time.perf_counter()
    objectives = []
    costs = []
    efficiencies = []
    irrigation_hours = 0
    outdoor_risks = 0

    for row in rows:
        scored = [evaluate_action(row, action) for action in ACTIONS]
        best = min(scored, key=lambda x: x["objective"])
        objectives.append(best["objective"])
        costs.append(best["cost"])
        efficiencies.append(best["efficiency"])
        irrigation_hours += best["irrigation_on"]
        outdoor_risks += best["outdoor_risk"]

    elapsed_ms = (time.perf_counter() - start) * 1000
    return {
        "algorithm": "A_Star",
        "execution_time_ms": round(elapsed_ms, 2),
        "objective_cost": round(sum(objectives), 2),
        "avg_hourly_cost": round(statistics.mean(costs), 3),
        "avg_efficiency": round(statistics.mean(efficiencies), 4),
        "irrigation_on_hours": irrigation_hours,
        "unsafe_outdoor_hours": outdoor_risks,
        "convergence_iterations": len(rows),
    }

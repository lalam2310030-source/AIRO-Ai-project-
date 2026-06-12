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
    total_iterations = 0

    for row in rows:
        current_idx = 0
        current = evaluate_action(row, ACTIONS[current_idx])

        improved = True
        while improved:
            improved = False
            neighbor_indices = [idx for idx in [current_idx - 1, current_idx + 1] if 0 <= idx < len(ACTIONS)]
            for idx in neighbor_indices:
                candidate = evaluate_action(row, ACTIONS[idx])
                total_iterations += 1
                if candidate["objective"] < current["objective"]:
                    current_idx = idx
                    current = candidate
                    improved = True
                    break

        objectives.append(current["objective"])
        costs.append(current["cost"])
        efficiencies.append(current["efficiency"])
        irrigation_hours += current["irrigation_on"]
        outdoor_risks += current["outdoor_risk"]

    elapsed_ms = (time.perf_counter() - start) * 1000
    return {
        "algorithm": "Hill_Climbing",
        "execution_time_ms": round(elapsed_ms, 2),
        "objective_cost": round(sum(objectives), 2),
        "avg_hourly_cost": round(statistics.mean(costs), 3),
        "avg_efficiency": round(statistics.mean(efficiencies), 4),
        "irrigation_on_hours": irrigation_hours,
        "unsafe_outdoor_hours": outdoor_risks,
        "convergence_iterations": total_iterations,
    }

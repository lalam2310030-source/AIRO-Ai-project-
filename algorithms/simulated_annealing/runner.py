import math
import random
import statistics
import time

from algorithms.common.evaluator import ACTIONS, evaluate_action


def run(rows, seed=42):
    rng = random.Random(seed)
    start = time.perf_counter()
    objectives = []
    costs = []
    efficiencies = []
    irrigation_hours = 0
    outdoor_risks = 0
    total_iterations = 0

    for row in rows:
        current_idx = rng.randrange(len(ACTIONS))
        current = evaluate_action(row, ACTIONS[current_idx])
        temperature = 1.0

        for _ in range(15):
            proposal_idx = rng.randrange(len(ACTIONS))
            proposal = evaluate_action(row, ACTIONS[proposal_idx])
            delta = proposal["objective"] - current["objective"]
            if delta < 0 or rng.random() < math.exp(-delta / max(0.01, temperature)):
                current_idx = proposal_idx
                current = proposal
            temperature *= 0.87
            total_iterations += 1

        objectives.append(current["objective"])
        costs.append(current["cost"])
        efficiencies.append(current["efficiency"])
        irrigation_hours += current["irrigation_on"]
        outdoor_risks += current["outdoor_risk"]

    elapsed_ms = (time.perf_counter() - start) * 1000
    return {
        "algorithm": "Simulated_Annealing",
        "execution_time_ms": round(elapsed_ms, 2),
        "objective_cost": round(sum(objectives), 2),
        "avg_hourly_cost": round(statistics.mean(costs), 3),
        "avg_efficiency": round(statistics.mean(efficiencies), 4),
        "irrigation_on_hours": irrigation_hours,
        "unsafe_outdoor_hours": outdoor_risks,
        "convergence_iterations": total_iterations,
    }

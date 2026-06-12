"""
Optimization Algorithms Module
==============================
Contains implementations of multiple optimization algorithms for farm recommendations:
- A* Search: Pathfinding algorithm for optimal solutions
- Hill Climbing: Local search optimization
- Simulated Annealing: Probabilistic metaheuristic for global optimization

All algorithms are used for comparing performance in farm optimization tasks.
"""

from . import a_star, hill_climbing, simulated_annealing

__all__ = ['a_star', 'hill_climbing', 'simulated_annealing']

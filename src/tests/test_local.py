import pytest
from tests.mock_env import MockEnvironment
from algorithms.local_search import SimpleHillClimbing, StochasticHillClimbing, LocalBeamSearch

def test_hill_climbing_local_maxima():
    # To force a local maxima, we create a situation where the heuristic
    # strictly increases unless we step completely backwards.
    # Actually, in SimpleHillClimbing, it looks at neighbors and picks the one with best heuristic.
    # If all neighbors have worse (higher) heuristic than current, it should stop.
    
    # We want a target at (4,0)
    # Start at (0,0)
    # The heuristic is Manhattan distance.
    # We place a U-shaped wall so that from (2,0), going right to (3,0) is blocked.
    # Going up to (2,1) increases heuristic distance from target (from 2 to 3)
    # Wait, Manhattan distance from (2,1) to (4,0) is |4-2| + |0-1| = 2 + 1 = 3.
    # Manhattan distance from (2,0) to (4,0) is |4-2| + 0 = 2.
    # So (2,1) is WORSE than (2,0).
    # Thus, SimpleHillClimbing should STOP at (2,0) because all valid neighbors
    # (1,0) and (2,1) have distance 3, which is worse than current 2.
    
    obstacles = {(3, 0), (3, -1), (3, 1)} # Wall at x=3
    env = MockEnvironment(5, 5, obstacles=obstacles)
    
    hc = SimpleHillClimbing()
    history = hc.run(env, (0, 0), (4, 0))
    path = history[-1].current_path
    
    # It correctly stops at local maxima (2, 0)
    assert path[-1] == (2, 0)

import pytest
from unittest.mock import MagicMock
from algorithms.adversarial import Minimax, AlphaBeta
from tests.mock_env import MockEnvironment

def test_alpha_beta_prunes_nodes():
    # 5x5 grid, no obstacles to maximize branching factor and allow pruning
    env = MockEnvironment(5, 5)
    
    # We will wrap get_neighbors to count how many times it's called
    original_get_neighbors = env.get_neighbors
    
    env.get_neighbors = MagicMock(side_effect=original_get_neighbors)
    minimax = Minimax()
    minimax.run_adversarial(env, (0, 0), (4, 4))
    minimax_calls = env.get_neighbors.call_count
    
    env.get_neighbors = MagicMock(side_effect=original_get_neighbors)
    alphabeta = AlphaBeta()
    alphabeta.run_adversarial(env, (0, 0), (4, 4))
    alphabeta_calls = env.get_neighbors.call_count
    
    # Alpha-Beta should explore fewer nodes than Minimax
    assert alphabeta_calls < minimax_calls

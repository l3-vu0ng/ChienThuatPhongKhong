# tests/test_mock_env.py
import pytest
from tests.mock_env import MockEnvironment

def test_mock_env_neighbors():
    env = MockEnvironment(5, 5, obstacles={(1, 1)})
    neighbors = env.get_neighbors(0, 1)
    assert (1, 1) not in neighbors
    assert (0, 0) in neighbors
    assert (0, 2) in neighbors

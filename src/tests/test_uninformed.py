import pytest
from tests.mock_env import MockEnvironment
from algorithms.uninformed import DFS, BFS

def test_dfs_no_infinite_loop():
    env = MockEnvironment(3, 3)
    dfs = DFS()
    history = dfs.run(env, (0, 0), (2, 2))
    assert history[-1].current_path[-1] == (2, 2)

def test_bfs_shortest_path():
    env = MockEnvironment(5, 5, obstacles={(1, 0), (1, 1), (1, 2)})
    bfs = BFS()
    history = bfs.run(env, (0, 0), (2, 0))
    path = history[-1].current_path
    assert len(path) == 9

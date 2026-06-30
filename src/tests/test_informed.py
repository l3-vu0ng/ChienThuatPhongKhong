import pytest
from tests.mock_env import MockEnvironment
from algorithms.informed import AStar, GreedySearch

def test_astar_optimality():
    costs = {(1, 0): 10, (2, 0): 10, (3, 0): 10}
    env = MockEnvironment(5, 5, costs=costs)
    astar = AStar()
    history = astar.run(env, (0, 0), (4, 0))
    path = history[-1].current_path
    
    # Path around: (0,0)->(0,1)->(1,1)->(2,1)->(3,1)->(4,1)->(4,0) = length 7
    # Path straight: (0,0)->(1,0)->(2,0)->(3,0)->(4,0) = length 5 (but cost 30+)
    # To fail first, we asserted it goes straight. Now we assert it goes around.
    assert (1, 0) not in path

def test_greedy_u_shape():
    # Create an obstacle wall that forces a detour.
    # Start: (0, 0), Target: (4, 0)
    # Wall at x=2, from y=0 to y=3
    obstacles = {(2, 0), (2, 1), (2, 2), (2, 3)}
    env = MockEnvironment(5, 5, obstacles=obstacles)
    
    # Greedy will go towards target and hit the wall: (0,0)->(1,0)
    # Then it has to go up along the wall to go around it.
    greedy = GreedySearch()
    g_history = greedy.run(env, (0, 0), (4, 0))
    g_path = g_history[-1].current_path
    
    astar = AStar()
    a_history = astar.run(env, (0, 0), (4, 0))
    a_path = a_history[-1].current_path
    
    # Verify both found the target
    assert g_path[-1] == (4, 0)
    assert a_path[-1] == (4, 0)
    
    # A* path is guaranteed optimal.
    # Greedy might find a sub-optimal path (e.g. going up then down instead of directly optimal)
    # Actually, in this simple case Greedy and A* might both find path of same length 
    # but Greedy explores differently. Let's just assert length of A* path.
    assert len(a_path) <= len(g_path)

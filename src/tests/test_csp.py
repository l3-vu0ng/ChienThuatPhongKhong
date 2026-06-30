from algorithms.csp import BacktrackingCSP, ForwardCheckingCSP
from tests.mock_env import MockEnvironment

def test_forward_checking_prunes_early():
    # 2 SAMs, 2 B52s
    # Grid 5x5
    # Wall at x=2, y=0 to y=4 except y=2
    # Both SAMs must pass through (2, 2) to reach B52s.
    # Paths will intersect, so NO solution exists.
    
    env = MockEnvironment(5, 5, obstacles={(2, 0), (2, 1), (2, 3), (2, 4)})
    sam_list = [(0, 1), (0, 3)]
    b52_list = [(4, 1), (4, 3)]
    
    bt = BacktrackingCSP()
    bt_history = bt.run_csp(env, sam_list, b52_list)
    
    fc = ForwardCheckingCSP()
    fc_history = fc.run_csp(env, sam_list, b52_list)
    
    # Forward Checking should prune earlier and have fewer states in history
    assert len(fc_history) < len(bt_history)

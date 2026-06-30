# tests/mock_env.py
class MockEnvironment:
    def __init__(self, width, height, obstacles=None, costs=None):
        self.width = width
        self.height = height
        self.obstacles = obstacles or set()
        self.costs = costs or {}

    def get_neighbors(self, x, y):
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if (nx, ny) not in self.obstacles:
                    neighbors.append((nx, ny))
        return neighbors

    def get_cost(self, x, y):
        return self.costs.get((x, y), 1)

# algorithms/informed.py
import heapq
from algorithms.base_algorithm import BaseAlgorithm, State

def heuristic(a, b):
    """
    Hàm lượng giá heuristic sử dụng khoảng cách Manhattan.
    Khoảng cách này đặc biệt phù hợp và tối ưu admissible trên lưới dạng ô vuông (chỉ di chuyển ngang/dọc)
    để định hướng thuật toán tìm kiếm về phía mục tiêu.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

class GreedySearch(BaseAlgorithm):
    """
    Thuật toán Tìm kiếm Tham lam (Greedy Best-First Search).
    Thuật toán này chỉ xem xét chi phí ước tính h(n) từ nút hiện tại đến đích để quyết định nút tiếp theo.
    Nó thường giải quyết mục tiêu rất nhanh nhưng không đảm bảo đường đi tìm được là ngắn nhất.
    """
    def run(self, environment, start, target):
        history = []
        
        # Hàng đợi ưu tiên (Priority Queue) sẽ luôn bật ra phần tử có giá trị h(n) thấp nhất trước tiên.
        pq = [(heuristic(start, target), [start])]
        explored = set([start])
        
        while pq:
            h_cost, path = heapq.heappop(pq)
            node = path[-1]
            
            history.append(State(
                frontier=[p[-1] for _, p in pq],
                explored=explored.copy(),
                current_path=path,
                hud_metrics={
                    "Current Algorithm": "Greedy Search",
                    "h(n)": f"{h_cost:.1f}",
                    "Nodes Explored": str(len(explored))
                },
                action_description=f"Duyệt tọa độ {node} với h(n) = {h_cost:.1f}."
            ))
            
            if node == target:
                history.append(State(
                    frontier=[],
                    explored=explored.copy(),
                    current_path=path,
                    hud_metrics={
                        "Current Algorithm": "Greedy Search",
                        "h(n)": "0.0",
                        "Nodes Explored": str(len(explored))
                    },
                    action_description=f"Đã tìm thấy B-52 tại {target}!"
                ))
                break
                
            for neighbor in environment.get_neighbors(node[0], node[1]):
                if neighbor not in explored:
                    explored.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    heapq.heappush(pq, (heuristic(neighbor, target), new_path))
                    
        return history

class AStar(BaseAlgorithm):
    """
    Thuật toán A* (A-Star Search).
    Sử dụng kết hợp chi phí thực tế đã đi qua g(n) và chi phí ước tính đến đích h(n) thành hàm f(n) = g(n) + h(n).
    A* luôn tìm ra đường đi tối ưu nhất nếu hàm heuristic thỏa mãn điều kiện admissible (không đánh giá quá cao).
    """
    def run(self, environment, start, target):
        history = []
        
        # Priority queue so sánh theo thứ tự: f_cost trước, nếu bằng nhau thì g_cost hoặc tuple dữ liệu.
        pq = [(heuristic(start, target), 0, [start])]
        
        # Bảng tra g_costs nhằm lưu lại con đường rẻ nhất để đi đến một nút, 
        # giúp nhanh chóng cắt tỉa những nhánh có g(n) lớn hơn.
        g_costs = {start: 0}
        explored = set()
        
        while pq:
            f_cost, g_cost, path = heapq.heappop(pq)
            node = path[-1]
            
            if node in explored and g_cost > g_costs.get(node, float('inf')):
                continue
                
            explored.add(node)
            h_cost = f_cost - g_cost
            
            history.append(State(
                frontier=[p[-1] for _, _, p in pq],
                explored=explored.copy(),
                current_path=path,
                hud_metrics={
                    "Current Algorithm": "A* Search",
                    "f(n)": f"{f_cost:.1f}",
                    "g(n)": f"{g_cost}",
                    "h(n)": f"{h_cost:.1f}",
                    "Nodes Explored": str(len(explored))
                },
                action_description=f"Duyệt {node} với f(n) = {f_cost:.1f}."
            ))
            
            if node == target:
                history.append(State(
                    frontier=[],
                    explored=explored.copy(),
                    current_path=path,
                    hud_metrics={
                        "Current Algorithm": "A* Search",
                        "f(n)": f"{f_cost:.1f}",
                        "Nodes Explored": str(len(explored))
                    },
                    action_description=f"Đã tìm thấy B-52 tại {target} bằng đường đi tối ưu nhất!"
                ))
                break
                
            for neighbor in environment.get_neighbors(node[0], node[1]):
                new_g_cost = g_cost + environment.get_cost(neighbor[0], neighbor[1])
                
                if new_g_cost < g_costs.get(neighbor, float('inf')):
                    g_costs[neighbor] = new_g_cost
                    new_f_cost = new_g_cost + heuristic(neighbor, target)
                    new_path = list(path)
                    new_path.append(neighbor)
                    heapq.heappush(pq, (new_f_cost, new_g_cost, new_path))
                    
        return history

class IDAStar(BaseAlgorithm):
    """
    Thuật toán IDA* (Iterative Deepening A*).
    Kết hợp cơ chế lặp độ sâu của IDS với sự định hướng ưu việt của A*. 
    Bảo toàn tính tối ưu của A* trong khi giải quyết triệt để bài toán rò rỉ bộ nhớ (memory overhead).
    """
    def run(self, environment, start, target):
        history = []
        
        # Ngưỡng ban đầu (threshold) chính là khoảng cách lý thuyết h(n) từ nút bắt đầu tới đích.
        threshold = heuristic(start, target)
        explored_total = set() 
        
        while True:
            stack = [([start], 0)] 
            
            # Biến lưu trữ ngưỡng nhỏ nhất vượt qua threshold ở vòng lặp hiện tại,
            # làm cơ sở cho ngưỡng (threshold) của vòng lặp tiếp theo.
            min_exceeded_f = float('inf')
            found = False
            visited_g = {} 
            
            while stack:
                path, g_cost = stack.pop()
                node = path[-1]
                
                f_cost = g_cost + heuristic(node, target)
                
                # Cắt tỉa nhánh: nếu hàm ước tính vượt quá giới hạn đang quét, bỏ qua và lưu ngưỡng lại.
                if f_cost > threshold:
                    min_exceeded_f = min(min_exceeded_f, f_cost)
                    continue
                
                # Loại bỏ việc duyệt trùng lặp nếu đi đến cùng một nút với chi phí cao hơn hoặc bằng.
                if node in visited_g and visited_g[node] <= g_cost:
                    continue
                visited_g[node] = g_cost
                
                explored_total.add(node)
                
                history.append(State(
                    frontier=[p[-1] for p, _ in stack],
                    explored=explored_total.copy(),
                    current_path=path,
                    hud_metrics={
                        "Current Algorithm": "IDA* Search",
                        "Threshold f(n)": f"{threshold:.1f}",
                        "Current f(n)": f"{f_cost:.1f}",
                        "Nodes Explored": str(len(explored_total))
                    },
                    action_description=f"IDA* duyệt {node} (f={f_cost:.1f}, Ngưỡng={threshold:.1f})."
                ))
                    
                if node == target:
                    history.append(State(
                        frontier=[],
                        explored=explored_total.copy(),
                        current_path=path,
                        hud_metrics={
                            "Current Algorithm": "IDA* Search",
                            "Threshold f(n)": f"{threshold:.1f}",
                            "Nodes Explored": str(len(explored_total))
                        },
                        action_description=f"Đã tìm thấy B-52 tại {target} ở vòng ngưỡng f(n)={threshold:.1f}!"
                    ))
                    found = True
                    break
                    
                for neighbor in environment.get_neighbors(node[0], node[1]):
                    if neighbor not in path:
                        new_path = list(path)
                        new_path.append(neighbor)
                        neighbor_cost = environment.get_cost(neighbor[0], neighbor[1])
                        stack.append((new_path, g_cost + neighbor_cost))
                        
            if found:
                break
                
            if min_exceeded_f == float('inf'):
                break
                
            threshold = min_exceeded_f
            
        return history

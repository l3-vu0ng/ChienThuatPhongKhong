# algorithms/uninformed.py
from collections import deque
from algorithms.base_algorithm import BaseAlgorithm, State

class BFS(BaseAlgorithm):
    """
    Thuật toán Tìm kiếm theo chiều rộng (Breadth-First Search).
    Duyệt qua không gian trạng thái theo từng cấp độ sâu, đảm bảo tìm được đường đi ngắn nhất 
    (tối ưu số bước di chuyển) nếu đồ thị không có trọng số.
    """
    def run(self, environment, start, target):
        history = []
        
        # Hàng đợi (Queue) quản lý thứ tự FIFO (First In First Out) để quét các nút theo từng tầng.
        queue = deque([[start]])
        
        # Tập hợp quản lý các nút đã thăm để chống việc duyệt lại, tránh vòng lặp vô hạn.
        explored = set([start])
        
        while queue:
            path = queue.popleft()
            node = path[-1]
            
            # Khởi tạo bản ghi State dùng để cung cấp dữ liệu theo thời gian thực cho hệ thống vẽ UI.
            history.append(State(
                frontier=[p[-1] for p in queue],
                explored=explored.copy(),
                current_path=path,
                hud_metrics={"Current Algorithm": "BFS", "Nodes Explored": str(len(explored))},
                action_description=f"Duyệt tọa độ {node}, mở rộng các node kề vào Frontier."
            ))
            
            if node == target:
                history.append(State(
                    frontier=[],
                    explored=explored.copy(),
                    current_path=path,
                    hud_metrics={"Current Algorithm": "BFS", "Nodes Explored": str(len(explored))},
                    action_description=f"Đã tìm thấy B-52 tại {target}!"
                ))
                break
                
            for neighbor in environment.get_neighbors(node[0], node[1]):
                if neighbor not in explored:
                    explored.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)
                    
        return history

class DFS(BaseAlgorithm):
    """
    Thuật toán Tìm kiếm theo chiều sâu (Depth-First Search).
    Mở rộng nút đi sâu nhất có thể dọc theo mỗi nhánh trước khi quay lui. 
    Không đảm bảo tìm được đường đi ngắn nhất và có thể tiêu tốn bộ nhớ lớn ở cây tìm kiếm sâu.
    """
    def run(self, environment, start, target):
        history = []
        
        # Ngăn xếp (Stack) quản lý thứ tự LIFO (Last In First Out) phục vụ việc đi sâu xuống nhánh.
        stack = [[start]]
        explored = set()
        
        while stack:
            path = stack.pop()
            node = path[-1]
            
            # Nếu node này đã từng được duyệt (từ một nhánh khác rẽ qua), bỏ qua luôn để tránh vòng lặp
            if node in explored:
                continue
                
            explored.add(node)
                
            history.append(State(
                frontier=[p[-1] for p in stack],
                explored=explored.copy(),
                current_path=path,
                hud_metrics={"Current Algorithm": "DFS", "Nodes Explored": str(len(explored))},
                action_description=f"Quét sâu (DFS) tới tọa độ {node}."
            ))
            
            if node == target:
                history.append(State(
                    frontier=[],
                    explored=explored.copy(),
                    current_path=path,
                    hud_metrics={"Current Algorithm": "DFS", "Nodes Explored": str(len(explored))},
                    action_description=f"Đã tìm thấy B-52 tại {target}!"
                ))
                break
                
            for neighbor in environment.get_neighbors(node[0], node[1]):
                if neighbor not in explored:
                    new_path = list(path)
                    new_path.append(neighbor)
                    stack.append(new_path)
                    
        return history

class IDS(BaseAlgorithm):
    """
    Thuật toán Tìm kiếm sâu dần (Iterative Deepening Search).
    Kết hợp ưu điểm giới hạn bộ nhớ của DFS với khả năng tìm đường đi tối ưu (nếu bước giá đều) của BFS.
    Thực hiện lặp lại DFS với giới hạn độ sâu tăng dần.
    """
    def run(self, environment, start, target):
        history = []
        
        # Đặt giới hạn tối đa bằng diện tích lưới để giới hạn việc tìm kiếm vô tận.
        max_depth = environment.width * environment.height 
        total_explored_count = 0
        
        for limit in range(max_depth):
            stack = [([start], 0)]
            explored = set() 
            
            # Bảng băm dùng để cắt tỉa nhánh: chặn việc tiếp tục tìm kiếm nếu nút này đã được tìm thấy
            # ở một độ sâu nhỏ hơn hoặc bằng trong cùng mức limit.
            visited_depth = {} 
            
            found = False
            
            while stack:
                path, depth = stack.pop()
                node = path[-1]
                
                if node in visited_depth and visited_depth[node] <= depth:
                    continue
                visited_depth[node] = depth
                
                explored.add(node)
                total_explored_count += 1
                
                history.append(State(
                    frontier=[p[-1] for p, d in stack],
                    explored=explored.copy(),
                    current_path=path,
                    hud_metrics={
                        "Current Algorithm": "IDS", 
                        "Depth Limit": str(limit),
                        "Nodes Explored": str(total_explored_count)
                    },
                    action_description=f"IDS duyệt tọa độ {node} ở độ sâu {depth} (Limit: {limit})."
                ))
                
                if node == target:
                    history.append(State(
                        frontier=[],
                        explored=explored.copy(),
                        current_path=path,
                        hud_metrics={
                            "Current Algorithm": "IDS", 
                            "Depth Limit": str(limit),
                            "Nodes Explored": str(total_explored_count)
                        },
                        action_description=f"Đã tìm thấy B-52 tại {target} ở vòng quét {limit}!"
                    ))
                    found = True
                    break
                    
                if depth < limit:
                    for neighbor in environment.get_neighbors(node[0], node[1]):
                        # Chặn quay đầu ngay lập tức về nút vừa đi qua trên nhánh hiện tại.
                        if neighbor not in path: 
                            new_path = list(path)
                            new_path.append(neighbor)
                            stack.append((new_path, depth + 1))
                            
            if found:
                break
                
        return history

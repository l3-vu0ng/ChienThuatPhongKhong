# algorithms/local_search.py
import random
from algorithms.base_algorithm import BaseAlgorithm, State

def heuristic(a, b):
    """
    Hàm lượng giá heuristic sử dụng khoảng cách Manhattan.
    Khoảng cách này đặc biệt phù hợp và tối ưu admissible trên lưới dạng ô vuông (chỉ di chuyển ngang/dọc)
    để định hướng thuật toán tìm kiếm về phía mục tiêu.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

class SimpleHillClimbing(BaseAlgorithm):
    """
    Thuật toán Leo đồi Cơ bản (Simple Hill Climbing).
    Thuật toán tìm kiếm cục bộ (local search) luôn chọn trạng thái láng giềng có giá trị đánh giá tốt nhất.
    Nó giống như việc leo núi trong sương mù: luôn bước lên hướng dốc nhất nhưng dễ bị mắc kẹt tại cực đại địa phương (local maxima)
    nếu gặp vật cản dạng lõm (như hình chữ U) che khuất đích đến.
    """
    def run(self, environment, start, target):
        history = []
        current_node = start
        current_path = [start]
        explored = set([start])
        
        while True:
            current_eval = heuristic(current_node, target)
            
            # Thuật toán cục bộ không duy trì hàng đợi chứa các nút chờ duyệt (frontier rỗng).
            history.append(State(
                frontier=[], 
                explored=explored.copy(),
                current_path=list(current_path),
                hud_metrics={
                    "Current Algorithm": "Simple Hill Climbing",
                    "f(n) eval": f"{current_eval:.1f}",
                },
                action_description=f"Đang đứng tại {current_node} với eval = {current_eval:.1f}."
            ))
            
            if current_node == target:
                history.append(State(
                    frontier=[],
                    explored=explored.copy(),
                    current_path=list(current_path),
                    hud_metrics={
                        "Current Algorithm": "Simple Hill Climbing",
                        "f(n) eval": "0.0",
                    },
                    action_description=f"Đã bắt kịp B-52 tại {target}!"
                ))
                break
                
            neighbors = environment.get_neighbors(current_node[0], current_node[1])
            best_neighbor = None
            
            # Trong bài toán tìm đường, ta đang cố cực tiểu hóa khoảng cách đến đích, 
            # nên "tốt nhất" nghĩa là "nhỏ nhất" (Gradient Descent).
            best_eval = current_eval 
            
            for neighbor in neighbors:
                if neighbor in explored:
                    continue
                    
                # Hàm đánh giá cục bộ kết hợp chi phí di chuyển (tránh bão, núi) và khoảng cách tới mục tiêu.
                e = environment.get_cost(neighbor[0], neighbor[1]) + heuristic(neighbor, target)
                if e <= best_eval:
                    best_eval = e
                    best_neighbor = neighbor
                    
            if best_neighbor is None:
                # Trạng thái bế tắc: Mọi nút xung quanh đều có giá trị đánh giá kém hơn nút hiện tại.
                history.append(State(
                    frontier=[],
                    explored=explored.copy(),
                    current_path=list(current_path),
                    hud_metrics={
                        "Current Algorithm": "Simple Hill Climbing",
                        "Status": "Stuck (Local Maxima)"
                    },
                    action_description=f"Sợ bão! Bị kẹt tại Cực trị địa phương {current_node}!"
                ))
                break
                
            current_node = best_neighbor
            current_path.append(current_node)
            explored.add(current_node)
            
        return history

class StochasticHillClimbing(BaseAlgorithm):
    """
    Thuật toán Leo đồi Ngẫu nhiên (Stochastic Hill Climbing).
    Phiên bản nâng cấp của Hill Climbing, thay vì luôn chọn hướng dốc nhất, thuật toán sẽ chọn ngẫu nhiên
    một hướng trong số các hướng đi tốt hơn vị trí hiện tại. 
    Điều này giúp thuật toán có khả năng (dù nhỏ) thoát khỏi các cực đại địa phương thoai thoải,
    nhưng đổi lại tốc độ hội tụ về đích sẽ biến động và không tối ưu.
    """
    def run(self, environment, start, target):
        history = []
        current_node = start
        current_path = [start]
        explored = set([start])
        
        while True:
            current_eval = heuristic(current_node, target)
            
            history.append(State(
                frontier=[],
                explored=explored.copy(),
                current_path=list(current_path),
                hud_metrics={
                    "Current Algorithm": "Stochastic Hill Climbing",
                    "f(n) eval": f"{current_eval:.1f}",
                },
                action_description=f"Đang đứng tại {current_node} với eval = {current_eval:.1f}."
            ))
            
            if current_node == target:
                history.append(State(
                    frontier=[],
                    explored=explored.copy(),
                    current_path=list(current_path),
                    hud_metrics={
                        "Current Algorithm": "Stochastic Hill Climbing",
                        "f(n) eval": "0.0",
                    },
                    action_description=f"Đã bắt kịp B-52 tại {target}!"
                ))
                break
                
            neighbors = environment.get_neighbors(current_node[0], current_node[1])
            better_neighbors = []
            
            for neighbor in neighbors:
                if neighbor in explored:
                    continue
                e = environment.get_cost(neighbor[0], neighbor[1]) + heuristic(neighbor, target)
                if e <= current_eval:
                    better_neighbors.append(neighbor)
                    
            if not better_neighbors:
                history.append(State(
                    frontier=[],
                    explored=explored.copy(),
                    current_path=list(current_path),
                    hud_metrics={
                        "Current Algorithm": "Stochastic Hill Climbing",
                        "Status": "Stuck"
                    },
                    action_description=f"Sợ bão! Không có đường nào tốt hơn từ {current_node}."
                ))
                break
                
            # Đưa yếu tố ngẫu nhiên vào quyết định chọn bước kế tiếp để tăng tính đa dạng khám phá.
            current_node = random.choice(better_neighbors)
            current_path.append(current_node)
            explored.add(current_node)
            
        return history

class LocalBeamSearch(BaseAlgorithm):
    """
    Thuật toán Tìm kiếm Chùm (Local Beam Search).
    Bắt đầu với k trạng thái ngẫu nhiên (hoặc cùng 1 điểm xuất phát). Ở mỗi bước, sinh ra tất cả các 
    trạng thái kế tiếp từ k trạng thái hiện tại. Sau đó, nó lọc ra đúng k trạng thái có hàm đánh giá 
    tốt nhất để đi tiếp. Khác với việc chạy độc lập k lần Hill Climbing, k nhánh này liên tục chia sẻ
    thông tin bằng việc loại bỏ các nhánh yếu và nhân bản các nhánh mạnh.
    """
    def __init__(self, k=3):
        self.k = k

    def run(self, environment, start, target):
        history = []
        
        # 'Beam' là tập hợp gồm k trạng thái tốt nhất. Cấu trúc: (f_cost, g_cost, path).
        # Nó là một sự mô phỏng của A* nhưng chỉ giữ lại tối đa k phần tử ở frontier tại mọi thời điểm.
        beam = [(heuristic(start, target), 0, [start])]
        explored = set([start])
        
        while True:
            target_reached_path = None
            for f_cost, g_cost, path in beam:
                if path[-1] == target:
                    target_reached_path = path
                    break
                    
            history.append(State(
                frontier=[path[-1] for _, _, path in beam],
                explored=explored.copy(),
                current_path=beam[0][2], 
                hud_metrics={
                    "Current Algorithm": f"Local Beam Search (k={self.k})",
                    "Best f(n)": f"{beam[0][0]:.1f}",
                },
                action_description=f"Đang duy trì {len(beam)} trạng thái. Tốt nhất đang ở {beam[0][2][-1]}."
            ))
            
            if target_reached_path:
                history.append(State(
                    frontier=[],
                    explored=explored.copy(),
                    current_path=target_reached_path,
                    hud_metrics={
                        "Current Algorithm": f"Local Beam Search (k={self.k})",
                        "Best f(n)": "0.0",
                    },
                    action_description=f"Đã bắt kịp B-52 tại {target}!"
                ))
                break
                
            all_successors = []
            
            # Sinh ra toàn bộ thế hệ F1 từ tập cha (beam).
            for f_cost, g_cost, path in beam:
                node = path[-1]
                for neighbor in environment.get_neighbors(node[0], node[1]):
                    if neighbor not in explored:
                        explored.add(neighbor)
                        new_path = list(path)
                        new_path.append(neighbor)
                        new_g = g_cost + environment.get_cost(neighbor[0], neighbor[1])
                        new_f = new_g + heuristic(neighbor, target)
                        all_successors.append((new_f, new_g, new_path))
                        
            if not all_successors:
                history.append(State(
                    frontier=[],
                    explored=explored.copy(),
                    current_path=beam[0][2],
                    hud_metrics={
                        "Current Algorithm": f"Local Beam Search (k={self.k})",
                        "Status": "Stuck"
                    },
                    action_description=f"Tất cả {len(beam)} tia đều bị kẹt!"
                ))
                break
                
            # Xếp hạng toàn bộ nhánh con và chỉ chọn ra k cá thể ưu tú nhất để đi tiếp.
            all_successors.sort(key=lambda x: x[0])
            beam = all_successors[:self.k]
            
        return history

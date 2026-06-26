# algorithms/complex_env.py
import random
from collections import deque
from algorithms.base_algorithm import BaseAlgorithm, State

def heuristic(a, b):
    """
    Hàm lượng giá heuristic sử dụng khoảng cách Manhattan.
    Khoảng cách này đặc biệt phù hợp và tối ưu admissible trên lưới dạng ô vuông (chỉ di chuyển ngang/dọc)
    để định hướng thuật toán tìm kiếm về phía mục tiêu.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

class AndOrSearch(BaseAlgorithm):
    """
    Thuật toán Tìm kiếm AND-OR (AND-OR Graph Search).
    Sử dụng trong môi trường không tất định (non-deterministic). 
    - Nút OR (Hệ thống): Quyết định chọn hành động nào tốt nhất.
    - Nút AND (Môi trường): Đại diện cho mọi kết quả có thể xảy ra của một hành động do ảnh hưởng của nhiễu.
    Một kế hoạch hoàn chỉnh phải chỉ định một phản ứng hợp lý cho mọi kết quả do nút AND sinh ra.
    """
    def run(self, environment, start, target):
        history = []
        current_node = start
        current_path = [start]
        
        while current_node != target:
            history.append(State(
                frontier=[],
                explored=set(current_path),
                current_path=list(current_path),
                hud_metrics={
                    "Current Algorithm": "AND-OR Search",
                    "Status": "Executing Conditional Plan"
                },
                action_description=f"Tiến về {target}. Đang ở {current_node}."
            ))
            
            # OR Node: Hệ thống quyết định chọn hướng đi tốt nhất tiến về đích
            neighbors = environment.get_neighbors(current_node[0], current_node[1])
            best_neighbor = min(neighbors, key=lambda n: heuristic(n, target))
            
            # AND Node: Mô phỏng nhiễu từ môi trường khiến kết quả hành động bị thay đổi (tỷ lệ 20% bị tạt gió).
            if random.random() < 0.20:
                actual_move = random.choice(neighbors)
                history.append(State(
                    frontier=[],
                    explored=set(current_path),
                    current_path=list(current_path),
                    hud_metrics={
                        "Current Algorithm": "AND-OR Search",
                        "Status": "Wind Disruption!"
                    },
                    action_description=f"Gió tạt ngẫu nhiên! Dự kiến {best_neighbor} nhưng lại bay sang {actual_move}."
                ))
            else:
                actual_move = best_neighbor
                
            current_node = actual_move
            current_path.append(current_node)
            
            # Cơ chế ngắt (Circuit breaker) nhằm chống vòng lặp vô hạn nếu môi trường quá khắc nghiệt.
            if len(current_path) > 500: 
                break
                
        if current_node == target:
            history.append(State(
                frontier=[],
                explored=set(current_path),
                current_path=list(current_path),
                hud_metrics={"Current Algorithm": "AND-OR Search", "Status": "Target Destroyed"},
                action_description=f"Đã diệt mục tiêu tại {target} bất chấp gió bão!"
            ))
            
        return history

class ComplexSearchBase(BaseAlgorithm):
    """
    Lớp cơ sở cung cấp thuật toán duyệt đồ thị (BFS mở rộng) phục vụ việc dò tìm không gian trạng thái
    khi vị trí đích bị ẩn giấu (Môi trường có trạng thái niềm tin - Belief States).
    """
    def run_bfs_complex(self, algo_name, environment, start, belief_states, target):
        history = []
        queue = deque([[start]])
        explored = {start}
        
        found_targets = []
        paths = []
        
        # Hệ thống ra đa (Radar sweep) giới hạn quét và bắn đồng thời tối đa 2 mục tiêu.
        max_bullets = 2
        
        while queue and len(found_targets) < max_bullets:
            path = queue.popleft()
            node = path[-1]
            
            history.append(State(
                frontier=[p[-1] for p in queue],
                explored=explored.copy(),
                current_path=list(path),
                hud_metrics={
                    "Current Algorithm": algo_name,
                    "Belief States": str(belief_states),
                    "Found Targets": str(found_targets),
                    "Paths": str(paths)
                },
                action_description=f"Dò RADAR: Đang mở rộng vùng quét. Đã khóa {len(found_targets)}/2 mục tiêu."
            ))
            
            # Nếu node hiện tại nằm trong tập giả thuyết (Belief States) mà hệ thống tình báo báo cáo.
            if node in belief_states and node not in found_targets:
                found_targets.append(node)
                paths.append(list(path))
                
                # Thoát vòng lặp ngay khi đã trích xuất đủ quỹ đạo cho k mục tiêu tiềm năng.
                if len(found_targets) == max_bullets:
                    history.append(State(
                        frontier=[p[-1] for p in queue],
                        explored=explored.copy(),
                        current_path=list(path),
                        hud_metrics={
                            "Current Algorithm": algo_name,
                            "Belief States": str(belief_states),
                            "Found Targets": str(found_targets),
                            "Paths": str(paths)
                        },
                        action_description=f"Dò RADAR hoàn tất! Đã khóa đủ 2 mục tiêu."
                    ))
                    break
                    
            for neighbor in environment.get_neighbors(node[0], node[1]):
                if neighbor not in explored:
                    explored.add(neighbor)
                    queue.append(path + [neighbor])
                    
        # Đối chiếu kết quả tìm kiếm với vị trí thực của mục tiêu
        is_success = target in found_targets
        status = "Success" if is_success else "Failed"
        msg = "Đã tiêu diệt B-52!" if is_success else "Bắn trượt! B-52 không nằm trong vùng tấn công."
        
        history.append(State(
            frontier=[],
            explored=explored.copy(),
            
            # Ở chế độ đa mục tiêu, việc vẽ đường đạn trên màn hình được xử lý riêng bởi UI Renderer, 
            # dựa trên thông số mảng 'Paths' trong `hud_metrics`, nên path chính được làm rỗng.
            current_path=[], 
            
            hud_metrics={
                "Current Algorithm": algo_name,
                "Belief States": str(belief_states),
                "Found Targets": str(found_targets),
                "Paths": str(paths),
                "Status": status
            },
            action_description=msg
        ))
        return history

class NoObservationSearch(ComplexSearchBase):
    """
    Thuật toán Không quan sát (Sensorless / Conformant Search).
    Vị trí mục tiêu hoàn toàn không thể quan sát (sương mù chiến tranh). 
    Hệ thống sẽ thực thi chuỗi hành động hòng ép tất cả các trạng thái có thể xảy ra (Belief State)
    hội tụ về một kết quả kiểm soát được.
    """
    def run_no_observation(self, environment, start, belief_states, target):
        return self.run_bfs_complex("No Observation Search", environment, start, belief_states, target)

class PartiallyObservableSearch(ComplexSearchBase):
    """
    Thuật toán Quan sát một phần (Partially Observable Search).
    Có cảm biến cung cấp một số manh mối giới hạn về vị trí hoặc khoảng cách tới mục tiêu.
    Tập Belief State sẽ được thu gọn dần theo từng lần quan sát để vạch ra lộ trình tối ưu nhất.
    """
    def run_partial_observation(self, environment, start, belief_states, target):
        return self.run_bfs_complex("Partially Observable", environment, start, belief_states, target)

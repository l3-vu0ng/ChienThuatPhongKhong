# algorithms/csp.py
import random
import heapq
from algorithms.base_algorithm import BaseAlgorithm, State

def get_a_star_path(env, start, goal, obstacles=None):
    """
    Hàm tiện ích tìm đường A* rút gọn được dùng nội bộ trong bài toán CSP (Constraint Satisfaction Problem).
    Nó tìm đường đi tối ưu từ hệ thống SAM-2 đến mục tiêu B-52 nhưng phải **chắc chắn** 
    tránh né các đường đạn (obstacles) của các hệ thống khác đã được gán trước đó.
    """
    if obstacles is None:
        obstacles = set()
    queue = []
    heapq.heappush(queue, (0, start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while queue:
        _, current = heapq.heappop(queue)

        if current == goal:
            break

        for next_node in env.get_neighbors(*current):
            # Tuân thủ ràng buộc không gian: Nếu ô kế tiếp bị khóa bởi đường đạn khác thì cấm đi vào.
            if next_node in obstacles and next_node != goal:
                continue
            new_cost = cost_so_far[current] + 1
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                priority = new_cost + abs(goal[0]-next_node[0]) + abs(goal[1]-next_node[1])
                heapq.heappush(queue, (priority, next_node))
                came_from[next_node] = current

    if goal not in came_from:
        return []

    path = []
    curr = goal
    while curr != start:
        path.append(curr)
        curr = came_from[curr]
    path.append(start)
    path.reverse()
    return path

def paths_intersect(path1, path2):
    """
    Kiểm tra hai quỹ đạo đạn đạo có giao cắt nhau hay không. 
    Trừ điểm xuất phát và đích đến, nếu có bất kỳ node nào trùng nhau tức là vi phạm ràng buộc không gian.
    """
    if not path1 or not path2: return False
    set1 = set(path1[1:-1]) if len(path1)>2 else set()
    set2 = set(path2[1:-1]) if len(path2)>2 else set()
    return len(set1 & set2) > 0

def is_valid_assignment(assignment):
    """
    Bộ ràng buộc (Constraints) cốt lõi của bài toán CSP trong đánh chặn diện rộng:
    1. Phân biệt (AllDiff): Mỗi bệ SAM phải bắn một mục tiêu B-52 khác nhau.
    2. Có khả thi (Exist): Phải tồn tại một đường đạn kết nối được từ SAM đến B-52.
    3. Không cản trở (No Intersection): Đường đạn của các bệ phóng không được cắt chéo vào nhau.
    """
    sams = list(assignment.keys())
    b52s = [assignment[sam]["target"] for sam in sams]
    
    # Kiểm tra ràng buộc AllDiff
    if len(set(b52s)) != len(b52s):
        return False
        
    for sam in sams:
        if not assignment[sam]["path"]:
            return False
            
    # Kiểm tra ràng buộc Intersection (Độ phức tạp O(n^2) cặp so sánh)
    for i in range(len(sams)):
        for j in range(i + 1, len(sams)):
            p1 = assignment[sams[i]]["path"]
            p2 = assignment[sams[j]]["path"]
            if paths_intersect(p1, p2):
                return False
    return True


class BacktrackingCSP(BaseAlgorithm):
    """
    Thuật toán Quay lui (Backtracking Search) dành cho Bài toán Thỏa mãn Ràng buộc (CSP).
    Thực hiện theo chiều sâu DFS: Thử gán giá trị cho một biến, nếu gặp phải trạng thái vi phạm 
    bộ quy tắc `is_valid_assignment`, lập tức hoàn tác (backtrack) và thử giá trị khác.
    """
    def run_csp(self, environment, sam_list, b52_list):
        history = []
        assignment = {}
        
        def backtrack():
            history.append(State(
                frontier=[v["target"] for v in assignment.values()],
                explored=set(sam_list),
                current_path=[],
                hud_metrics={
                    "Current Algorithm": "Backtracking CSP",
                    "Constraints": "\n- AllDiff(B-52)\n- Không giao quỹ đạo\n- Tránh B-52 khác",
                    "Variables": str([f"X{i+1}: {sam}" for i, sam in enumerate(sam_list)]),
                    "Domains": str([f"D{i+1}: {b52}" for i, b52 in enumerate(b52_list)]),
                    "Assigned": str(len(assignment)),
                    "Assignment": str([f"X{sam_list.index(k)+1}->D{b52_list.index(v['target'])+1}" for k, v in assignment.items()]),
                    "IsValid": str(is_valid_assignment(assignment)),
                    "Paths": str([assignment[s]["path"] if s in assignment else [] for s in sam_list])
                },
                action_description=f"Thử gán: {[(k, v['target']) for k, v in assignment.items()]}"
            ))
            
            # Trạng thái kết thúc: Đã gán xong mục tiêu cho toàn bộ tiểu đoàn SAM
            if len(assignment) == len(sam_list):
                return assignment
                
            # Chọn biến chưa được gán (SAM tiếp theo)
            unassigned_sam = [s for s in sam_list if s not in assignment][0]
            
            # Duyệt qua các miền giá trị có thể gán (Danh sách các mục tiêu B-52)
            for b52 in b52_list:
                
                # Biến tất cả các thực thể khác thành vật cản để A* tránh đi qua
                obstacles = set(s for s in sam_list if s != unassigned_sam)
                obstacles.update(b for b in b52_list if b != b52)
                for val in assignment.values():
                    obstacles.update(val["path"])
                
                path = get_a_star_path(environment, unassigned_sam, b52, obstacles)
                if not path:
                    continue
                    
                assignment[unassigned_sam] = {"target": b52, "path": path}
                
                # Nếu phép gán hiện tại chưa phá vỡ quy tắc, tiếp tục đào sâu (DFS) xuống cấp tiếp theo
                if is_valid_assignment(assignment):
                    result = backtrack()
                    if result:
                        return result
                        
                # Nếu sai hoặc đào sâu gặp ngõ cụt, thực hiện hoàn tác (Quay lui)
                del assignment[unassigned_sam]
                
            return None
            
        final_assignment = backtrack()
        if final_assignment:
            history.append(State(
                frontier=[v["target"] for v in final_assignment.values()],
                explored=set(sam_list),
                current_path=[],
                hud_metrics={
                    "Current Algorithm": "Backtracking CSP", 
                    "Constraints": "\n- AllDiff(B-52)\n- Không giao quỹ đạo\n- Tránh B-52 khác",
                    "Variables": str([f"X{i+1}: {sam}" for i, sam in enumerate(sam_list)]),
                    "Domains": str([f"D{i+1}: {b52}" for i, b52 in enumerate(b52_list)]),
                    "Status": "Success",
                    "Assignment": str([f"X{sam_list.index(k)+1}->D{b52_list.index(v['target'])+1}" for k, v in final_assignment.items()]),
                    "IsValid": "True",
                    "Paths": str([final_assignment[s]["path"] if s in final_assignment else [] for s in sam_list])
                },
                action_description=f"Hoàn tất phân công! Kết quả: {[(k, v['target']) for k, v in final_assignment.items()]}"
            ))
        else:
            history.append(State(
                frontier=[],
                explored=set(sam_list),
                current_path=[],
                hud_metrics={
                    "Current Algorithm": "Backtracking CSP", 
                    "Variables": str([f"X{i+1}: {sam}" for i, sam in enumerate(sam_list)]),
                    "Domains": str([f"D{i+1}: {b52}" for i, b52 in enumerate(b52_list)]),
                    "Status": "Failed"
                },
                action_description="Không tìm thấy phương án gán hợp lệ nào."
            ))
            
        return history

class ForwardCheckingCSP(BaseAlgorithm):
    """
    Thuật toán Forward Checking (Dò trước) trong hệ thống CSP.
    Giống với Backtracking nhưng có thêm cơ chế "nhìn xa trông rộng". 
    Mỗi khi một SAM gán cho một mục tiêu B-52, nó sẽ ngay lập tức loại bỏ B-52 đó (và các lộ trình bị chéo) 
    khỏi danh sách lựa chọn (domain) của các bệ SAM còn lại. Nếu bất kỳ SAM nào còn lại không còn mục tiêu khả thi, 
    nó sẽ quay lui (backtrack) ngay lập tức, tiết kiệm tài nguyên tính toán rất lớn.
    """
    def run_csp(self, environment, sam_list, b52_list):
        history = []
        assignment = {}
        
        # Miền giá trị (Domain) khởi tạo cho mỗi SAM là toàn bộ phi đội B-52.
        domains = {sam: list(b52_list) for sam in sam_list}
        
        def backtrack():
            history.append(State(
                frontier=[v["target"] for v in assignment.values()],
                explored=set(sam_list),
                current_path=[],
                hud_metrics={
                    "Current Algorithm": "Forward Checking", 
                    "Constraints": "\n- AllDiff(B-52)\n- Không giao quỹ đạo\n- Tránh B-52 khác",
                    "Variables": str([f"X{i+1}: {sam}" for i, sam in enumerate(sam_list)]),
                    "Domains": str([f"D{i+1}: {b52}" for i, b52 in enumerate(b52_list)]),
                    "Assigned": str(len(assignment)),
                    "Assignment": str([f"X{sam_list.index(k)+1}->D{b52_list.index(v['target'])+1}" for k, v in assignment.items()]),
                    "IsValid": str(is_valid_assignment(assignment)),
                    "Paths": str([assignment[s]["path"] if s in assignment else [] for s in sam_list])
                },
                action_description=f"Thử gán: {[(k, v['target']) for k, v in assignment.items()]}. Domains còn lại: {sum(len(d) for d in domains.values())} lựa chọn."
            ))
            
            if len(assignment) == len(sam_list):
                return assignment
                
            unassigned_sam = [s for s in sam_list if s not in assignment][0]
            
            for b52 in list(domains[unassigned_sam]):
                obstacles = set(s for s in sam_list if s != unassigned_sam)
                obstacles.update(b for b in b52_list if b != b52)
                for val in assignment.values():
                    obstacles.update(val["path"])
                
                path = get_a_star_path(environment, unassigned_sam, b52, obstacles)
                if not path:
                    continue
                
                assignment[unassigned_sam] = {"target": b52, "path": path}
                if is_valid_assignment(assignment):
                    
                    # ---- Bắt đầu logic Forward Checking ----
                    pruned = []
                    valid_forward = True
                    for other_sam in sam_list:
                        if other_sam not in assignment:
                            for other_b52 in list(domains[other_sam]):
                                temp_assignment = assignment.copy()
                                temp_obs = set(s for s in sam_list if s != other_sam)
                                temp_obs.update(b for b in b52_list if b != other_b52)
                                for k, v in temp_assignment.items(): temp_obs.update(v["path"])
                                
                                t_path = get_a_star_path(environment, other_sam, other_b52, temp_obs)
                                temp_assignment[other_sam] = {"target": other_b52, "path": t_path}
                                
                                # Cắt tỉa (Pruning) domain của các biến chưa gán nếu vi phạm ràng buộc
                                if not t_path or not is_valid_assignment(temp_assignment):
                                    domains[other_sam].remove(other_b52)
                                    pruned.append((other_sam, other_b52))
                                    
                            # Lỗi cung cấp sớm (Early failure): Một biến bị rỗng domain
                            if not domains[other_sam]:
                                valid_forward = False
                    # ---- Kết thúc logic Forward Checking ----
                                
                    if valid_forward:
                        result = backtrack()
                        if result:
                            return result
                            
                    # Hoàn tác lại domain đã bị cắt tỉa (Phục hồi lại trạng thái trước khi gọi backtrack)
                    for p_sam, p_b52 in pruned:
                        domains[p_sam].append(p_b52)
                        
                del assignment[unassigned_sam]
            return None
            
        final_assignment = backtrack()
        if final_assignment:
            history.append(State(
                frontier=[v["target"] for v in final_assignment.values()],
                explored=set(sam_list),
                current_path=[],
                hud_metrics={
                    "Current Algorithm": "Forward Checking", 
                    "Constraints": "\n- AllDiff(B-52)\n- Không giao quỹ đạo\n- Tránh B-52 khác",
                    "Variables": str([f"X{i+1}: {sam}" for i, sam in enumerate(sam_list)]),
                    "Domains": str([f"D{i+1}: {b52}" for i, b52 in enumerate(b52_list)]),
                    "Status": "Success",
                    "Assignment": str([f"X{sam_list.index(k)+1}->D{b52_list.index(v['target'])+1}" for k, v in final_assignment.items()]),
                    "IsValid": "True",
                    "Paths": str([final_assignment[s]["path"] if s in final_assignment else [] for s in sam_list])
                },
                action_description=f"Hoàn tất phân công cực nhanh! Kết quả: {[(k, v['target']) for k, v in final_assignment.items()]}"
            ))
        else:
            history.append(State(
                frontier=[],
                explored=set(sam_list),
                current_path=[],
                hud_metrics={
                    "Current Algorithm": "Forward Checking", 
                    "Variables": str([f"X{i+1}: {sam}" for i, sam in enumerate(sam_list)]),
                    "Domains": str([f"D{i+1}: {b52}" for i, b52 in enumerate(b52_list)]),
                    "Status": "Failed"
                },
                action_description="Không tìm thấy phương án gán hợp lệ nào."
            ))
        return history

class MinConflictsCSP(BaseAlgorithm):
    """
    Thuật toán Min-Conflicts dùng trong CSP (Tìm kiếm cục bộ - Local Search).
    Khác với DFS (Backtracking), thuật toán này khởi tạo một bộ gán NGẪU NHIÊN hoàn chỉnh ban đầu (bất chấp lỗi).
    Sau đó, ở mỗi bước, nó chọn ra một biến đang vi phạm điều kiện (bị xung đột) và đổi lại giá trị cho nó 
    sao cho số lượng xung đột giảm đi nhiều nhất. Nó rất hiệu quả trên các ma trận lớn mang tính ràng buộc lỏng (như lập lịch n-queens).
    """
    def run_csp(self, environment, sam_list, b52_list):
        history = []
        assignment = {}
        
        # Bước 1: Khởi tạo giá trị gán ngẫu nhiên ban đầu cho tất cả các bệ SAM
        for sam in sam_list:
            b52 = random.choice(b52_list)
            obstacles = set(s for s in sam_list if s != sam)
            obstacles.update(b for b in b52_list if b != b52)
            for val in assignment.values():
                obstacles.update(val["path"])
            path = get_a_star_path(environment, sam, b52, obstacles)
            if not path:
                path = []
            assignment[sam] = {"target": b52, "path": path}
            
        def count_conflicts(var, b52_target, current_assignment):
            """Hàm tính toán trọng số lỗi vi phạm (số lượng conflicts) của một phép thử gán."""
            temp = current_assignment.copy()
            obstacles = set(s for s in sam_list if s != var)
            obstacles.update(b for b in b52_list if b != b52_target)
            for k, val in temp.items():
                if k != var:
                    obstacles.update(val["path"])
            
            path = get_a_star_path(environment, var, b52_target, obstacles)
            temp[var] = {"target": b52_target, "path": path}
            
            conflicts = 0
            b52s = [val["target"] for val in temp.values()]
            
            # Phạt rất nặng nếu nhiều SAM cùng nhắm vào một B-52 (Ràng buộc AllDiff)
            if b52s.count(b52_target) > 1:
                conflicts += 100  
                
            # Phạt cực nặng nếu không tìm thấy đường đạn
            if not path:
                conflicts += 1000 
            else:
                for other_var, other_val in temp.items():
                    if var != other_var and paths_intersect(path, other_val["path"]):
                        conflicts += 1
            return conflicts, path

        # Bước 2: Vòng lặp cải thiện dần dần bộ gán
        for step in range(100):
            history.append(State(
                frontier=[v["target"] for v in assignment.values()],
                explored=set(sam_list),
                current_path=[],
                hud_metrics={
                    "Current Algorithm": "Min-Conflicts", 
                    "Constraints": "\n- AllDiff(B-52)\n- Không giao quỹ đạo\n- Tránh B-52 khác",
                    "Variables": str([f"X{i+1}: {sam}" for i, sam in enumerate(sam_list)]),
                    "Domains": str([f"D{i+1}: {b52}" for i, b52 in enumerate(b52_list)]),
                    "Step": str(step),
                    "Assignment": str([f"X{sam_list.index(k)+1}->D{b52_list.index(v['target'])+1}" for k, v in assignment.items()]),
                    "IsValid": str(is_valid_assignment(assignment)),
                    "Paths": str([assignment[s]["path"] if s in assignment else [] for s in sam_list])
                },
                action_description=f"Vòng lặp {step}: Đang cố sửa xung đột của {[(k, v['target']) for k, v in assignment.items()]}"
            ))
            
            if is_valid_assignment(assignment):
                history.append(State(
                    frontier=[v["target"] for v in assignment.values()],
                    explored=set(sam_list),
                    current_path=[],
                    hud_metrics={
                        "Current Algorithm": "Min-Conflicts", 
                        "Constraints": "\n- AllDiff(B-52)\n- Không giao quỹ đạo\n- Tránh B-52 khác",
                        "Variables": str([f"X{i+1}: {sam}" for i, sam in enumerate(sam_list)]),
                        "Domains": str([f"D{i+1}: {b52}" for i, b52 in enumerate(b52_list)]),
                        "Status": "Success",
                        "Assignment": str([f"X{sam_list.index(k)+1}->D{b52_list.index(v['target'])+1}" for k, v in assignment.items()]),
                        "IsValid": "True",
                        "Paths": str([assignment[s]["path"] if s in assignment else [] for s in sam_list])
                    },
                    action_description=f"Đã giải quyết xong mọi xung đột ở bước {step}! Kết quả: {[(k, v['target']) for k, v in assignment.items()]}"
                ))
                return history
                
            conflicted_vars = []
            for sam in sam_list:
                c, _ = count_conflicts(sam, assignment[sam]["target"], assignment)
                if c > 0:
                    conflicted_vars.append(sam)
                    
            # Tránh rơi vào Cực tiểu Địa phương (Local Minima) bằng cách chèn 20% xác suất biến đổi một SAM ngẫu nhiên
            if not conflicted_vars or random.random() < 0.2: 
                var = random.choice(sam_list)
            else:
                var = random.choice(conflicted_vars)
            
            min_c = float('inf')
            best_vals = []
            
            # Chọn giá trị giúp làm giảm số lượng conflict xuống thấp nhất
            for val in b52_list:
                c, p = count_conflicts(var, val, assignment)
                if c < min_c:
                    min_c = c
                    best_vals = [(val, p)]
                elif c == min_c:
                    best_vals.append((val, p))
                    
            chosen_b52, chosen_path = random.choice(best_vals)
            assignment[var] = {"target": chosen_b52, "path": chosen_path}
            
        history.append(State(
            frontier=[v["target"] for v in assignment.values()],
            explored=set(sam_list),
            current_path=[],
            hud_metrics={
                "Current Algorithm": "Min-Conflicts", 
                "Variables": str([f"X{i+1}: {sam}" for i, sam in enumerate(sam_list)]),
                "Domains": str([f"D{i+1}: {b52}" for i, b52 in enumerate(b52_list)]),
                "Status": "Failed"
            },
            action_description="Thất bại: Đạt giới hạn 100 bước mà vẫn còn xung đột."
        ))
        return history

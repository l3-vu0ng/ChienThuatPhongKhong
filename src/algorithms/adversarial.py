# algorithms/adversarial.py
import random
from algorithms.base_algorithm import BaseAlgorithm, State

def heuristic(a, b):
    """
    Hàm lượng giá heuristic sử dụng khoảng cách Manhattan.
    Được dùng để ước tính chi phí và phần thưởng ở tận cùng của cây trò chơi đối kháng.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

class Minimax(BaseAlgorithm):
    """
    Thuật toán Đối kháng Minimax.
    Được xây dựng cho trò chơi zero-sum có tổng lợi ích bằng 0. 
    Hệ thống SAM-2 đóng vai trò MAX (cố gắng tối đa hóa điểm số, tức là áp sát để tiêu diệt mục tiêu).
    Hệ máy bay B-52 đóng vai trò MIN (cố gắng giảm thiểu điểm số của MAX, tức là bay tránh ra xa).
    """
    def run_adversarial(self, environment, start, initial_target):
        history = []
        sam_pos = start
        b52_pos = initial_target
        current_path = [sam_pos]
        
        def minimax(s_pos, b_pos, depth, is_max):
            """
            Hàm đệ quy phân tích cây trò chơi Minimax.
            Khám phá luân phiên giữa lượt đi của SAM và lượt phản ứng của B-52.
            """
            # Trạng thái kết thúc: Duyệt tới độ sâu tối đa hoặc mục tiêu bị tiêu diệt
            if depth == 0 or s_pos == b_pos:
                # Điểm số đánh giá là nghịch đảo của khoảng cách. Khoảng cách càng ngắn, SAM càng có lợi (giá trị càng lớn)
                return -heuristic(s_pos, b_pos), None
                
            if is_max:
                best_val = -float('inf')
                best_moves = [s_pos]
                for move in environment.get_neighbors(s_pos[0], s_pos[1]):
                    # MAX gọi MIN (Đến lượt B-52 chạy)
                    val, _ = minimax(move, b_pos, depth - 1, False)
                    if val > best_val:
                        best_val = val
                        best_moves = [move]
                    elif val == best_val:
                        best_moves.append(move)
                return best_val, random.choice(best_moves)
            else:
                best_val = float('inf')
                best_moves = [b_pos]
                for move in environment.get_neighbors(b_pos[0], b_pos[1]):
                    # MIN gọi MAX (Đến lượt SAM đi)
                    val, _ = minimax(s_pos, move, depth - 1, True)
                    if val < best_val:
                        best_val = val
                        best_moves = [move]
                    elif val == best_val:
                        best_moves.append(move)
                return best_val, random.choice(best_moves)

        step = 0
        while sam_pos != b52_pos and step < 100:
            # Bước 1: Lượt của SAM-2 (Đóng vai trò MAX - tối đa hóa điểm số)
            _, best_sam_move = minimax(sam_pos, b52_pos, depth=3, is_max=True)
            sam_pos = best_sam_move
            current_path.append(sam_pos)
            
            history.append(State(
                frontier=[b52_pos], 
                explored=set(current_path),
                current_path=list(current_path),
                hud_metrics={"Current Algorithm": "Minimax", "Turn": "SAM-2", "Distance": str(heuristic(sam_pos, b52_pos))},
                action_description=f"SAM-2 đi tới {sam_pos}. Đang dùng Minimax (depth=3) đuổi theo B-52 tại {b52_pos}."
            ))
            
            if sam_pos == b52_pos:
                break
                
            # Bước 2: Lượt của B-52 (Đóng vai trò MIN - cực tiểu hóa điểm số của SAM-2)
            _, best_b52_move = minimax(sam_pos, b52_pos, depth=3, is_max=False)
            b52_pos = best_b52_move
            
            history.append(State(
                frontier=[b52_pos],
                explored=set(current_path),
                current_path=list(current_path),
                hud_metrics={"Current Algorithm": "Minimax", "Turn": "B-52", "Distance": str(heuristic(sam_pos, b52_pos))},
                action_description=f"B-52 né tránh sang {b52_pos}. Khoảng cách hiện tại: {heuristic(sam_pos, b52_pos)}."
            ))
            step += 1
            
        history.append(State(
            frontier=[],
            explored=set(current_path),
            current_path=list(current_path),
            hud_metrics={"Current Algorithm": "Minimax", "Status": "Game Over"},
            action_description="Trò chơi kết thúc! SAM-2 đã tiêu diệt B-52." if sam_pos == b52_pos else "B-52 đã trốn thoát!"
        ))
        return history

class AlphaBeta(BaseAlgorithm):
    """
    Thuật toán Tỉa nhánh Alpha-Beta (Alpha-Beta Pruning).
    Là phiên bản tối ưu của Minimax. Nó duy trì 2 biến `alpha` và `beta` để theo dõi những giá trị xấu nhất 
    mà MAX và MIN chắc chắn sẽ phải nhận. Nếu nhận thấy có một nhánh nào đó dẫn đến một kết quả "chắc chắn tệ hơn" 
    những phương án đã tìm được, nó sẽ từ chối duyệt sâu xuống nhánh đó để tiết kiệm tài nguyên.
    """
    def run_adversarial(self, environment, start, initial_target):
        history = []
        sam_pos = start
        b52_pos = initial_target
        current_path = [sam_pos]
        
        def alphabeta(s_pos, b_pos, depth, alpha, beta, is_max):
            if depth == 0 or s_pos == b_pos:
                return -heuristic(s_pos, b_pos), None
                
            if is_max:
                best_val = -float('inf')
                best_moves = [s_pos]
                for move in environment.get_neighbors(s_pos[0], s_pos[1]):
                    val, _ = alphabeta(move, b_pos, depth - 1, alpha, beta, False)
                    if val > best_val:
                        best_val = val
                        best_moves = [move]
                    elif val == best_val:
                        best_moves.append(move)
                    
                    # Cập nhật chặn dưới của MAX
                    alpha = max(alpha, best_val)
                    
                    # Beta cut-off: Nhánh này đã đưa cho MAX một giá trị quá lớn, 
                    # do đó MIN ở nút cha chắc chắn sẽ không bao giờ để MAX đi vào nhánh này.
                    # Ngừng quét!
                    if beta <= alpha:
                        break 
                return best_val, random.choice(best_moves)
            else:
                best_val = float('inf')
                best_moves = [b_pos]
                for move in environment.get_neighbors(b_pos[0], b_pos[1]):
                    val, _ = alphabeta(s_pos, move, depth - 1, alpha, beta, True)
                    if val < best_val:
                        best_val = val
                        best_moves = [move]
                    elif val == best_val:
                        best_moves.append(move)
                    
                    # Cập nhật chặn trên của MIN
                    beta = min(beta, best_val)
                    
                    # Alpha cut-off: Nhánh này đã dồn MIN tới giá trị tồi tệ, 
                    # do đó MAX ở nút cha chắc chắn sẽ không bao giờ chọn con đường đến đây.
                    # Ngừng quét!
                    if beta <= alpha:
                        break 
                return best_val, random.choice(best_moves)

        step = 0
        while sam_pos != b52_pos and step < 100:
            _, best_sam_move = alphabeta(sam_pos, b52_pos, 3, -float('inf'), float('inf'), True)
            sam_pos = best_sam_move
            current_path.append(sam_pos)
            
            history.append(State(
                frontier=[b52_pos],
                explored=set(current_path),
                current_path=list(current_path),
                hud_metrics={"Current Algorithm": "Alpha-Beta Pruning", "Turn": "SAM-2", "Distance": str(heuristic(sam_pos, b52_pos))},
                action_description=f"SAM-2 đi tới {sam_pos}. Dùng Alpha-Beta (depth=3) với bộ tỉa nhanh hơn."
            ))
            
            if sam_pos == b52_pos:
                break
                
            _, best_b52_move = alphabeta(sam_pos, b52_pos, 3, -float('inf'), float('inf'), False)
            b52_pos = best_b52_move
            
            history.append(State(
                frontier=[b52_pos],
                explored=set(current_path),
                current_path=list(current_path),
                hud_metrics={"Current Algorithm": "Alpha-Beta Pruning", "Turn": "B-52", "Distance": str(heuristic(sam_pos, b52_pos))},
                action_description=f"B-52 né tránh khôn ngoan sang {b52_pos}."
            ))
            step += 1
            
        history.append(State(
            frontier=[],
            explored=set(current_path),
            current_path=list(current_path),
            hud_metrics={"Current Algorithm": "Alpha-Beta Pruning", "Status": "Game Over"},
            action_description="Trò chơi kết thúc!"
        ))
        return history

class Expectimax(BaseAlgorithm):
    """
    Thuật toán Expectimax.
    Áp dụng cho môi trường có yếu tố ngẫu nhiên (hoặc đối thủ di chuyển hoàn toàn phi lý trí).
    Không giống như Minimax (Giả định đối thủ luôn đưa ra lựa chọn thông minh nhất gây bất lợi cho ta), 
    trong Expectimax, nút MIN được thay thế bằng nút CHANCE (Môi trường/Sự kiện ngẫu nhiên).
    Kết quả trả về không phải điểm tối thiểu mà là trung bình có trọng số của mọi khả năng.
    """
    def run_adversarial(self, environment, start, initial_target):
        history = []
        sam_pos = start
        b52_pos = initial_target
        current_path = [sam_pos]
        
        def expectimax(s_pos, b_pos, depth, is_max):
            if depth == 0 or s_pos == b_pos:
                return -heuristic(s_pos, b_pos), None
                
            if is_max:
                best_val = -float('inf')
                best_moves = [s_pos]
                for move in environment.get_neighbors(s_pos[0], s_pos[1]):
                    val, _ = expectimax(move, b_pos, depth - 1, False)
                    if val > best_val:
                        best_val = val
                        best_moves = [move]
                    elif val == best_val:
                        best_moves.append(move)
                return best_val, random.choice(best_moves)
            else:
                # Nút Chance: Tính toán Giá trị Kỳ vọng (Expected Value) bằng trung bình cộng 
                # (Vì mô phỏng tỷ lệ phần trăm xảy ra sự kiện là đồng đều giữa các lân cận).
                moves = environment.get_neighbors(b_pos[0], b_pos[1])
                if not moves:
                    return -heuristic(s_pos, b_pos), b_pos
                avg_val = 0
                for move in moves:
                    val, _ = expectimax(s_pos, move, depth - 1, True)
                    avg_val += val
                return avg_val / len(moves), None

        step = 0
        while sam_pos != b52_pos and step < 100:
            # Lượt của SAM-2 (Giả định rằng mục tiêu sẽ bay loạn xạ, không có chiến thuật)
            _, best_sam_move = expectimax(sam_pos, b52_pos, depth=3, is_max=True)
            sam_pos = best_sam_move
            current_path.append(sam_pos)
            
            history.append(State(
                frontier=[b52_pos],
                explored=set(current_path),
                current_path=list(current_path),
                hud_metrics={"Current Algorithm": "Expectimax", "Turn": "SAM-2", "Distance": str(heuristic(sam_pos, b52_pos))},
                action_description=f"SAM-2 đi tới {sam_pos}. Đang dùng mô hình kỳ vọng (Expectimax) dự đoán."
            ))
            
            if sam_pos == b52_pos:
                break
                
            # Lượt của B-52: B-52 bay hoàn toàn ngẫu nhiên do hoảng loạn
            b52_pos = random.choice(environment.get_neighbors(b52_pos[0], b52_pos[1]))
            
            history.append(State(
                frontier=[b52_pos],
                explored=set(current_path),
                current_path=list(current_path),
                hud_metrics={"Current Algorithm": "Expectimax", "Turn": "B-52", "Distance": str(heuristic(sam_pos, b52_pos))},
                action_description=f"B-52 di chuyển ngẫu nhiên (Chance Node) sang {b52_pos}."
            ))
            step += 1
            
        history.append(State(
            frontier=[],
            explored=set(current_path),
            current_path=list(current_path),
            hud_metrics={"Current Algorithm": "Expectimax", "Status": "Game Over"},
            action_description="Trò chơi kết thúc!"
        ))
        return history

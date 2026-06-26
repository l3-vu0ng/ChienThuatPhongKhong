# algorithms/base_algorithm.py
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Set

@dataclass
class State:
    """
    Lớp dữ liệu biểu diễn một trạng thái tại một thời điểm cụ thể của thuật toán tìm kiếm.
    Trạng thái này được chụp lại (snapshot) sau mỗi vòng lặp và dùng để kết xuất đồ hoạ (rendering) trên giao diện PyGame.
    """
    frontier: List[Tuple[int, int]] = field(default_factory=list)
    explored: Set[Tuple[int, int]] = field(default_factory=set)
    current_path: List[Tuple[int, int]] = field(default_factory=list)
    hud_metrics: Dict[str, str] = field(default_factory=dict)
    action_description: str = ""

class BaseAlgorithm:
    """
    Lớp trừu tượng định nghĩa cấu trúc chung cho tất cả các thuật toán AI.
    Mọi thuật toán (như BFS, DFS, A*, Minimax...) đều kế thừa lớp này và bắt buộc phải ghi đè phương thức `run()`.
    """
    def run(self, environment, start: Tuple[int, int], target: Tuple[int, int]) -> List[State]:
        """
        Thực thi quá trình tìm kiếm đường đi từ điểm bắt đầu đến mục tiêu.

        Args:
            environment: Thể hiện của lớp Environment, cung cấp thông tin về không gian trạng thái và chi phí di chuyển.
            start: Tọa độ bắt đầu của hệ thống.
            target: Tọa độ của mục tiêu cần tìm kiếm.

        Returns:
            List[State]: Một danh sách chứa toàn bộ lịch sử (history) các trạng thái phát sinh trong quá trình thuật toán chạy.
        """
        raise NotImplementedError("Algorithms must implement run()")

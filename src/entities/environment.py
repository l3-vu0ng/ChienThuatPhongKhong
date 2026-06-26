# entities/environment.py
import random
import config

class Environment:
    """
    Lớp Môi trường (Environment) chịu trách nhiệm quản lý không gian lưới 2D (Grid) ảo.
    Nó là đại diện cho hệ quy chiếu địa lý mà các thực thể (SAM-2, B-52) tương tác.
    Lớp này lưu trữ và quản lý cấu trúc liên kết của các chướng ngại vật (đám mây/vật cản cứng)
    và các khu vực thời tiết xấu (bão/vùng nhiễu động), đồng thời cung cấp các API để các thuật toán 
    tìm kiếm đường đi có thể truy vấn thông tin lân cận (neighbors) và chi phí di chuyển (cost) tại mỗi tọa độ.
    """
    def __init__(self, width=None, height=None):
        self.width = width if width else config.GRID_SIZE
        self.height = height if height else config.GRID_SIZE
        # Ma trận không gian grid được biểu diễn dưới dạng mảng 2 chiều.
        # Quy ước giá trị của lưới:
        # 0: Không gian trống (có thể bay qua an toàn, chi phí tiêu chuẩn).
        # 1: Đám mây tĩnh điện (vật cản cứng, không thể bay qua, thuật toán tìm đường phải né tránh hoàn toàn).
        # 2: Cơn bão/Nhiễu động không khí (vùng có thể đi qua nhưng phải chịu phạt chi phí cao, cost = 5).
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
    def generate_terrains(self, num_clouds, num_storms, avoid_positions):
        """
        Khởi tạo ngẫu nhiên cấu hình địa hình trên lưới không gian.
        Đảm bảo tính toàn vẹn của trò chơi bằng cách không sinh vật cản đè lên 
        các tọa độ nhạy cảm đã được bảo lưu (avoid_positions) như vị trí xuất phát của tên lửa hoặc mục tiêu.
        """
        # Phân bổ các đám mây (vật cản tuyệt đối/cứng)
        placed_clouds = 0
        while placed_clouds < num_clouds:
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            # Kiểm tra tránh ghi đè lên các ô đã có địa hình hoặc vị trí cấm
            if (x, y) not in avoid_positions and self.grid[y][x] == 0:
                self.grid[y][x] = 1
                placed_clouds += 1
                
        # Phân bổ các cơn bão (vật cản tương đối/vùng chi phí cao)
        placed_storms = 0
        while placed_storms < num_storms:
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            if (x, y) not in avoid_positions and self.grid[y][x] == 0:
                self.grid[y][x] = 2
                placed_storms += 1

    def get_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        """
        Trích xuất danh sách các node lân cận hợp lệ từ một tọa độ (x, y) cho trước.
        Chỉ cho phép di chuyển theo 4 hướng trực giao (Von Neumann neighborhood): Lên, Xuống, Trái, Phải.
        Hàm này là cốt lõi cho chức năng mở rộng nút (node expansion) trong mọi thuật toán tìm kiếm.
        Tự động loại bỏ các node lân cận nằm ngoài biên của ma trận (out of bounds) hoặc bị chặn bởi mây (giá trị = 1).
        """
        neighbors = []
        # Các vector chỉ hướng tương ứng với: [Phải, Dưới, Trái, Trên]
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            # Ràng buộc biên và ràng buộc vật lý
            if 0 <= nx < self.width and 0 <= ny < self.height and self.grid[ny][nx] != 1:
                neighbors.append((nx, ny))
        return neighbors
        
    def get_cost(self, x: int, y: int) -> int:
        """
        Truy vấn chi phí di chuyển (g-cost) để tiến vào một tọa độ cụ thể.
        Được sử dụng bởi các thuật toán tìm kiếm có thông tin (Informed Search) như Dijkstra hoặc A* 
        để ưu tiên các quỹ đạo an toàn và tối ưu tài nguyên.
        
        Trả về:
            5: Nếu tọa độ chứa bão (Vùng nhiễu).
            1: Nếu tọa độ là không gian bình thường.
        """
        if self.grid[y][x] == 2:
            return 5
        return 1

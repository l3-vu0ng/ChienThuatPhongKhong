# entities/sam2.py

class SAM2:
    """
    Thực thể SAM-2 đại diện cho hệ thống Tên lửa phòng không (Surface-to-Air Missile).
    Trong ngữ cảnh của đồ thị tìm kiếm không gian trạng thái, đây chính là node khởi nguồn (start node/root node).
    Mọi thuật toán dò đường sẽ lấy tọa độ (x, y) của thể hiện (instance) này làm điểm bắt đầu 
    để tính toán quỹ đạo bay đến mục tiêu.
    """
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

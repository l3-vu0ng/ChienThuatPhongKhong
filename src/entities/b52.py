# entities/b52.py

class B52:
    """
    Thực thể B-52 đại diện cho mục tiêu trên không của đối phương.
    Trong mô hình biểu diễn bài toán AI, đối tượng này đóng vai trò là trạng thái đích (goal state).
    Tọa độ (x, y) của nó được sử dụng để kiểm tra điều kiện kết thúc của thuật toán tìm kiếm (goal test),
    cũng như làm đầu vào cho hàm đánh giá Heuristic (ví dụ: tính khoảng cách Manhattan từ một node bất kỳ đến đích).
    """
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

# BÁO CÁO MÔN HỌC: TRÍ TUỆ NHÂN TẠO

**TRƯỜNG ĐẠI HỌC CÔNG NGHỆ KỸ THUẬT TP. HỒ CHÍ MINH**  
**KHOA CÔNG NGHỆ THÔNG TIN**

---

## ĐỀ TÀI: TRÒ CHƠI CHIẾN THUẬT PHÒNG KHÔNG

- **LỚP HỌC PHẦN:** 252ARIN330585_07
- **GVHD:** TS. Phan Thị Huyền Trang

### Nhóm sinh viên thực hiện:
1. **Võ Lê Vương** - 24110391
2. **Đoàn Thanh Liêm** - 24110270
3. **Lê Trung Đông** - 24110201

---

## 1. Giới thiệu dự án
**Trò chơi Chiến Thuật Phòng Không** là một phần mềm mô phỏng đồ họa 2D (phát triển trên `pygame-ce`). Lấy cảm hứng từ chiến dịch lịch sử "12 ngày đêm Điện Biên Phủ trên không", dự án ứng dụng **18 thuật toán Trí Tuệ Nhân Tạo (AI)** kinh điển để điều khiển hệ thống tên lửa phòng không (SAM-2) làm nhiệm vụ dò tìm và đánh chặn pháo đài bay B-52 của đối phương trên không gian lưới (Grid).

Trò chơi áp dụng **Cấu trúc 2 Giai Đoạn (2 Phases)** cho phần lớn các thuật toán:
- **Phase 1 (Dò RADAR):** Áp dụng thuật toán AI để tìm kiếm đường bay tối ưu, tránh chướng ngại vật (Núi, Bão). Quá trình này được trực quan hóa từng bước trên màn hình.
- **Phase 2 (Khai Hoả):** Sau khi vạch xong lộ trình, hệ thống phóng tên lửa rượt đuổi mục tiêu với hiệu ứng hạt (Particles VFX) mô phỏng đuôi lửa tên lửa và hoạt ảnh nổ chân thực. Đầu tên lửa tự động xoay theo hướng di chuyển.

## 2. Phân tích bài toán theo hệ thống PEAS
Hệ thống AI trong dự án được mô hình hóa chi tiết thông qua PEAS:
- **P (Performance Measure - Tiêu chí đánh giá):** Tối đa hóa xác suất tiêu diệt B-52, tối thiểu hóa đạn SAM-2 tiêu hao. Tối ưu số bước duyệt (Node) để duy trì tốc độ khung hình (>= 30 FPS).
- **E (Environment - Môi trường):** Không gian lưới 2D tối ưu hóa cho đồ họa mô phỏng. Bắt đầu từ môi trường tĩnh, tất định (chỉ có mây nhiễu, núi), phát triển lên môi trường động, ngẫu nhiên và tàng hình. Môi trường mới được nâng cấp hiển thị 3D khối cho "Núi" và hiệu ứng sấm sét cho "Bão".
- **A (Actuators - Cơ cấu tác động):** Trạm radar phát tia dò tìm; Bệ phóng chọn góc bắn; Tên lửa trên không bẻ lái lách mây đuổi theo mục tiêu.
- **S (Sensors - Cảm biến):** Radar trả về toạ độ (x, y) của mục tiêu và đạn. Tín hiệu có thể rõ ràng, bị nhiễu chập chờn, hoặc mù hoàn toàn (đối với môi trường phức tạp).

## 3. Các thuật toán AI được áp dụng
Dự án tích hợp 18 thuật toán, chia thành 6 nhóm bối cảnh chiến thuật từ cơ bản đến phức tạp:

### Nhóm 1: Tìm kiếm mù (Uninformed Search)
*Bối cảnh: B-52 ĐỨNG YÊN. Đài radar đứt liên lạc, tự dò tìm trên lưới mù.*
- **Breadth-First Search (BFS):** Radar lan toả vòng tròn đồng tâm 360 độ.
- **Depth-First Search (DFS):** Tia sóng quét sâu một đường thẳng, đụng vật cản mới lùi lại (backtrack).
- **Iterative Deepening Search (IDS):** Quét tia giống DFS nhưng nâng dần công suất tia sóng từ khoảng cách gần ra xa.

### Nhóm 2: Tìm kiếm có thông tin (Informed Search)
*Bối cảnh: B-52 ĐỨNG YÊN. Radar đã chốt toạ độ. SAM-2 lập kế hoạch bay bằng Heuristic (Khoảng cách đường chim bay).*
- **Greedy Search:** Bay mù quáng về hướng đích nhanh nhất, dễ kẹt vào bẫy nhiễu sóng chữ U.
- **A-Star Search:** Cân bằng giữa quãng đường đã bay và Heuristic, vẽ quỹ đạo luồn lách né nhiễu thông minh.
- **IDA-Star:** Hoạt động như A* nhưng kiểm soát bộ nhớ qua giới hạn "nhiên liệu" (f-cost threshold), tránh tràn RAM khi map lớn.

### Nhóm 3: Tìm kiếm cục bộ (Local Search)
*Bối cảnh: B-52 DI CHUYỂN VÔ TRI. SAM-2 không tính trước toàn bộ quỹ đạo mà điều chỉnh góc lái theo từng Khung hình (Frame).*
- **Simple Hill Climbing:** Bẻ lái để bám đuôi liên tục, dễ kẹt ở Local Maxima (đám mây lớn).
- **Stochastic Hill Climbing:** Lâu lâu bẻ lái chệch hướng ngẫu nhiên để vọt thoát khỏi vùng mây nhiễu bị kẹt.
- **Local Beam:** Bắn loạt k quả đạn (Salvo). Quả nào lệch hướng quá xa tự hủy, các quả còn lại chia sẻ dữ liệu toạ độ bám đuổi để bủa vây B-52.

### Nhóm 4: Môi trường phức tạp (Complex Environments)
*Bối cảnh: B-52 ĐỨNG YÊN. Môi trường có gió bão ngẫu nhiên, tín hiệu radar chập chờn.*
- **AND-OR Search:** Lập kế hoạch dự phòng đối phó với gió tạt ngẫu nhiên.
- **No Observation:** B-52 tàng hình 100%. Radar ngẫu nhiên khoanh vùng 3 vị trí tình nghi (Belief States). Bệ phóng rải BFS chạm 2 vị trí tình nghi, thu thập 2 đường đi và phóng 2 tên lửa kiểm tra cùng lúc (Phase 2 bắn song song).
- **Partially Observable:** Radar chập chờn. Có 3 vị trí tình nghi, trong đó chắc chắn 1 vị trí là mục tiêu thực. Dùng BFS chung lõi với No Observation để phóng 2 tên lửa. Nếu trúng đúng vị trí B-52 thì báo Success.

### Nhóm 5: Thoả mãn ràng buộc (CSP)
*Bối cảnh: B-52 dự kiến ở 3 toạ độ. Cần phân công góc bắn cho 3 bệ phóng (L1, L2, L3) sao cho đạn không bay đan chéo.*
- **Backtracking:** Thử gán tuần tự, gặp lỗi cắt chéo thì quay lui.
- **Forward Checking:** Khi gán xong 1 mục tiêu, gạch bỏ mục tiêu cắt chéo ở các bệ phóng khác ngay lập tức, tiết kiệm tài nguyên duyệt.
- **Min-Conflicts:** Gán bừa tất cả bệ phóng. Hệ thống tráo đổi mục tiêu sao cho giảm thiểu số lỗi đan chéo. Tia đỏ loạn xạ tự gỡ rối thành quỹ đạo chuẩn.

### Nhóm 6: Tìm kiếm đối kháng (Adversarial Search)
*Bối cảnh: Trò chơi Zero-Sum. B-52 DI CHUYỂN CÓ TRÍ TUỆ lẩn trốn, SAM-2 (MAX) đối đầu B-52 (MIN). Hành động diễn ra đồng thời (Không có 2 phase tách biệt).*
- **Minimax:** Tính trước mọi bước để ép góc đối phương hoàn hảo. (FPS có thể giảm).
- **Alpha-Beta Pruning:** Cắt tỉa nhánh thừa để tăng tốc độ tính toán, giữ FPS mượt 60 mà chiến thuật không đổi.
- **Expectimax:** Coi phi công B-52 là Nút Xác Suất (đôi khi mắc sai lầm). SAM-2 bẻ lái bắt bài rủi ro thay vì phòng thủ tuyệt đối.

## 4. Cài đặt và Chạy mô phỏng

### Yêu cầu hệ thống:
- Python 3.10+ (Đề xuất)
- Thư viện đồ họa hiện đại `pygame-ce`

### Cài đặt:
Khuyến nghị bạn nên tạo môi trường ảo (virtual environment) trước khi cài đặt các thư viện để tránh xung đột:
```bash
python -m venv .venv

# Kích hoạt môi trường ảo (Windows):
.venv\Scripts\activate
# (Hoặc trên macOS/Linux): 
source .venv/bin/activate

# Cài đặt thư viện:
pip install pygame-ce pytest
```

### Khởi chạy trò chơi:
```bash
python main.py
```

### Chạy Unit Test (Kiểm tra AI):
Dự án được áp dụng Test-Driven Development (TDD) để đảm bảo độ tin cậy của cả 18 thuật toán. Để xác thực tính đúng đắn của AI, bạn hãy chạy lệnh:
```bash
python -m pytest tests/ -v
```

### Hướng dẫn sử dụng UI:
- **Chọn Thuật Toán:** Sử dụng ComboBox bên cột HUD phải để lựa chọn 1 trong 6 Nhóm Thuật Toán và Thuật Toán Tương Ứng.
- **Nút `RUN`:** Bắt đầu quá trình dò tìm RADAR (Phase 1).
- **Điều Khiển Time-lapse:**
  - `<` / `>`: Lùi lại hoặc đi tới 1 bước duyệt của radar.
  - `AUTO` / `STOP`: Chạy tự động hoặc tạm dừng animation vẽ đường đi.
  - `>>`: Bỏ qua quá trình vẽ đường, đi thẳng đến kết quả cuối của thuật toán tìm kiếm.
- **Nút `FIRE`:** Kích hoạt Phase 2, khai hoả và xem tên lửa bay tiêu diệt mục tiêu với các hiệu ứng hình ảnh (VFX). (Chỉ áp dụng cho các thuật toán ngoài nhóm Đối kháng).
- **Phím tắt hiện có:** `Left Arrow` / `Right Arrow` để lùi/tiến từng bước, `Esc` để thoát chương trình.


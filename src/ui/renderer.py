# ui/renderer.py
import pygame
import math
import random
import os

class Particle:
    """
    Lớp Particle đại diện cho một hạt cơ bản trong hệ thống hiệu ứng hạt (Particle System).
    Được sử dụng để tạo ra các hiệu ứng hình ảnh động như tia lửa, vụ nổ, hoặc khói.
    """
    def __init__(self, x, y, color, speed, size, life):
        self.x = x
        self.y = y
        self.color = color
        self.dx = random.uniform(-speed, speed)
        self.dy = random.uniform(-speed, speed)
        self.size = size
        self.life = life
        self.max_life = life

    def update(self):
        """
        Cập nhật trạng thái vật lý của hạt qua mỗi khung hình (frame).
        Suy giảm thời gian sống (life) và kích thước (size) để tạo hiệu ứng tan biến dần.
        """
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
        self.size = max(0, self.size * 0.95)

    def draw(self, screen):
        """
        Render hạt lên màn hình với kênh Alpha (độ trong suốt) mờ dần theo thời gian sống.
        """
        if self.life > 0:
            alpha = int((self.life / self.max_life) * 255)
            s = pygame.Surface((int(self.size)*2, int(self.size)*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            screen.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class UIRenderer:
    """
    Hệ thống kết xuất đồ họa (Graphics Renderer) cốt lõi của trò chơi.
    Sử dụng Pygame để vẽ các thành phần: bản đồ lưới (grid), địa hình (terrains), 
    trạng thái thuật toán dò đường, thực thể (SAM-2, B-52), và Bảng điều khiển HUD.
    """
    def __init__(self, width=1920, height=1080, grid_size=30):
        pygame.init()
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.cell_size = 1080 // grid_size  # Tính toán kích thước pixel cho mỗi ô vuông lưới (mặc định 36px)
        
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        pygame.display.set_caption("CHIẾN THUẬT PHÒNG KHÔNG")
        
        # Bảng màu chuẩn hóa (Color Palette) cho toàn bộ hệ thống giao diện
        self.COLOR_RADAR_BG = (11, 25, 44)       # #0B192C
        self.COLOR_HUD_BG = (235, 231, 217)      # #EBE7D9 Tactical Paper
        self.COLOR_GRID = (26, 44, 71)           # #1a2c47
        self.COLOR_EXPLORED = (51, 65, 85)       # #334155
        self.COLOR_FRONTIER = (255, 170, 0)      # #FFAA00
        self.COLOR_PATH = (255, 51, 51)          # #FF3333
        self.COLOR_TEXT_DARK = (47, 79, 79)      # #2F4F4F Dark Slate Gray
        self.COLOR_TEXT_LIGHT = (105, 105, 105)  # #696969 Dim Gray
        self.COLOR_SAM2 = (0, 255, 255)          # Cyan
        self.COLOR_B52 = (255, 0, 85)            # Hot Pink / Red
        self.COLOR_MOUNTAIN_BASE = (92, 64, 51)  # Dark Brown
        self.COLOR_MOUNTAIN_DOTS = (34, 139, 34) # Forest Green
        self.COLOR_STORM_BASE = (169, 169, 169)  # Dark Gray
        self.COLOR_STORM_LINES = (20, 30, 80)    # Dark Blue
        
        # Tải phông chữ pixel nghệ thuật để tạo cảm giác Retro/Tactical
        ps2p_path = os.path.join("assets", "font", "PressStart2P-Regular.ttf")
        vt323_path = os.path.join("assets", "font", "VT323-Regular.ttf")
        try:
            # Phông chữ pixel yêu cầu kích thước cố định để không bị vỡ nét (anti-aliasing)
            self.font_hero = pygame.font.Font(ps2p_path, 80)
            self.font_title = pygame.font.Font(ps2p_path, 40)
            self.font_body = pygame.font.Font(vt323_path, 36)
            self.font_credits = pygame.font.Font(vt323_path, 41)
            self.font_small = pygame.font.Font(vt323_path, 28)
        except:
            print("Could not load custom font, falling back to default")
            self.font_hero = pygame.font.Font(None, 96)
            self.font_title = pygame.font.Font(None, 48)
            self.font_body = pygame.font.Font(None, 36)
            self.font_credits = pygame.font.Font(None, 41)
            self.font_small = pygame.font.Font(None, 24)
            
        # Tải và xử lý hình ảnh sprite của các thực thể
        try:
            b52_path = os.path.join("assets", "pictures", "b52.png")
            sam_path = os.path.join("assets", "pictures", "sam.png")
            self.img_b52 = pygame.image.load(b52_path).convert_alpha()
            self.img_b52 = pygame.transform.scale(self.img_b52, (int(self.cell_size * 1.5), int(self.cell_size * 1.5)))
            self.img_sam = pygame.image.load(sam_path).convert_alpha()
            self.img_sam = pygame.transform.scale(self.img_sam, (int(self.cell_size * 1.2), int(self.cell_size * 1.2)))
        except Exception as e:
            print("Could not load assets:", e)
            self.img_b52 = None
            self.img_sam = None

    def draw_polygon_glow(self, color, points, glow_radius=2):
        """
        Vẽ một đa giác có hiệu ứng phát sáng (glow) viền ngoài.
        Hữu ích để làm nổi bật các thực thể vector trên nền radar tối.
        """
        # Render đa giác lõi (phần thân)
        pygame.draw.polygon(self.screen, color, points)
        # Render viền dày tạo hiệu ứng hào quang (halo)
        pygame.draw.lines(self.screen, color, True, points, glow_radius)

    def draw_image_with_glow(self, image, center, angle_deg, glow_color):
        """
        Render một hình ảnh sprite với góc xoay động và tạo viền sáng bao quanh.
        Áp dụng kỹ thuật Masking trong Pygame để sinh ra lớp viền bao quanh vật thể.
        """
        rotated_img = pygame.transform.rotate(image, angle_deg)
        rect = rotated_img.get_rect(center=center)
        
        # Tạo hiệu ứng phát sáng sử dụng mask
        mask = pygame.mask.from_surface(rotated_img)
        glow_surf = mask.to_surface(setcolor=glow_color, unsetcolor=(0,0,0,0))
        
        # Vẽ hiệu ứng phát sáng hơi lệch về nhiều hướng để tạo viền dày hơn
        offsets = [(-2,0), (2,0), (0,-2), (0,2), (-1,-1), (1,-1), (-1,1), (1,1)]
        for dx, dy in offsets:
            glow_rect = glow_surf.get_rect(center=(center[0] + dx, center[1] + dy))
            self.screen.blit(glow_surf, glow_rect)
            
        # Vẽ hình ảnh thực lên trên hiệu ứng phát sáng
        self.screen.blit(rotated_img, rect)

    def draw_sam2(self, x, y, dx=0, dy=-1):
        """
        Vẽ bệ phóng/tên lửa SAM-2 tại tọa độ lưới (x, y).
        Hỗ trợ vẽ bằng ảnh sprite (nếu có) hoặc vẽ fallback bằng vector thuần túy.
        """
        cx, cy = x * self.cell_size + self.cell_size // 2, y * self.cell_size + self.cell_size // 2
        
        if hasattr(self, 'img_sam') and self.img_sam:
            angle_deg = math.degrees(math.atan2(-dy, dx)) - 90
            self.draw_image_with_glow(self.img_sam, (cx, cy), angle_deg, (0, 255, 255))
            return
            
        # Cơ chế Fallback: Vẽ mô hình tên lửa SAM-2 bằng các điểm vector học (Polygon)
        s = self.cell_size
        points = [
            (0, -s//2),      # Tip
            (s//3, s//2), # Right Fin
            (0, s//4),      # Base Center
            (-s//3, s//2)  # Left Fin
        ]
        
        angle = math.atan2(dy, dx) + math.pi/2 # Cộng thêm 90 độ vì gốc hình trỏ lên trên
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        rotated_points = []
        for px, py in points:
            rx = px * cos_a - py * sin_a
            ry = px * sin_a + py * cos_a
            rotated_points.append((cx + rx, cy + ry))
            
        self.draw_polygon_glow(self.COLOR_SAM2, rotated_points)

    def draw_b52(self, x, y, dx=0, dy=-1, color=None):
        """
        Vẽ máy bay B-52 tại tọa độ lưới (x, y).
        Hỗ trợ xoay linh hoạt (dx, dy) và dự phòng (fallback) vẽ vector nếu ảnh bị lỗi.
        """
        cx, cy = x * self.cell_size + self.cell_size // 2, y * self.cell_size + self.cell_size // 2
        
        draw_color = color if color else self.COLOR_B52

        if hasattr(self, 'img_b52') and self.img_b52:
            angle_deg = math.degrees(math.atan2(-dy, dx)) - 90
            self.draw_image_with_glow(self.img_b52, (cx, cy), angle_deg, draw_color)
            return

        # Cơ chế Fallback: Vẽ mô hình máy bay ném bom B-52 bằng đa giác 2D
        s = self.cell_size
        points = [
            (0, -s//3),      # Nose
            (s//2, s//3), # Right Wing
            (0, s//6),      # Tail
            (-s//2, s//3)  # Left Wing
        ]
        angle = math.atan2(dy, dx) + math.pi/2 # Cộng thêm 90 độ vì gốc hình trỏ lên trên
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        rotated_points = []
        for px, py in points:
            rx = px * cos_a - py * sin_a
            ry = px * sin_a + py * cos_a
            rotated_points.append((cx + rx, cy + ry))
            
        self.draw_polygon_glow(draw_color, rotated_points)

    def draw_grid_and_state(self, state, env_grid, current_step, total_steps, fixed_b52=None, fixed_sams=None, is_phase_2=False, history=None):
        """
        Hàm trung tâm (Core Renderer) chịu trách nhiệm kết xuất toàn bộ môi trường và dữ liệu của thuật toán.
        Xử lý chồng lớp (layering) từ dưới lên: Lưới -> Địa hình -> Hiệu ứng Radar -> Đường đi -> Thực thể.
        """
        algo_name = state.hud_metrics.get("Current Algorithm", "")
        
        # Render Lưới không gian (Grid Base) và Địa hình tĩnh (Terrains)
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                rect = (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                
                # Draw Terrains
                if env_grid and env_grid[y][x] == 1:
                    # Gốc đồi núi (Vẽ bằng đa giác)
                    bx, by = rect[0], rect[1]
                    s = self.cell_size
                    pts1 = [(bx, by+s), (bx+s//2, by), (bx+s, by+s)]
                    pygame.draw.polygon(self.screen, self.COLOR_MOUNTAIN_BASE, pts1)
                    
                    # Đổ bóng bên phải núi (Shadow)
                    pts2 = [(bx+s//4, by+s), (bx+s*3//4, by+s//2), (bx+s, by+s)]
                    pygame.draw.polygon(self.screen, (72, 44, 31), pts2)
                    
                    # Nửa chóp trên phối hợp màu xanh đậm/nhạt mô phỏng rừng cây (Forest Peak)
                    pts_top = [(bx+s//4, by+s//2), (bx+s//2, by), (bx+s*3//4, by+s//2)]
                    pygame.draw.polygon(self.screen, (34, 139, 34), pts_top) # Xanh lá đậm
                    
                    pts_top_light = [(bx+s*3//8, by+s//4), (bx+s//2, by), (bx+s*5//8, by+s//4)]
                    pygame.draw.polygon(self.screen, (50, 205, 50), pts_top_light) # Xanh lá nhạt
                    
                    # Chấm vài pixel ngẫu nhiên mô phỏng tán lá
                    pygame.draw.rect(self.screen, (0, 100, 0), (bx + s//2, by + s//4 + 2, 3, 3))
                    pygame.draw.rect(self.screen, (144, 238, 144), (bx + s//2 - 3, by + s//3, 2, 2))
                    pygame.draw.rect(self.screen, (0, 128, 0), (bx + s//2 + 4, by + s//3 + 2, 3, 3))
                elif env_grid and env_grid[y][x] == 2:
                    # Gốc đám mây bão
                    bx, by = rect[0], rect[1]
                    s = self.cell_size
                    pygame.draw.circle(self.screen, self.COLOR_STORM_BASE, (bx+s//3, by+s//2), s//3)
                    pygame.draw.circle(self.screen, self.COLOR_STORM_BASE, (bx+s*2//3, by+s//2), s//3)
                    pygame.draw.circle(self.screen, (100, 100, 100), (bx+s//2, by+s//3), s//4)
                    # Tia sét
                    pygame.draw.lines(self.screen, (255, 255, 0), False, [(bx+s//2, by+s//2), (bx+s//3, by+s*3//4), (bx+s//2, by+s*3//4), (bx+s//3, by+s)], 2)
                    
                pygame.draw.rect(self.screen, self.COLOR_GRID, rect, 1)

        if not is_phase_2:
            # Mô phỏng hiệu ứng quét Radar (Radar Sweep Line) để tăng tính chiến thuật
            import math
            time_ticks = pygame.time.get_ticks()
            sweep_angle = (time_ticks * 0.1) % 360
            
            if state.current_path and len(state.current_path) > 0:
                sx, sy = state.current_path[0]
                center = (sx * self.cell_size + self.cell_size // 2, sy * self.cell_size + self.cell_size // 2)
            else:
                cx = self.grid_size // 2
                cy = self.grid_size // 2
                center = (cx * self.cell_size + self.cell_size // 2, cy * self.cell_size + self.cell_size // 2)
                
            radius = max(self.grid_size * self.cell_size - center[0], center[0], self.grid_size * self.cell_size - center[1], center[1])
            end_x = center[0] + radius * math.cos(math.radians(sweep_angle))
            end_y = center[1] + radius * math.sin(math.radians(sweep_angle))
            pygame.draw.line(self.screen, (50, 255, 50), center, (end_x, end_y), 2)
            
            # Các điểm đã quét (Chấm sáng mờ)
            for x, y in state.explored:
                pygame.draw.circle(self.screen, (50, 150, 50), 
                                 (x * self.cell_size + self.cell_size // 2, y * self.cell_size + self.cell_size // 2), 6)
            
            # Các điểm đang chờ duyệt (Chấm sáng chói)
            for x, y in state.frontier:
                pygame.draw.circle(self.screen, (100, 255, 100), 
                                 (x * self.cell_size + self.cell_size // 2, y * self.cell_size + self.cell_size // 2), 8)
                
            # Đường đi hiện tại (Đường nét liền sáng)
            if state.current_path and len(state.current_path) > 1:
                pts = [(px * self.cell_size + self.cell_size // 2, py * self.cell_size + self.cell_size // 2) for px, py in state.current_path]
                pygame.draw.lines(self.screen, (0, 255, 0), False, pts, 3)

            # Vùng nghi ngờ (Hiệu ứng chớp nháy)
            belief_str = state.hud_metrics.get("Belief States", "[]")
            if belief_str != "[]":
                import ast
                try:
                    beliefs = ast.literal_eval(belief_str)
                    for bx, by in beliefs:
                        pulse = (time_ticks % 1000) / 1000.0
                        pygame.draw.circle(self.screen, (255, 255, 0), 
                                        (bx * self.cell_size + self.cell_size // 2, by * self.cell_size + self.cell_size // 2), int(15 * pulse), 2)
                except:
                    pass
        # Nếu đang ở Giai đoạn 2, vẽ bệ phóng tại điểm bắt đầu của đường đạn
        if is_phase_2 and state.current_path:
            self.draw_launcher(*state.current_path[0])
            
        # Vẽ Đường đạn
        if state.current_path and len(state.current_path) > 1:
            points = [(px * self.cell_size + self.cell_size//2, py * self.cell_size + self.cell_size//2) for px, py in state.current_path]
            pygame.draw.lines(self.screen, self.COLOR_PATH, False, points, 3)
            
        # Vẽ các thực thể dựa trên trạng thái hoặc cố định
        status = state.hud_metrics.get("Status", "")
        
        # Vẽ Sương mù chiến tranh cho chế độ Không quan sát
        if "No Observation" in algo_name:
            bombed_str = state.hud_metrics.get("Bombed", "[]")
            try:
                import ast
                bombed = ast.literal_eval(bombed_str)
            except:
                bombed = []
            
            # Vẽ các hố bom/vệt nổ
            for bx, by in bombed:
                pygame.draw.circle(self.screen, (30, 30, 30), 
                                 (bx * self.cell_size + self.cell_size//2, 
                                  by * self.cell_size + self.cell_size//2), 
                                 self.cell_size//2 - 2)
            
        # Vẽ chữ CLEAR (An toàn) cho chế độ Quan sát một phần
        if "Partially Observable" in algo_name and "CLEAR" in state.action_description:
            if state.current_path:
                lx, ly = state.current_path[-1]
                clear_font = pygame.font.SysFont("segoeui", 14, bold=True)
                clear_surf = clear_font.render("CLEAR", True, (50, 255, 50))
                self.screen.blit(clear_surf, (lx * self.cell_size - 10, ly * self.cell_size - 15))

        is_csp = "CSP" in algo_name or "Forward" in algo_name or "Conflicts" in algo_name
        csp_colors = [(50, 255, 50), (50, 200, 255), (255, 150, 50)]
        
        assigned_b52_colors = {}
        if is_csp:
            paths_str = state.hud_metrics.get("Paths", "[]")
            try:
                import ast
                paths = ast.literal_eval(paths_str)
                for i, path in enumerate(paths):
                    if path and len(path) > 0:
                        assigned_b52_colors[path[-1]] = csp_colors[i % len(csp_colors)]
            except:
                pass

        if fixed_b52:
            show_b52 = True
            algo_n = state.hud_metrics.get("Current Algorithm", algo_name)
            status = state.hud_metrics.get("Status", "")
            
            if "Partially Observable" in algo_n or "No Observation" in algo_n:
                if status in ["Success", "Failed"]:
                    # Hiệu ứng nhấp nháy trong Giai đoạn 2
                    if pygame.time.get_ticks() % 500 < 250:
                        show_b52 = False
                else:
                    show_b52 = False # Ẩn đi cho đến Giai đoạn 2
                    
            if show_b52:
                if isinstance(fixed_b52, list):
                    for i, b in enumerate(fixed_b52):
                        b_color = assigned_b52_colors.get(b, None)
                        self.draw_b52(*b, color=b_color)
                        if is_csp:
                            label = self.font_small.render(f"D{i+1}", True, (255, 255, 255))
                            self.screen.blit(label, (b[0] * self.cell_size + self.cell_size - 10, b[1] * self.cell_size - 10))
                else:
                    self.draw_b52(*fixed_b52)
        elif "Adversarial" in algo_name or "Minimax" in algo_name or "Alpha-Beta" in algo_name or "Expectimax" in algo_name:
            if state.frontier:
                b52_curr = state.frontier[0]
                b52_dx, b52_dy = 0, -1
                if history and current_step > 0:
                    for i in range(current_step - 1, -1, -1):
                        prev_state = history[i]
                        if prev_state.frontier and prev_state.frontier[0] != b52_curr:
                            prev_b52 = prev_state.frontier[0]
                            b52_dx = b52_curr[0] - prev_b52[0]
                            b52_dy = b52_curr[1] - prev_b52[1]
                            break
                self.draw_b52(b52_curr[0], b52_curr[1], b52_dx, b52_dy)
            if state.current_path:
                sam_curr = state.current_path[-1]
                dx, dy = 0, -1
                if len(state.current_path) > 1:
                    prev = state.current_path[-2]
                    dx = sam_curr[0] - prev[0]
                    dy = sam_curr[1] - prev[1]
                self.draw_sam2(sam_curr[0], sam_curr[1], dx, dy)
        elif "Đã bắt kịp" in state.action_description and state.current_path:
            self.draw_b52(*state.current_path[-1])
        elif "Phát hiện B-52" in state.action_description and state.current_path:
            self.draw_b52(*state.current_path[-1])
        elif status == "Destroyed" and "No Observation" in algo_name:
            bombed_str = state.hud_metrics.get("Bombed", "[]")
            try:
                import ast
                bombed = ast.literal_eval(bombed_str)
                self.draw_b52(*bombed[-1])
            except:
                pass
                
        if fixed_sams:
            for i, (sx, sy) in enumerate(fixed_sams):
                self.draw_sam2(sx, sy)
                if is_csp:
                    label = self.font_small.render(f"X{i+1}", True, (255, 255, 255))
                    self.screen.blit(label, (sx * self.cell_size + 10, sy * self.cell_size - 15))
                
        # Vẽ nhiều đường đạn (Cho CSP & thuật toán BFS phức tạp)
        if "Paths" in state.hud_metrics:
            paths_str = state.hud_metrics.get("Paths", "[]")
            try:
                import ast
                paths = ast.literal_eval(paths_str)
            except:
                paths = []
                
            is_valid = state.hud_metrics.get("IsValid", "True") == "True"
            status = state.hud_metrics.get("Status", "")
            
            if status in ["Success", "Destroyed"]:
                base_thickness = 4
            elif not is_valid or status in ["Failed", "Missed"]:
                base_thickness = 2
            else:
                base_thickness = 2 if "CSP" in algo_name else 3
                
            csp_colors = [(50, 255, 50), (50, 200, 255), (255, 150, 50)]
            for i, path in enumerate(paths):
                if len(path) > 1:
                    pixel_points = [(px * self.cell_size + self.cell_size//2, py * self.cell_size + self.cell_size//2) for (px, py) in path]
                    if not is_phase_2:
                        draw_color = csp_colors[i % len(csp_colors)] if is_csp else (50, 200, 50)
                        pygame.draw.lines(self.screen, draw_color, False, pixel_points, 2)
                    else:
                        if status in ["Success", "Destroyed"]:
                            draw_color = csp_colors[i % len(csp_colors)] if is_csp else (50, 255, 50)
                        elif not is_valid or status in ["Failed", "Missed"]:
                            draw_color = (255, 50, 50)
                        else:
                            draw_color = csp_colors[i % len(csp_colors)] if is_csp else self.COLOR_PATH
                        pygame.draw.lines(self.screen, draw_color, False, pixel_points, base_thickness)
                


    def draw_launcher(self, x, y):
        """
        Vẽ biểu tượng bệ phóng tĩnh (Static Launcher Base) trên mặt đất.
        Chủ yếu dùng trong Giai đoạn 2 (Tên lửa rời bệ bay theo quỹ đạo đã tính toán).
        """
        cx = x * self.cell_size + self.cell_size // 2
        cy = y * self.cell_size + self.cell_size // 2
        
        # Base
        pygame.draw.rect(self.screen, (100, 100, 100), (cx - 10, cy + 5, 20, 10))
        # Tháp pháo
        pygame.draw.circle(self.screen, (80, 80, 80), (cx, cy + 5), 8)
        # Nòng pháo
        pygame.draw.line(self.screen, (60, 60, 60), (cx, cy + 5), (cx + 10, cy - 10), 4)

    def draw_text_wrapped(self, surface, text, color, rect, font):
        """
        Render văn bản có khả năng tự động xuống dòng (Word Wrap) khi chạm tới biên bounding-box.
        Đảm bảo các mô tả thuật toán dài không bị tràn ra ngoài màn hình HUD.
        """
        explicit_lines = text.split('\n')
        lines = []
        for explicit_line in explicit_lines:
            words = explicit_line.split(' ')
            current_line = []
            for word in words:
                current_line.append(word)
                fw, fh = font.size(' '.join(current_line))
                if fw > rect[2]:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
            
        y_offset = rect[1]
        for line in lines:
            fw, fh = font.size(line)
            surface.blit(font.render(line, True, color), (rect[0], y_offset))
            y_offset += fh + 5
            
        return y_offset

    def draw_dashed_line(self, surface, color, start_pos, end_pos, width=1, dash_length=10):
        """
        Vẽ đường nét đứt (Dashed Line) chuyên dùng làm viền phân cách thẩm mỹ trong thiết kế HUD quân sự.
        """
        x1, y1 = start_pos
        x2, y2 = end_pos
        import math
        dl = math.hypot(x2 - x1, y2 - y1)
        if dl == 0: return
        dashes = int(dl / dash_length)
        for i in range(dashes):
            if i % 2 == 0:
                sx = x1 + (x2 - x1) * i / dashes
                sy = y1 + (y2 - y1) * i / dashes
                ex = x1 + (x2 - x1) * (i + 1) / dashes
                ey = y1 + (y2 - y1) * (i + 1) / dashes
                pygame.draw.line(surface, color, (sx, sy), (ex, ey), width)

    def draw_hud(self, state, current_step, total_steps):
        """
        Render màn hình điều khiển HUD (Heads-Up Display) hiển thị thông số theo thời gian thực (Telemetry).
        Hệ thống HUD đọc dữ liệu thô (raw metrics) từ 'State' của thuật toán và nội địa hóa (localize) sang tiếng Việt.
        """
        # Panel nền HUD
        pygame.draw.rect(self.screen, self.COLOR_HUD_BG, (1080, 0, 840, 1080))
        
        px = 1100
        self.draw_dashed_line(self.screen, self.COLOR_TEXT_DARK, (px, 240), (1900, 240), 2, 15)
        
        # Bảng từ điển chuyển đổi thuật ngữ kỹ thuật sang tiếng Việt chuẩn Quốc tế
        term_map = {
            "g(n)": "Khoảng cách bay [g(n)]",
            "h(n)": "Cách mục tiêu [h(n)]",
            "f(n)": "Chi phí dự tính [f(n)]",
            "Node": "Lượt quét",
            "Cost": "Tổn hao",
            "Nodes Evaluated": "Số điểm đã phân tích",
            "Best Cost": "Chi phí tối ưu",
            "Utility": "Giá trị hữu ích",
            "Alpha": "Ngưỡng Alpha",
            "Beta": "Ngưỡng Beta"
        }
        
        y_offset = 270
        for key, val in state.hud_metrics.items():
            if key in ["Current Algorithm", "Paths"]: continue
            display_key = term_map.get(key, key)
            full_text = f"{display_key}: {val}"
            y_offset = self.draw_text_wrapped(self.screen, full_text, self.COLOR_TEXT_DARK, (px, y_offset, 800, 1000), self.font_body)
            y_offset += 10 # Thêm khoảng cách giữa các chỉ số
            
        # Dịch và điều chỉnh các mô tả hành động nội tại (Action Descriptions)
        y_offset += 40
        desc_title = self.font_body.render("Hành động hiện tại:", True, self.COLOR_TEXT_DARK)
        self.screen.blit(desc_title, (px, y_offset))
        
        desc = state.action_description
        action_map = {
            "Khám phá": "Đang quét vị trí",
            "Khởi tạo": "Hệ thống radar đang khởi tạo...",
            "Đã tìm thấy đường đi": "Đã khóa mục tiêu! Xác nhận quỹ đạo.",
            "Mở rộng": "Mở rộng vùng quét",
            "Đã bắt kịp": "Mục tiêu đã bị tiêu diệt!",
            "Phát hiện B-52": "Phát hiện mục tiêu",
            "Lùi lại": "Đang chuyển hướng (Backtrack)",
            "Chưa tìm thấy": "Tín hiệu bị nhiễu, đang tiếp tục...",
            "Hoàn thành": "Nhiệm vụ hoàn tất."
        }
        for k, v in action_map.items():
            if k in desc:
                desc = desc.replace(k, v)
        
        y_offset += 35
        y_offset = self.draw_text_wrapped(self.screen, desc, self.COLOR_TEXT_DARK, (px, y_offset, 800, 300), self.font_body)
        
        # Khu vực Bảng điều khiển thanh cuộn tiến độ thuật toán (Progress Tracker)
        ctrl_y = 900
        self.draw_dashed_line(self.screen, self.COLOR_TEXT_DARK, (px, ctrl_y), (1900, ctrl_y), 2, 15)
        
        step_surf = self.font_body.render(f"Bước: {current_step} / {max(0, total_steps - 1)}", True, self.COLOR_TEXT_DARK)
        self.screen.blit(step_surf, (px, ctrl_y + 15))

    def draw_frame(self, state, env_grid, current_step, total_steps, fixed_b52=None, fixed_sams=None, is_phase_2=False, history=None):
        """
        Hàm bao đóng (Wrapper) thực thi toàn bộ luồng kết xuất khung hình đồ họa.
        Xóa màn hình, vẽ bản đồ chiến thuật và áp đặt giao diện HUD lên trên cùng.
        """
        self.screen.fill(self.COLOR_RADAR_BG, (0, 0, 1080, 1080))
        self.draw_grid_and_state(state, env_grid, current_step, total_steps, fixed_b52, fixed_sams, is_phase_2, history)
        self.draw_hud(state, current_step, total_steps)

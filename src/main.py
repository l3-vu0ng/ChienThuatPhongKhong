import sys
import pygame
import os
import ctypes
import random
from entities.environment import Environment
from entities.sam2 import SAM2
from entities.b52 import B52
from ui.renderer import UIRenderer, Particle
from ui.widgets import Button, ComboBox

# Tích hợp các module thuật toán cốt lõi
from algorithms.uninformed import BFS, DFS, IDS
from algorithms.informed import GreedySearch, AStar, IDAStar
from algorithms.local_search import SimpleHillClimbing, StochasticHillClimbing, LocalBeamSearch
from algorithms.complex_env import AndOrSearch, NoObservationSearch, PartiallyObservableSearch
from algorithms.csp import BacktrackingCSP, ForwardCheckingCSP, MinConflictsCSP
from algorithms.adversarial import Minimax, AlphaBeta, Expectimax

# Từ điển Hệ thống: Ánh xạ danh mục (Category) với các Thuật toán tìm kiếm (Algorithms) cụ thể
ALGORITHMS = {
    "Uninformed Search": ["BFS", "DFS", "IDS"],
    "Informed Search": ["Greedy Search", "A*", "IDA*"],
    "Local Search": ["Simple Hill Climbing", "Stochastic Hill Climbing", "Local Beam Search"],
    "Complex Environment": ["AND-OR Search", "No Observation", "Partially Observable"],
    "Constraint Satisfaction (CSP)": ["Backtracking CSP", "Forward Checking CSP", "Min-Conflicts CSP"],
    "Adversarial Search": ["Minimax", "Alpha-Beta Pruning", "Expectimax"]
}

import random

def run_simulation(algo_name):
    env = Environment()
    start_pos = (15, 15) # Điểm đặt bệ phóng SAM-2 (Trung tâm lưới tọa độ)
    target_pos = (random.randint(0, 29), random.randint(0, 29)) # Vị trí B-52 xuất hiện ngẫu nhiên
    while target_pos == start_pos:
        target_pos = (random.randint(0, 29), random.randint(0, 29))
    avoid_pos = [start_pos, target_pos]
    if "CSP" in algo_name or "Conflicts" in algo_name or "Forward" in algo_name:
        avoid_pos.extend([(5, 29), (15, 29), (25, 29)])
        
    # Yêu cầu Environment sinh tự động 40 đám mây và 60 vùng bão
    env.generate_terrains(40, 60, avoid_positions=avoid_pos)
        
    # Lịch sử (Trajectory) lưu lại từng bước duyệt của đồ thị để render UI theo từng frame
    history = []
    fixed_b52 = None
    fixed_sams = None
    
    if algo_name == "BFS":
        history = BFS().run(env, start_pos, target_pos)
        fixed_b52 = target_pos
    elif algo_name == "DFS":
        history = DFS().run(env, start_pos, target_pos)
        fixed_b52 = target_pos
    elif algo_name == "IDS":
        history = IDS().run(env, start_pos, target_pos)
        fixed_b52 = target_pos
    elif algo_name == "Greedy Search":
        history = GreedySearch().run(env, start_pos, target_pos)
        fixed_b52 = target_pos
    elif algo_name == "A*":
        history = AStar().run(env, start_pos, target_pos)
        fixed_b52 = target_pos
    elif algo_name == "IDA*":
        history = IDAStar().run(env, start_pos, target_pos)
        fixed_b52 = target_pos
    elif algo_name == "Simple Hill Climbing":
        history = SimpleHillClimbing().run(env, start_pos, target_pos)
        fixed_b52 = target_pos
    elif algo_name == "Stochastic Hill Climbing":
        history = StochasticHillClimbing().run(env, start_pos, target_pos)
        fixed_b52 = target_pos
    elif algo_name == "Local Beam Search":
        history = LocalBeamSearch(k=3).run(env, start_pos, target_pos)
        fixed_b52 = target_pos
    elif algo_name == "AND-OR Search":
        history = AndOrSearch().run(env, start_pos, target_pos)
        fixed_b52 = target_pos
    elif algo_name == "No Observation":
        belief_states = []
        while len(belief_states) < 3:
            rx, ry = random.randint(0, 29), random.randint(0, 29)
            if (rx, ry) not in belief_states and env.grid[ry][rx] == 0:
                belief_states.append((rx, ry))
        history = NoObservationSearch().run_no_observation(env, start_pos, belief_states, target_pos)
        fixed_b52 = target_pos
    elif algo_name == "Partially Observable":
        if "fixed_beliefs" in locals():
            belief_states = fixed_beliefs
        else:
            belief_states = [target_pos]
            while len(belief_states) < 3:
                rx, ry = random.randint(0, 29), random.randint(0, 29)
                if (rx, ry) not in belief_states and env.grid[ry][rx] == 0:
                    belief_states.append((rx, ry))
            random.shuffle(belief_states)
            
        history = PartiallyObservableSearch().run_partial_observation(env, start_pos, belief_states, target_pos)
        fixed_b52 = target_pos
    elif algo_name in ["Backtracking CSP", "Forward Checking CSP", "Min-Conflicts CSP"]:
        if "sam_list" not in locals() or "b52_list" not in locals():
            sam_list = [(5, 29), (15, 29), (25, 29)]
            b52_list = []
            while len(b52_list) < 3:
                rx, ry = random.randint(0, 29), random.randint(0, 15)
                if (rx, ry) not in b52_list and env.grid[ry][rx] == 0:
                    b52_list.append((rx, ry))
        
        if algo_name == "Backtracking CSP":
            history = BacktrackingCSP().run_csp(env, sam_list, b52_list)
        elif algo_name == "Forward Checking CSP":
            history = ForwardCheckingCSP().run_csp(env, sam_list, b52_list)
        elif algo_name == "Min-Conflicts CSP":
            history = MinConflictsCSP().run_csp(env, sam_list, b52_list)
            
        fixed_b52 = b52_list
        fixed_sams = sam_list
    elif algo_name == "Minimax":
        history = Minimax().run_adversarial(env, start_pos, target_pos)
    elif algo_name == "Alpha-Beta Pruning":
        history = AlphaBeta().run_adversarial(env, start_pos, target_pos)
    elif algo_name == "Expectimax":
        history = Expectimax().run_adversarial(env, start_pos, target_pos)
        
    return history, fixed_b52, fixed_sams, env.grid

def main():
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass
    pygame.init()
    try:
        from audio import AudioManager
        audio_manager = AudioManager()
    except ImportError:
        audio_manager = None
    renderer = UIRenderer(width=1920, height=1080, grid_size=30)
    screen = renderer.screen
    screen = renderer.screen
    # Nạp Texture hình nền giao diện (Mô phỏng bàn chỉ huy quân sự)
    try:
        bg_image = pygame.image.load(os.path.join("assets", "pictures", "bg.jpg"))
        bg_image = pygame.transform.scale(bg_image, (1920, 1080))
    except:
        bg_image = pygame.Surface((1920, 1080))
        bg_image.fill((20, 20, 20))
        
    # Khởi tạo Cỗ máy trạng thái (Finite State Machine) quản lý bộ chuyển cảnh UI
    STATE_MENU = 0
    STATE_SIMULATION = 1
    STATE_CREDITS = 2
    STATE_OPTIONS = 3
    current_state = STATE_MENU
    
    # Trình diễn: Nút tương tác cho Màn hình Chính (Main Menu)
    btn_play = Button(1350, 650, 400, 80, "PLAY", renderer.font_hero, None, (200, 200, 200), (255, 255, 255), "right")
    btn_options = Button(1350, 750, 400, 80, "OPTIONS", renderer.font_hero, None, (200, 200, 200), (255, 255, 255), "right")
    btn_credits = Button(1350, 850, 400, 80, "CREDITS", renderer.font_hero, None, (200, 200, 200), (255, 255, 255), "right")
    btn_exit = Button(1350, 950, 400, 80, "EXIT", renderer.font_hero, None, (200, 200, 200), (255, 50, 50), "right")
    
    # Trình diễn: Nút tương tác cho Màn hình Cài đặt (Options)
    btn_toggle_vfx = Button(1350, 650, 400, 80, "VFX: ON", renderer.font_hero, None, (200, 200, 200), (255, 255, 255), "right")
    btn_toggle_sfx = Button(1350, 750, 400, 80, "SFX: ON", renderer.font_hero, None, (200, 200, 200), (255, 255, 255), "right")
    btn_options_back = Button(1350, 850, 400, 80, "RETURN", renderer.font_hero, None, (200, 200, 200), (255, 255, 255), "right")
    
    # Cờ trạng thái Audio (Visual/Sound Effects Flags)
    vfx_enabled = True
    sfx_enabled = True
    
    # Trình diễn: Nút điều hướng Quay lại dùng chung cho các Modal/Sub-menu
    btn_back = Button(1450, 960, 400, 80, "RETURN", renderer.font_hero, None, (200, 200, 200), (255, 255, 255), "right")
    
    # Bảng điều khiển (Control Panel) trên màn hình Mô phỏng Radar
    group_options = list(ALGORITHMS.keys())
    combo_group = ComboBox(1100, 60, 800, 60, group_options, renderer.font_body, (235, 231, 217), (47, 79, 79))
    combo_algo = ComboBox(1100, 150, 650, 60, ALGORITHMS[group_options[0]], renderer.font_body, (235, 231, 217), (47, 79, 79))
    btn_run = Button(1770, 150, 130, 60, "RUN", renderer.font_body, None, (47, 79, 79), (255, 51, 51), shadow=False, border=True)
    
    # Các nút bấm quản lý chu trình thời gian của thuật toán (Time-travel controls)
    btn_prev = Button(1100, 990, 110, 60, "<", renderer.font_body, None, (47, 79, 79), (255, 51, 51), shadow=False, border=True)
    btn_auto = Button(1230, 990, 120, 60, "AUTO", renderer.font_body, None, (47, 79, 79), (255, 51, 51), shadow=False, border=True)
    btn_next = Button(1370, 990, 110, 60, ">", renderer.font_body, None, (47, 79, 79), (255, 51, 51), shadow=False, border=True)
    btn_skip = Button(1500, 990, 110, 60, ">>", renderer.font_body, None, (47, 79, 79), (255, 51, 51), shadow=False, border=True)
    btn_fire = Button(1630, 990, 130, 60, "FIRE", renderer.font_body, None, (255, 51, 51), (200, 0, 0), shadow=False, border=True)
    btn_sim_menu = Button(1780, 990, 120, 60, "MENU", renderer.font_body, None, (47, 79, 79), (255, 51, 51), shadow=False, border=True)
    
    # Trạng thái luồng mô phỏng (Simulation Context)
    history = []
    fixed_b52 = None
    fixed_sams = None
    current_env_grid = [[0 for _ in range(30)] for _ in range(30)]
    current_step = 0
    total_steps = 0
    
    # Trạng thái điều hướng rảnh tay (Auto-Play Controller)
    is_auto_playing = False
    last_auto_step_time = 0
    auto_delay = 500  # ms
    
    # Máy trạng thái cho Giai đoạn Đánh chặn (Phase 2: Bắn đạn thật)
    is_phase_2 = False
    anim_progress = 0.0
    particles = []
    has_played_explosion = False
    
    running = True
    while running:
        # ---------------- VÒNG LẶP RENDER (RENDER PIPELINE) ----------------
        if current_state == STATE_MENU:
            screen.blit(bg_image, (0, 0))
            
            btn_play.draw(screen)
            btn_options.draw(screen)
            btn_credits.draw(screen)
            btn_exit.draw(screen)
            
        elif current_state == STATE_OPTIONS:
            screen.blit(bg_image, (0, 0))
            
            # Áp dụng Overlay để làm tối hình nền (Dimming Effect)
            overlay = pygame.Surface((1920, 1080))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            btn_toggle_vfx.draw(screen)
            btn_toggle_sfx.draw(screen)
            btn_options_back.draw(screen)
            
        elif current_state == STATE_CREDITS:
            screen.blit(bg_image, (0, 0))
            
            # Lớp phủ (Dim) tối hơn cho màn Credits để nổi bật văn bản
            overlay = pygame.Surface((1920, 1080))
            overlay.set_alpha(220)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Kết xuất nội dung vinh danh đội ngũ phát triển (Rolling Credits)
            cred_title = renderer.font_hero.render("CREDITS", True, (255, 255, 255))
            screen.blit(cred_title, cred_title.get_rect(center=(960, 90)))
            
            lines = [
                "BÁO CÁO MÔN HỌC: TRÍ TUỆ NHÂN TẠO",
                "ĐỀ TÀI: TRÒ CHƠI CHIẾN THUẬT PHÒNG KHÔNG",
                "GVHD: TS. Phan Thị Huyền Trang",
                "",
                "Lấy bối cảnh chiến dịch 'Điện Biên Phủ trên không' năm 1972.",
                "Trò chơi này mô phỏng cuộc đối đầu giữa siêu pháo đài bay B-52 và",
                "hệ thống phòng không SAM-2, vận dụng AI và các thuật toán tìm kiếm.",
                "",
                "Nhóm sinh viên thực hiện:",
                "1. Võ Lê Vương - 24110391",
                "2. Đoàn Thanh Liêm - 24110270",
                "3. Lê Trung Đông - 24110201"
            ]
            y_off = 250
            for line in lines:
                surf = renderer.font_credits.render(line, True, (255, 255, 255))
                screen.blit(surf, surf.get_rect(center=(960, y_off)))
                y_off += 50
                
            btn_back.draw(screen)
            
        elif current_state == STATE_SIMULATION:
            if total_steps > 0:
                # Cập nhật khung hình tự động theo chu kỳ đếm thời gian (Delta time tick)
                if is_auto_playing:
                    current_time = pygame.time.get_ticks()
                    if current_time - last_auto_step_time >= auto_delay:
                        if current_step < total_steps - 1:
                            current_step += 1
                            last_auto_step_time = current_time
                        else:
                            is_auto_playing = False
                            btn_auto.text = "AUTO"
                            
                algo_n = combo_algo.get_selected()
                is_adversarial = any(adv in algo_n for adv in ["Minimax", "Alpha-Beta", "Expectimax"])
                
                if is_adversarial and total_steps > 0:
                    is_phase_2 = True
                
                renderer.draw_frame(history[current_step], current_env_grid, current_step, total_steps, fixed_b52, fixed_sams, is_phase_2, history)
                
                if is_phase_2 and not is_adversarial:
                    import ast
                    algo_n = combo_algo.get_selected()
                    final_state = history[-1]
                    
                    paths = []
                    if "Paths" in final_state.hud_metrics:
                        try:
                            paths = ast.literal_eval(final_state.hud_metrics["Paths"])
                        except:
                            paths = []
                    else:
                        paths = [final_state.current_path] if final_state.current_path else []
                        
                    # Ở Giai đoạn 2, chúng ta vẽ chuyển động của Tên lửa trượt dọc theo quỹ đạo đã tính
                    anim_progress += 0.015
                    if anim_progress > 1.0:
                        anim_progress = 1.0
                        
                    for p in paths:
                        if not p: continue
                        total_nodes = len(p)
                        if total_nodes == 1:
                            renderer.draw_sam2(p[0][0], p[0][1])
                            continue
                            
                        # Phép nội suy tuyến tính (Linear Interpolation - LERP) giữa 2 tọa độ lưới
                        # để vẽ vector tên lửa bay mượt mà ở các khung hình phụ.
                        idx = min(int(anim_progress * (total_nodes - 1)), total_nodes - 2)
                        sub_prog = (anim_progress * (total_nodes - 1)) - idx
                        if anim_progress == 1.0:
                            idx = total_nodes - 2
                            sub_prog = 1.0
                            
                        p1 = p[idx]
                        p2 = p[idx+1]
                        
                        dx = p2[0] - p1[0]
                        dy = p2[1] - p1[1]
                        
                        cx = p1[0] + dx * sub_prog
                        cy = p1[1] + dy * sub_prog
                        
                        renderer.draw_sam2(cx, cy, dx, dy)
                        
                        # Sinh hệ thống Hạt (Particle System) tạo hiệu ứng đuôi lửa phản lực
                        if anim_progress < 1.0:
                            px = cx * renderer.cell_size + renderer.cell_size//2
                            py = cy * renderer.cell_size + renderer.cell_size//2
                            if vfx_enabled:
                                particles.append(Particle(px - dx*5, py - dy*5, (255, 100, 0), 1.5, 4, 20))
                        elif anim_progress == 1.0 and final_state.hud_metrics.get("Status", "Success") == "Success":
                            hit_target = False
                            if isinstance(fixed_b52, list):
                                hit_target = p[-1] in fixed_b52
                            elif p[-1] == fixed_b52:
                                hit_target = True
                            
                            if hit_target and audio_manager and sfx_enabled and not has_played_explosion:
                                audio_manager.play_explosion()
                                has_played_explosion = True
                                
                            if hit_target and vfx_enabled:
                                if random.random() < 0.3:
                                    px = p[-1][0] * renderer.cell_size + renderer.cell_size//2
                                    py = p[-1][1] * renderer.cell_size + renderer.cell_size//2
                                    particles.append(Particle(px + random.randint(-20,20), py + random.randint(-20,20), (255, random.randint(50,200), 0), 2, random.randint(10, 20), 30))
                                
                    # Vòng lặp dọn dẹp Hạt: Loại bỏ những hạt đã tắt (life <= 0)
                    if vfx_enabled:
                        for part in particles:
                            part.update()
                            part.draw(screen)
                        particles = [pt for pt in particles if pt.life > 0]
                    else:
                        particles.clear()
            else:
                # Fallback: Trạng thái chưa chạy thuật toán (Màn hình chờ Idle)
                from collections import namedtuple
                DummyState = namedtuple('State', ['explored', 'frontier', 'current_path', 'hud_metrics', 'action_description'])
                dummy_state = DummyState(explored=[], frontier=[], current_path=[], hud_metrics={}, action_description="")
                
                # Reset bộ đệm màn hình (Buffer Clear) để vẽ đồ họa mới
                pygame.draw.rect(screen, renderer.COLOR_RADAR_BG, (0, 0, 1080, 1080))
                renderer.draw_grid_and_state(dummy_state, current_env_grid, None, None)
                pygame.draw.rect(screen, renderer.COLOR_HUD_BG, (1080, 0, 840, 1080))
                pygame.draw.line(screen, renderer.COLOR_TEXT_DARK, (1100, 240), (1900, 240), 2)
                
                hint_surf = renderer.font_body.render("Select algorithm and press RUN", True, renderer.COLOR_TEXT_DARK)
                screen.blit(hint_surf, (1100, 300))
            
            # Render các thành phần UI nổi (Dropdown Box, Nút bấm)
            # Áp dụng nguyên lý Z-Index: ComboBox thuật toán phải được vẽ đè lên ComboBox nhóm
            combo_algo.draw_main_box(screen)
            btn_run.draw(screen)
            btn_sim_menu.draw(screen)
            
            if total_steps > 0:
                btn_prev.draw(screen)
                btn_auto.draw(screen)
                btn_next.draw(screen)
                btn_skip.draw(screen)
                if current_step == total_steps - 1 and not is_phase_2:
                    algo_n = combo_algo.get_selected()
                    if algo_n not in ["Minimax", "Alpha-Beta Pruning", "Expectimax"]:
                        btn_fire.draw(screen)
                
            combo_group.draw_main_box(screen)
            
            combo_algo.draw_dropdown(screen)
            combo_group.draw_dropdown(screen)
            
        pygame.display.flip()
        
        # ---------------- XỬ LÝ SỰ KIỆN (EVENT LOOP) ----------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
            if current_state == STATE_MENU:
                if btn_play.handle_event(event):
                    current_state = STATE_SIMULATION
                if btn_options.handle_event(event):
                    current_state = STATE_OPTIONS
                if btn_credits.handle_event(event):
                    current_state = STATE_CREDITS
                if btn_exit.handle_event(event):
                    running = False
            
            elif current_state == STATE_OPTIONS:
                if btn_toggle_vfx.handle_event(event):
                    vfx_enabled = not vfx_enabled
                    btn_toggle_vfx.text = "VFX: ON" if vfx_enabled else "VFX: OFF"
                if btn_toggle_sfx.handle_event(event):
                    sfx_enabled = not sfx_enabled
                    btn_toggle_sfx.text = "SFX: ON" if sfx_enabled else "SFX: OFF"
                if btn_options_back.handle_event(event):
                    current_state = STATE_MENU
            
            elif current_state == STATE_CREDITS:
                if btn_back.handle_event(event):
                    current_state = STATE_MENU

            
            elif current_state == STATE_SIMULATION:
                # Phân tầng lắng nghe sự kiện: ComboBox cần ưu tiên chặn sự kiện Click nếu nó đang Dropdown
                if combo_group.handle_event(event):
                    # Trình kích hoạt (Trigger): Thay đổi danh mục cha -> Load lại danh sách thuật toán con
                    new_group = combo_group.get_selected()
                    combo_algo.update_options(ALGORITHMS[new_group])
                    total_steps = 0
                    is_phase_2 = False
                    is_auto_playing = False
                
                if not combo_group.is_expanded:
                    if combo_algo.handle_event(event):
                        total_steps = 0
                        is_phase_2 = False
                        is_auto_playing = False
                    
                if not combo_group.is_expanded and not combo_algo.is_expanded:
                    if btn_sim_menu.handle_event(event):
                        current_state = STATE_MENU
                        total_steps = 0
                        is_auto_playing = False
                        is_phase_2 = False
                        anim_progress = 0.0
                        particles = []
                        has_played_explosion = False
                        if audio_manager and sfx_enabled: audio_manager.play_ping()
                        
                    if btn_run.handle_event(event):
                        algo_name = combo_algo.get_selected()
                        history, fixed_b52, fixed_sams, current_env_grid = run_simulation(algo_name)
                        current_step = 0
                        total_steps = len(history)
                        is_auto_playing = False
                        btn_auto.text = "AUTO"
                        is_phase_2 = False
                        anim_progress = 0.0
                        particles = []
                        has_played_explosion = False
                        
                    if total_steps > 0 and (not is_phase_2 or is_adversarial):
                        if btn_prev.handle_event(event):
                            if current_step > 0:
                                current_step -= 1
                                if audio_manager and sfx_enabled: audio_manager.play_ping()
                            is_auto_playing = False
                            btn_auto.text = "AUTO"
                            
                        if btn_next.handle_event(event):
                            if current_step < total_steps - 1:
                                current_step += 1
                                if audio_manager and sfx_enabled: audio_manager.play_ping()
                            is_auto_playing = False
                            btn_auto.text = "AUTO"
                            
                        if btn_auto.handle_event(event):
                            if current_step < total_steps - 1:
                                is_auto_playing = not is_auto_playing
                                btn_auto.text = "STOP" if is_auto_playing else "AUTO"
                                last_auto_step_time = pygame.time.get_ticks()
                                
                        if btn_skip.handle_event(event):
                            current_step = total_steps - 1
                            is_auto_playing = False
                            btn_auto.text = "AUTO"
                            
                        if current_step == total_steps - 1:
                            if btn_fire.handle_event(event):
                                if not is_phase_2 and anim_progress == 0.0:
                                    is_phase_2 = True
                                    has_played_explosion = False
                                    if audio_manager and sfx_enabled: audio_manager.play_launch()
                
                # Cụm phím tắt (Hotkeys) dùng điều hướng timeline của Thuật toán bằng bàn phím
                if event.type == pygame.KEYDOWN and total_steps > 0 and (not is_phase_2 or is_adversarial):
                    if event.key == pygame.K_RIGHT:
                        if current_step < total_steps - 1:
                            current_step += 1
                            if audio_manager and sfx_enabled: audio_manager.play_ping()
                        is_auto_playing = False
                        btn_auto.text = "AUTO"
                    elif event.key == pygame.K_LEFT:
                        if current_step > 0:
                            current_step -= 1
                            if audio_manager and sfx_enabled: audio_manager.play_ping()
                        is_auto_playing = False
                        btn_auto.text = "AUTO"

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

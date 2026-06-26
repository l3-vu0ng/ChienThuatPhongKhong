# ui/widgets.py
import pygame

class Button:
    """
    Lớp Button đại diện cho một nút bấm tương tác trên giao diện đồ họa.
    Quản lý các trạng thái hiển thị (bình thường, di chuột qua), hiệu ứng đổ bóng
    và xử lý sự kiện click chuột từ người dùng.
    """
    def __init__(self, x, y, width, height, text, font, bg_color, text_color, hover_color, align="center", shadow=True, border=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.align = align
        self.shadow = shadow
        self.border = border
        self.is_hovered = False

    def draw(self, surface):
        """
        Vẽ nút bấm lên một bề mặt (surface) của pygame.
        Tự động điều chỉnh màu sắc và hiệu ứng dựa trên trạng thái `is_hovered`.
        """
        if self.bg_color is not None:
            color = self.hover_color if self.is_hovered else self.bg_color
            pygame.draw.rect(surface, color, self.rect, border_radius=8)
            # Vẽ viền nút bấm để tạo cảm giác nổi
            pygame.draw.rect(surface, (100, 100, 100), self.rect, width=2, border_radius=8) 
            current_text_color = self.text_color
        else:
            current_text_color = self.hover_color if self.is_hovered else self.text_color
            if self.border:
                pygame.draw.rect(surface, current_text_color, self.rect, width=2, border_radius=4)
            
        text_surf = self.font.render(self.text, True, current_text_color)
        
        # Xử lý căn lề và hiệu ứng đổ bóng cho văn bản bên trong nút
        if self.bg_color is None:
            if self.shadow:
                shadow_surf = self.font.render(self.text, True, (0, 0, 0))
                if self.align == "left":
                    shadow_rect = shadow_surf.get_rect(midleft=(self.rect.left + 4, self.rect.centery + 4))
                    text_rect = text_surf.get_rect(midleft=(self.rect.left, self.rect.centery))
                elif self.align == "right":
                    shadow_rect = shadow_surf.get_rect(midright=(self.rect.right - 4, self.rect.centery + 4))
                    text_rect = text_surf.get_rect(midright=(self.rect.right - 8, self.rect.centery))
                else:
                    shadow_rect = shadow_surf.get_rect(center=(self.rect.centerx + 4, self.rect.centery + 4))
                    text_rect = text_surf.get_rect(center=self.rect.center)
                surface.blit(shadow_surf, shadow_rect)
            else:
                if self.align == "left":
                    text_rect = text_surf.get_rect(midleft=(self.rect.left, self.rect.centery))
                elif self.align == "right":
                    text_rect = text_surf.get_rect(midright=(self.rect.right, self.rect.centery))
                else:
                    text_rect = text_surf.get_rect(center=self.rect.center)
        else:
            if self.align == "left":
                text_rect = text_surf.get_rect(midleft=(self.rect.left + 10, self.rect.centery))
            elif self.align == "right":
                text_rect = text_surf.get_rect(midright=(self.rect.right - 10, self.rect.centery))
            else:
                text_rect = text_surf.get_rect(center=self.rect.center)
                
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        """
        Xử lý các sự kiện chuột (di chuyển, click) tác động lên nút bấm.
        Trả về True nếu nút bị click, ngược lại trả về False.
        """
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        return False

class ComboBox:
    """
    Lớp ComboBox đại diện cho một danh sách thả xuống (dropdown list).
    Cho phép người dùng chọn một giá trị duy nhất từ một tập hợp các tùy chọn có sẵn.
    """
    def __init__(self, x, y, width, height, options, font, bg_color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_index = 0
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.is_expanded = False
        self.hovered_index = -1

    def get_selected(self):
        """Trích xuất giá trị văn bản của tùy chọn đang được chọn hiện tại."""
        return self.options[self.selected_index] if self.options else ""

    def update_options(self, new_options):
        """Đồng bộ lại danh sách tùy chọn mới và reset trạng thái."""
        self.options = new_options
        self.selected_index = 0
        self.is_expanded = False

    def draw_main_box(self, surface):
        """Vẽ khung chính của ComboBox hiển thị tùy chọn hiện tại và biểu tượng mũi tên."""
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=4)
        pygame.draw.rect(surface, (47, 79, 79), self.rect, width=2, border_radius=4)
        
        text = self.get_selected()
        text_surf = self.font.render(text, True, self.text_color)
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + (self.rect.height - text_surf.get_height()) // 2))
        
        # Vẽ đa giác mô phỏng mũi tên chỉ xuống/chỉ lên tùy theo trạng thái expanded
        arrow_x = self.rect.right - 20
        arrow_y = self.rect.centery
        if self.is_expanded:
            pygame.draw.polygon(surface, self.text_color, [(arrow_x-5, arrow_y+3), (arrow_x+5, arrow_y+3), (arrow_x, arrow_y-3)])
        else:
            pygame.draw.polygon(surface, self.text_color, [(arrow_x-5, arrow_y-3), (arrow_x+5, arrow_y-3), (arrow_x, arrow_y+3)])

    def draw_dropdown(self, surface):
        """Vẽ danh sách các tùy chọn xổ xuống khi ComboBox được kích hoạt."""
        if not self.is_expanded:
            return
            
        drop_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, len(self.options) * self.rect.height)
        pygame.draw.rect(surface, self.bg_color, drop_rect)
        pygame.draw.rect(surface, (47, 79, 79), drop_rect, width=2)
        
        for i, option in enumerate(self.options):
            opt_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * self.rect.height, self.rect.width, self.rect.height)
            if i == self.hovered_index:
                pygame.draw.rect(surface, (210, 205, 190), opt_rect)
                
            text_surf = self.font.render(option, True, self.text_color)
            surface.blit(text_surf, (opt_rect.x + 10, opt_rect.y + (opt_rect.height - text_surf.get_height()) // 2))

    def handle_event(self, event):
        """
        Lắng nghe và xử lý sự kiện tương tác của người dùng trên ComboBox.
        Quản lý thao tác đóng/mở danh sách và cập nhật chỉ mục lựa chọn (selected_index).
        """
        changed = False
        if event.type == pygame.MOUSEMOTION:
            if self.is_expanded:
                drop_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, len(self.options) * self.rect.height)
                if drop_rect.collidepoint(event.pos):
                    self.hovered_index = (event.pos[1] - self.rect.bottom) // self.rect.height
                else:
                    self.hovered_index = -1
                    
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_expanded:
                drop_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, len(self.options) * self.rect.height)
                if drop_rect.collidepoint(event.pos):
                    idx = (event.pos[1] - self.rect.bottom) // self.rect.height
                    if 0 <= idx < len(self.options):
                        self.selected_index = idx
                        changed = True
                self.is_expanded = False
            else:
                if self.rect.collidepoint(event.pos):
                    self.is_expanded = True
                else:
                    self.is_expanded = False
                    
        return changed

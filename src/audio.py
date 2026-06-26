import pygame
import numpy as np

class AudioManager:
    """
    Hệ thống quản lý Âm thanh (Audio Manager).
    Sử dụng kỹ thuật tổng hợp âm thanh bằng toán học (Procedural Audio Synthesis) qua thư viện NumPy
    thay vì tải các file âm thanh rời rạc có sẵn. Điều này giúp tối ưu hóa dung lượng lưu trữ 
    và mô phỏng được các tín hiệu điện tử mang phong cách radar chiến thuật.
    """
    def __init__(self):
        try:
            # Khởi tạo bộ trộn âm thanh (mixer) của Pygame với tần số lấy mẫu chuẩn (44.1 kHz)
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
                
            # Tạo sẵn các buffer âm thanh vào bộ nhớ để giảm độ trễ khi phát
            self.ping_snd = self._generate_ping()
            self.launch_snd = self._generate_launch()
            self.explosion_snd = self._generate_explosion()
            self.enabled = True
        except Exception as e:
            print("Lỗi khởi tạo hệ thống âm thanh:", e)
            self.enabled = False

    def _generate_ping(self):
        """
        Tạo tín hiệu âm thanh 'Ping' của sóng Radar.
        Sử dụng sóng hình sin (Sine Wave) ở tần số 1000Hz (âm bổng) kết hợp với đường bao 
        suy giảm theo hàm số mũ (Exponential Decay) để mô phỏng sự dội lại của sóng điện từ.
        """
        sample_rate = 44100
        duration = 0.1
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Công thức: Sóng Sine x Khẩu độ suy giảm
        wave = 0.5 * np.sin(2 * np.pi * 1000 * t) * np.exp(-15 * t)
        
        sound = np.int16(wave * 32767)
        stereo_sound = np.column_stack((sound, sound))
        return pygame.sndarray.make_sound(stereo_sound)

    def _generate_launch(self):
        """
        Tạo hiệu ứng âm thanh tên lửa khai hỏa (Launch).
        Tổng hợp từ nhiễu trắng (White Noise) kết hợp với đường bao dập tắt để tạo ra âm thanh xé gió chói tai.
        """
        sample_rate = 44100
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Sinh ngẫu nhiên biên độ nhiễu trắng
        noise = np.random.uniform(-1, 1, len(t))
        envelope = np.exp(-2 * t)
        
        sound = np.int16(noise * envelope * 15000)
        stereo_sound = np.column_stack((sound, sound))
        return pygame.sndarray.make_sound(stereo_sound)

    def _generate_explosion(self):
        """
        Tạo hiệu ứng âm thanh vụ nổ dội tiếng (Explosion).
        Sử dụng nhiễu trắng được làm mịn bằng bộ lọc trung bình động (Moving Average Filter) 
        nhằm triệt tiêu tần số cao, tạo cảm giác âm trầm uy lực của thuốc nổ.
        """
        sample_rate = 44100
        duration = 1.5
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        noise = np.random.uniform(-1, 1, len(t))
        
        # Áp dụng bộ lọc Low-pass cơ bản (Convolution Filter)
        window = 20
        noise = np.convolve(noise, np.ones(window)/window, mode='same')
        
        envelope = np.exp(-3 * t)
        sound = np.int16(noise * envelope * 32767)
        stereo_sound = np.column_stack((sound, sound))
        return pygame.sndarray.make_sound(stereo_sound)

    def play_ping(self):
        """Phát âm thanh Radar Ping."""
        if self.enabled: self.ping_snd.play()

    def play_launch(self):
        """Phát âm thanh Tên lửa khai hỏa."""
        if self.enabled: self.launch_snd.play()

    def play_explosion(self):
        """Phát âm thanh Mục tiêu bị tiêu diệt (Vụ nổ)."""
        if self.enabled: self.explosion_snd.play()

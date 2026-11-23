import math
import random
import sys
import pygame

# Inisialisasi Pygame
pygame.init()

# Konfigurasi Layar & Animasi
class Config:
    WIDTH = 1000
    HEIGHT = 750
    FPS = 60
    BG_COLOR = (8, 4, 4)  # Hitam kemerahan gelap
    
    # Variasi teks partikel & palet warna merah-oranye menyala
    HEART_WORDS = ["I LOVE YOU", "LOVE", "I ♥ YOU", "love you"]
    COLORS = [
        (255, 30, 30),
        (255, 65, 45),
        (255, 95, 60),
        (230, 20, 20),
        (255, 130, 80),
        (200, 15, 15),
    ]
    
    # Parameter pembentukan hati
    TOTAL_HEART_PARTICLES = 450
    TOTAL_FLOATING_PARTICLES = 140
    SCALE = 17.5

    @property
    def center(self):
        return (self.WIDTH / 2, self.HEIGHT / 2 - 20)

CFG = Config()

# Setup layar
screen = pygame.display.set_mode((CFG.WIDTH, CFG.HEIGHT))
pygame.display.set_caption("Heart Particle Animation")
clock = pygame.time.Clock()

# Font untuk partikel & teks utama
particle_fonts = {
    size: pygame.font.SysFont("consolas", size, bold=True)
    for size in range(10, 20)
}
main_font = pygame.font.SysFont("georgia", 46, bold=True)


def heart_parametric(t: float) -> tuple[float, float]:
    """Menghitung koordinat kurva hati parametrik."""
    x = 16.0 * (math.sin(t) ** 3)
    y = (
        13.0 * math.cos(t)
        - 5.0 * math.cos(2 * t)
        - 2.0 * math.cos(3 * t)
        - math.cos(4 * t)
    )
    return x, y


def heart_to_screen(hx: float, hy: float, scale: float = CFG.SCALE) -> tuple[float, float]:
    """Mengonversi koordinat matematika hati ke koordinat piksel layar."""
    cx, cy = CFG.center
    sx = cx + hx * scale
    sy = cy - hy * scale  # Sumbu Y layar terbalik
    return sx, sy


class HeartParticle:
    """Partikel teks yang membentuk struktur utama hati."""
    def __init__(self, target_x: float, target_y: float, order: int):
        self.tx = target_x
        self.ty = target_y
        # Posisi awal acak menyebar dari tengah
        self.x = CFG.center[0] + random.uniform(-250, 250)
        self.y = CFG.center[1] + random.uniform(-250, 250)
        self.order = order
        self.word = random.choice(CFG.HEART_WORDS)
        self.color = random.choice(CFG.COLORS)
        self.size = random.randint(11, 17)
        self.flicker_offset = random.uniform(0, math.tau)
        self.alpha = 0
        self.active = False

    def update(self, frame: int, beat_scale: float):
        # Muncul secara bertahap sesuai urutan (efek menggambar hati)
        if frame >= self.order * 0.45:
            self.active = True

        if not self.active:
            return

        # Hitung target dengan efek denyut (heartbeat)
        cx, cy = CFG.center
        dx = (self.tx - cx) * beat_scale
        dy = (self.ty - cy) * beat_scale
        goal_x = cx + dx
        goal_y = cy + dy

        # Gerakan halus menuju posisi target (easing)
        self.x += (goal_x - self.x) * 0.08
        self.y += (goal_y - self.y) * 0.08

        # Efek kelap-kelip cahaya (flicker)
        flicker = math.sin(frame * 0.12 + self.flicker_offset)
        target_alpha = int(185 + 70 * flicker)
        self.alpha = min(255, max(60, self.alpha + (target_alpha - self.alpha) * 0.1))

    def draw(self, surface: pygame.Surface):
        if not self.active or self.alpha <= 5:
            return

        font = particle_fonts[self.size]
        # Efek glow tipis di belakang teks
        glow_surf = font.render(self.word, True, self.color)
        glow_surf.set_alpha(int(self.alpha * 0.35))
        rect = glow_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(glow_surf, (rect.x - 1, rect.y - 1))
        surface.blit(glow_surf, (rect.x + 1, rect.y + 1))

        # Teks utama partikel
        text_surf = font.render(self.word, True, self.color)
        text_surf.set_alpha(int(self.alpha))
        surface.blit(text_surf, rect)


class FloatingParticle:
    """Partikel teks kecil yang melayang acak di latar belakang."""
    def __init__(self):
        self.reset()
        self.y = random.uniform(0, CFG.HEIGHT)

    def reset(self):
        self.x = random.uniform(0, CFG.WIDTH)
        self.y = random.uniform(CFG.HEIGHT * 0.1, CFG.HEIGHT)
        self.vy = random.uniform(-0.6, -0.15)
        self.vx = random.uniform(-0.2, 0.2)
        self.word = random.choice(["love you", "I LOVE YOU", "love"])
        self.color = random.choice(CFG.COLORS)
        self.size = random.randint(10, 13)
        self.alpha = random.randint(40, 120)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.y < -20:
            self.reset()
            self.y = CFG.HEIGHT + 10

    def draw(self, surface: pygame.Surface):
        font = particle_fonts[self.size]
        text_surf = font.render(self.word, True, self.color)
        text_surf.set_alpha(self.alpha)
        surface.blit(text_surf, (int(self.x), int(self.y)))


def create_heart_particles() -> list[HeartParticle]:
    particles = []
    # Lapisan luar dan dalam agar bentuk hati tampak tebal dan penuh
    layers = [
        (1.0, 220),   # Garis tepi luar
        (0.85, 110),  # Lapisan tengah
        (0.68, 70),   # Lapisan dalam
        (0.45, 50),   # Inti hati
    ]
    order_counter = 0
    for layer_scale, count in layers:
        for i in range(count):
            t = (i / count) * math.tau
            hx, hy = heart_parametric(t)
            # Tambahkan sedikit variasi acak agar tidak terlalu kaku
            jitter_x = random.uniform(-0.6, 0.6)
            jitter_y = random.uniform(-0.6, 0.6)
            sx, sy = heart_to_screen(
                hx * layer_scale + jitter_x,
                hy * layer_scale + jitter_y
            )
            particles.append(HeartParticle(sx, sy, order_counter))
            order_counter += 1
    return particles


def draw_center_text(surface: pygame.Surface, frame: int):
    """Memunculkan tulisan 'I Love you' putih di tengah setelah hati terbentuk."""
    start_frame = 240  # Muncul setelah sekitar 4 detik
    if frame < start_frame:
        return

    progress = min(1.0, (frame - start_frame) / 60.0)
    alpha = int(255 * progress)

    text = "I Love you"
    # Efek cahaya lembut (glow) di sekitar teks putih
    glow = main_font.render(text, True, (255, 120, 120))
    glow.set_alpha(int(alpha * 0.45))
    glow_rect = glow.get_rect(center=(CFG.WIDTH // 2, CFG.HEIGHT // 2))
    for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        surface.blit(glow, (glow_rect.x + ox, glow_rect.y + oy))

    # Teks utama berwarna putih
    main_surf = main_font.render(text, True, (255, 255, 255))
    main_surf.set_alpha(alpha)
    surface.blit(main_surf, glow_rect)


def main():
    heart_particles = create_heart_particles()
    floating_particles = [FloatingParticle() for _ in range(CFG.TOTAL_FLOATING_PARTICLES)]
    frame = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        screen.fill(CFG.BG_COLOR)

        # Efek detak jantung halus (heartbeat)
        beat = 1.0 + 0.035 * math.sin(frame * 0.08)

        # Gambar partikel latar belakang
        for fp in floating_particles:
            fp.update()
            fp.draw(screen)

        # Gambar partikel pembentuk hati
        for hp in heart_particles:
            hp.update(frame, beat)
            hp.draw(screen)

        # Gambar teks tengah "I Love you"
        draw_center_text(screen, frame)

        pygame.display.flip()
        clock.tick(CFG.FPS)
        frame += 1

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
import math
import random
import pygame

# =====================================
# INISIALISASI
# =====================================

pygame.init()
pygame.mixer.init()

WIDTH = 900
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blue Love Music Animation")

clock = pygame.time.Clock()

# WARNA
BLACK = (0, 0, 0)
BLUE = (0, 150, 255)
WHITE = (255, 255, 255)
LIGHT_BLUE = (80, 200, 255)

# FONT
font = pygame.font.SysFont("Arial", 16, bold=True)
small_font = pygame.font.SysFont("Arial", 18)

# =====================================
# MEMUAT MUSIK
# =====================================

pygame.mixer.music.load("ssstik.io_1795228447060.mp3")

# =====================================
# LIRIK LAGU & WAKTU SESUAI VIDEO
# =====================================

lyrics = [
    (0.0, "Got nothing to hide no more"),
    (4.2, "I don't know where to start"),
    (8.0, "But to show you the shape of my heart"),
    (20.5, "I'm lookin' back on things i've done"),
    (25.8, "I never wanna play the same old part"),
    (30.5, "I'll keep you in the dark"),
    (34.5, "Now let me show you"),
    (37.0, "The shape of my heart"),
]

current_lyric_index = 0

# =====================================
# LOVE KECIL
# =====================================

small_hearts = []

for i in range(45):
  small_hearts.append({
      "x": random.randint(0, WIDTH),
      "y": random.randint(0, HEIGHT),
      "speed": random.uniform(0.5, 1.2),
      "size": random.randint(8, 16),
  })

# =====================================
# LOVE BESAR
# =====================================

big_hearts = []

positions = [WIDTH * 0.25, WIDTH * 0.50, WIDTH * 0.75]

position_index = 0


# =====================================
# GAMBAR LOVE
# =====================================
def draw_heart(x, y, size, color):
  points = []

  for i in range(100):
    t = i * 2 * math.pi / 100

    hx = 16 * math.sin(t) ** 3

    hy = (
        13 * math.cos(t)
        - 5 * math.cos(2 * t)
        - 2 * math.cos(3 * t)
        - math.cos(4 * t)
    )

    px = x + hx * size / 32
    py = y - hy * size / 32

    points.append((int(px), int(py)))

  pygame.draw.polygon(screen, color, points)


# =====================================
# TEKS DI DALAM LOVE
# =====================================
def draw_text_center(text, x, y):
  words = text.split()

  lines = []
  current_line = ""

  for word in words:
    test_line = (current_line + " " + word).strip()

    if font.size(test_line)[0] > 125:
      if current_line:
        lines.append(current_line)
      current_line = word
    else:
      current_line = test_line

  if current_line:
    lines.append(current_line)

  line_height = 20
  start_y = y - (len(lines) * line_height) / 2

  for i, line in enumerate(lines):
    text_surface = font.render(line, True, WHITE)
    text_rect = text_surface.get_rect(
        center=(int(x), int(start_y + i * line_height))
    )
    screen.blit(text_surface, text_rect)


# =====================================
# ANIMASI LOVE KECIL
# =====================================
def animate_small_hearts():
  for heart in small_hearts:
    heart["y"] -= heart["speed"]

    if heart["y"] < -30:
      heart["y"] = HEIGHT + 20
      heart["x"] = random.randint(0, WIDTH)

    draw_heart(heart["x"], heart["y"], heart["size"], BLUE)


# =====================================
# MEMBUAT LOVE BESAR
# =====================================
def create_big_heart(text):
  global position_index

  x = positions[position_index % len(positions)]
  position_index += 1

  big_hearts.append({
      "x": x,
      "y": HEIGHT + 120,
      "speed": 1.7,
      "size": 210,
      "text": text,
      "phase": random.random() * 6.28,
      "spawn_time": pygame.time.get_ticks(),  # Waktu saat love dibuat untuk efek ketik
  })


# =====================================
# ANIMASI LOVE BESAR
# =====================================
def animate_big_hearts():
  for heart in big_hearts[:]:
    heart["y"] -= heart["speed"]

    pulse = math.sin(pygame.time.get_ticks() / 180 + heart["phase"])
    size = int(heart["size"] + pulse * 5)

    draw_heart(heart["x"], heart["y"], size, BLUE)

    # Efek Ketik (Typewriter Effect)
    elapsed_ms = pygame.time.get_ticks() - heart["spawn_time"]
    # 1 karakter muncul setiap 50 milidetik (bisa diubah agar lebih cepat/lambat)
    chars_to_show = int(elapsed_ms / 50)
    displayed_text = heart["text"][:chars_to_show]

    # Tampilkan teks yang sudah difilter efek ketik
    draw_text_center(displayed_text, heart["x"], heart["y"] - 5)

    if heart["y"] < -280:
      big_hearts.remove(heart)


# =====================================
# TOMBOL
# =====================================
play_button = pygame.Rect(340, 520, 100, 40)
pause_button = pygame.Rect(460, 520, 100, 40)


def draw_button(rect, text):
  pygame.draw.rect(screen, BLUE, rect, border_radius=20)
  label = small_font.render(text, True, WHITE)
  screen.blit(label, label.get_rect(center=rect.center))


# =====================================
# PENGATURAN MUSIK
# =====================================
playing = False
paused = False

elapsed = 0
start_ticks = 0

# =====================================
# PROGRAM UTAMA
# =====================================
running = True

while running:
  clock.tick(60)
  screen.fill(BLACK)

  # EVENT
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

    if event.type == pygame.MOUSEBUTTONDOWN:
      # PLAY
      if play_button.collidepoint(event.pos):
        if not playing:
          pygame.mixer.music.play()
          elapsed = 0
          start_ticks = pygame.time.get_ticks()

          current_lyric_index = 0
          position_index = 0
          big_hearts.clear()

          playing = True
          paused = False

        elif paused:
          pygame.mixer.music.unpause()
          start_ticks = pygame.time.get_ticks()
          paused = False

      # PAUSE
      if pause_button.collidepoint(event.pos):
        if playing and not paused:
          elapsed += (pygame.time.get_ticks() - start_ticks) / 1000
          pygame.mixer.music.pause()
          paused = True

  # =====================================
  # WAKTU MUSIK
  # =====================================
  if playing and not paused:
    current_time = elapsed + (pygame.time.get_ticks() - start_ticks) / 1000
  else:
    current_time = elapsed

  # =====================================
  # LOVE KECIL
  # =====================================
  animate_small_hearts()

  # =====================================
  # MUNCULKAN LOVE BESAR SESUAI WAKTU LIRIK
  # =====================================
  if playing and not paused:
    if current_lyric_index < len(lyrics):
      target_time, text_content = lyrics[current_lyric_index]
      if current_time >= target_time:
        create_big_heart(text_content)
        current_lyric_index += 1

  # =====================================
  # GERAKAN LOVE BESAR
  # =====================================
  animate_big_hearts()

  # =====================================
  # JUDUL
  # =====================================
  title = small_font.render("LOVE MUSIC", True, LIGHT_BLUE)
  screen.blit(title, title.get_rect(center=(WIDTH // 2, 35)))

  # =====================================
  # TOMBOL
  # =====================================
  draw_button(play_button, "PLAY")
  draw_button(pause_button, "PAUSE")

  pygame.display.flip()

# =====================================
# KELUAR
# =====================================
pygame.mixer.music.stop()
pygame.quit()
import pygame
import sys
import colorsys
import random

pygame.init()
# pygame.mixer.init()  # Descomenta si vas a usar sonido

WIDTH, HEIGHT = 470, 680
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders - Barba Edition")

# enter = pygame.mixer.Sound('./LB_SpaceInvaders/assets/music/undertale-save.mp3')
# select = pygame.mixer.Sound('./LB_SpaceInvaders/assets/music/undertale-select-sound.mp3')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (142, 124, 0)

title_font = pygame.font.SysFont("Press Start 2P Regular", 30)
subtitle_font = pygame.font.SysFont("Press Start 2P Regular", 18)
menu_font = pygame.font.SysFont("Press Start 2P Regular", 25)
score_font = pygame.font.SysFont("Press Start 2P Regular", 12)
copy_font = pygame.font.SysFont("Press Start 2P Regular", 12)

menu_options = ["PLAY", "OPTIONS", "CREDITS"]
selected_index = 0
current_screen = "menu"

# Variables para opciones de sonido
music_muted = False
sfx_muted = False
options_menu = ["MUSIC: ON", "SFX: ON", "BACK"]
options_index = 0

def rainbow_color(phase):
    h = (phase % 360) / 360.0
    r, g, b = colorsys.hsv_to_rgb(h, 1, 1)
    return (int(r * 255), int(g * 255), int(b * 255))

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.speed = random.uniform(1, 3)
        self.size = random.randint(1, 3)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = random.randint(-HEIGHT, 0)
            self.x = random.randint(0, WIDTH)
            self.speed = random.uniform(1, 3)

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.size)

stars = [Star() for _ in range(100)]

color_phase = 0
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if current_screen == "menu":
                if event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(menu_options)
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    selected_option = menu_options[selected_index]
                    if selected_option == "CREDITS":
                        current_screen = "credits"
                    elif selected_option == "PLAY":
                        current_screen = "play"
                    elif selected_option == "OPTIONS":
                        current_screen = "options"

            elif current_screen == "credits":
                if event.key == pygame.K_ESCAPE:
                    current_screen = "menu"

            elif current_screen == "options":
                if event.key == pygame.K_DOWN:
                    options_index = (options_index + 1) % len(options_menu)
                elif event.key == pygame.K_UP:
                    options_index = (options_index - 1) % len(options_menu)
                elif event.key == pygame.K_RETURN:
                    if options_index == 0:
                        music_muted = not music_muted
                        options_menu[0] = "MUSIC: OFF" if music_muted else "MUSIC: ON"
                        # pygame.mixer.music.set_volume(0 if music_muted else 1)
                    elif options_index == 1:
                        sfx_muted = not sfx_muted
                        options_menu[1] = "SFX: OFF" if sfx_muted else "SFX: ON"
                        # Aquí podrías mutear los sonidos tipo: select.set_volume(0)
                    elif options_index == 2:
                        current_screen = "menu"
                elif event.key == pygame.K_ESCAPE:
                    current_screen = "menu"

    screen.fill(BLACK)

    for star in stars:
        star.update()
        star.draw(screen)

    if current_screen == "menu":
        title_text = title_font.render("SPACE INVADERS", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 150))

        copy_text = copy_font.render("Barbi Industries© - 2025", True, WHITE)
        screen.blit(copy_text, (WIDTH // 2 - copy_text.get_width() // 2, 650))

        current_color = rainbow_color(color_phase)
        color_phase += 2
        subtitle_text = subtitle_font.render("BARBA EDITION", True, current_color)
        screen.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, 200))

        score_text = score_font.render("HI - SCORE: XXXXXX", True, WHITE)
        screen.blit(score_text, (20, 20))

        for i, option in enumerate(menu_options):
            color = YELLOW if i == selected_index else WHITE
            text = menu_font.render(option, True, color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 250 + i * 80))

    elif current_screen == "credits":
        title = title_font.render("CREDITOS", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        lines = [
            "Creado por: Lucas Barba",
            "Musica: Undertale OST",
            "Colegio: Instituto Huergo",
            "",
            "'ESC' para regresar"
        ]

        for i, line in enumerate(lines):
            text = score_font.render(line, True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 30))

    elif current_screen == "options":
        title = title_font.render("OPCIONES", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        for i, option in enumerate(options_menu):
            color = YELLOW if i == options_index else WHITE
            text = menu_font.render(option, True, color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 60))

    elif current_screen == "play":
        screen.fill(BLACK)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

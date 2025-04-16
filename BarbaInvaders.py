import pygame
import sys
import colorsys
import random
import time

pygame.init()
pygame.mixer.init()

IMAGE_player = pygame.image.load('./assets/images/player.png')
IMAGE_player = pygame.transform.scale(IMAGE_player, (50, 30))

IMAGE_bala = pygame.image.load('./assets/images/bala.png')
IMAGE_bala = pygame.transform.scale(IMAGE_bala, (5, 20))

IMAGE_enemy = pygame.image.load('./assets/images/enemy1.png')
IMAGE_enemy = pygame.transform.scale(IMAGE_enemy, (35, 30))

IMAGE_barrera = pygame.Surface((50, 20))
IMAGE_barrera.fill((128, 128, 128))


IMAGE_bala_enemiga = pygame.Surface((5, 20))
IMAGE_bala_enemiga.fill((255, 255, 0))

WIDTH, HEIGHT = 470, 680
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders - Barba Edition")

enter = pygame.mixer.Sound('./assets/music/undertale-save.mp3')
select = pygame.mixer.Sound('./assets/music/undertale-select-sound.mp3')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (230, 230, 0)
def rainbow_color(phase):
    h = (phase % 360) / 360.0
    r, g, b = colorsys.hsv_to_rgb(h, 1, 1)
    return (int(r * 255), int(g * 255), int(b * 255))

menu_font = pygame.font.SysFont("Press Start 2P Regular", 25)
title_font = pygame.font.SysFont("Press Start 2P Regular", 30)
subtitle_font = pygame.font.SysFont("Press Start 2P Regular", 18)
score_font = pygame.font.SysFont("Press Start 2P Regular", 12)
copy_font = pygame.font.SysFont("Press Start 2P Regular", 12)

menu_options = ["PLAY", "OPTIONS", "CREDITS", "QUIT"]
selected_index = 0
current_screen = "menu"

music_muted = False
sfx_muted = False
options_menu = ["MUSIC: ON", "SFX: ON", "BACK"]
options_index = 0

vidas = 3
balas = []
tiempo_ultimo_disparo = 0
cooldown_disparo = 300

nivel = 1
puntos = 0
puntaje_max = 0
cooldown_enemigo = max(300, 100 - (nivel * 50))
ultimo_disparo_enemigo = 0
def disparo_enemigo():
    global ultimo_disparo_enemigo
    tiempo_actual = pygame.time.get_ticks()

    if tiempo_actual - ultimo_disparo_enemigo >= cooldown_enemigo:
        if enemigos:

            disparadores = [e for e in enemigos if random.random() < 0.02 + 0.005 * nivel]
            for enemigo in disparadores:
                balas_enemigas.append(Bala(enemigo.rect.centerx, enemigo.rect.bottom, velocidad=5, enemigo=True))
        ultimo_disparo_enemigo = tiempo_actual

def game_over():
    screen.fill(BLACK)
    end_text = title_font.render("GAME OVER", True, WHITE)
    screen.blit(end_text, (WIDTH // 2 - end_text.get_width() // 2, 150))

class Bala:
    def __init__(self, x, y, velocidad=-7, enemigo=False):
        self.image = IMAGE_bala_enemiga if enemigo else IMAGE_bala
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.velocidad = velocidad
        self.enemigo = enemigo

    def mover(self):
        self.rect.y += self.velocidad

    def dibujar(self, pantalla):
        pantalla.blit(self.image, self.rect)

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

class Enemy:
    def __init__(self, x, y, fila):
        self.image = IMAGE_enemy
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direccion = 1
        self.fila = fila
        self.puntos = [50, 20, 10][fila]
        self.can_shoot = False  # Agregar la propiedad que determinará si puede disparar

    def mover(self, velocidad):
        self.rect.x += velocidad * self.direccion

    def dibujar(self, pantalla):
        pantalla.blit(self.image, self.rect)

    def disparar(self):
        return Bala(self.rect.centerx, self.rect.bottom, velocidad=2, enemigo=True)


class Barrera(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.original_image = pygame.Surface((40, 30), pygame.SRCALPHA)
        self.original_image.fill((0, 255, 0))  # Verde fosforescente
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mascara = pygame.mask.from_surface(self.image)

    def impactar(self, bala):
        # Coordenadas relativas dentro de la barrera
        x_rel = bala.rect.centerx - self.rect.x
        y_rel = bala.rect.centery - self.rect.y

        # "Romper" zona alrededor del impacto (círculo de daño)
        pygame.draw.circle(self.image, (0, 0, 0, 0), (x_rel, y_rel), 5)

        # Actualizar la máscara después del daño
        self.mascara = pygame.mask.from_surface(self.image)

    def draw(self, pantalla):
        pantalla.blit(self.image, self.rect.topleft)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if current_screen == "menu":
                if event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(menu_options)
                    select.play()
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(menu_options)
                    select.play()
                elif event.key == pygame.K_RETURN:
                    selected_option = menu_options[selected_index]
                    if selected_option == "CREDITS":
                        current_screen = "credits"
                    elif selected_option == "PLAY":
                        current_screen = "play"
                        enemigos = [Enemy(x * 50 + 50, y * 40 + 50, y) for y in range(3) for x in range(7)]
                        balas_enemigas = []
                        barreras = [Barrera(i, HEIGHT - 150) for i in [50, WIDTH//2 - 25, WIDTH - 100]]
                        enemigos_direccion = 1
                        enemigos_velocidad = 1 + (nivel - 1) * 0.5
                    elif selected_option == "OPTIONS":
                        current_screen = "options"
                    elif selected_option == "QUIT":
                        running = False
                    enter.play()
            elif current_screen == "credits":
                if event.key == pygame.K_ESCAPE:
                    current_screen = "menu"
            elif current_screen == "play":
                if event.key == pygame.K_SPACE:
                    tiempo_actual = pygame.time.get_ticks()
                    if tiempo_actual - tiempo_ultimo_disparo > cooldown_disparo:
                        nueva_bala = Bala(jugador.rect.centerx, jugador.rect.top)
                        balas.append(nueva_bala)
                        tiempo_ultimo_disparo = tiempo_actual
            elif current_screen == "options":
           
                if event.key == pygame.K_DOWN:
                    options_index = (options_index + 1) % len(options_menu)
                elif event.key == pygame.K_UP:
                    options_index = (options_index - 1) % len(options_menu)
                elif event.key == pygame.K_RETURN:
                    if options_index == 0:
                        music_muted = not music_muted
                        options_menu[0] = "MUSIC: OFF" if music_muted else "MUSIC: ON"
                        # Cambia el volumen de la música de fondo según la opción seleccionada
                        pygame.mixer.music.set_volume(0 if music_muted else 1)
                    elif options_index == 1:
                        sfx_muted = not sfx_muted
                        options_menu[1] = "SFX: OFF" if sfx_muted else "SFX: ON"
                        # Aquí podrías mutear los sonidos tipo: select.set_volume(0) para efectos de sonido
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
        nivel = 1
        puntos = 0
        if 'jugador' not in locals():
            grupo_barreras = pygame.sprite.Group()
            for i in [50, WIDTH//2 - 25, WIDTH - 100]:
                grupo_barreras.add(Barrera(i, HEIGHT - 150))
            class Player:
                def __init__(self, x, y):
                    self.image = IMAGE_player
                    self.rect = self.image.get_rect()
                    self.rect.centerx = x
                    self.rect.bottom = y
                    self.velocidad = 5

                def move(self, teclas):
                    if teclas[pygame.K_LEFT] and self.rect.left > 0:
                        self.rect.x -= self.velocidad
                    if teclas[pygame.K_RIGHT] and self.rect.right < WIDTH:
                        self.rect.x += self.velocidad

                def dibujar(self, pantalla):
                    pantalla.blit(self.image, self.rect)

            jugador = Player(WIDTH // 2, HEIGHT - 50)

        grupo_barreras = pygame.sprite.Group()

        pos_x = 80
        for i in range(4):
            barrera = Barrera(pos_x + i * 130, 400)  # Ajustá posición Y según tu juego
            grupo_barreras.add(barrera)

        for barrera in grupo_barreras:
            barrera.draw(screen)
        teclas = pygame.key.get_pressed()
        jugador.move(teclas)
        jugador.dibujar(screen)

        # Mover las balas del jugador
        for bala in balas[:]:
            bala.mover()
            bala.dibujar(screen)
            if bala.rect.bottom < 0:
                balas.remove(bala)
            else:
                for enemigo in enemigos[:]:
                    if bala.rect.colliderect(enemigo.rect):
                        puntos += enemigo.puntos
                        enemigos.remove(enemigo)
                        balas.remove(bala)
                        break

        for bala in balas + balas_enemigas:
            for barrera in grupo_barreras:
                if pygame.sprite.collide_rect(bala, barrera):
                    # Precisión con máscara para más realismo
                    offset = (bala.rect.x - barrera.rect.x, bala.rect.y - barrera.rect.y)
                    if barrera.mascara.overlap(pygame.mask.from_surface(bala.image), offset):
                        barrera.impactar(bala)
                        balas.remove(bala) if bala in balas else balas_enemigas.remove(bala)
                        break

        # Mover y dibujar los enemigos
        for enemigo in enemigos:
            enemigo.mover(enemigos_velocidad)
            enemigo.dibujar(screen)

        # Comprobar si los enemigos han llegado a los bordes
        if enemigos:
            borde_izq = min(e.rect.left for e in enemigos)
            borde_der = max(e.rect.right for e in enemigos)
            if borde_izq < 0 or borde_der > WIDTH:
                for enemigo in enemigos:
                    enemigo.direccion *= -1
                    enemigo.rect.y += 10

        # Si no hay enemigos, empezar un nuevo nivel
        if not enemigos:
            nivel += 1
            enemigos = [Enemy(x * 50 + 50, y * 40 + 50, y) for y in range(3) for x in range(7)]
            enemigos_velocidad += 0.9

        # Disparo de los enemigos más cercanos
        disparo_enemigo()

        # Mover y dibujar las balas enemigas
        for bala in balas_enemigas[:]:
            bala.mover()
            bala.dibujar(screen)
            if bala.rect.top > HEIGHT:
                balas_enemigas.remove(bala)

        # Comprobar si las balas enemigas colisionan con el jugador
        for bala in balas_enemigas[:]:
            if bala.rect.colliderect(jugador.rect):
                vidas -= 1  # Restar puntos por colisión
                balas_enemigas.remove(bala)

        # Dibujar las barreras
        for barrera in barreras[:]:
            barrera.dibujar(screen)
            for bala in balas[:]:
                if barrera.rect.colliderect(bala.rect):
                    balas.remove(bala)
                    if barrera.recibir_golpe():
                        barreras.remove(barrera)
                for bala in balas_enemigas[:]:
                    if barrera.rect.colliderect(bala.rect):
                        balas_enemigas.remove(bala)
                        if barrera.recibir_golpe():
                            barreras.remove(barrera)

        # Mostrar el puntaje y nivel en la pantalla
        nivel_texto = score_font.render(f"NIVEL: {nivel}", True, WHITE)
        screen.blit(nivel_texto, (10, 10))

        puntos_texto = score_font.render(f"PUNTOS: {puntos}", True, WHITE)
        screen.blit(puntos_texto, (WIDTH - 140, 10))

        if vidas == 0:
            game_over()
            time.sleep(3)
            current_screen = "menu"
            vidas = 3




    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

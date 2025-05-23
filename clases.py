import pygame
import random
import sys
import colorsys
#region CARGA DE IMAGENES Y VARIABLES

WIDTH, HEIGHT = 470, 680
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (230, 230, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)

IMAGE_player = pygame.image.load('./assets/images/player.png')
IMAGE_player = pygame.transform.scale(IMAGE_player, (50, 30))

IMAGE_player2 = pygame.image.load('./assets/images/player2.png')
IMAGE_player2 = pygame.transform.scale(IMAGE_player2, (50, 30))

IMAGE_bullet = pygame.image.load('./assets/images/bala.png')
IMAGE_bullet = pygame.transform.scale(IMAGE_bullet, (5, 20))

IMAGE_enemy = pygame.image.load('./assets/images/enemy1.png')
IMAGE_enemy = pygame.transform.scale(IMAGE_enemy, (35, 30))

IMAGE_enemy2 = pygame.image.load('./assets/images/enemy2.png')
IMAGE_enemy2 = pygame.transform.scale(IMAGE_enemy2, (35, 30))

IMAGE_enemy3 = pygame.image.load('./assets/images/enemy3.png')
IMAGE_enemy3 = pygame.transform.scale(IMAGE_enemy3, (35, 30))

IMAGE_barrier = pygame.Surface((50, 20))
IMAGE_barrier.fill((128, 128, 128))

IMAGE_enemy_bullet = pygame.Surface((5, 20))
IMAGE_enemy_bullet.fill((255, 255, 0))
#endregion
class Player:
    def __init__(self, x, y, player_num=1):
        self.image = IMAGE_player.copy()
        if player_num == 2:
            self.image = IMAGE_player2.copy()

        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 5
        self.player_num = player_num
        self.score = 0

    def move(self, keys):
        if self.player_num == 1:
            if keys[pygame.K_LEFT] and self.rect.left > 0:
                self.rect.x -= self.speed
            if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
                self.rect.x += self.speed
        else:
            #elcontrol del juugador 2
            if keys[pygame.K_a] and self.rect.left > 0:
                self.rect.x -= self.speed
            if keys[pygame.K_d] and self.rect.right < WIDTH:
                self.rect.x += self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Bullet:
    def __init__(self, x, y, speed=-7, is_enemy=False, player_num=1):
        self.image = IMAGE_enemy_bullet if is_enemy else IMAGE_bullet
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = speed
        self.is_enemy = is_enemy
        self.player_num = player_num  

    def move(self):
        self.rect.y += self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Enemy:
    def __init__(self, x, y, row):
        self.image = IMAGE_enemy
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = 1
        self.row = row
        self.points = [50, 20, 10][row]
        self.can_shoot = False  # propiedad para determinar si el enemigo puede disparar

    def move(self, speed):
        self.rect.x += speed * self.direction

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def shoot(self):
        return Bullet(self.rect.centerx, self.rect.bottom, speed=5, is_enemy=True)

class Barrier(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # crear una barrera
        self.original_image = pygame.Surface((60, 40), pygame.SRCALPHA)
        self.original_image.fill((0, 0, 0, 0))  
        
        # dibujo la barrera con un hueco
        pygame.draw.rect(self.original_image, GREEN, (0, 10, 60, 30))  
        pygame.draw.rect(self.original_image, (0, 0, 0, 0), (15, 0, 30, 15))  
        
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.health = 5  # Más puntos de vida para permitir destrucción gradual
        
    def impact(self, bullet):
        """Crea daño visual preciso en el punto de impacto"""
        # Obtener coordenadas relativas del impacto
        x_rel = bullet.rect.centerx - self.rect.x
        y_rel = bullet.rect.centery - self.rect.y
        
        # Verificar que las coordenadas estén dentro de los límites
        if 0 <= x_rel < self.image.get_width() and 0 <= y_rel < self.image.get_height():
            # Tamaño del daño basado en el tipo de bala
            damage_radius = 30 if bullet.is_enemy else 5
            
            # Crear un patrón de daño aleatorio pero realista
            for i in range(damage_radius * 2):
                for j in range(damage_radius * 2):
                    damage_x = x_rel + i - damage_radius
                    damage_y = y_rel + j - damage_radius
                    
                    # Verificar límites
                    if (0 <= damage_x < self.image.get_width() and 
                        0 <= damage_y < self.image.get_height()):
                        
                        # Distancia al centro del impacto
                        dist = ((damage_x - x_rel) ** 2 + (damage_y - y_rel) ** 2) ** 0.5
                        
                        # Aplicar daño basado en la distancia al centro
                        if dist < damage_radius and random.random() > (dist / damage_radius) * 0.6:
                            # Hacer transparente el píxel (eliminar parte de la barrera)
                            self.image.set_at((int(damage_x), int(damage_y)), (0, 0, 0, 0))
            
            # Reducir salud y actualizar la máscara
            self.health -= 1
            self.mask = pygame.mask.from_surface(self.image)
            
            # Verificar si queda muy poco de la barrera (menos del 25% de los píxeles originales)
            pixel_count = 0
            for x in range(self.image.get_width()):
                for y in range(self.image.get_height()):
                    if self.image.get_at((x, y))[3] > 0:  # Si el pixel tiene alfa > 0 (no es transparente)
                        pixel_count += 1
            
            # Devolver True si la barrera debe ser destruida (pocos píxeles o salud <= 0)
            if pixel_count < 150 or self.health <= 0:  # Umbral arbitrario de píxeles
                return True
        return False
        
    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

# clase para crear estrellas en el fondo
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


#region FUNCIONES Y DEMAS
#cosas necesarias que precisa el codigo para ejecutarse
def rainbow_color(phase):
    h = (phase % 360) / 360.0
    r, g, b = colorsys.hsv_to_rgb(h, 1, 1)
    return (int(r * 255), int(g * 255), int(b * 255))
    
def initialize_game():
    """inicializa o reinicia el estado del juego"""
    global player, player2, enemies, enemy_bullets, barrier_group, level, score, lives, bullets
    
    # crear jugador(es)
    if multiplayer:
        player = Player(WIDTH // 3, HEIGHT - 50, 1)
        player2 = Player(WIDTH * 2 // 3, HEIGHT - 50, 2)
    else:
        player = Player(WIDTH // 2, HEIGHT - 50, 1)
        player2 = None
    
    # crear enemigos
    enemies = [Enemy(x * 50 + 50, y * 40 + 50, y) for y in range(3) for x in range(7)]
    enemy_bullets = []
    bullets = []
    
    # crear barreras con la nueva implementación
    barrier_group.empty()
    for i in range(4):
        barrier = Barrier(60 + i * 110, HEIGHT - 150)
        barrier_group.add(barrier)
    
    level = 1
    score = 0
    lives = 3 if not multiplayer else 5  # Más vidas en modo multijugador

# funcion para manegar los disparos de los enemigos
def enemy_shoot():
    """maneja la logica de disparo de los enemigos"""
    global enemy_bullets, last_enemy_shot_time
    
    current_time = pygame.time.get_ticks()
    enemy_cooldown = max(300, 1000 - (level * 50))
    
    if current_time - last_enemy_shot_time >= enemy_cooldown and enemies:
        # seleccionar enemigos que pueden disparar (probabilidad aleatoria basada en nivel)
        shooters = [e for e in enemies if random.random() < 0.02 + 0.015 * level]
        for enemy in shooters:
            enemy_bullets.append(Bullet(enemy.rect.centerx, enemy.rect.bottom, speed=5, is_enemy=True))
        if shooters and not sfx_muted:
            shoot_sound.play()
            
        last_enemy_shot_time = current_time

# funcion para mostrar pantalla de game over
def show_game_over():
    """muestra la pantalla de fin de juego"""
    screen.fill(BLACK)
    end_text = title_font.render("GAME OVER", True, WHITE)
    score_text = subtitle_font.render(f"FINAL SCORE: {score}", True, WHITE)
    
    screen.blit(end_text, (WIDTH // 2 - end_text.get_width() // 2, 150))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 250))
    
    # En modo multijugador mostrar puntajes individuales
    if multiplayer and player and player2:
        p1_text = subtitle_font.render(f"PLAYER 1: {player.score}", True, WHITE)
        p2_text = subtitle_font.render(f"PLAYER 2: {player2.score}", True, CYAN)
        screen.blit(p1_text, (WIDTH // 2 - p1_text.get_width() // 2, 300))
        screen.blit(p2_text, (WIDTH // 2 - p2_text.get_width() // 2, 330))
    
    instruction = subtitle_font.render("Press any key to continue", True, WHITE)
    screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, 400))
    
    pygame.display.flip()
    
    # esperar a que se presione una tecla
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

# funcion para guardar la puntuacion maxima
def save_high_score():
    """guarda la puntuacion maxima en un archivo"""
    global high_score
    try:
        with open('highscore.txt', 'w') as file:
            file.write(str(high_score))
    except:
        pass  # falla silenciosamente si no se puede guardar

# funcion para cargar la puntuacion maxima
def load_high_score():
    """carga la puntuacion maxima desde el archibgo"""
    global high_score
    try:
        with open('highscore.txt', 'r') as file:
            high_score = int(file.read())
    except:
        high_score = 0
#endregion
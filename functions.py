import pygame
import random
import sys
import colorsys
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
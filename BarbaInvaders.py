import pygame
import sys
import colorsys
import random
from clases import *
# inicializamos pygame y el mezclador de sonido para que todo funcione bien
pygame.init()
pygame.mixer.init()

# dimensiones de la ventana del juego
WIDTH, HEIGHT = 470, 680
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders - Barba Edition")

# cargamos los efectos de sonido del juego
enter_sound = pygame.mixer.Sound('./assets/music/undertale-save.mp3')
select_sound = pygame.mixer.Sound('./assets/music/undertale-select-sound.mp3')
shoot_sound = pygame.mixer.Sound('./assets/music/shoot.mp3')  
hit_sound = pygame.mixer.Sound('./assets/music/hit.mp3')
hitp1_sound = pygame.mixer.Sound('./assets/music/hitp1.mp3')
hitp2_sound = pygame.mixer.Sound('./assets/music/hitp2.mp3')


# definimos los colores basicos que usaremos
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (230, 230, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)

# cargamos las fuentes que usaremos para los textos del juego
menu_font = pygame.font.SysFont("Press Start 2P Regular", 25)
title_font = pygame.font.SysFont("Press Start 2P Regular", 30)
subtitle_font = pygame.font.SysFont("Press Start 2P Regular", 18)
score_font = pygame.font.SysFont("Press Start 2P Regular", 12)
copy_font = pygame.font.SysFont("Press Start 2P Regular", 12)

# configuracion del menu principal (modificado para incluir modo 2 jugadores)
menu_options = ["1 JUGADOR", "MULTIJUGADOR", "OPCIONES", "CREDITOS", "QUIT"]
selected_index = 0
current_screen = "menu"
multiplayer = False

# configuracion de opciones de sonido
music_muted = False
sfx_muted = False
options_menu = [ "SFX: ON", "BACK"]
options_index = 0

# variables del estado del juego
lives = 3
bullets = []
last_shot_time = 0
last_shot_player2_time = 0 
shoot_cooldown = 300

level = 1
score = 0
high_score = 0

# inicializamos las colecciones de objetos del juego
enemy_bullets = []
enemies = []
barrier_group = pygame.sprite.Group()


# inicializacion de objetos del juego
stars = [Star() for _ in range(100)]
color_phase = 0
clock = pygame.time.Clock()
running = True
load_high_score()

# inicializamos las variables del juego
player = None
player2 = None
enemies = []
enemy_bullets = []
barrier_group = pygame.sprite.Group()
last_enemy_shot_time = 0
enemy_direction = 1
enemy_speed = 1

#region FUNCIONES

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
    
    # crear barreras 
    barrier_group.empty()
    if multiplayer == True: 
        for i in range(3):
            barrier = Barrier(60 + i * 150, HEIGHT - 150)
            barrier_group.add(barrier)
    else:
        for i in range(4):
            barrier = Barrier(50 + i * 110, HEIGHT - 150)
            barrier_group.add(barrier)
    
    level = 1
    score = 0
    lives = 3 if not multiplayer else 5  # Más vidas en modo multijugador

# funcion para manegar los disparos de los enemigos
def enemy_shoot():
    """maneja la logica de disparo de los enemigos"""
    global enemy_bullets, last_enemy_shot_time
    
    current_time = pygame.time.get_ticks()
    if multiplayer == True:
        enemy_cooldown = max(200, 1000 - (level * 65))
    else:
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

# bucle principal del juego
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            # navegacion del menu
            if current_screen == "menu":
                if event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(menu_options)
                    if not sfx_muted:
                        select_sound.play()
                elif event.key == pygame.K_w:
                    high_score == 0
                    high_score = 0
                    save_high_score()
                    load_high_score()

                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(menu_options)
                    if not sfx_muted:
                        select_sound.play()
                elif event.key == pygame.K_RETURN:
                    selected_option = menu_options[selected_index]
                    if selected_option == "CREDITOS":
                        current_screen = "credits"
                    elif selected_option == "1 JUGADOR":
                        current_screen = "play"
                        multiplayer = False
                        initialize_game()
                    elif selected_option == "MULTIJUGADOR":
                        current_screen = "play"
                        multiplayer = True
                        initialize_game()
                    elif selected_option == "OPCIONES":
                        current_screen = "options"
                    elif selected_option == "QUIT":
                        running = False
                    if not sfx_muted:
                        enter_sound.play()
            
            # pantalla de creditos
            elif current_screen == "credits":
                if event.key == pygame.K_ESCAPE:
                    current_screen = "menu"
            
            elif current_screen == "play":
                if event.key == pygame.K_UP:  # jugador 1 dispara
                    current_time = pygame.time.get_ticks()
                    if current_time - last_shot_time > shoot_cooldown:
                        new_bullet = Bullet(player.rect.centerx, player.rect.top, player_num=1)
                        bullets.append(new_bullet)
                        last_shot_time = current_time
                        if not sfx_muted:
                            shoot_sound.play()
                
                elif event.key == pygame.K_w and multiplayer and player2:  #disapros del jugador 2
                    current_time = pygame.time.get_ticks()
                    if current_time - last_shot_player2_time > shoot_cooldown:
                        new_bullet = Bullet(player2.rect.centerx, player2.rect.top, player_num=2)
                        bullets.append(new_bullet)
                        last_shot_player2_time = current_time
                        if not sfx_muted:
                            shoot_sound.play()
                
                elif event.key == pygame.K_ESCAPE:
                    current_screen = "menu"
            
            # menu de opciones
            elif current_screen == "options":
                if event.key == pygame.K_DOWN:
                    options_index = (options_index + 1) % len(options_menu)
                elif event.key == pygame.K_UP:
                    options_index = (options_index - 1) % len(options_menu)
                elif event.key == pygame.K_RETURN:
                    if options_index == 0:
                        sfx_muted = not sfx_muted
                        options_menu[0] = "SFX: OFF" if sfx_muted else "SFX: ON"
                    elif options_index == 1:
                        current_screen = "menu"
                elif event.key == pygame.K_ESCAPE:
                    current_screen = "menu"
    
    #para dibujar estrellas
    screen.fill(BLACK)
    for star in stars:
        star.update()
        star.draw(screen)

    # menu principal del juego
    if current_screen == "menu":
        title_text = title_font.render("SPACE INVADERS", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 150))

        copy_text = copy_font.render("Barbi Industries© - 2025", True, WHITE)
        screen.blit(copy_text, (WIDTH // 2 - copy_text.get_width() // 2, 650))

        current_color = rainbow_color(color_phase)
        color_phase += 2
        subtitle_text = subtitle_font.render("BARBA EDITION", True, current_color)
        screen.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, 200))

        score_text = score_font.render(f"HI-SCORE: {high_score}", True, WHITE)
        screen.blit(score_text, (20, 20))

        for i, option in enumerate(menu_options):
            color = YELLOW if i == selected_index else WHITE
            text = menu_font.render(option, True, color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 250 + i * 60))

    # pantalla de creditos con informacion del autor
    elif current_screen == "credits":
        title = title_font.render("CREDITS", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        lines = [
            "Creado por: Lucas Barba",
            "Musica utilizada: Undertale",
            "Escuela: Ins. Ind. Luis A. Huergo",
            "",
            "PUNTAJES:",
            "1era fila: 50P",
            "2nda fila: 30P",
            "3era fila: 10P",
            "",
            "Jugador 1: A - D dispara con W",
            "Jugador 2: ← - → dispara con ↑",
            "",
            "REINICIAR PUNTAJE = R",
            "",
            "Press ESC to return"
        ]

        for i, line in enumerate(lines):
            text = score_font.render(line, True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 30))
    
    # pantalla de opciones para configurar sonidos
    elif current_screen == "options":
        title = title_font.render("OPCIONES", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        for i, option in enumerate(options_menu):
            color = YELLOW if i == options_index else WHITE
            text = menu_font.render(option, True, color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 60))
    
    elif current_screen == "play":
        # obtener entrada del teclado
        keys = pygame.key.get_pressed()
        player.move(keys)
        player.draw(screen)
        
        # crear el jugador 2
        if multiplayer and player2:
            player2.move(keys)
            player2.draw(screen)

        # procesamiento de balas del jugador
        for bullet in bullets[:]:
            bullet.move()
            bullet.draw(screen)
            
            # eliminar balas que salen de la pantalla
            if bullet.rect.bottom < 0:
                bullets.remove(bullet)
            else:
                # verificar colisiones con enemigos
                for enemy in enemies[:]:
                    if bullet.rect.colliderect(enemy.rect):
                        # Asignar puntos al jugador correspondiente
                        if bullet.player_num == 1:
                            player.score += enemy.points
                        elif multiplayer and player2:
                            player2.score += enemy.points
                        
                        # Actualizar puntuación global
                        score += enemy.points
                        enemies.remove(enemy)
                        if sfx_muted == False:
                            hit_sound.play()
                        if bullet in bullets:  # verificar si la bala todavia existe
                            bullets.remove(bullet)
                        break

        # verificar colisiones de balas con barreras
        for bullet in bullets[:] + enemy_bullets[:]:
            for barrier in list(barrier_group):
                if pygame.sprite.collide_rect(bullet, barrier):
                    offset = (bullet.rect.x - barrier.rect.x, bullet.rect.y - barrier.rect.y)
                    if barrier.mask.overlap_area(pygame.mask.from_surface(bullet.image), offset) > 0:
                        destroyed = barrier.impact(bullet)
                        
                        # eliminar la bala tras colisionar
                        if bullet in bullets:
                            bullets.remove(bullet)
                        elif bullet in enemy_bullets:
                            enemy_bullets.remove(bullet)
                        
                        # eliminar barrera si está muy dañada
                        if destroyed:
                            barrier_group.remove(barrier)
                        break

        # mover y dibujar enemigos en la pantalla
        enemy_moved = False
        for enemy in enemies[:]:
            enemy.move(enemy_speed)
            enemy.draw(screen)
            enemy_moved = True

        # comprobar si los enemigos han llegado a los bordes
        if enemies:
            left_edge = min(e.rect.left for e in enemies)
            right_edge = max(e.rect.right for e in enemies)
            if left_edge < 10 or right_edge > WIDTH - 10:
                # cambiar direccion y bajar
                enemy_direction *= -1
                for enemy in enemies:
                    enemy.direction *= -1
                    enemy.rect.y += 10
                    
                # comprobar si los enemigos han llegado al jugador
                if max(e.rect.bottom for e in enemies) > player.rect.top:
                    lives = 0  # fin del juego si los enemigos llegan al jugador

        # iniciar nuevo nivel si todos los enemigos son eliminados
        if not enemies:
            level += 1
            enemies = [Enemy(x * 50 + 50, y * 40 + 50, y) for y in range(3) for x in range(7)]
            enemy_speed = 1 + (level - 1) * 0.2  # aumentar gradualmente la velocidad de los enemigos
            
        # manejo de disparos enemigos que nos atacan
        enemy_shoot()

        # procesar balas enemigas que vienen hacia nosotros
        for bullet in enemy_bullets[:]:
            bullet.move()
            bullet.draw(screen)
            
            # eliminar balas que salen de la pantalla por abajo
            if bullet.rect.top > 600:
                enemy_bullets.remove(bullet)
                
            # verificar colisiones con los jugadores
            if bullet.rect.colliderect(player.rect):
                lives -= 1
                if sfx_muted == False:
                    hitp1_sound.play()
                enemy_bullets.remove(bullet)
            
            # Comprobar colisión con jugador 2 en multijugador
            if multiplayer and player2 and bullet.rect.colliderect(player2.rect):
                lives -= 1
                if sfx_muted == False:
                    hitp2_sound.play()
                enemy_bullets.remove(bullet)

        # dibujar barreras en pantalla que nos protejen
        for barrier in barrier_group:
            barrier.draw(screen)

        # mostrar puntuacion y nivel del juego
        level_text = score_font.render(f"LEVEL: {level}", True, WHITE)
        screen.blit(level_text, (10, 10))

        # Mostrar puntuaciones en modo multijugador
        if multiplayer:
            p1_score_text = score_font.render(f"P1: {player.score}", True, WHITE)
            p2_score_text = score_font.render(f"P2: {player2.score}", True, CYAN)
            screen.blit(p1_score_text, (WIDTH - 350, 650))
            screen.blit(p2_score_text, (WIDTH - 170, 650))
            score_text = score_font.render(f"TOTAL: {score}", True, YELLOW)
            screen.blit(score_text, (WIDTH // 2 - 40, 30))
        else:
            score_text = score_font.render(f"SCORE: {score}", True, WHITE)
            screen.blit(score_text, (WIDTH - 140, 10))
        
        # mostrar vidas restantes
        lives_text = score_font.render(f"LIVES: {lives}", True, WHITE)
        screen.blit(lives_text, (WIDTH // 2 - 40, 10))

        # comprobar si el juego termino
        if lives <= 0:
            # actualizar puntuacion maxima si es necesario
            if score > high_score:
                high_score = score
                save_high_score()
                
            # mostrar pantalla de game over
            show_game_over()
            current_screen = "menu"

    # actualizar la pantala
    pygame.display.flip()
    clock.tick(60)

# limpiar y salir del juego
pygame.quit()
sys.exit()
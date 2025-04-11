import pygame
import random
import sys

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
ANCHO = 800
ALTO = 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Space Invaders")

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)

# Cargar imágenes
jugador_img = pygame.image.load("jugador.png")  # Usa una imagen de nave pequeña (64x64)
enemigo_img = pygame.image.load("enemigo.png")  # Imagen de enemigo
bala_img = pygame.image.load("bala.png")        # Imagen de bala

# Jugador
jugador_x = ANCHO // 2 - 32
jugador_y = ALTO - 100
jugador_velocidad = 5

# Bala
bala_x = 0
bala_y = jugador_y
bala_velocidad = 10
bala_visible = False

# Enemigos
num_enemigos = 6
enemigos = []
for i in range(num_enemigos):
    enemigos.append({
        "x": random.randint(0, ANCHO - 64),
        "y": random.randint(50, 150),
        "velocidad_x": 3,
        "velocidad_y": 40
    })

# Puntaje
puntaje = 0
fuente = pygame.font.Font(None, 36)

# Funciones
def dibujar_jugador(x, y):
    pantalla.blit(jugador_img, (x, y))

def disparar_bala(x, y):
    global bala_visible
    bala_visible = True
    pantalla.blit(bala_img, (x + 16, y))

def dibujar_enemigo(x, y, i):
    pantalla.blit(enemigo_img, (x, y))

def detectar_colision(x1, y1, x2, y2):
    distancia = ((x1 - x2)**2 + (y1 - y2)**2)**0.5
    return distancia < 27

# Bucle principal
reloj = pygame.time.Clock()
jugador_x_cambio = 0

while True:
    pantalla.fill(NEGRO)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_LEFT:
                jugador_x_cambio = -jugador_velocidad
            if evento.key == pygame.K_RIGHT:
                jugador_x_cambio = jugador_velocidad
            if evento.key == pygame.K_SPACE and not bala_visible:
                bala_x = jugador_x
                disparar_bala(bala_x, bala_y)
        if evento.type == pygame.KEYUP:
            if evento.key in (pygame.K_LEFT, pygame.K_RIGHT):
                jugador_x_cambio = 0

    jugador_x += jugador_x_cambio
    jugador_x = max(0, min(ANCHO - 64, jugador_x))

    # Movimiento bala
    if bala_visible:
        disparar_bala(bala_x, bala_y)
        bala_y -= bala_velocidad
        if bala_y <= 0:
            bala_y = jugador_y
            bala_visible = False

    # Movimiento enemigos
    for i, enemigo in enumerate(enemigos):
        enemigo["x"] += enemigo["velocidad_x"]
        if enemigo["x"] <= 0 or enemigo["x"] >= ANCHO - 64:
            enemigo["velocidad_x"] *= -1
            enemigo["y"] += enemigo["velocidad_y"]

        # Colisión
        if detectar_colision(bala_x, bala_y, enemigo["x"], enemigo["y"]):
            bala_y = jugador_y
            bala_visible = False
            puntaje += 1
            enemigo["x"] = random.randint(0, ANCHO - 64)
            enemigo["y"] = random.randint(50, 150)

        dibujar_enemigo(enemigo["x"], enemigo["y"], i)

    # Dibujar jugador
    dibujar_jugador(jugador_x, jugador_y)

    # Mostrar puntaje
    texto_puntaje = fuente.render(f"Puntaje: {puntaje}", True, BLANCO)
    pantalla.blit(texto_puntaje, (10, 10))

    pygame.display.update()
    reloj.tick(60)

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
        if row == 0:
            self.points = 50
            self.image = IMAGE_enemy
        elif row == 1:
            self.points = 30
            self.image = IMAGE_enemy2
        else:
            self.points = 10
            self.image = IMAGE_enemy3

        self.image:[]
        self.can_shoot = False  # propiedad para determinar si el enemigo puede disparar

    def move(self, speed):
        self.rect.x += speed * self.direction

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def shoot(self):
        return Bullet(self.rect.centerx, self.rect.bottom, speed=7, is_enemy=True)

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
        self.health = 8 
        
    def impact(self, bullet):
        #obtener las coords del impacto
        x_rel = bullet.rect.centerx - self.rect.x
        y_rel = bullet.rect.centery - self.rect.y
        
        #verificar que las coordenadas estén dentro de los límites
        if 0 <= x_rel < self.image.get_width() and 0 <= y_rel < self.image.get_height():
            #Tamaño del daño basado en el tipo de bala
            damage_radius = 25 if bullet.is_enemy else 5
            
            #crear un patrón de daño aleatorio pero realista
            for i in range(damage_radius * 3):
                for j in range(damage_radius * 2):
                    damage_x = x_rel + i - damage_radius
                    damage_y = y_rel + j - damage_radius
                    
                    #verificar límites
                    if (0 <= damage_x < self.image.get_width() and 
                        0 <= damage_y < self.image.get_height()):
                        
                        # Distancia al centro del impacto
                        dist = ((damage_x - x_rel) ** 2 + (damage_y - y_rel) ** 2) ** 0.5
                        
                        #daño basado en el cenrto
                        if dist < damage_radius and random.random() > (dist / damage_radius) * 0.6:
                            #eliminar parte de la barrera
                            self.image.set_at((int(damage_x), int(damage_y)), (0, 0, 0, 0))
            
            # Reducir salud y actualizar la máscara
            self.health -= 1
            self.mask = pygame.mask.from_surface(self.image)
            
            pixel_count = 0
            for x in range(self.image.get_width()):
                for y in range(self.image.get_height()):
                    if self.image.get_at((x, y))[3] > 0:  
                        pixel_count += 1
            

            if pixel_count < 150 or self.health <= 0: 
                return True
        return False
        
    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

#clase para crear estrellas en el fondo
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

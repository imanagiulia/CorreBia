import copy
import threading
from board import boards
import pygame
import math
from threading import Lock
import time

pygame.init()
inimigo_lock = Lock()
# tamanho do "console" do jogo
WIDTH = 900
HEIGHT = 950
screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
fpd = 60
font = pygame.font.Font('freesansbold.ttf', 20)
level_inicial = boards
level = copy.deepcopy(boards)
color = 'orange'
PI = math.pi
player_images = []
for i in range (1, 3):
    player_images.append(pygame.transform.scale(pygame.image.load(f'assets/{i}.png'), (45, 45)))
cloudius_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/nuvem.png'), (45, 45))
ping_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/redes.png'), (45, 45))
glitch_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/computacional.png'), (45, 45))
kernel_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/operacional.png'), (45, 45))
check_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/check.png'), (45, 45))
turbo_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/turbo.png'), (45, 45))
# posição inicial Bia
player_x = 450
player_y = 663
# posição inicial inimigos
cloudius_x = 56
cloudius_y = 58
cloudius_direction = 0
ping_x = 400
ping_y = 438
ping_direction = 2
glitch_x = 440
glitch_y = 438
glitch_direction = 2
kernel_x = 440
kernel_y = 438
kernel_direction = 2
direction = 0
counter = 0
flicker = 0
# direita, esquerda, cima, baixo
direction_command = 0
player_speed = 3
score = 0
powerup = False
powerup_count = 0
# nuvem, redes, compu, opera
eaten_inimigo = [False, False, False, False]
targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]
cloudius_dead = False
ping_dead = False
glitch_dead = False
kernel_dead = False
cloudius_box = False
ping_box = False
glitch_box = False
kernel_box = False
moving = False
# nuvem, redes, compu, opera
inimigo_speeds = [2, 2, 2, 2]
startup_counter = 0
lives = 3
game_over = False
game_won = False

class Inimigo:
    def __init__(self, x_coord, y_coord, target, speed, img, direction, dead, box, id):
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22
        self.target = target
        self.speed = speed
        self.img = img
        self.direction = direction
        self.dead = dead
        self.in_box = box
        self.id = id
        self.turns, self.in_box = self.check_collisions()
        self.rect = self.draw()
        self.running = True

    def draw(self):
        if (not powerup and not self.dead) or (eaten_inimigo[self.id] and powerup and not self.dead):
            screen.blit(self.img, (self.x_pos, self.y_pos))
        elif powerup and not self.dead and not eaten_inimigo[self.id]:
            screen.blit(turbo_img, (self.x_pos, self.y_pos))
        else:
            screen.blit(check_img, (self.x_pos, self.y_pos))
        ghost_rect = pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))
        return ghost_rect

    def check_collisions(self): # D, E, C, B
        # semáforo
        with inimigo_lock:
            cell_height = (HEIGHT - 50) // 32
            cell_width = (WIDTH // 30)
            margem = 15
            self.turns = [False, False, False, False]
            if 0 < self.center_x // 30 < 29:
                if level[(self.center_y - margem) // cell_height][self.center_x // cell_width] == 9:
                    self.turns[2] = True
                if level[self.center_y // cell_height][(self.center_x - margem) // cell_width] < 3 \
                    or level[self.center_y // cell_height][(self.center_x - margem) // cell_width] == 9 and (self.dead or self.in_box):
                    self.turns[1] = True
                if level[self.center_y // cell_height][(self.center_x + margem) // cell_width] < 3 \
                    or level[self.center_y // cell_height][(self.center_x + margem) // cell_width] == 9 and (self.dead or self.in_box):
                    self.turns[0] = True
                if level[(self.center_y + margem) // cell_height][self.center_x // cell_width] < 3 \
                    or level[(self.center_y + margem) // cell_height][self.center_x // cell_width] == 9 and (self.dead or self.in_box):
                    self.turns[3] = True
                if level[(self.center_y - margem) // cell_height][self.center_x // cell_width] < 3 \
                    or level[(self.center_y - margem) // cell_height][self.center_x // cell_width] == 9 and (self.dead or self.in_box):
                    self.turns[2] = True

                if self.direction == 2 or self.direction == 3:
                    if 12 <= self.center_x % cell_width <= 18:
                        if level[(self.center_y + margem) // cell_height][self.center_x // cell_width] < 3 \
                            or (level[(self.center_y + margem) // cell_height][self.center_x // cell_width] == 9 and (self.dead or self.in_box)):
                            self.turns[3] = True
                        if level[(self.center_y - margem) // cell_height][self.center_x // cell_width] < 3 \
                            or (level[(self.center_y - margem) // cell_height][self.center_x // cell_width] == 9 and (self.dead or self.in_box)):
                            self.turns[2] = True
                    if 12 <= self.center_y % cell_height <= 18:
                        if level[self.center_y // cell_height][(self.center_x - cell_width) // cell_width] < 3 \
                            or (level[self.center_y // cell_height][(self.center_x - cell_width) // cell_width] == 9 and (self.dead or self.in_box)):
                            self.turns[1] = True
                        if level[self.center_y // cell_height][(self.center_x + cell_width) // cell_width] < 3 \
                            or (level[self.center_y // cell_height][(self.center_x + cell_width) // cell_width] == 9 and (self.dead or self.in_box)):
                            self.turns[0] = True

                if self.direction == 0 or self.direction == 1:
                    if 12 <= self.center_x % cell_width <= 18:
                        if level[(self.center_y + margem) // cell_height][self.center_x // cell_width] < 3 \
                            or (level[(center_y + margem) // cell_height][self.center_x // cell_width] == 9 and (self.dead or self.in_box)):
                            self.turns[3] = True
                        if level[(self.center_y - margem) // cell_height][self.center_x // cell_width] < 3 \
                            or (level[(self.center_y - margem) // cell_height][self.center_x // cell_width] == 9 and (self.dead or self.in_box)):
                            self.turns[2] = True
                    if 12 <= self.center_y % cell_height <= 18:
                        if level[self.center_y // cell_height][(self.center_x - margem) // cell_width] < 3 \
                            or (level[self.center_y // cell_height][(self.center_x - margem) // cell_width] == 9 and (self.dead or self.in_box)):
                            self.turns[1] = True
                        if level[self.center_y // cell_height][(self.center_x + margem) // cell_width] < 3 \
                            or (level[self.center_y // cell_height][(self.center_x + margem) // cell_width] == 9 and (self.dead or self.in_box)):
                            self.turns[0] = True
            else:
                self.turns[0] = True
                self.turns[1] = True
            if 350 <= self.x_pos < 550 and 370 < self.y_pos < 480:
                self.in_box = True
            else:
                self.in_box = False
            return self.turns, self.in_box

    def move_kernel(self): # vira sempre que for vantajoso para perseguição
        #semáforo
        with inimigo_lock: # D, E, C, B
            if self.direction == 0:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.x_pos += self.speed
                elif not self.turns[0]:
                    if self.target[1] > self.y_pos and self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.target[1] < self.y_pos and self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.target[0] < self.x_pos and self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    elif self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                elif self.turns[0]:
                    if self.target[1] > self.y_pos and self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    if self.target[1] < self.y_pos and self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    else:
                        self.x_pos += self.speed
            elif self.direction == 1:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.x_pos -= self.speed
                elif not self.turns[1]:
                    if self.target[1] > self.y_pos and self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.target[1] < self.y_pos and self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.target[0] > self.x_pos and self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                    elif self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                elif self.turns[1]:
                    if self.target[1] > self.y_pos and self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    if self.target[1] < self.y_pos and self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    else:
                        self.x_pos -= self.speed
            elif self.direction == 2:
                if self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif not self.turns[2]:
                    if self.target[0] > self.x_pos and self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                    elif self.target[0] < self.x_pos and self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    elif self.target[1] > self.y_pos and self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    elif self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                elif self.turns[2]:
                    if self.target[0] > self.x_pos and self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                    if self.target[0] < self.x_pos and self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    else:
                        self.y_pos -= self.speed
            elif self.direction == 3:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.y_pos += self.speed
                elif not self.turns[3]:
                    if self.target[0] > self.x_pos and self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                    elif self.target[0] < self.x_pos and self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    elif self.target[1] < self.y_pos and self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    elif self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                elif self.turns[3]:
                    if self.target[0] > self.x_pos and self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                    elif self.target[0] < self.x_pos and self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    else:
                        self.y_pos += self.speed
            if self.x_pos < -30:
                self.x_pos = 900
            elif self.x_pos > 900:
                self.x_pos -= 30
            return self.x_pos, self.y_pos, self.direction

    def move_cloudius(self): # vira sempre que colidir com parede, caso contrário continua reto
        #semáforo
        with inimigo_lock: # D, E, C, B
            if self.direction == 0:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.x_pos += self.speed
                elif not self.turns[0]:
                    if self.target[1] > self.y_pos and self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.target[1] < self.y_pos and self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.target[0] < self.x_pos and self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    elif self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                elif self.turns[0]:
                    self.x_pos += self.speed
            elif self.direction == 1:
                if self.target[0] < self.x_pos and self.turns[1]:
                    self.x_pos -= self.speed
                elif not self.turns[1]:
                    if self.target[1] > self.y_pos and self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.target[1] < self.y_pos and self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.target[0] > self.x_pos and self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                    elif self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                elif self.turns[1]:
                        self.x_pos -= self.speed
            elif self.direction == 2:
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif not self.turns[2]:
                    if self.target[0] > self.x_pos and self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                    elif self.target[0] < self.x_pos and self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    elif self.target[1] > self.y_pos and self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                    elif self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                elif self.turns[2]:
                    self.y_pos -= self.speed
            elif self.direction == 3:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.y_pos += self.speed
                elif not self.turns[3]:
                    if self.target[0] > self.x_pos and self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                    elif self.target[0] < self.x_pos and self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    elif self.target[1] < self.y_pos and self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                    elif self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                elif self.turns[3]:
                    self.y_pos += self.speed
            if self.x_pos < -30:
                self.x_pos = 900
            elif self.x_pos > 900:
                self.x_pos -= 30
            return self.x_pos, self.y_pos, self.direction

    def move_ping(self): # vira para cima ou para baixo qualquer momento para perseguir, mas para esquerda ou para direita somente em colisões
        #semáforo
        with inimigo_lock: # D, E, C, B
            if self.direction == 0:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.x_pos += self.speed
                elif not self.turns[0]:
                    if self.target[1] > self.y_pos and self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.target[1] < self.y_pos and self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.target[0] < self.x_pos and self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    elif self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                elif self.turns[0]:
                    if self.target[1] > self.y_pos and self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    if self.target[1] < self.y_pos and self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    else:
                        self.x_pos += self.speed
            elif self.direction == 1:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.x_pos -= self.speed
                elif not self.turns[1]:
                    if self.target[1] > self.y_pos and self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.target[1] < self.y_pos and self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.target[0] > self.x_pos and self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                    elif self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                elif self.turns[1]:
                    if self.target[1] > self.y_pos and self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    if self.target[1] < self.y_pos and self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    else:
                        self.x_pos -= self.speed
            elif self.direction == 2:
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif not self.turns[2]:
                    if self.target[0] > self.x_pos and self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                    elif self.target[0] < self.x_pos and self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    elif self.target[1] > self.y_pos and self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    elif self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                elif self.turns[2]:
                    self.y_pos -= self.speed
            elif self.direction == 3:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.y_pos += self.speed
                elif not self.turns[3]:
                    if self.target[0] > self.x_pos and self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                    elif self.target[0] < self.x_pos and self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    elif self.target[1] < self.y_pos and self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    elif self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                elif self.turns[3]:
                    if self.target[0] > self.x_pos and self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                    elif self.target[0] < self.x_pos and self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    else:
                        self.y_pos += self.speed
            if self.x_pos < -30:
                self.x_pos = 900
            elif self.x_pos > 900:
                self.x_pos -= 30
            return self.x_pos, self.y_pos, self.direction

    def move_glitch(self): # vira para a esquera ou para a direita sempre que for vantajoso para perseguição, mas para cima ou para baixo apenas em cplisões
        #semáforo
        with inimigo_lock: # D, E, C, B
            if self.direction == 0:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.x_pos += self.speed
                elif not self.turns[0]:
                    if self.target[1] > self.y_pos and self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.target[1] < self.y_pos and self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.target[0] < self.x_pos and self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    elif self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                elif self.turns[0]:
                    self.x_pos += self.speed
            elif self.direction == 1:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.x_pos -= self.speed
                elif not self.turns[1]:
                    if self.target[1] > self.y_pos and self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.target[1] < self.y_pos and self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.target[0] > self.x_pos and self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                    elif self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                elif self.turns[1]:
                    self.x_pos -= self.speed
            elif self.direction == 2:
                if self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif not self.turns[2]:
                    if self.target[0] > self.x_pos and self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                    elif self.target[0] < self.x_pos and self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    elif self.target[1] > self.y_pos and self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    elif self.turns[3]:
                        self.direction = 3
                        self.y_pos += self.speed
                    elif self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                elif self.turns[2]:
                    if self.target[0] > self.x_pos and self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                    if self.target[0] < self.x_pos and self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    else:
                        self.y_pos -= self.speed
            elif self.direction == 3:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.y_pos += self.speed
                elif not self.turns[3]:
                    if self.target[0] > self.x_pos and self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                    elif self.target[0] < self.x_pos and self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    elif self.target[1] < self.y_pos and self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.turns[2]:
                        self.direction = 2
                        self.y_pos -= self.speed
                    elif self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    elif self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                elif self.turns[3]:
                    if self.target[0] > self.x_pos and self.turns[0]:
                        self.direction = 0
                        self.x_pos += self.speed
                    elif self.target[0] < self.x_pos and self.turns[1]:
                        self.direction = 1
                        self.x_pos -= self.speed
                    else:
                        self.y_pos += self.speed
            if self.x_pos < -30:
                self.x_pos = 900
            elif self.x_pos > 900:
                self.x_pos -= 30
            return self.x_pos, self.y_pos, self.direction

def draw_alter():
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 720))
    if powerup == True:
        pygame.draw.circle(screen, 'red', (140, 720), 15)
    for l in range(lives):
        screen.blit(pygame.transform.scale(player_images[1], (40,40)), (650 + l * 40, 705))
    if game_over:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('Game Over! Aperte [espaço] para recomeçar!', True, 'red')
        screen.blit(gameover_text, (100, 300))
    if game_won:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('VICTORY!!! Aperte [espaço] para recomeçar!', True, 'yellow')
        screen.blit(gameover_text, (100, 300))

def check_collisions(scor, power, power_count, eaten_inimigo):
    cell_height = (HEIGHT - 50)  // 32
    cell_widht = WIDTH // 30
    if 0 < player_x < 870:
        if level[center_y // cell_height][center_x // cell_widht] == 1:
            level[center_y // cell_height][center_x // cell_widht] = 0
            scor += 10
        if level[center_y // cell_height][center_x // cell_widht] == 2:
            level[center_y // cell_height][center_x // cell_widht] = 0
            scor += 50
            power = True
            power_count = 0
            eaten_inimigo = [False, False, False, False]
    return scor, power, power_count, eaten_inimigo

def draw_board(level):
    num1 = ((HEIGHT - 50) // 32)
    num2 = (WIDTH // 30)
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 1:
                pygame.draw.circle(
                    surface=screen,
                    color='yellow',
                    center=(j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)),
                    radius=4
                )
            if level[i][j] == 2 and not flicker:
                pygame.draw.circle(
                    surface=screen,
                    color='yellow',
                    center=(j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)),
                    radius=10
                )
            if level[i][j] == 3:
                pygame.draw.line(
                    surface=screen,
                    color=color,
                    start_pos=(j * num2 + (0.5 * num2), i * num1),
                    end_pos=(j * num2 + (0.5 * num2), i * num1 + num1),
                    width=3
                )
            if level[i][j] == 4:
                pygame.draw.line(
                    surface=screen,
                    color=color,
                    start_pos=(j * num2, i * num1 + (0.5 * num1)),
                    end_pos=(j * num2 + num2, i * num1 + (0.5 * num1)),
                    width=3
                )
            if level[i][j] == 5:
                pygame.draw.arc(
                    surface=screen,
                    color=color,
                    rect=[(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (0.5 * num1)), num2, num1],
                    start_angle=0,
                    stop_angle=PI/2,
                    width=3
                )
            if level[i][j] == 6:
                pygame.draw.arc(
                    surface=screen,
                    color=color,
                    rect=[(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1],
                    start_angle=PI/2,
                    stop_angle=PI,
                    width=3
                )
            if level[i][j] == 7:
                pygame.draw.arc(
                    surface=screen,
                    color=color,
                    rect=[(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1],
                    start_angle=PI,
                    stop_angle=3*PI/2,
                    width=3
                )
            if level[i][j] == 8:
                pygame.draw.arc(
                    surface=screen,
                    color=color,
                    rect=[(j * num2 - (num2 * 0.4)) - 2, (i * num1 - (0.4 * num1)), num2, num1],
                    start_angle=3*PI/2,
                    stop_angle=2*PI,
                    width=3
                )
            if level[i][j] == 9:
                pygame.draw.line(
                    surface=screen,
                    color='white',
                    start_pos=(j * num2, i * num1 + (0.5 * num1)),
                    end_pos=(j * num2 + num2, i * num1 + (0.5 * num1)),
                    width=3
                )
            if level[i][j] == 10:
                pygame.draw.line(
                    surface=screen,
                    color= 'white',
                    start_pos=(j * num2 + (0.5 * num2), i * num1),
                    end_pos=(j * num2 + (0.5 * num2), i * num1 + num1),
                    width=3
                )

def draw_player():
    # direita, esquerda, cima, baixo
    if direction == 0:
        screen.blit(player_images[counter // 15 % len(player_images)], (player_x, player_y))
    elif direction == 1:
        screen.blit(pygame.transform.flip(player_images[counter // 15 % len(player_images)], True, False), (player_x, player_y))
    elif direction == 2:
        screen.blit(pygame.transform.rotate(player_images[counter // 15 % len(player_images)], 90),  (player_x, player_y))
    elif direction == 3:
        screen.blit(pygame.transform.rotate(player_images[counter // 15 % len(player_images)], -90), (player_x, player_y))

def check_position(centerx, centery):
    # D, E, C, B
    turns = [False, False, False, False]
    cell_height = (HEIGHT - 50) // 32
    cell_width = (WIDTH // 30)
    margem = 15
    # checa as colisões baseadas no center x e center y +/- um fugde number
    if 0 <= centerx < WIDTH and 0 <= centery < HEIGHT - 50:
        if direction == 0:
            if level[centery // cell_height][(centerx - margem) // cell_width] < 3:
                turns[1] = True
        if direction == 1:
            if level[centery // cell_height][(centerx + margem) // cell_width] < 3:
                turns[0] = True
        if direction == 2:
            if level[(centery  + margem) // cell_height][centerx // cell_width] < 3:
                turns[3] = True
        if direction == 3:
            if level[(centery - margem) // cell_height][centerx // cell_width] < 3:
                turns[2] = True


        if 10 <= centerx % cell_width <= 16:  # Perto do centro horizontal
            if level[(centery + margem) // cell_height][centerx // cell_width] < 3:
                turns[3] = True  # Pode ir para baixo
            if level[(centery - margem) // cell_height][centerx // cell_width] < 3:
                turns[2] = True  # Pode ir para cima

        if 10 <= centery % cell_height <= 16:  # Perto do centro vertical
            if level[centery // cell_height][(centerx + margem) // cell_width] < 3:
                turns[0] = True  # Pode ir para direita
            if level[centery // cell_height][(centerx - margem) // cell_width] < 3:
                turns[1] = True  # Pode ir para esquerda


        #if direction == 2 or direction == 3:
         #   if 12 <= centerx % n2 <= 18:
          #      if level[(centery + n3) // n1][centerx // n2] < 3:
           #         turns[3] = True
            #    if level[(centery - n3) // n1][centerx // n2] < 3:
             #       turns[2] = True
            #if 12 <= centery % n1 <= 18:
             #   if level[centery // n1][(centerx - n2) // n2] < 3:
              #      turns[1] = True
               # if level[centery // n1][(centerx + n2) // n2] < 3:
                #    turns[0] = True

      #  if direction == 0 or direction == 1:
       #     if 12 <= centerx % n2 <= 18:
        #        if level[(centery + n1) // n1][centerx // n2] < 3:
         #           turns[3] = True
          #      if level[(centery - n1) // n1][centerx // n2] < 3:
           #         turns[2] = True
            #if 12 <= centery % n1 <= 18:
             #   if level[centery // n1][(centerx - n3) // n2] < 3:
              #      turns[1] = True
               # if level[centery // n1][(centerx + n3) // n2] < 3:
                #    turns[0] = True
    else:
        turns[0] = True
        turns[1] = True
    return turns

def move_player(play_x, play_y):
    #direita, esquerda, cima, baixo
    if direction == 0 and turns_allowed[0]:
        play_x += player_speed
    elif direction == 1 and turns_allowed[1]:
        play_x -= player_speed
    if direction == 2 and turns_allowed[2]:
        play_y -= player_speed
    elif direction == 3 and turns_allowed[3]:
        play_y += player_speed

    # Limita a posição dentro dos limites da tela
    play_x = max(-50, min(play_x, WIDTH + 50))
    play_y = max(0, min(play_y, HEIGHT - 50))

    return play_x, play_y

def get_targets(kerne_x, kerne_y, glitc_x, glitc_y, nuve_x, nuve_y, pin_x, pin_y):
    runaway_x = 900 if player_x < 450 else 0
    runaway_y = 900 if player_y < 450 else 0
    return_target = (380, 400)
    if powerup:
        if not cloudius.dead and not eaten_inimigo[0]:
            nuve_target = (runaway_x, runaway_y)
        elif not cloudius.dead and eaten_inimigo[0]:
            if 340 < nuve_x < 560 and 340 < nuve_y < 500:
                nuve_target = (400, 100)
            else:
                nuve_target = (player_x, player_y)
        else:
            nuve_target = return_target
        if not ping.dead and not eaten_inimigo[1]:
            pin_target = (runaway_x, player_y)
        elif not ping.dead and eaten_inimigo[1]:
            if 340 < pin_x < 560 and 340 < pin_y < 500:
                pin_target = (400, 100)
            else:
                pin_target = (player_x, player_y)
        else:
            pin_target = return_target
        if not kernel.dead and not eaten_inimigo[2]:
            kerne_target = (player_x, runaway_y)
        elif not kernel.dead and eaten_inimigo[2]:
            if 340 < kerne_x < 560 and 340 < kerne_y < 500:
                kerne_target = (400, 100)
            else:
                kerne_target = (player_x, player_y)
        else:
            kerne_target = return_target
        if not glitch.dead and not eaten_inimigo[3]:
            glitc_target = (450, 450)
        elif not glitch.dead and eaten_inimigo[3]:
            if 340 < glitc_x < 560 and 340 < glitc_y < 500:
                glitc_target = (400, 100)
            else:
                glitc_target = (player_x, player_y)
        else:
            glitc_target = return_target
    else:
        if not cloudius.dead:
            if 340 < nuve_x < 560 and 340 < nuve_y < 500: # está na caixa
                nuve_target = (400, 100)
            else:
                nuve_target = (player_x, player_y)
        else:
            nuve_target = return_target
        if not ping.dead:
            if 340 < pin_x < 560 and 340 < pin_y < 500:
                pin_target = (400, 100)
            else:
                pin_target = (player_x, player_y)
        else:
            pin_target = return_target
        if not kernel.dead:
            if 340 < kerne_x < 560 and 340 < kerne_y < 500:
                kerne_target = (400, 100)
            else:
                kerne_target = (player_x, player_y)
        else:
            kerne_target = return_target
        if not glitch.dead:
            if 340 < glitc_x < 560 and 340 < glitc_y < 500:
                glitc_target = (400, 100)
            else:
                glitc_target = (player_x, player_y)
        else:
            glitc_target = return_target

    return [nuve_target, pin_target, kerne_target, glitc_target]

run = True


while run:
    timer.tick(fpd)
    if counter < 19:
        counter += 1
        if counter > 2:
            flicker = False
    else:
        counter = 0
        flicker = True
    if powerup == True and powerup_count < 600:
        powerup_count += 1
    elif powerup and powerup_count >= 600:
        powerup_count = 0
        powerup = False
        eaten_inimigo = [False, False, False, False]
    if startup_counter  < 180 and not game_over and not game_won:
        moving = False
        startup_counter += 1
    else:
        moving = True

    screen.fill('black')
    draw_board(level)
    center_x = player_x + 25
    center_y = player_y + 25
    if powerup:
        inimigo_speeds = [1, 1, 1, 1]
    else:
        inimigo_speeds = [2, 2, 2, 2]
    if eaten_inimigo[0]:
        inimigo_speeds[0] = 2
    if eaten_inimigo[1]:
        inimigo_speeds[1] = 2
    if eaten_inimigo[2]:
        inimigo_speeds[2] = 2
    if eaten_inimigo[3]:
        inimigo_speeds[3] = 2
    if cloudius_dead:
        inimigo_speeds[0] = 4
    if ping_dead:
        inimigo_speeds[1] = 4
    if glitch_dead:
        inimigo_speeds[2] = 4
    if kernel_dead:
        inimigo_speeds[3] = 4

    game_won = True
    for i in range(len(level)):
        if 1 in level[i] or 2 in level[1]:
            game_won = False

    player_circle = pygame.draw.circle(screen, 'black', (center_x, center_y), 21, 2)
    draw_player()

    cloudius = Inimigo(cloudius_x, cloudius_y, targets[0], inimigo_speeds[0], cloudius_img, cloudius_direction, cloudius_dead, cloudius_box, 0)
    ping = Inimigo(ping_x, ping_y, targets[1], inimigo_speeds[1], ping_img, ping_direction, ping_dead, ping_box, 1)
    glitch = Inimigo(glitch_x, glitch_y, targets[2], inimigo_speeds[2], glitch_img, glitch_direction, glitch_dead, glitch_box, 2)
    kernel = Inimigo(kernel_x, kernel_y, targets[3], inimigo_speeds[3], kernel_img, kernel_direction, kernel_dead, kernel_box, 3)
    '''with inimigo_lock:
        cloudius.rect = cloudius.draw()
        ping.rect = ping.draw()
        glitch.rect = glitch.draw()
        kernel.rect = kernel.draw()'''

    draw_alter()
    targets = get_targets(kernel_x, kernel_y, glitch_x, glitch_y, cloudius_x, cloudius_y, ping_x, ping_y)
    turns_allowed = check_position(center_x, center_y)
    if moving:
        player_x, player_y = move_player(player_x, player_y)
        if not cloudius_dead and not cloudius.in_box:
            cloudius_x, cloudius_y, cloudius_direction = cloudius.move_cloudius()
        else:
            cloudius_x, cloudius_y, cloudius_direction = cloudius.move_kernel()
        if not ping_dead and not ping.in_box:
            ping_x, ping_y, ping_direction = ping.move_ping()
        else:
            ping_x, ping_y, ping_direction = ping.move_kernel()
        if not glitch_dead and not glitch.in_box:
            glitch_x, glitch_y, glitch_direction = glitch.move_glitch()
        else:
            glitch_x, glitch_y, glitch_direction = glitch.move_kernel()

        kernel_x, kernel_y, kernel_direction = kernel.move_kernel()
    score, powerup, powerup_count, eaten_inimigo = check_collisions(score, powerup, powerup_count, eaten_inimigo)

    if not powerup:
        if (player_circle.colliderect(cloudius.rect) and not cloudius.dead) or (player_circle.colliderect(ping.rect) and not ping.dead) or (player_circle.colliderect(kernel.rect) and not kernel.dead) or (player_circle.colliderect(glitch.rect) and not glitch.dead):
            if lives > 0:
                lives -= 1
                startup_counter = 0
                powerup = False
                powerup_count = 0
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                cloudius_x = 56
                cloudius_y = 58
                cloudius_direction = 0
                ping_x = 400
                ping_y = 438
                ping_direction = 2
                glitch_x = 440
                glitch_y = 438
                glitch_direction = 2
                kernel_x = 440
                kernel_y = 438
                kernel_direction = 2
                eaten_inimigo = [False, False, False, False]
                cloudius_dead = False
                ping_dead = False
                glitch_dead = False
                kernel_dead = False
            else:
                game_over = True
                moving = False
                startup_counter = 0
    if powerup and (player_circle.colliderect(cloudius.rect) and eaten_inimigo[0]) and not cloudius.dead:
        if lives > 0:
            lives -= 1
            startup_counter = 0
            powerup = False
            powerup_count = 0
            player_x = 450
            player_y = 663
            direction = 0
            direction_command = 0
            cloudius_x = 56
            cloudius_y = 58
            cloudius_direction = 0
            ping_x = 400
            ping_y = 438
            ping_direction = 2
            glitch_x = 440
            glitch_y = 438
            glitch_direction = 2
            kernel_x = 440
            kernel_y = 438
            kernel_direction = 2
            eaten_inimigo = [False, False, False, False]
            cloudius_dead = False
            ping_dead = False
            glitch_dead = False
            kernel_dead = False
            if powerup and (player_circle.colliderect(cloudius.rect) and eaten_inimigo[0]):
                if lives > 0:
                    lives -= 1
                    startup_counter = 0
                    player_x = 450
                    player_y = 663
                    direction = 0
                    direction_command = 0
                    cloudius_x = 56
                    cloudius_y = 58
                    cloudius_direction = 0
                    ping_x = 400
                    ping_y = 438
                    ping_direction = 2
                    glitch_x = 440
                    glitch_y = 438
                    glitch_direction = 2
                    kernel_x = 440
                    kernel_y = 438
                    kernel_direction = 2
                    eaten_inimigo = [False, False, False, False]
                    cloudius_dead = False
                    ping_dead = False
                    glitch_dead = False
                    kernel_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and (player_circle.colliderect(ping.rect) and eaten_inimigo[1] and not ping.dead):
        if lives > 0:
            lives -= 1
            startup_counter = 0
            powerup = False
            powerup_count = 0
            player_x = 450
            player_y = 663
            direction = 0
            direction_command = 0
            cloudius_x = 56
            cloudius_y = 58
            cloudius_direction = 0
            ping_x = 400
            ping_y = 438
            ping_direction = 2
            glitch_x = 440
            glitch_y = 438
            glitch_direction = 2
            kernel_x = 440
            kernel_y = 438
            kernel_direction = 2
            eaten_inimigo = [False, False, False, False]
            cloudius_dead = False
            ping_dead = False
            glitch_dead = False
            kernel_dead = False
            if powerup and (player_circle.colliderect(cloudius.rect) and eaten_inimigo[0]):
                if lives > 0:
                    lives -= 1
                    startup_counter = 0
                    player_x = 450
                    player_y = 663
                    direction = 0
                    direction_command = 0
                    cloudius_x = 56
                    cloudius_y = 58
                    cloudius_direction = 0
                    ping_x = 400
                    ping_y = 438
                    ping_direction = 2
                    glitch_x = 440
                    glitch_y = 438
                    glitch_direction = 2
                    kernel_x = 440
                    kernel_y = 438
                    kernel_direction = 2
                    eaten_inimigo = [False, False, False, False]
                    cloudius_dead = False
                    ping_dead = False
                    glitch_dead = False
                    kernel_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and (player_circle.colliderect(glitch.rect) and eaten_inimigo[2] and not glitch.dead):
        if lives > 0:
            lives -= 1
            startup_counter = 0
            powerup = False
            powerup_count = 0
            player_x = 450
            player_y = 663
            direction = 0
            direction_command = 0
            cloudius_x = 56
            cloudius_y = 58
            cloudius_direction = 0
            ping_x = 400
            ping_y = 438
            ping_direction = 2
            glitch_x = 440
            glitch_y = 438
            glitch_direction = 2
            kernel_x = 440
            kernel_y = 438
            kernel_direction = 2
            eaten_inimigo = [False, False, False, False]
            cloudius_dead = False
            ping_dead = False
            glitch_dead = False
            kernel_dead = False
            if powerup and (player_circle.colliderect(cloudius.rect) and eaten_inimigo[0]):
                if lives > 0:
                    lives -= 1
                    startup_counter = 0
                    player_x = 450
                    player_y = 663
                    direction = 0
                    direction_command = 0
                    cloudius_x = 56
                    cloudius_y = 58
                    cloudius_direction = 0
                    ping_x = 400
                    ping_y = 438
                    ping_direction = 2
                    glitch_x = 440
                    glitch_y = 438
                    glitch_direction = 2
                    kernel_x = 440
                    kernel_y = 438
                    kernel_direction = 2
                    eaten_inimigo = [False, False, False, False]
                    cloudius_dead = False
                    ping_dead = False
                    glitch_dead = False
                    kernel_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and (player_circle.colliderect(kernel.rect) and eaten_inimigo[3] and not kernel.dead):
        if lives > 0:
            lives -= 1
            startup_counter = 0
            powerup = False
            powerup_count = 0
            player_x = 450
            player_y = 663
            direction = 0
            direction_command = 0
            cloudius_x = 56
            cloudius_y = 58
            cloudius_direction = 0
            ping_x = 400
            ping_y = 438
            ping_direction = 2
            glitch_x = 440
            glitch_y = 438
            glitch_direction = 2
            kernel_x = 440
            kernel_y = 438
            kernel_direction = 2
            eaten_inimigo = [False, False, False, False]
            cloudius_dead = False
            ping_dead = False
            glitch_dead = False
            kernel_dead = False
            if powerup and (player_circle.colliderect(cloudius.rect) and eaten_inimigo[0]):
                if lives > 0:
                    lives -= 1
                    startup_counter = 0
                    player_x = 450
                    player_y = 663
                    direction = 0
                    direction_command = 0
                    cloudius_x = 56
                    cloudius_y = 58
                    cloudius_direction = 0
                    ping_x = 400
                    ping_y = 438
                    ping_direction = 2
                    glitch_x = 440
                    glitch_y = 438
                    glitch_direction = 2
                    kernel_x = 440
                    kernel_y = 438
                    kernel_direction = 2
                    eaten_inimigo = [False, False, False, False]
                    cloudius_dead = False
                    ping_dead = False
                    glitch_dead = False
                    kernel_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(cloudius.rect) and not cloudius.dead and not eaten_inimigo[0]:
        cloudius_dead = True
        eaten_inimigo[0] = True
        score += (2 * eaten_inimigo.count(True)) * 100
    if powerup and player_circle.colliderect(ping.rect) and not ping.dead and not eaten_inimigo[1]:
        ping_dead = True
        eaten_inimigo[1] = True
        score += (2 * eaten_inimigo.count(True)) * 100
    if powerup and player_circle.colliderect(glitch.rect) and not glitch.dead and not eaten_inimigo[2]:
        glitch_dead = True
        eaten_inimigo[2] = True
        score += (2 * eaten_inimigo.count(True)) * 100
    if powerup and player_circle.colliderect(kernel.rect) and not kernel.dead and not eaten_inimigo[3]:
        kernel_dead = True
        eaten_inimigo[3] = True
        score += (2 * eaten_inimigo.count(True)) * 100


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cloudius.running = False
            ping.running = False
            glitch.running = False
            kernel.running = False
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT and turns_allowed[0]:
                direction_command = 0
            if event.key == pygame.K_LEFT and turns_allowed[1]:
                direction_command = 1
            if event.key == pygame.K_UP and turns_allowed[2]:
                direction_command = 2
            if event.key == pygame.K_DOWN and turns_allowed[3]:
                direction_command = 3
            if event.key == pygame.K_SPACE and (game_over or game_won):
                lives -= 1
                startup_counter = 0
                powerup = False
                powerup_count = 0
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                cloudius_x = 56
                cloudius_y = 58
                cloudius_direction = 0
                ping_x = 400
                ping_y = 438
                ping_direction = 2
                glitch_x = 440
                glitch_y = 438
                glitch_direction = 2
                kernel_x = 440
                kernel_y = 438
                kernel_direction = 2
                eaten_inimigo = [False, False, False, False]
                cloudius_dead = False
                ping_dead = False
                glitch_dead = False
                kernel_dead = False
                score = 0
                lives = 3
                level = copy.deepcopy(boards)
                game_over = False
                game_won = False


    if event.type == pygame.KEYUP:
        if event.key == pygame.K_RIGHT and direction_command == 0:
            direction_command = direction
        if event.key == pygame.K_LEFT and direction_command == 1:
            direction_command = direction
        if event.key == pygame.K_UP and direction_command == 2:
            direction_command = direction
        if event.key == pygame.K_DOWN and direction_command == 3:
            direction_command = direction

    for i in range(4):
        if direction_command == i and turns_allowed[i]:
             direction = i

    if player_x > WIDTH:
        player_x = 45
    elif player_x < 0:
        player_x = WIDTH - 45

    if  cloudius.in_box and cloudius_dead:
        cloudius_dead = False
    if  ping.in_box and ping_dead:
        ping_dead = False
    if  kernel.in_box and kernel_dead:
        kernel_dead = False
    if  glitch.in_box and glitch_dead:
        glitch_dead = False
    pygame.display.flip()

pygame.quit()
import copy
import threading
import time

from board import boards
import pygame
import math

pygame.init()
inimigo_lock = threading.RLock()

#confi jogo
# tamanho do "console" do jogo
WIDTH = 900
HEIGHT = 950
screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font('freesansbold.ttf', 20)
level_inicial = boards
level = copy.deepcopy(boards)
color = 'orange'
PI = math.pi

#imgs
player_images = []
for i in range (1, 3):
    player_images.append(pygame.transform.scale(pygame.image.load(f'assets/{i}.png'), (45, 45)))
nuvem_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/nuvem.png'), (45, 45))
redes_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/redes.png'), (45, 45))
computacional_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/computacional.png'), (45, 45))
operacional_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/operacional.png'), (45, 45))
check_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/check.png'), (45, 45))
turbo_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/turbo.png'), (45, 45))

#variaveis player
# posição inicial Bia
player_x = 450
player_y = 663
direction = 0
direction_command = 0
player_speed = 3
counter = 0
flicker = 0

# variaveis inimigos
inimigo_speeds = [2, 2, 2, 2]
eaten_inimigo = [False, False, False, False]
targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]

# posição inicial inimigos
#nuvem_x = 56
#nuvem_y = 58
#nuvem_direction = 0
#redes_x = 400
#redes_y = 438
#redes_direction = 2
#computacional_x = 440
#computacional_y = 438
#computacional_direction = 2
#operacional_x = 440
#operacional_y = 438
#operacional_direction = 2
# direita, esquerda, cima, baixo


# defi jogo
score = 0
powerup = False
powerup_count = 0
moving = False
lives = 3
startup_counter = 0
game_over = False
game_won = False

#nuvem_dead = False
#redes_dead = False
#computacional_dead = False
#operacional_dead = False
#nuvem_box = False
#redes_box = False
#computacional_box = False
#operacional_box = False

class Inimigo:
    def __init__(self, x_coord, y_coord, target, speed, img, direction, dead, box, id):
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22
        self.target = (0,0)
        self.speed = speed
        self.img = img
        self.direction = direction
        self.dead = dead
        self.in_box = box
        self.id = id
        self.turns = [False, False, False, False]
        self.rect = pygame.Rect(self.x_pos, self.y_pos, 45, 45)
        self.running = True
        self.thread = threading.Thread(target = self.move)
        self.thread.daemon = True
        self.thread.start()

    def draw(self):
        if (not powerup and not self.dead) or (eaten_inimigo[self.id] and powerup and not self.dead):
            screen.blit(self.img, (self.x_pos,self.y_pos))
        elif powerup and not self.dead and not eaten_inimigo[self.id]:
            screen.blit(turbo_img, (self.x_pos,self.y_pos))
        else:
            screen.blit(check_img, (self.x_pos,self.y_pos))
        self.rect = pygame.rect.Rect(self.x_pos, self.y_pos, 45, 45)
        return self.rect


   #def run_nuvem(self):
    #    while self.running:
     #       with inimigo_lock:
      #          if moving and not game_over and not game_won:
       #             if not nuvem_dead and not self.in_box:
        #                nuvem_x, nuvem_y, nuvem_direction = self.move_nuvem()
         #           else:
          #              nuvem_x, nuvem_y, nuvem_direction = self.move_operacional()


    #def run_redes(self):
     #   while self.running:
      #      with inimigo_lock:
       #         if moving and not game_over and not game_won:
        #            if not redes_dead and not self.in_box:
         #               redes_x, redes_y, redes_direction = self.move_redes()
          #          else:
           #             redes_x, redes_y, redes_direction = self.move_operacional()


   # def run_computacional(self):
    #    while self.running:
     #       with inimigo_lock:
      #          if moving and not game_over and not game_won:
       #             if not computacional_dead and not self.in_box:
        #                computacional_x, computacional_y, computacional_direction = self.move_computacional()
         #           else:
          #              computacional_x, computacional_y, computacional_direction = self.move_operacional()


   # def run_operacional(self):
    #    while self.running:
     #       with inimigo_lock:
      #          if moving and not game_over and not game_won:
       #             operacional_x, operacional_y, operacional_direction = self.move_operacional()


    def check_collisions(self): # D, E, C, B
        cell_height = (HEIGHT - 50) // 32
        cell_width = (WIDTH // 30)
        margem = 15
        #linha = max(0, min((self.center_y) // cell_height, len(level) - 1))
        #coluna = max(0, min((self.center_x) // cell_width, len(level[0]) - 1))
        '''self.turns = [False, False, False, False]
        if 0 < self.center_x // 30 < 29:
            if level[linha][coluna] == 9:
                self.turns[2] = True
            if level[linha][coluna] < 3 \
                or level[linha][coluna] == 9 and (self.dead or self.in_box):
                self.turns[1] = True
            if level[linha][coluna] < 3 \
                or level[linha][coluna] == 9 and (self.dead or self.in_box):
                self.turns[0] = True
            if level[linha][coluna] < 3 \
                or level[linha][coluna] == 9 and (self.dead or self.in_box):
                self.turns[3] = True
            if level[linha][coluna] < 3 \
                or level[linha][coluna] == 9 and (self.dead or self.in_box):
                self.turns[2] = True

            if self.direction == 2 or self.direction == 3:
                if 12 <= self.center_x % cell_width <= 18:
                    if level[linha][coluna] < 3 \
                        or (level[linha][coluna] == 9 and (self.dead or self.in_box)):
                        self.turns[3] = True
                    if level[linha][coluna] < 3 \
                        or (level[linha][coluna] == 9 and (self.dead or self.in_box)):
                        self.turns[2] = True
                if 12 <= self.center_y % cell_height <= 18:
                    if level[linha][coluna] < 3 \
                        or (level[linha][coluna] == 9 and (self.dead or self.in_box)):
                        self.turns[1] = True
                    if level[linha][coluna] < 3 \
                        or (level[linha][coluna] == 9 and (self.dead or self.in_box)):
                        self.turns[0] = True

            if self.direction == 0 or self.direction == 1:
                if 12 <= self.center_x % cell_width <= 18:
                    if level[linha][coluna] < 3 \
                        or (level[linha][coluna] == 9 and (self.dead or self.in_box)):
                        self.turns[3] = True
                    if level[linha][coluna] < 3 \
                        or (level[linha][coluna] == 9 and (self.dead or self.in_box)):
                        self.turns[2] = True
                if 12 <= self.center_y % cell_height <= 18:
                    if level[linha][coluna] < 3 \
                        or (level[linha][coluna] == 9 and (self.dead or self.in_box)):
                        self.turns[1] = True
                    if level[linha][coluna] < 3 \
                        or (level[linha][coluna] == 9 and (self.dead or self.in_box)):
                        self.turns[0] = True
        else:
            self.turns[0] = True
            self.turns[1] = True
        if 350 <= self.x_pos < 550 and 370 < self.y_pos < 480:
            self.in_box = True
        else:
            self.in_box = False
        return self.turns, self.in_box'''

        cell_h = (HEIGHT - 50) // 32
        cell_w = WIDTH // 30
        linha = max(0, min(int((self.y_pos + 22) // cell_h), len(level) - 1))
        coluna = max(0, min(int((self.x_pos + 22) // cell_w), len(level[0]) - 1))
        return level[linha][coluna] < 3

    def check_turns(self):
        cell_h = (HEIGHT - 50) // 32
        cell_w = WIDTH // 30
        margem = 15

        linha = int((self.y_pos + 22) // cell_h)
        coluna = int((self.x_pos + 22) // cell_w)

        turns = [False, False, False, False]  # [direita, esquerda, cima, baixo]

        if coluna + 1 < len(level[0]):
            if level[linha][coluna + 1] < 3 or level[linha][coluna + 1] == 9:
                turns[0] = True
        if coluna - 1 >= 0:
            if level[linha][coluna - 1] < 3 or level[linha][coluna - 1] == 9:
                turns[1] = True
        if linha - 1 >= 0:
            if level[linha - 1][coluna] < 3 or level[linha - 1][coluna] == 9:
                turns[2] = True
        if linha + 1 < len(level):
            if level[linha + 1][coluna] < 3 or level[linha + 1][coluna] == 9:
                turns[3] = True

        return turns

    def move(self):
        while True:
            time.sleep(0.02)
            with inimigo_lock:
                if not moving or game_over:
                    continue

                self.target = targets[self.id]
                dx = self.target[0] - self.x_pos
                dy = self.target[1] - self.y_pos

                turns = self.check_turns()

                # Escolher eixo prioritário
                if abs(dx) > abs(dy):
                    if dx > 0 and turns[0]:
                        self.x_pos += self.speed
                    elif dx < 0 and turns[1]:
                        self.x_pos -= self.speed
                    elif dy > 0 and turns[3]:
                        self.y_pos += self.speed
                    elif dy < 0 and turns[2]:
                        self.y_pos -= self.speed
                else:
                    if dy > 0 and turns[3]:
                        self.y_pos += self.speed
                    elif dy < 0 and turns[2]:
                        self.y_pos -= self.speed
                    elif dx > 0 and turns[0]:
                        self.x_pos += self.speed
                    elif dx < 0 and turns[1]:
                        self.x_pos -= self.speed

                self.x = max(0, min(self.x_pos, WIDTH - 45))
                self.y = max(0, min(self.y_pos, HEIGHT - 50))

                print(f"Inimigo {self.id} - pos: ({self.x_pos:.1f}, {self.y_pos:.1f}) target: {self.target}")

    def update_target(self):
        with inimigo_lock:
            self.target = targets[self.id]
            #print(f"Inimigo {self.id} target atualizado para {self.target}")

    def update_position(self):
        if self.id == 0:
            self.x_pos, self.y_pos, self.direction = self.move_nuvem()
        elif self.id == 1:
            self.x_pos, self.y_pos, self.direction = self.move_redes()
        elif self.id == 2:
            self.x_pos, self.y_pos, self.direction = self.move_computacional()
        elif self.id == 3:
            self.x_pos, self.y_pos, self.direction = self.move_operacional()

    def move_operacional(self): # vira sempre que for vantajoso para perseguição
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

            self.x_pos = max(-30, min(self.x_pos, WIDTH + 30))
            self.y_pos = max(-30, min(self.y_pos, HEIGHT + 30))

            return self.x_pos, self.y_pos, self.direction

    def move_nuvem(self): # vira sempre que colidir com paredes, caso contrário continua reto
     # D, E, C, B
     with inimigo_lock:
         if self.direction == 0 and self.turns[0]:  # direita
             self.x_pos += self.speed
         elif self.direction == 1 and self.turns[1]:  # esquerda
             self.x_pos -= self.speed
         elif self.direction == 2 and self.turns[2]:  # cima
             self.y_pos -= self.speed
         elif self.direction == 3 and self.turns[3]:  # baixo
             self.y_pos += self.speed
         else:
             # Colidiu com parede — precisa virar
             for i in range(4):  # direita, esquerda, cima, baixo
                 if self.turns[i]:
                     self.direction = i
                     break

             # Após mudar a direção, aplica movimento
             if self.direction == 0 and self.turns[0]:
                 self.x_pos += self.speed
             elif self.direction == 1 and self.turns[1]:
                 self.x_pos -= self.speed
             elif self.direction == 2 and self.turns[2]:
                 self.y_pos -= self.speed
             elif self.direction == 3 and self.turns[3]:
                 self.y_pos += self.speed

             # Teleporte horizontal (túnel)
         if self.x_pos < -30:
             self.x_pos = 900
         elif self.x_pos > 900:
             self.x_pos -= 30

         return self.x_pos, self.y_pos, self.direction

    def move_redes(self): # vira para cima ou para baixo qualquer momento para perseguir, mas para esquerda ou para direita somente em colisões
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

    def move_computacional(self): # vira para a esquera ou para a direita sempre que for vantajoso para perseguição, mas para cima ou para baixo apenas em cplisões
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
    with inimigo_lock:
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

def get_targets():
    with inimigo_lock:
        runaway_x = 900 if player_x < 450 else 0
        runaway_y = 900 if player_y < 450 else 0
        return_target = (380, 400)
        targets = []

        for inimigo in [nuvem, redes, computacional, operacional]:
            if powerup:
                if not inimigo.dead and not eaten_inimigo[inimigo.id]:
                   if inimigo.id == 0:
                       targets.append((runaway_x, runaway_y))
                   elif inimigo.id == 1:
                        targets.append((runaway_x, player_y))
                   elif inimigo.id == 2:
                       targets.append((player_x, runaway_y))
                   elif inimigo.id == 3:
                       targets.append((450, 450))
                elif not inimigo.dead and eaten_inimigo[inimigo.id]:
                    if 340 < inimigo.x_pos < 560 and 340 < inimigo.y_pos < 500:
                        targets.append((400, 100))
                    else:
                        targets.append((player_x, player_y))
                else:
                    targets.append(return_target)
            else:
                if not inimigo.dead:
                    if inimigo.id == 0:
                        targets.append((player_x, player_y))
                    elif inimigo.id == 1:
                        targets.append((
                            min(max(0, player_x), WIDTH - 50),
                            min(max(0, player_y - 100), HEIGHT - 100)
                        ))
                    elif inimigo.id == 2:
                        targets.append((
                            min(max(0, player_x + 100), WIDTH - 50),
                            min(max(0, player_y), HEIGHT - 100)
                        ))
                    elif inimigo.id == 3:
                        targets.append((
                            min(max(0, player_x - 100), WIDTH - 50),
                            min(max(0, player_y), HEIGHT - 100)
                        ))

        return targets


nuvem = Inimigo(56, 58 , targets[0], inimigo_speeds[0], nuvem_img, 0, False, False, 0)
redes = Inimigo(400, 438, targets[1], inimigo_speeds[1], redes_img, 1, False, False, 1)
computacional = Inimigo(400, 438, targets[2], inimigo_speeds[2], computacional_img, 2, False, False, 2)
operacional = Inimigo(400, 438, targets[3], inimigo_speeds[3], operacional_img, 3, False, False, 3)

run = True

while run:
    timer.tick(fps)
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
    if startup_counter  < 30 and not game_over and not game_won:
        moving = False
        startup_counter += 1
    else:
        moving = True

    screen.fill('black')
    draw_board(level)
    center_x = player_x + 25
    center_y = player_y + 25

    targets = get_targets()
    turns_allowed = check_position(center_x, center_y)

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
    #if nuvem_dead:
     #   inimigo_speeds[0] = 4
    #if redes_dead:
     #   inimigo_speeds[1] = 4
    #if computacional_dead:
     #   inimigo_speeds[2] = 4
    #if operacional_dead:
        inimigo_speeds[3] = 4

    game_won = True
    for i in range(len(level)):
        if 1 in level[i] or 2 in level[i]:
            game_won = False

    player_circle = pygame.draw.circle(screen, 'black', (center_x, center_y), 21, 2)
    draw_player()


    with inimigo_lock:
        nuvem.rect = nuvem.draw()
        redes.rect = redes.draw()
        computacional.rect = computacional.draw()
        operacional.rect = operacional.draw()

    draw_alter()

    if moving:
        player_x, player_y = move_player(player_x, player_y)

    score, powerup, powerup_count, eaten_inimigo = check_collisions(score, powerup, powerup_count, eaten_inimigo)

    if not powerup:
        if (player_circle.colliderect(nuvem.rect) and not nuvem.dead) or (player_circle.colliderect(redes.rect) and not redes.dead) or (player_circle.colliderect(operacional.rect) and not operacional.dead) or (player_circle.colliderect(computacional.rect) and not computacional.dead):
            if lives > 0:
                lives -= 1
                startup_counter = 0
                powerup = False
                powerup_count = 0
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                nuvem.x_pos = 56
                nuvem.y_pos = 58
                nuvem.direction = 0
                redes.x_pos = 400
                redes.y_pos = 438
                redes.direction = 2
                computacional.x_pos = 440
                computacional.y_pos = 438
                computacional.direction = 2
                operacional.x_pos = 440
                operacional.y_pos = 438
                operacional.direction = 2
                eaten_inimigo = [False, False, False, False]
                nuvem.dead = False
                redes.dead = False
                computacional.dead = False
                operacional.dead = False
            else:
                game_over = True
                moving = False
                startup_counter = 0

    if powerup:
        if player_circle.colliderect(nuvem.rect) and not nuvem.dead and not eaten_inimigo[0]:
            nuvem.dead = True
            eaten_inimigo[0] = True
            score += (2 * eaten_inimigo.count(True)) * 100
        if player_circle.colliderect(redes.rect) and not redes.dead and not eaten_inimigo[1]:
            redes.dead = True
            eaten_inimigo[1] = True
            score += (2 * eaten_inimigo.count(True)) * 100
        if player_circle.colliderect(computacional.rect) and not computacional.dead and not eaten_inimigo[2]:
            computacional.dead = True
            eaten_inimigo[2] = True
            score += (2 * eaten_inimigo.count(True)) * 100
        if player_circle.colliderect(operacional.rect) and not operacional.dead and not eaten_inimigo[3]:
            operacional.dead = True
            eaten_inimigo[3] = True
            score += (2 * eaten_inimigo.count(True)) * 100


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            nuvem.running = False
            redes.running = False
            computacional.running = False
            operacional.running = False
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
                nuvem.x_pos = 56
                nuvem.y_pos = 58
                nuvem.direction = 0
                redes.x_pos = 400
                redes.y_pos = 438
                redes.direction = 2
                computacional.x_pos = 440
                computacional.y_pos = 438
                computacional.direction = 2
                operacional.x_pos = 440
                operacional.y_pos = 438
                operacional.direction = 2
                eaten_inimigo = [False, False, False, False]
                nuvem.dead = False
                redes.dead = False
                computacional.dead = False
                operacional.dead = False
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
    pygame.display.flip()

nuvem.running = False
redes.running = False
computacional.running = False
operacional.running = False

nuvem.thread.join()
redes.thread.join()
computacional.thread.join()
operacional.thread.join()

pygame.quit()
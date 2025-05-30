import copy
import threading
import time
from board import boards
import pygame
import math

pygame.init()
inimigo_lock = threading.Lock()

#confi jogo
# tamanho do "console" do jogo
WIDTH = 900
HEIGHT = 950
screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font('freesansbold.ttf', 20)
font2 = pygame.font.Font('freesansbold.ttf', 30)
level_inicial = boards
level = copy.deepcopy(boards)
color = 'orange'
PI = math.pi

#imgs
player_images = []
for i in range (1, 3):
    player_images.append(pygame.transform.scale(pygame.image.load(f'assets/{i}.png'), (45, 45)))
cloudius_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/nuvem.png'), (45, 45))
ping_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/redes.png'), (45, 45))
glitch_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/computacional.png'), (45, 45))
kernel_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/operacional.png'), (45, 45))
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

# defi jogo
score = 0
powerup = False
powerup_count = 0
moving = False
lives = 3
startup_counter = 0
game_over = False
game_won = False


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

        self.box_center_x = 450
        self.box_center_y = 438

        box_xmax, box_xmin = 350,550
        box_ymax, box_ymin = 370,480
        initialy_in_box = (box_xmin <= self.x_pos < box_xmax and box_ymin < self.y_pos < box_ymax)

        self.left_box = (id == 0)


        if id == 0:
            self.thread = threading.Thread(target=self.run_cloudius_thread)
        elif id == 1:
            self.thread = threading.Thread(target=self.run_ping_thread)
        elif id == 2:
            self.thread = threading.Thread(target=self.run_glitch_thread)
        elif id == 3:
            self.thread = threading.Thread(target=self.run_kernel_thread)


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

    def check_collisions(self): # D, E, C, B
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22

        cell_h = (HEIGHT - 50) // 32
        cell_w = WIDTH // 30
        linha = max(0, min(int((self.y_pos + 22) // cell_h), len(level) - 1))
        coluna = max(0, min(int((self.x_pos + 22) // cell_w), len(level[0]) - 1))

        box_xmin, box_xmax = 350, 550
        box_ymin, box_ymax = 370, 480

        is_in_box = (box_xmin <= self.x_pos < box_xmax and box_ymin < self.y_pos < box_ymax)

        if is_in_box:
            self.in_box = True
            if self.dead:
                self.left_box = False
        else:
            self.in_box = False
            self.left_box = True

        return self.check_turns()

    def check_turns(self):
        cell_height = (HEIGHT - 50) // 32
        cell_width = WIDTH // 30
        margem = 15

        linha = int((self.y_pos + 22) // cell_height)
        coluna = int((self.x_pos + 22) // cell_width)

        turns = [False, False, False, False]  # direita, esquerda, cima, baixo

        # verifica se pode virar d, e, c, b
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

        if 10 <= self.center_x % cell_width <= 16:
            if level[(self.center_y + margem) // cell_height][self.center_x // cell_width] < 3:
                turns[3] = True
            if level[(self.center_y - margem) // cell_height][self.center_x // cell_width] < 3:
                turns[2] = True
        if 10 <= self.center_y % cell_height <= 16:
            if level[self.center_y // cell_height][(self.center_x + margem) // cell_width] < 3:
                turns[0] = True
            if level[self.center_y // cell_height][(self.center_x - margem) // cell_width] < 3:
                turns[1] = True

        return turns

    def move_to_box(self):
        target_x, target_y = self.box_center_x, self.box_center_y

        if abs(self.x_pos - target_x) > self.speed:
            if self.x_pos < target_x:
                self.x_pos += self.speed
            elif self.x_pos > target_x:
                self.x_pos -= self.speed
        else:
            self.x_pos = target_x

        if abs(self.y_pos - target_y) > self.speed:
            if self.y_pos < target_y:
                self.y_pos += self.speed
            elif self.y_pos > target_y:
                self.y_pos -= self.speed
        else:
            self.y_pos = target_y

    def move_out_box(self):
        exit_y = 350
        if self.y_pos > exit_y and self.turns[2]:
            self.y_pos -= self.speed
            self.direction = 2
        elif self.y_pos <+ exit_y:
            self.in_box = False
            self.left_box = True


    def run_cloudius_thread(self):
        while self.running:
            time.sleep(0.02)
            with inimigo_lock:
                if moving and not game_over and not game_won:
                    self.turns = self.check_collisions()
                if self.dead:
                    self.move_to_box()
                elif self.in_box:
                    self.move_out_box()
                else:
                    self.move_cloudius()

    def run_ping_thread(self):
        while self.running:
            time.sleep(0.02)
            with inimigo_lock:
                if moving and not game_over and not game_won:
                    self.turns = self.check_collisions()
                    if self.dead:
                        self.move_to_box()
                    elif self.in_box:
                        self.move_out_box()
                    else:
                        self.move_ping()

    def run_glitch_thread(self):
        while self.running:
            time.sleep(0.02)
            with inimigo_lock:
                if moving and not game_over and not game_won:
                    self.turns = self.check_collisions()
                if self.dead:
                    self.move_to_box()
                elif self.in_box:
                    self.move_out_box()
                else:
                    self.move_glitch() # voltar para a caixa quando tá morto

    def run_kernel_thread(self):
        while self.running:
            time.sleep(0.02)
            with inimigo_lock:
                if moving and not game_over and not game_won:
                    self.turns = self.check_collisions()
                    if self.dead:
                        self.move_to_box()
                    elif self.in_box:
                        self.move_out_box()
                    else:
                        self.move_kernel()

    def update_target(self, player_x, player_y):
        with inimigo_lock:
            self.target = (player_x, player_y)
            print(f"Inimigo {self.id} target atualizado para {self.target}")

    def update_position(self):
        if self.id == 0:
            self.x_pos, self.y_pos, self.direction = self.move_cloudius()
        elif self.id == 1:
            self.x_pos, self.y_pos, self.direction = self.move_ping()
        elif self.id == 2:
            self.x_pos, self.y_pos, self.direction = self.move_glitch()
        elif self.id == 3:
            self.x_pos, self.y_pos, self.direction = self.move_kernel()

    def move_kernel(self): # vira sempre que for vantajoso para perseguição
        #semáforo
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22

        target_x, target_y = self.target
        if self.dead:
            if self.x_pos < target_x:
                self.x_pos += self.speed
            elif self.x_pos > target_x:
                self.x_pos -= self.speed

            if self.y_pos < target_y:
                self.y_pos += self.speed
            elif self.y_pos > target_y:
                self.y_pos -= self.speed

            return

        dx = self.target[0] - self.x_pos
        dy = self.target[1] - self.y_pos
         # D, E, C, B

        if abs(dx) > abs(dy): # mov horizontal
            if dx > 0 and self.turns[0]:
                self.x_pos += self.speed
                self.direction = 0
            elif dx < 0 and self.turns[1]:
                self.x_pos -= self.speed
                self.direction = 1
            elif dy > 0 and self.turns[3]:
                self.y_pos += self.speed
                self.direction = 3
            elif dy < 0 and self.turns[2]:
                self.y_pos -= self.speed
                self.direction = 2
            else:
                for i in range(4):
                    if self.turns[i]:
                        self.direction = i
                        if self.direction == 0:
                            self.x_pos += self.speed
                        elif self.direction == 1:
                            self.x_pos -= self.speed
                        elif self.direction == 2:
                            self.y_pos -= self.speed
                        elif direction == 3:
                            self.y_pos += self.speed
                        break
        else: # mov vertical
            if dy > 0 and self.turns[3]:
                self.y_pos += self.speed
                self.direction = 3
            elif dy < 0 and self.turns[2]:
                self.y_pos -= self.speed
                self.direction = 2
            elif dx > 0 and self.turns[0]:
                self.x_pos += self.speed
                self.direction = 0
            elif dx < 0 and self.turns[1]:
                self.x_pos -= self.speed
                self.direction = 1

        #teletranspote tunel
        if self.x_pos < -30:
            self.x_pos = WIDTH - 45
        elif self.x_pos > WIDTH - 15:
            self.x_pos = -25

    def move_cloudius(self): # vira sempre que colidir com paping, caso contrário continua reto
     # D, E, C, B

     self.center_x = self.x_pos + 22
     self.center_y = self.y_pos + 22


     if self.direction == 0 and self.turns[0]:  # direita
         self.x_pos += self.speed
     elif self.direction == 1 and self.turns[1]:  # esquerda
         self.x_pos -= self.speed
     elif self.direction == 2 and self.turns[2]:  # cima
         self.y_pos -= self.speed
     elif self.direction == 3 and self.turns[3]:  # baixo
         self.y_pos += self.speed
     else:
         # Colidiu com papin — precisa virar
         new_direction = False
         for i in range(4):
             if self.turns[i]:
                 self.direction = i
                 new_direction = True
                 break

         if new_direction:
            if self.direction == 0:
                 self.x_pos += self.speed
            elif self.direction == 1:
                 self.x_pos -= self.speed
            elif self.direction == 2:
                 self.y_pos -= self.speed
            elif self.direction == 3:
                 self.y_pos += self.speed

         # Teleporte horizontal (túnel)
     if self.x_pos < -30:
         self.x_pos = 900
     elif self.x_pos > 900:
         self.x_pos -= 30

    def move_ping(self): # vira para cima ou para baixo qualquer momento para perseguir, mas para esquerda ou para direita somente em colisões
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22

        dx = self.target[0] - self.x_pos
        dy = self.target[1] - self.y_pos

        if dy > 0 and self.turns[3]:
            self.y_pos += self.speed
            self.direction = 3
        elif dy < 0 and self.turns[2]:
            self.y_pos -= self.speed
            self.direction = 2
        elif dx > 0 and self.turns[0]:
            self.x_pos += self.speed
            self.direction = 0
        elif dx < 0 and self.turns[1]:
            self.x_pos -= self.speed
            self.direction = 1
        else:
            for i in range(4):
                if self.turns[i]:
                    self.direction = i
                    if self.direction == 0:
                        self.x_pos += self.speed
                    elif self.direction == 1:
                        self.x_pos -= self.speed
                    elif self.direction == 2:
                        self.y_pos -= self.speed
                    elif direction == 3:
                        self.y_pos += self.speed
                    break

        if self.x_pos < -30:
            self.x_pos = WIDTH - 45
        elif self.x_pos > WIDTH - 15:
            self.x_pos = -25

    def move_glitch(self): # vira para a esquera ou para a direita sempre que for vantajoso para perseguição, mas para cima ou para baixo apenas em cplisões
        # D, E, C, B
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22

        dx = self.target[0] - self.x_pos
        dy = self.target[1] - self.y_pos

        if dx > 0 and self.turns[0]:
            self.x_pos += self.speed
            self.direction = 0
        elif dx < 0 and self.turns[1]:
            self.x_pos -= self.speed
            self.direction = 1
        elif dy > 0  and self.turns[3]:
            self.y_pos += self.speed
            self.direction = 3
        elif dy < 0  and self.turns[2]:
            self.y_pos -= self.speed
            self.direction = 2
        else:
            for i in range(4):
                if self.turns[i]:
                    self.direction = i
                    if self.direction == 0:
                        self.x_pos += self.speed
                    elif self.direction == 1:
                        self.x_pos -= self.speed
                    elif self.direction == 2:
                        self.y_pos -= self.speed
                    elif direction == 3:
                        self.y_pos += self.speed
                    break

        if self.x_pos < -30:
            self.x_pos = WIDTH - 45
        elif self.x_pos > WIDTH - 15:
            self.x_pos = -25



def draw_alter():
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 720))
    if powerup:
        pygame.draw.circle(screen, 'red', (140, 720), 15)
    for l in range(lives):
        screen.blit(pygame.transform.scale(player_images[1], (40,40)), (650 + l * 40, 705))
    if game_over:
        pygame.draw.rect(screen, 'dark gray', [50, 300, 800, 300], 0, 10)
        pygame.draw.rect(screen, 'orange', [70, 320, 760, 260], 0, 10)
        gameover_text1 = font2.render('Game Over!', True, 'red')
        gameover_text2 = font.render(' Aperte [espaço] para recomeçar!', True, 'red')
        gameover_rect1 = gameover_text1.get_rect(center=(900 // 2, 850 //2))
        gameover_rect2 = gameover_text2.get_rect(center=(900 // 2, 950 //2))
        screen.blit(gameover_text1, gameover_rect1)
        screen.blit(gameover_text2, gameover_rect2)
    if game_won:
        pygame.draw.rect(screen, 'white', [50, 300, 800, 300], 0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 320, 760, 260], 0, 10)
        gamewon_text1 = font2.render('Game Won!!!', True, 'yellow')
        gamewon_text2 = font.render('Aperte [espaço] para recomeçar!', True, 'yellow')
        gamewon_rect1 = gamewon_text1.get_rect(center=(900 // 2, 850 // 2))
        gamewon_rect2 = gamewon_text2.get_rect(center=(900 // 2, 950 // 2))
        screen.blit(gamewon_text1, gamewon_rect1)
        screen.blit(gamewon_text2, gamewon_rect2)

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

def get_targets(player_x, player_y):
    runaway_x = 900 if player_x < 450 else 0
    runaway_y = 900 if player_y < 450 else 0
    return_target = (380, 400)

    cloudiu_target = (0,0)
    pin_target = (0,0)
    glitc_target = (0,0)
    kerne_target = (0,0)

    if powerup:
        if not cloudius.dead and not eaten_inimigo[0]:
            cloudiu_target = (runaway_x, runaway_y)
        elif not cloudius.dead and eaten_inimigo[0]:
            if 340 < cloudius.x_pos < 560 and 340 < cloudius.y_pos < 500:
                cloudiu_target = (400, 100)
            else:
                cloudiu_target = (player_x, player_y)
        else:
            cloudiu_target = return_target
    else:
        if not cloudius.dead:
            if 340 < cloudius.x_pos < 560 and 340 < cloudius.y_pos < 500:
                cloudiu_target = (400, 100)
            else:
                cloudiu_target = (player_x, player_y)
        else:
            cloudiu_target = return_target


    if powerup:
        if not ping.dead and not eaten_inimigo[1]:
            pin_target = (runaway_x, runaway_y)
        elif not ping.dead and eaten_inimigo[1]:
            if 340 < ping.x_pos < 560 and 340 < ping.y_pos < 500:
                pin_target = (400, 100)
            else:
                pin_target = (player_x, player_y)
        else:
            pin_target = return_target
    else:
        if not ping.dead:
            if 340 < ping.x_pos < 560 and 340 < ping.y_pos < 500:
                pin_target = (400, 100)
            else:
                pin_target = (player_x + 100, player_y - 100)
        else:
            pin_target = return_target

    if powerup:
        if not glitch.dead and not eaten_inimigo[2]:
            glitc_target = (player_x, runaway_y)
        elif not glitch.dead and eaten_inimigo[2]:
            if 340 < glitch.x_pos < 560 and 340 < glitch.y_pos < 500:
                glitc_target = (400, 100)
            else:
                glitc_target = (player_x, player_y)
        else:
            glitc_target = return_target
    else:
        if not glitch.dead:
            if 340 < glitch.x_pos < 560 and 340 < glitch.y_pos < 500:
                glitc_target = (400, 100)
            else:
                glitc_target = (player_x - 150, player_y + 50)
        else:
            glitc_target = return_target

    if powerup:
        if not kernel.dead and not eaten_inimigo[3]:
            kerne_target = (runaway_x, runaway_y)
        elif not kernel.dead and eaten_inimigo[3]:
            if 340 < kernel.x_pos < 560 and 340 < kernel.y_pos < 500:
                kerne_target = (400, 100)
            else:
                kerne_target = (player_x, player_y)
        else:
            kerne_target = return_target
    else:
        if not kernel.dead:
            if 340 < kernel.x_pos < 560 and 340 < kernel.y_pos < 500:
                kerne_target = (400, 100)
            else:
                kerne_target = (player_x - 150, player_y + 50)
        else:
            kerne_target = return_target

    return [cloudiu_target, pin_target, glitc_target, kerne_target]


cloudius = Inimigo(56, 58 , targets[0], inimigo_speeds[0], cloudius_img, 0, False, False, 0)
ping = Inimigo(400, 438, targets[1], inimigo_speeds[1], ping_img, 1, False, False, 1)
glitch = Inimigo(400, 438, targets[2], inimigo_speeds[2], glitch_img, 2, False, False, 2)
kernel = Inimigo(400, 438, targets[3], inimigo_speeds[3], kernel_img, 3, False, False, 3)

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

    # powerup
    if powerup == True and powerup_count < 600:
        powerup_count += 1
    elif powerup and powerup_count >= 600:
        powerup_count = 0
        powerup = False
        eaten_inimigo = [False, False, False, False]

    # inicio/reinicio
    if startup_counter  < 30 and not game_over and not game_won:
        moving = False
        startup_counter += 1
    else:
        moving = True

    screen.fill('black')
    draw_board(level)
    center_x = player_x + 25
    center_y = player_y + 25

    #velocidades
    if powerup:
        cloudius.speed = 1
        ping.speed = 1
        glitch.speed = 1
        kernel.speed = 1
    else:
        cloudius.speed = 2
        ping.speed = 2
        glitch.speed = 2
        kernel.speed = 2

    if eaten_inimigo[0]:
        cloudius.speed = 4
    if eaten_inimigo[1]:
        cloudius.speed = 4
    if eaten_inimigo[2]:
        cloudius.speed = 4
    if eaten_inimigo[3]:
        cloudius.speed = 4

    game_won = True
    for i in range(len(level)):
        if 1 in level[i] or 2 in level[i]:
            game_won = False

    player_circle = pygame.draw.circle(screen, 'black', (center_x, center_y), 21, 2)
    draw_player()

    target_atual = get_targets(player_x, player_y)
    cloudius.target = target_atual[0]
    ping.target = target_atual[1]
    glitch.target = target_atual[2]
    kernel.target = target_atual[3]

    turns_allowed = check_position(center_x, center_y)

    with inimigo_lock:
        cloudius.rect = cloudius.draw()
        ping.rect = ping.draw()
        glitch.rect = glitch.draw()
        kernel.rect = kernel.draw()

    draw_alter()

    if moving:
        player_x, player_y = move_player(player_x, player_y)

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
                cloudius.x_pos = 56
                cloudius.y_pos = 58
                cloudius.direction = 0
                ping.x_pos = 400
                ping.y_pos = 438
                ping.direction = 2
                glitch.x_pos = 440
                glitch.y_pos = 438
                glitch.direction = 2
                kernel.x_pos = 440
                kernel.y_pos = 438
                kernel.direction = 2
                eaten_inimigo = [False, False, False, False]
                cloudius.dead = False
                ping.dead = False
                glitch.dead = False
                kernel.dead = False
                cloudius.left_box = True
                ping.left_box = False
                glitch.left_box = False
                kernel.left_box = False
            else:
                game_over = True
                moving = False
                startup_counter = 0

    if powerup:
        if player_circle.colliderect(cloudius.rect) and not cloudius.dead and not eaten_inimigo[0]:
            cloudius.dead = True
            eaten_inimigo[0] = True
            score += (2 * eaten_inimigo.count(True)) * 100
        if player_circle.colliderect(ping.rect) and not ping.dead and not eaten_inimigo[1]:
            ping.dead = True
            eaten_inimigo[1] = True
            score += (2 * eaten_inimigo.count(True)) * 100
        if player_circle.colliderect(glitch.rect) and not glitch.dead and not eaten_inimigo[2]:
            glitch.dead = True
            eaten_inimigo[2] = True
            score += (2 * eaten_inimigo.count(True)) * 100
        if player_circle.colliderect(kernel.rect) and not kernel.dead and not eaten_inimigo[3]:
            kernel.dead = True
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
                lives = 3
                startup_counter = 0
                powerup = False
                powerup_count = 0
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                cloudius.x_pos = 56
                cloudius.y_pos = 58
                cloudius.direction = 0
                ping.x_pos = 400
                ping.y_pos = 438
                ping.direction = 2
                glitch.x_pos = 440
                glitch.y_pos = 438
                glitch.direction = 2
                kernel.x_pos = 440
                kernel.y_pos = 438
                kernel.direction = 2
                eaten_inimigo = [False, False, False, False]
                cloudius.dead = False
                ping.dead = False
                glitch.dead = False
                kernel.dead = False
                score = 0
                level = copy.deepcopy(boards)
                game_over = False
                game_won = False
                cloudius.left_box = True
                ping.left_box = False
                glitch.left_box = False
                kernel.left_box = False


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


    if cloudius.dead and cloudius.in_box:
        cloudius.dead = False
    if ping.dead and ping.in_box:
        ping.dead = False
    if glitch.dead and glitch.in_box:
        glitch.dead = False
    if kernel.dead and kernel.in_box:
        kernel.dead = False

    pygame.display.flip()

cloudius.running = False
ping.running = False
glitch.running = False
kernel.running = False

cloudius.thread.join()
ping.thread.join()
glitch.thread.join()
kernel.thread.join()

pygame.quit()
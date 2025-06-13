import copy
import threading
import time
from board import boards
import pygame
import math

pygame.init()
inimigo_lock = threading.Lock()

# Configurações do jogo
# Tamanho do "console" do jogo
WIDTH = 800
HEIGHT = 790
screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font('freesansbold.ttf', 20)
font2 = pygame.font.Font('freesansbold.ttf', 30)
level = copy.deepcopy(boards)
color = 'orange'
PI = math.pi

# Imagens
player_images = []
for i in range (1, 3):
    player_images.append(pygame.transform.scale(pygame.image.load(f'assets/{i}.png'), (45, 45)))
cloudius_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/nuvem.png'), (45, 45))
ping_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/redes.png'), (45, 45))
glitch_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/computacional.png'), (45, 45))
kernel_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/operacional.png'), (45, 45))
check_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/check.png'), (45, 45))
turbo_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/turbo.png'), (45, 45))

# Variáveis do jogador
player_x = WIDTH // 2
player_y = int(650 * (HEIGHT / 950))
direction = 0
direction_command = 0
player_speed = 3
counter = 0
flicker = 0

# Variáveis inimigos
inimigo_speeds = [2, 2, 2, 2]
eaten_inimigo = [False, False, False, False]
targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]

# Definições do jogo
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

        # Posição central da caixa dos inimigos
        self.box_center_x = WIDTH // 2
        self.box_center_y = HEIGHT // 2 + 30

        # Limites da caixa dos inimigos
        box_width = 200
        box_height = 110
        self.box_xmin = self.box_center_x - box_width // 2
        self.box_xmax = self.box_center_x + box_width // 2
        self.box_ymin = self.box_center_y - box_height // 2
        self.box_ymax = self.box_center_y + box_height // 2

        self.left_box = (id == 0) # Cloudius começa fora da caixa

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

        # Ajusta os limites da caixa dos inimigos
        is_in_box = (self.box_xmin <= self.x_pos < self.box_xmax and self.box_ymin < self.y_pos < self.box_ymax)

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
        exit_y = self.box_ymin - 50
        if self.y_pos > exit_y and self.turns[2]:
            self.y_pos -= self.speed
            self.direction = 2
        elif self.y_pos <= exit_y:
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
                    self.move_glitch()

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

        # D, E, C, B (Direita, Esquerda, Cima, Baixo)
        if abs(dx) > abs(dy): # Movimento horizontal preferencial
            if dx > 0 and self.turns[0]: # Se o alvo está à direita e pode virar
                self.x_pos += self.speed
                self.direction = 0
            elif dx < 0 and self.turns[1]: # Se o alvo está à esquerda e pode virar
                self.x_pos -= self.speed
                self.direction = 1
            elif dy > 0 and self.turns[3]: # Senão, tenta ir para baixo se puder
                self.y_pos += self.speed
                self.direction = 3
            elif dy < 0 and self.turns[2]: # Senão, tenta ir para cima se puder
                self.y_pos -= self.speed
                self.direction = 2
            else: # Se nenhuma das direções preferenciais funciona, tenta qualquer uma
                for i in range(4):
                    if self.turns[i]:
                        self.direction = i
                        if self.direction == 0:
                            self.x_pos += self.speed
                        elif self.direction == 1:
                            self.x_pos -= self.speed
                        elif self.direction == 2:
                            self.y_pos -= self.speed
                        elif self.direction == 3:
                            self.y_pos += self.speed
                        break
        else: # Movimento vertical preferencial
            if dy > 0 and self.turns[3]: # Se o alvo está abaixo e pode virar
                self.y_pos += self.speed
                self.direction = 3
            elif dy < 0 and self.turns[2]: # Se o alvo está acima e pode virar
                self.y_pos -= self.speed
                self.direction = 2
            elif dx > 0 and self.turns[0]: # Senão, tenta ir para direita se puder
                self.x_pos += self.speed
                self.direction = 0
            elif dx < 0 and self.turns[1]: # Senão, tenta ir para esquerda se puder
                self.x_pos -= self.speed
                self.direction = 1



    def move_cloudius(self): # vira sempre que colidir com paping, caso contrário continua reto
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

     # D, E, C, B (Direita, Esquerda, Cima, Baixo)
     if abs(dx) > abs(dy): # Movimento horizontal preferencial
         if dx > 0 and self.turns[0]:
             self.x_pos += self.speed
             self.direction = 0
         elif dx < 0 and self.turns[1]:
             self.x_pos -= self.speed
             self.direction = 1
         elif dy > 0 and self.turns[3]:
             self.y_pos += self.speed # CORRIGIDO: Usar self.y_pos
             self.direction = 3
         elif dy < 0 and self.turns[2]:
             self.y_pos -= self.speed # CORRIGIDO: Usar self.y_pos
             self.direction = 2
         else: # Se nenhuma das direções preferenciais funciona, tenta qualquer uma
             for i in range(4):
                 if self.turns[i]:
                     self.direction = i
                     if self.direction == 0:
                         self.x_pos += self.speed
                     elif self.direction == 1:
                         self.x_pos -= self.speed
                     elif self.direction == 2:
                         self.y_pos -= self.speed
                     elif self.direction == 3:
                         self.y_pos += self.speed
                     break
     else: # Movimento vertical preferencial
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

    def move_ping(self): # vira para cima ou para baixo qualquer momento para perseguir, mas para esquerda ou para direita somente em colisões
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22

        dx = self.target[0] - self.x_pos
        dy = self.target[1] - self.y_pos

        # Prioriza movimento vertical
        if dy > 0 and self.turns[3]:
            self.y_pos += self.speed
            self.direction = 3
        elif dy < 0 and self.turns[2]:
            self.y_pos -= self.speed
            self.direction = 2
        elif dx > 0 and self.turns[0]: # Se não puder mover verticalmente, tenta horizontal
            self.x_pos += self.speed
            self.direction = 0
        elif dx < 0 and self.turns[1]:
            self.x_pos -= self.speed
            self.direction = 1
        else: # Se nenhuma das direções preferenciais funciona, tenta qualquer uma
            for i in range(4):
                if self.turns[i]:
                    self.direction = i
                    if self.direction == 0:
                        self.x_pos += self.speed
                    elif self.direction == 1:
                        self.x_pos -= self.speed
                    elif self.direction == 2:
                        self.y_pos -= self.speed
                    elif self.direction == 3:
                        self.y_pos += self.speed
                    break

    def move_glitch(self): # vira para a esquerda ou para a direita sempre que for vantajoso para perseguição, mas para cima ou para baixo apenas em colisões
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22

        dx = self.target[0] - self.x_pos
        dy = self.target[1] - self.y_pos

        # Prioriza movimento horizontal
        if dx > 0 and self.turns[0]:
            self.x_pos += self.speed
            self.direction = 0
        elif dx < 0 and self.turns[1]:
            self.x_pos -= self.speed
            self.direction = 1
        elif dy > 0  and self.turns[3]: # Se não puder mover horizontalmente, tenta vertical
            self.y_pos += self.speed
            self.direction = 3
        elif dy < 0  and self.turns[2]:
            self.y_pos -= self.speed
            self.direction = 2
        else: # Se nenhuma das direções preferenciais funciona, tenta qualquer uma
            for i in range(4):
                if self.turns[i]:
                    self.direction = i
                    if self.direction == 0:
                        self.x_pos += self.speed
                    elif self.direction == 1:
                        self.x_pos -= self.speed
                    elif self.direction == 2:
                        self.y_pos -= self.speed
                    elif self.direction == 3:
                        self.y_pos += self.speed



def draw_alter():
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, HEIGHT - 30)) # Ajustado para o novo HEIGHT
    for l in range(lives):
        screen.blit(pygame.transform.scale(player_images[1], (40,40)), (WIDTH - 150 + l * 40, HEIGHT - 40))
    if game_over:
        pygame.draw.rect(screen, 'dark gray', [50, HEIGHT // 2 - 150, WIDTH - 100, 300], 0, 10)
        pygame.draw.rect(screen, 'orange', [70, HEIGHT // 2 - 130, WIDTH - 140, 260], 0, 10)
        gameover_text1 = font2.render('Game Over!', True, 'red')
        gameover_text2 = font.render(' Aperte [espaço] para recomeçar!', True, 'red')
        gameover_rect1 = gameover_text1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        gameover_rect2 = gameover_text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        screen.blit(gameover_text1, gameover_rect1)
        screen.blit(gameover_text2, gameover_rect2)
    if game_won:
        pygame.draw.rect(screen, 'white', [50, HEIGHT // 2 - 150, WIDTH - 100, 300], 0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, HEIGHT // 2 - 130, WIDTH - 140, 260], 0, 10)
        gamewon_text1 = font2.render('Game Won!!!', True, 'yellow')
        gamewon_text2 = font.render('Aperte [espaço] para recomeçar!', True, 'yellow')
        gamewon_rect1 = gamewon_text1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        gamewon_rect2 = gamewon_text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        screen.blit(gamewon_text1, gamewon_rect1)
        screen.blit(gamewon_text2, gamewon_rect2)

def check_collisions(scor, power, power_count, eaten_inimigo):
    cell_height = (HEIGHT - 50)  // 32
    cell_widht = WIDTH // 30
    if 0 < player_x < WIDTH - 30:
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

    play_x = max(-50, min(play_x, WIDTH + 50))
    play_y = max(0, min(play_y, HEIGHT - 50))

    return play_x, play_y

def get_targets(player_x, player_y):
    runaway_x = WIDTH if player_x < WIDTH // 2 else 0
    runaway_y = HEIGHT if player_y < HEIGHT // 2 else 0
    return_target = (WIDTH // 2 - 20, HEIGHT // 2 + 50) # Ajustado para o centro da caixa

    cloudiu_target = (0,0)
    pin_target = (0,0)
    glitc_target = (0,0)
    kerne_target = (0,0)

    # Lógica de alvo para Cloudius
    if powerup:
        if not cloudius.dead and not eaten_inimigo[0]:
            cloudiu_target = (runaway_x, runaway_y)
        elif not cloudius.dead and eaten_inimigo[0]:
            # Ajustar limites da caixa para alvo de retorno
            if cloudius.box_xmin < cloudius.x_pos < cloudius.box_xmax and cloudius.box_ymin < cloudius.y_pos < cloudius.box_ymax:
                cloudiu_target = (WIDTH // 2, 100) # Alvo genérico fora da caixa
            else:
                cloudiu_target = (player_x, player_y)
        else:
            cloudiu_target = return_target
    else:
        if not cloudius.dead:
            if cloudius.box_xmin < cloudius.x_pos < cloudius.box_xmax and cloudius.box_ymin < cloudius.y_pos < cloudius.box_ymax:
                cloudiu_target = (WIDTH // 2, 100)
            else:
                cloudiu_target = (player_x, player_y)
        else:
            cloudiu_target = return_target


    # Lógica de alvo para Ping
    if powerup:
        if not ping.dead and not eaten_inimigo[1]:
            pin_target = (runaway_x, runaway_y)
        elif not ping.dead and eaten_inimigo[1]:
            if ping.box_xmin < ping.x_pos < ping.box_xmax and ping.box_ymin < ping.y_pos < ping.box_ymax:
                pin_target = (WIDTH // 2, 100)
            else:
                pin_target = (player_x, player_y)
        else:
            pin_target = return_target
    else:
        if not ping.dead:
            if ping.box_xmin < ping.x_pos < ping.box_xmax and ping.box_ymin < ping.y_pos < ping.box_ymax:
                pin_target = (WIDTH // 2, 100)
            else:
                pin_target = (player_x + 100, player_y - 100)
        else:
            pin_target = return_target

    # Lógica de alvo para Glitch
    if powerup:
        if not glitch.dead and not eaten_inimigo[2]:
            glitc_target = (player_x, runaway_y)
        elif not glitch.dead and eaten_inimigo[2]:
            if glitch.box_xmin < glitch.x_pos < glitch.box_xmax and glitch.box_ymin < glitch.y_pos < glitch.box_ymax:
                glitc_target = (WIDTH // 2, 100)
            else:
                glitc_target = (player_x, player_y)
        else:
            glitc_target = return_target
    else:
        if not glitch.dead:
            if glitch.box_xmin < glitch.x_pos < glitch.box_xmax and glitch.box_ymin < glitch.y_pos < glitch.box_ymax:
                glitc_target = (WIDTH // 2, 100)
            else:
                glitc_target = (player_x - 150, player_y + 50)
        else:
            glitc_target = return_target

    # Lógica de alvo para Kernel
    if powerup:
        if not kernel.dead and not eaten_inimigo[3]:
            kerne_target = (runaway_x, runaway_y)
        elif not kernel.dead and eaten_inimigo[3]:
            if kernel.box_xmin < kernel.x_pos < kernel.box_xmax and kernel.box_ymin < kernel.y_pos < kernel.box_ymax:
                kerne_target = (WIDTH // 2, 100)
            else:
                kerne_target = (player_x, player_y)
        else:
            kerne_target = return_target
    else:
        if not kernel.dead:
            if kernel.box_xmin < kernel.x_pos < kernel.box_xmax and kernel.box_ymin < kernel.y_pos < kernel.box_ymax:
                kerne_target = (WIDTH // 2, 100)
            else:
                kerne_target = (player_x - 150, player_y + 50)
        else:
            kerne_target = return_target

    return [cloudiu_target, pin_target, glitc_target, kerne_target]

cloudius = Inimigo(56 * WIDTH // 900, 58 * HEIGHT // 950 , targets[0], inimigo_speeds[0], cloudius_img, 0, False, False, 0)
ping = Inimigo(400 * WIDTH // 900, 438 * HEIGHT // 950, targets[1], inimigo_speeds[1], ping_img, 1, False, False, 1)
glitch = Inimigo(440 * WIDTH // 900, 438 * HEIGHT // 950, targets[2], inimigo_speeds[2], glitch_img, 2, False, False, 2)
kernel = Inimigo(440 * WIDTH // 900, 438 * HEIGHT // 950, targets[3], inimigo_speeds[3], kernel_img, 3, False, False, 3)

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
        ping.speed = 4
    if eaten_inimigo[2]:
        glitch.speed = 4
    if eaten_inimigo[3]:
        kernel.speed = 4

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
        if (player_circle.colliderect(cloudius.rect) and not cloudius.dead) or \
           (player_circle.colliderect(ping.rect) and not ping.dead) or \
           (player_circle.colliderect(kernel.rect) and not kernel.dead) or \
           (player_circle.colliderect(glitch.rect) and not glitch.dead):
            if lives > 0:
                lives -= 1
                startup_counter = 0
                powerup = False
                powerup_count = 0
                player_x = WIDTH // 2 # Reset player position
                player_y = int(650 * (HEIGHT / 950)) # Reset player position, proporcionalmente
                direction = 0
                direction_command = 0
                # Reset enemy positions to adjusted values
                cloudius.x_pos = 56 * WIDTH // 900
                cloudius.y_pos = 58 * HEIGHT // 950
                cloudius.direction = 0
                ping.x_pos = 400 * WIDTH // 900
                ping.y_pos = 438 * HEIGHT // 950
                ping.direction = 2
                glitch.x_pos = 440 * WIDTH // 900
                glitch.y_pos = 438 * HEIGHT // 950
                glitch.direction = 2
                kernel.x_pos = 440 * WIDTH // 900
                kernel.y_pos = 438 * HEIGHT // 950
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
                player_x = WIDTH // 2 # Reset player position
                player_y = int(650 * (HEIGHT / 950)) # Reset player position, proporcionalmente
                direction = 0
                direction_command = 0
                # Reset enemy positions to adjusted values
                cloudius.x_pos = 56 * WIDTH // 900
                cloudius.y_pos = 58 * HEIGHT // 950
                cloudius.direction = 0
                ping.x_pos = 400 * WIDTH // 900
                ping.y_pos = 438 * HEIGHT // 950
                ping.direction = 2
                glitch.x_pos = 440 * WIDTH // 900
                glitch.y_pos = 438 * HEIGHT // 950
                glitch.direction = 2
                kernel.x_pos = 440 * WIDTH // 900
                kernel.y_y_pos = 438 * HEIGHT // 950
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

    # Ajusta o teletransporte do jogador para o novo WIDTH
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
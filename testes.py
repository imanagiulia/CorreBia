import copy # fazer uma cópia do mapa, para que o original não seja alterado e o jogo possa ser resetado corretamente
import threading # conseguir implementar as threas
import time # força paradas em alguns lugares do código
from board import boards # importação da função boards do arquivo board, onde está o desenho do mapa
import pygame # para conseguir fazer com que o jogo rode e tenha a parte gráfica
import math # funções matemáticas

pygame.init() # forma padrão de inicializar todos os modulos do pygame necessários para fazer o jogo rodar
inimigo_lock = threading.Lock() # criação de uma variavel especifica que chama o lock, nosso caso mutex

# Configurações do jogo
# Tamanho da janela do jogo, em pixels
WIDTH = 800
HEIGHT = 790
screen = pygame.display.set_mode([WIDTH, HEIGHT]) # criação da variavel que vai fazer aparecer a janela do jogo nas dimensões estabelecidas
timer = pygame.time.Clock() # variavel usada para controlar o fps do jogo
fps = 60 # 60 quadros por segundo
# definição das fontes utilizadas no jogo
font = pygame.font.Font('freesansbold.ttf', 20)
font2 = pygame.font.Font('freesansbold.ttf', 30)
# variavél que vai ser responsavel por criar uma cópia do mapa
level = copy.deepcopy(boards)
color = 'orange' # definição da cor usada nas paredes do labirinto
PI = math.pi
# Imagens
player_images = []
# carrega e transforma as imagens para o tamanho 45x45
for i in range (1, 3): # lista das imagens da bia
    player_images.append(pygame.transform.scale(pygame.image.load(f'assets/{i}.png'), (45, 45)))
cloudius_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/nuvem.png'), (45, 45))
ping_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/redes.png'), (45, 45))
glitch_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/computacional.png'), (45, 45))
kernel_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/operacional.png'), (45, 45))
check_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/check.png'), (45, 45))
turbo_img = pygame.transform.scale(pygame.image.load(f'assets/inimigos/turbo.png'), (45, 45))

# Variáveis do jogador
# define a posição que a bia vai nascer
player_x = WIDTH // 2
player_y = int(650 * (HEIGHT / 950)) # garante que se a altura da tela mudar, a posição inical se ajuste para manter uma proporção similar
direction = 0 # definição da direção inicial da bia - nesse caso a direita
direction_command = 0
player_speed = 3
counter = 0 # contador para animar as imagens da bia - fazer parecer que ela está andando
flicker = 0 # faz com que os powerups fiquem piscando

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

# criação de uma classe para os inimigos, já que eles possuem os mesmos atributos
class Inimigo:
    def __init__(self, x_coord, y_coord, target, speed, img, direction, dead, box, id):
       # posições atuais dos inimigos
        self.x_pos = x_coord
        self.y_pos = y_coord
       # calculam o centro da imagem dos inimigos
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22
        self.target = (0,0) # coordenadas x e y para onde os inimigos estão se movendo
        self.speed = speed
        self.img = img
        self.direction = direction # direção que eles estão se movendo - direita esquerda cima baixo
        self.dead = dead
        self.in_box = box
        self.id = id
        self.turns = [False, False, False, False]
        self.rect = pygame.Rect(self.x_pos, self.y_pos, 45, 45) # cria um objeto para o inimigo que será usado para saber se houve colisão
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

        # inicialização da thread de cada inimigo
        if id == 0:
            self.thread = threading.Thread(target=self.run_cloudius_thread)
        elif id == 1:
            self.thread = threading.Thread(target=self.run_ping_thread)
        elif id == 2:
            self.thread = threading.Thread(target=self.run_glitch_thread)
        elif id == 3:
            self.thread = threading.Thread(target=self.run_kernel_thread)

        self.thread.daemon = True # garante que as threads serão encerradas quando o programa principal encerrar
        self.thread.start()

    def draw(self): # desenha os inimigos na tela
        if (not powerup and not self.dead) or (eaten_inimigo[self.id] and powerup and not self.dead): # se powerup está ativo e o inimigo não está morto ou se o powerup está ativo e o inimigo foi comido, ele desenha a imagem original
            screen.blit(self.img, (self.x_pos,self.y_pos))
        elif powerup and not self.dead and not eaten_inimigo[self.id]: # se o powerup está ativo e ele não foi comido, desenha a imagem que indica que ele pode ser comido
            screen.blit(turbo_img, (self.x_pos,self.y_pos))
        else: # se o inimigo está morto, desenha a imagem indicando que ele está morto
            screen.blit(check_img, (self.x_pos,self.y_pos))
        self.rect = pygame.rect.Rect(self.x_pos, self.y_pos, 45, 45) # atualiza o retangulo de colisão para a posição atual do inimigo
        return self.rect

    def check_collisions(self): # D, E, C, B
        # atualiza o center_x e center_y
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22

        # calcula a célula atual onde o centro do inimigo se encontra
        cell_h = (HEIGHT - 50) // 32 # altyra de cada célula do labirinto
        cell_w = WIDTH // 30 # largura de cada\ célula do labirinto

        # garante que os valores da linha e da coluna pernameçam dentro dos limites da grade do labirinto
        linha = max(0, min(int((self.y_pos + 22) // cell_h), len(level) - 1))
        coluna = max(0, min(int((self.x_pos + 22) // cell_w), len(level[0]) - 1))

        # Ajusta os limites da caixa dos inimigos
        is_in_box = (self.box_xmin <= self.x_pos < self.box_xmax and self.box_ymin < self.y_pos < self.box_ymax)

        # atualiza os estados das posições dos inimigos
        if is_in_box:
            self.in_box = True
            if self.dead:
                self.left_box = False
        else:
            self.in_box = False
            self.left_box = True
        return self.check_turns()

    def check_turns(self):
        # calucla as dimensões da célula e margem para verificação de viradas
        cell_height = (HEIGHT - 50) // 32
        cell_width = WIDTH // 30
        margem = 15

        linha = int((self.y_pos + 22) // cell_height)
        coluna = int((self.x_pos + 22) // cell_width)

        turns = [False, False, False, False]  # direita, esquerda, cima, baixo

        # verifica se pode virar d, e, c, b
        # verifica as células adjacentes - ao lado - para saber se são caminhos livres
        if coluna + 1 < len(level[0]): # garante que não está tenando acessar uma coluna fora dos limites do mapa a direita 
            if level[linha][coluna + 1] < 3 or level[linha][coluna + 1] == 9: # 9 número na matriz do mapa que representa o "portão" da caixa dos fantasmas
                turns[0] = True
        if coluna - 1 >= 0: # esquerda
            if level[linha][coluna - 1] < 3 or level[linha][coluna - 1] == 9:
                turns[1] = True
        if linha - 1 >= 0: # cima
            if level[linha - 1][coluna] < 3 or level[linha - 1][coluna] == 9:
                turns[2] = True
        if linha + 1 < len(level): # baixo
            if level[linha + 1][coluna] < 3 or level[linha + 1][coluna] == 9:
                turns[3] = True

        # verificam se o inimigo está proximo o suficiente do centro de uma célula para fazer a virada para uma nova direção, usa a margem para dar uma flexibilizada
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
        # move o inimigo para a caixa quando ele é comido
        target_x, target_y = self.box_center_x, self.box_center_y

        # move na direção do do target_x e target_y para a caixa
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

    # move o inimigo para fora da caixa
    def move_out_box(self):
        # prioriza o movimento vertical para cima, quando ele atinge a posição do exit_y ele é considerado fora da caixa
        exit_y = self.box_ymin - 50
        if self.y_pos > exit_y and self.turns[2]:
            self.y_pos -= self.speed
            self.direction = 2
        elif self.y_pos <= exit_y:
            self.in_box = False
            self.left_box = True

    # funções de destino para as threas
    def run_cloudius_thread(self):
        while self.running: # mantém a thread ativa
            time.sleep(0.02) # pausa a thread para controlar a taxa de atualização dos inimigos, evitar o consumo 100% da cpu
            with inimigo_lock: # lock para garantir que apenas uma thread por vez possa modificar as variaveis compartilhadas
                if moving and not game_over and not game_won:
                    self.turns = self.check_collisions()
                if self.dead: # se o inimigo está morto chama a função para ele ir para a caixa
                    self.move_to_box()
                elif self.in_box: # se está na caixa, chmama função para sair da caixa
                    self.move_out_box()
                else: # função de movimentação padrão dele
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


    def move_kernel(self): # vira sempre que for vantajoso para perseguição
        # função de movimentação padrão dele
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22

        target_x, target_y = self.target
        if self.dead: # se morto, move diretamentge para o seu target (caixa)
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
        # movimentação em direção ao jogador
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



    def move_cloudius(self): # prioriza a direção com maior distancia do alvo
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
    # desenha elementos de interface do usuário, pontuação, número de vidas, telas de game won e over
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, HEIGHT - 30)) # Ajustado para o novo HEIGHT
    for l in range(lives):
        screen.blit(pygame.transform.scale(player_images[1], (40,40)), (WIDTH - 150 + l * 40, HEIGHT - 40))
    if game_over:
        pygame.draw.rect(screen, 'dark gray', [50, HEIGHT // 2 - 150, WIDTH - 100, 300], 0, 10)
        pygame.draw.rect(screen, 'orange', [70, HEIGHT // 2 - 130, WIDTH - 140, 260], 0, 10)
        gameover_text1 = font2.render('Game Over!', True, 'red')
        gameover_text2 = font.render(' Aperte [espaço] para recomeçar!', True, 'red')
        gameover_rect1 = gameover_text1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)) # usado para centralizar o texto verticalmente e proporcionalmente com o tamanho da janela do jogo
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
    # verifica as colisoes do jogador com as bolinhas e powerups do labirinto

    # calcula a célula atual onde o centro do jogador se encontra
    cell_height = (HEIGHT - 50)  // 32
    cell_widht = WIDTH // 30
    if 0 < player_x < WIDTH - 30:
        if level[center_y // cell_height][center_x // cell_widht] == 1:
            level[center_y // cell_height][center_x // cell_widht] = 0 # substitui a bolinha pela espaço vazio
            scor += 10 # se atingiu uma bolinha soma 10 na pontuação
        if level[center_y // cell_height][center_x // cell_widht] == 2:
            level[center_y // cell_height][center_x // cell_widht] = 0 # substitui o poweup pela espaço vaziuo
            scor += 50 # se atingiu um poweup soma 50 na pontuaçãi
            power = True
            power_count = 0
            eaten_inimigo = [False, False, False, False]
    return scor, power, power_count, eaten_inimigo

def draw_board(level):
    # desenhar o mapa conferme os núemros do boards
    num1 = ((HEIGHT - 50) // 32) # altura de cada célula do labirinto
    num2 = (WIDTH // 30) # largura de cada célula do laboritno
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
    # desenha o jogador na tela
    # direita, esquerda, cima, baixo
    if direction == 0:
        #seleciona a imagem correta, desacelera a animação, garante que o indice esteja dentor dos limites da lista de imagens
        screen.blit(player_images[counter // 15 % len(player_images)], (player_x, player_y))
    elif direction == 1:
        # transform, flip e rotate, usados para orientar a imagem do jogador na direção correta
        screen.blit(pygame.transform.flip(player_images[counter // 15 % len(player_images)], True, False), (player_x, player_y))
    elif direction == 2:
        screen.blit(pygame.transform.rotate(player_images[counter // 15 % len(player_images)], 90),  (player_x, player_y))
    elif direction == 3:
        screen.blit(pygame.transform.rotate(player_images[counter // 15 % len(player_images)], -90), (player_x, player_y))

def check_position(centerx, centery):
    # D, E, C, B
    # verifica para quais direçãoes o jogador pode se mover a partir da sua posição atual
    turns = [False, False, False, False]
    # calcula a célula atual do jogador e uma margem
    cell_height = (HEIGHT - 50) // 32
    cell_width = (WIDTH // 30)
    margem = 15
    # checa as colisões baseadas no center x e center y +/- um fugde number para ver se ele não está colidindo com alguma parede
    if 0 <= centerx < WIDTH and 0 <= centery < HEIGHT - 50: # garante que o jogador esteja detro dos limites jogáveis da tela
        if direction == 0: # verifica se a célula a direita não é uma parede (< 3), se tiver livre ele pode virar. mesma coisa para os outros ( D, E, C, B)
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

    #atualiza a posição atual do jogar com base na direção e se a virada é permitida
    if direction == 0 and turns_allowed[0]: # ta direção para direita e pode virar para direita = se move
        play_x += player_speed
    elif direction == 1 and turns_allowed[1]:
        play_x -= player_speed
    if direction == 2 and turns_allowed[2]:
        play_y -= player_speed
    elif direction == 3 and turns_allowed[3]:
        play_y += player_speed

    # para que não saia dos limites da tela
    play_x = max(-50, min(play_x, WIDTH + 50))
    play_y = max(0, min(play_y, HEIGHT - 50))

    return play_x, play_y

def get_targets(player_x, player_y):
    # calcula as coordenas de destino dos inimigos com base no estado atuak do jogo

    # coordenas para onde os inimigos figirão caso o powerup estiver ativado - canto oposto ao do jogador
    runaway_x = WIDTH if player_x < WIDTH // 2 else 0
    runaway_y = HEIGHT if player_y < HEIGHT // 2 else 0
    return_target = (WIDTH // 2 - 20, HEIGHT // 2 + 50)

    cloudiu_target = (0,0)
    pin_target = (0,0)
    glitc_target = (0,0)
    kerne_target = (0,0)

    # Lógica de alvo para Cloudius
    if powerup: # powerup ativado
        if not cloudius.dead and not eaten_inimigo[0]: # e se ele não estpa morto e nem comido
            cloudiu_target = (runaway_x, runaway_y) # foge
        elif not cloudius.dead and eaten_inimigo[0]: # se não está morto , mas foi comido
            if cloudius.box_xmin < cloudius.x_pos < cloudius.box_xmax and cloudius.box_ymin < cloudius.y_pos < cloudius.box_ymax: # se esta dentro da caixa
                cloudiu_target = (WIDTH // 2, 100) # Alvo genérico fora da caixa
            else:
                cloudiu_target = (player_x, player_y) # persegue o jogador
        else:
            cloudiu_target = return_target
    else: # estado nromal - sem powerup
        if not cloudius.dead: # não morto
            if cloudius.box_xmin < cloudius.x_pos < cloudius.box_xmax and cloudius.box_ymin < cloudius.y_pos < cloudius.box_ymax: # mas dentro da caixa
                cloudiu_target = (WIDTH // 2, 100) # sai da caixa
            else:
                cloudiu_target = (player_x, player_y) #  alvo é o jogador
        else:
            cloudiu_target = return_target

# mesma coisa para os outros inimigos

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

# inicialização dos objetos da classe inimigo
# ta criando as instancias de cada inimigo
cloudius = Inimigo(56 * WIDTH // 900, 58 * HEIGHT // 950 , targets[0], inimigo_speeds[0], cloudius_img, 0, False, False, 0)
ping = Inimigo(400 * WIDTH // 900, 438 * HEIGHT // 950, targets[1], inimigo_speeds[1], ping_img, 1, False, False, 1)
glitch = Inimigo(440 * WIDTH // 900, 438 * HEIGHT // 950, targets[2], inimigo_speeds[2], glitch_img, 2, False, False, 2)
kernel = Inimigo(440 * WIDTH // 900, 438 * HEIGHT // 950, targets[3], inimigo_speeds[3], kernel_img, 3, False, False, 3)

run = True

# loop principal do jogo
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

    screen.fill('black') # preenche a tela com preto
    draw_board(level) # desenha o labirinto
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

    player_circle = pygame.draw.circle(screen, 'black', (center_x, center_y), 21, 2) # desenha um circulo do jagador, usado para colisões
    draw_player() # desenha o jogador

    # alvos dos inimigos
    target_atual = get_targets(player_x, player_y)
    cloudius.target = target_atual[0]
    ping.target = target_atual[1]
    glitch.target = target_atual[2]
    kernel.target = target_atual[3]

    turns_allowed = check_position(center_x, center_y)

    # dessenha cada inimigo e atualiza o rect para colisoes
    with inimigo_lock:
        cloudius.rect = cloudius.draw()
        ping.rect = ping.draw()
        glitch.rect = glitch.draw()
        kernel.rect = kernel.draw()

    draw_alter() # desenha a interface

    # move o jogador se o jogo estiver ativo
    if moving:
        player_x, player_y = move_player(player_x, player_y)

    # atualiza o estado do jogo conforme as colisoes
    score, powerup, powerup_count, eaten_inimigo = check_collisions(score, powerup, powerup_count, eaten_inimigo)

    if not powerup:# se jogador colide com um fantasma sem estar com o powerup ativo e sem eles estarem mortos: decrementa uma vida, reseta algumas variáveis, se a qtd de vidas chegar a 0 game over
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

    if powerup: # se colide com um inimigo com o power up ativo, altera o valor booleano de algumas coisas
        if player_circle.colliderect(cloudius.rect) and not cloudius.dead and not eaten_inimigo[0]:
            cloudius.dead = True
            eaten_inimigo[0] = True
            score += (2 * eaten_inimigo.count(True)) * 100 # aumenta a pontuação 2 vezes  a cada inimigo comido
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

    # loop para processar os eventos do pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # se fechar a janela
            cloudius.running = False
            ping.running = False
            glitch.running = False
            kernel.running = False
            run = False

        if event.type == pygame.KEYDOWN: # entradas do teclado
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
                player_y = int(650 * (HEIGHT / 950)) 
                direction = 0
                direction_command = 0
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

    # atualização da direção do jogador se a virada for permitida
    for i in range(4):
        if direction_command == i and turns_allowed[i]:
             direction = i

    # reset de inimigos mortos, se ele alcança a caixa ele não é mais considerado morto
    if cloudius.dead and cloudius.in_box:
        cloudius.dead = False
    if ping.dead and ping.in_box:
        ping.dead = False
    if glitch.dead and glitch.in_box:
        glitch.dead = False
    if kernel.dead and kernel.in_box:
        kernel.dead = False

    pygame.display.flip() # atualiza a tela inteira para mostrar oq foi desenhado

# garantindo que as threads dos inimigos parem de executar
cloudius.running = False
ping.running = False
glitch.running = False
kernel.running = False

# espera para que todas as threads dos inimigos terminem sua execução -  importante para garantir que todas as operações assíncronas sejam concluídas antes de sair.
cloudius.thread.join()
ping.thread.join()
glitch.thread.join()
kernel.thread.join()

# desinicializa os modulos do pygame
pygame.quit()

import pygame
from sys import exit  # evita erros no pygame ao fechar a janela do game
from random import randint, choice  # randomizar o spawn dos inimigos


class Player(pygame.sprite.Sprite):
    """Grupo único para o player. Aqui é gerenciado todas as funções do mesmo."""
    def __init__(self):
        super().__init__()
        player_walk_1 = pygame.image.load('graphics/player/player_walk_1.png').convert_alpha()
        player_walk_2 = pygame.image.load('graphics/player/player_walk_2.png').convert_alpha()
        self.player_walk = [player_walk_1, player_walk_2]
        self.player_index = 0
        self.player_jump = pygame.image.load('graphics/player/jump.png').convert_alpha()

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(80, 300))
        self.gravity = 0

        self.jump_sound = pygame.mixer.Sound('audio/jump.mp3')
        self.jump_sound.set_volume(0.5)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 300:  # Pulo
            self.gravity = -20
            self.jump_sound.play()

    def apply_gravity(self):  # Mantém o personagem no chão.
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 300:
            self.rect.bottom = 300

    def animation_state(self):
        if self.rect.bottom < 300:
            self.image = self.player_jump
        else:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk):
                self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]

    def update(self):  # esse método sempre precisa estar com esse nome.
        self.player_input()
        self.apply_gravity()
        self.animation_state()


class Obstacle(pygame.sprite.Sprite):
    """Grupo de todos os inimigos. Aqui eles são gerados, animados e excluídos constantemente"""
    def __init__(self, type):
        super().__init__()
        if type == 'fly':
            fly_1 = pygame.image.load('graphics/fly/fly1.png').convert_alpha()
            fly_2 = pygame.image.load('graphics/fly/fly2.png').convert_alpha()
            self.frames = [fly_1, fly_2]
            y_pos = 210
        else:
            snail_1 = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
            snail_2 = pygame.image.load('graphics/snail/snail2.png').convert_alpha()
            self.frames = [snail_1, snail_2]
            y_pos = 300

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom=(randint(900, 1100), y_pos))

    def animation_state(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()

    def update(self):  # essa função sempre deve ter esse mesmo nome. É ela que vai iniciar todos os métodos
        self.animation_state()
        self.rect.x -= 6
        self.destroy()


def display_score():
    """Desenha na tela o Score e Gerencia o Controle do Mesmo"""
    current_time = int(pygame.time.get_ticks() / 1000) - start_time
    score_surf = test_font.render(f'Score: {current_time}', False, (64, 64, 64))
    score_rect = score_surf.get_rect(center=(400, 50))
    screen.blit(score_surf, score_rect)
    return current_time


def collision_sprite():
    """Gerencia o controle de colisão entre grupos de sprites retornando True ou False"""
    if pygame.sprite.spritecollide(player.sprite, obstacle_group, False):  # sintaxe de colisão entre grupos de esprite
        obstacle_group.empty()  # empty() lima a lista.
        return False
    else:
        return True


pygame.init()  # Garante o uso das diversas ferramentas do pygame
screen = pygame.display.set_mode((800, 400))  # tamanho da tela
pygame.display.set_caption('Runner')  # Título da tela
clock = pygame.time.Clock()  # Usado para setar a frequencia de loops (fps)
test_font = pygame.font.Font('font/Pixeltype.ttf', 50)  # configuração da fonte)
game_active = False
start_time = 0  # Controle do Score
score = 0  # Controle do Score
bg_music = pygame.mixer.Sound('audio/music.wav')  # load musica
bg_music.set_volume(0.8)  # Set volume da música
bg_music.play(loops=-1)  # loops=-1 implica em loop infinito da música.

# Grupos
player = pygame.sprite.GroupSingle()  # GroupSingle usado para o nosso player
player.add(Player())

obstacle_group = pygame.sprite.Group()  # Group usado para vários sprits (inimigos)

# Carregando o backgroud
sky_surface = pygame.image.load('graphics/Sky.png').convert()  # .convert() usa o melhor formato possível para o pygame
ground_surface = pygame.image.load('graphics/ground.png').convert()

# Tela inicial
player_stand = pygame.image.load('graphics/player/player_stand.png').convert_alpha()  # convert_alpha p/ objetos móveis
player_stand = pygame.transform.rotozoom(player_stand, 0, 2)  # Param: superfície, grau rotação, multiplicador de escala
player_stand_rect = player_stand.get_rect(center=(400, 200))  # rectangle: adiciona colisão na superfície

game_name = test_font.render('Pixel Runner', False, (111, 196, 169))  # Param: Texto, anti-aliasing, cor
game_name_rect = game_name.get_rect(center=(400, 80))

game_message = test_font.render('Press space to run', False, (111, 196, 169))
game_message_rect = game_message.get_rect(center=(400, 330))

# Timer
obstacle_timer = pygame.USEREVENT + 1  # Evento específico que irá acontecer independente do usuário
pygame.time.set_timer(obstacle_timer, 1500)  # Param: evento a ser executado, quantas vezes por milissegundos

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Equivale ao "X" que fecha a aba do game. Evita erros ao fechar.
            pygame.quit()
            exit()

        # Spaw dos inimigos
        if game_active:
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choice(['fly', 'snail', 'snail', 'snail'])))

        # O que vai acontecer quando o usuário apertar espaço na tela inicial ou na de GAME OVER
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True
                start_time = int(pygame.time.get_ticks() / 1000)  # reseta o score.

    if game_active:
        screen.blit(sky_surface, (0, 0))  # blit() desenha na tela. Param: superície, posição
        screen.blit(ground_surface, (0, 300))
        score = display_score()

        player.draw(screen)  # draw() método da classe sprite. Param: tela na qual vc deseja desenhar
        player.update()  # update() método da classe sprite. Serve para reconhecer as interações e funções do sprite

        obstacle_group.draw(screen)
        obstacle_group.update()

        game_active = collision_sprite()

    else:
        screen.fill((94, 129, 162))  # Preencher a tela com uma determinada cor.
        screen.blit(player_stand, player_stand_rect)  # Param: superfície, posição (pode usar um rectangle pra isso)

        score_message = test_font.render(f'Your score: {score}', False, (111, 196, 169))
        score_message_rect = score_message.get_rect(center=(400, 330))
        screen.blit(game_name, game_name_rect)  # Rectangle está sendo usado para posicionar com precisão na tela.

        if score == 0:
            screen.blit(game_message, game_message_rect)
        else:
            screen.blit(score_message, score_message_rect)

    pygame.display.update()
    clock.tick(60)  # FPS travado em 60

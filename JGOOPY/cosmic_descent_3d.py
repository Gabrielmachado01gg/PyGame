# cosmic_descent_3d_explosoes_png_only.py
# Atualização solicitada: remover sistema de 'vida' dos meteoros e remover fallback gráfico
# para explosões — usar somente os PNGs 01..06.png (ou 1..6.png se renomeados).
# Se os arquivos não existirem, o jogo irá imprimir uma mensagem no console e NÃO
# desenhará uma animação alternativa (sem quadrados coloridos).

import pygame
import random
import sys
import os
import json
import time

pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🚀 Cosmic Descent - Explosões PNGs Somente")
clock = pygame.time.Clock()
FONT = pygame.font.Font(None, 36)

ASSETS = os.path.join(os.path.dirname(__file__), "assets")
SAVE_FILE = os.path.join(os.path.dirname(__file__), "savegame.json")
HIGHSCORES_FILE = os.path.join(os.path.dirname(__file__), "highscores.json")

# ---------------- util ----------------

def carregar_img(nome, escala=None):
    caminho = os.path.join(ASSETS, nome)
    try:
        img = pygame.image.load(caminho).convert_alpha()
        if escala:
            img = pygame.transform.scale(img, escala)
        return img
    except Exception:
        # devolve None para indicar ausência clara do asset
        return None


def carregar_som(nome):
    caminho = os.path.join(ASSETS, nome)
    try:
        return pygame.mixer.Sound(caminho)
    except Exception:
        return None


def draw_text(surf, text, size, x, y, color=(255,255,255)):
    font = pygame.font.Font(None, size)
    surf_txt = font.render(text, True, color)
    rect = surf_txt.get_rect()
    rect.midtop = (x, y)
    surf.blit(surf_txt, rect)


def draw_health_bar(surf, x, y, pct):
    pct = max(0, pct)
    BAR_LENGTH, BAR_HEIGHT = 250, 25
    fill = (pct / 100) * BAR_LENGTH
    outline = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    color = (0,200,0) if pct > 50 else (200,50,50)
    pygame.draw.rect(surf, color, fill_rect)
    pygame.draw.rect(surf, (255,255,255), outline, 2)


# ---------------- classes ----------------
class Background:
    def __init__(self):
        self.images = {}
        self.images[1] = carregar_img('bg_phase1.png', (WIDTH, HEIGHT))
        self.images[2] = carregar_img('bg_phase2.png', (WIDTH, HEIGHT))
        self.images[3] = carregar_img('bg_phase3.png', (WIDTH, HEIGHT))
        self.current = 1

    def set_phase(self, p):
        if p in self.images and self.images[p] is not None:
            self.current = p

    def draw(self):
        img = self.images.get(self.current)
        if img:
            screen.blit(img, (0,0))
        else:
            screen.fill((8,8,20))


class Planet:
    def __init__(self, image_name, x, y, size):
        img = carregar_img(image_name, (size, size))
        self.image = img if img is not None else pygame.Surface((size,size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, controls, color=(0,120,255), name='PLAYER'):
        super().__init__()
        img = carregar_img('player.png', (100,70))
        if img is None:
            self.image = pygame.Surface((100,70), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, color, [(50,0),(20,60),(80,60)])
        else:
            self.image = img
        self.rect = self.image.get_rect(center=(x,y))
        self.controls = controls
        self.speed = 6
        self.health = 100
        self.score = 0
        self.last_shot = 0
        self.shoot_delay = 300
        self.extra_guns = 0
        self.teleport_ability = False
        self.invulnerable_until = 0
        self.has_shield = False
        self.shield_time = 0
        self.mouse_control = False
        self.name = name

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[self.controls['left']]:
            self.rect.x -= self.speed
        if keys[self.controls['right']]:
            self.rect.x += self.speed
        if keys[self.controls['up']]:
            self.rect.y -= self.speed
        if keys[self.controls['down']]:
            self.rect.y += self.speed

        if self.mouse_control:
            mx,my = pygame.mouse.get_pos()
            self.rect.centerx += int((mx - self.rect.centerx)*0.35)
            self.rect.centery += int((my - self.rect.centery)*0.35)

        self.rect.clamp_ip(screen.get_rect())
        now = pygame.time.get_ticks()
        if self.shield_time and now > self.shield_time:
            self.has_shield = False
            self.shield_time = 0
        if self.invulnerable_until and now > self.invulnerable_until:
            self.invulnerable_until = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.shoot_delay:
            self.last_shot = now
            bullets = []
            bullets.append(Bullet(self.rect.centerx, self.rect.top, owner='player'))
            if self.extra_guns >= 1:
                bullets.append(Bullet(self.rect.left+10, self.rect.centery, owner='player'))
                bullets.append(Bullet(self.rect.right-10, self.rect.centery, owner='player'))
            return bullets
        return None

    def take_damage(self, amount):
        now = pygame.time.get_ticks()
        if self.invulnerable_until and now < self.invulnerable_until:
            return False
        if self.has_shield:
            self.has_shield = False
            return False
        self.health -= amount
        return True

    def teleport(self):
        if not self.teleport_ability:
            return False
        self.rect.centerx = random.randint(80, WIDTH-80)
        self.rect.centery = random.randint(80, HEIGHT-160)
        self.invulnerable_until = pygame.time.get_ticks() + 3000
        self.teleport_ability = False
        return True


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=-12, owner='player'):
        super().__init__()
        img = carregar_img('bullet.png', (12,20))
        if img is None:
            self.image = pygame.Surface((12,20), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (255,255,0), (0,0,12,20))
        else:
            self.image = img
        self.rect = self.image.get_rect(center=(x,y))
        self.speed = speed
        self.owner = owner

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()


class Meteor(pygame.sprite.Sprite):
    def __init__(self, kind='normal'):
        super().__init__()
        self.kind = kind
        img = carregar_img('asteroid-1.png', (64,64))
        if img is None:
            self.base = pygame.Surface((64,64), pygame.SRCALPHA)
            pygame.draw.circle(self.base, (120,120,120), (32,32), 30)
        else:
            self.base = img
        self.image = self.base.copy()
        self.rect = self.image.get_rect(center=(random.randint(40, WIDTH-40), random.randint(-300, -40)))
        if kind == 'evil':
            self.speedy = random.randint(4,6)
            self.damage = 40
        elif kind == 'big_damage':
            self.speedy = random.randint(3,5)
            self.damage = 60
        else:
            self.speedy = random.randint(1,3)
            self.damage = 20
        self.speedx = random.randint(-2,2)
        self.rot = 0
        self.rot_speed = random.randint(-5,5)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        self.rot = (self.rot + self.rot_speed) % 360
        self.image = pygame.transform.rotate(self.base, self.rot)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center
        if self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.respawn()

    def respawn(self):
        self.rect.x = random.randint(0, WIDTH-40)
        self.rect.y = random.randint(-220, -40)
        if self.kind == 'evil':
            self.speedy = random.randint(4,6)
        elif self.kind == 'big_damage':
            self.speedy = random.randint(3,5)
        else:
            self.speedy = random.randint(1,3)
        self.speedx = random.randint(-2,2)
        self.rot_speed = random.randint(-5,5)


# Explosion: apenas usa seus PNGs 01..06.png. Se ausentes, imprimimos aviso e
# NÃO desenhamos fallback (nenhum quadrado colorido).
EXPLOSION_FRAMES = []
EXPLOSION_LOOKED_UP = False
EXPLOSION_AVAILABLE = False


def load_explosion_frames():
    global EXPLOSION_FRAMES, EXPLOSION_LOOKED_UP, EXPLOSION_AVAILABLE
    if EXPLOSION_LOOKED_UP:
        return
    EXPLOSION_LOOKED_UP = True
    names = [f"0{i}.png" for i in range(1,7)] + [f"{i}.png" for i in range(1,7)]
    frames = []
    for name in names:
        p = os.path.join(ASSETS, name)
        if os.path.isfile(p):
            try:
                img = pygame.image.load(p).convert_alpha()
                img = pygame.transform.scale(img, (90, 90))
                frames.append(img)
            except Exception:
                pass
    if frames:
        EXPLOSION_FRAMES = frames
        EXPLOSION_AVAILABLE = True
    else:
        EXPLOSION_FRAMES = []
        EXPLOSION_AVAILABLE = False
        print("⚠️ Explosão: arquivos 01..06.png não encontrados na pasta assets. Nenhuma animação será mostrada.")


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        # certificar-se de carregar uma vez
        load_explosion_frames()
        if not EXPLOSION_AVAILABLE:
            # não cria sprite visível se frames não disponíveis
            self.frames = []
            self.index = 0
            self.image = pygame.Surface((1,1), pygame.SRCALPHA)
            self.rect = self.image.get_rect(center=center)
            # será eliminado imediatamente no primeiro update
            self._auto_kill = True
            return
        self.frames = EXPLOSION_FRAMES.copy()
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=center)
        self.last = pygame.time.get_ticks()
        self.rate = 60
        self._auto_kill = False

    def update(self):
        if getattr(self, '_auto_kill', False):
            self.kill()
            return
        now = pygame.time.get_ticks()
        if now - self.last > self.rate:
            self.last = now
            self.index += 1
            if self.index >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.index]


class Powerup(pygame.sprite.Sprite):
    def __init__(self, center, ptype='revive'):
        super().__init__()
        self.ptype = ptype
        self.size = 28
        self.image = pygame.Surface((self.size,self.size), pygame.SRCALPHA)
        if ptype == 'revive':
            self.image.fill((200,30,30))
        elif ptype == 'invul_gift':
            self.image.fill((30,100,200))
        elif ptype == 'upgrade':
            self.image.fill((220,200,30))
        elif ptype == 'extra_life':
            self.image.fill((30,200,60))
        elif ptype == 'teleporter':
            self.image.fill((180,80,180))
        else:
            self.image.fill((255,255,255))
        self.rect = self.image.get_rect(center=center)

    def update(self):
        self.rect.y += 2
        if self.rect.top > HEIGHT:
            self.kill()


# ---------------- sons ----------------
shoot_snd = carregar_som('shoot.wav')
explosion_snd = carregar_som('explosion.wav')
powerup_snd = carregar_som('powerup.wav')
try:
    pygame.mixer.music.load(os.path.join(ASSETS,'music_phase1.mp3'))
except Exception:
    pass


# ---------------- inicializacao ----------------
background = Background()
all_sprites = pygame.sprite.Group()
meteors = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
explosions = pygame.sprite.Group()

planets = [Planet('saturn.png', WIDTH-550, 40, 420), Planet('terra.png', 80, HEIGHT-420, 360)]

controls_p1 = {'left': pygame.K_a,'right':pygame.K_d,'up':pygame.K_w,'down':pygame.K_s,'shoot':pygame.K_SPACE}
controls_p2 = {'left': pygame.K_LEFT,'right': pygame.K_RIGHT,'up':pygame.K_UP,'down':pygame.K_DOWN,'shoot':pygame.K_KP0}

player1 = Player(WIDTH//2, HEIGHT-120, controls_p1, color=(0,120,255), name='PLAYER 1')
player2 = Player(WIDTH//4, HEIGHT-120, controls_p2, color=(255,100,100), name='PLAYER 2')

all_sprites.add(player1)

MAX_METEORS = 8
for _ in range(MAX_METEORS):
    m = Meteor(kind=random.choice(['normal','normal','evil','power','invul','extra_life','teleporter']))
    all_sprites.add(m); meteors.add(m)

phase = 1
two_player = False
menu_options = ['Jogar 1 Jogador','Jogar 2 Jogadores','Controles','Carregar Jogo','Sair']
menu_index = 0
game_state = 'intro'
VICTORY_SCORE = 200

# highscores
try:
    with open(HIGHSCORES_FILE,'r') as f:
        highscores = json.load(f)
except Exception:
    highscores = []


def add_highscore(name, score):
    global highscores
    highscores.append({'name':name,'score':score,'date':time.strftime('%Y-%m-%d')})
    highscores = sorted(highscores, key=lambda x:x['score'], reverse=True)[:10]
    with open(HIGHSCORES_FILE,'w') as f:
        json.dump(highscores, f, indent=2)


def reset_game(two_p=False):
    global player1, player2, all_sprites, meteors, bullets, powerups, explosions, phase, two_player
    phase = 1
    two_player = two_p
    all_sprites.empty(); meteors.empty(); bullets.empty(); powerups.empty(); explosions.empty()
    player1 = Player(WIDTH//2, HEIGHT-120, controls_p1, color=(0,120,255), name='PLAYER 1')
    player2 = Player(WIDTH//4, HEIGHT-120, controls_p2, color=(255,100,100), name='PLAYER 2')
    all_sprites.add(player1)
    if two_player:
        all_sprites.add(player2)
    for _ in range(MAX_METEORS):
        m = Meteor(kind=random.choice(['normal','normal','evil']))
        all_sprites.add(m); meteors.add(m)


def save_game():
    data = {
        'phase': phase,
        'two_player': two_player,
        'player1': {'x': player1.rect.centerx, 'y': player1.rect.centery, 'health': player1.health, 'score': player1.score, 'extra_guns': player1.extra_guns, 'teleport': player1.teleport_ability},
        'player2': {'x': player2.rect.centerx, 'y': player2.rect.centery, 'health': player2.health, 'score': player2.score, 'extra_guns': player2.extra_guns, 'teleport': player2.teleport_ability},
        'meteors': [{'x': m.rect.x, 'y': m.rect.y, 'speedy': m.speedy, 'speedx': m.speedx, 'kind': m.kind} for m in meteors]
    }
    with open(SAVE_FILE,'w') as f:
        json.dump(data,f,indent=2)
    print('💾 Jogo salvo')


def load_game():
    global phase, two_player
    try:
        with open(SAVE_FILE,'r') as f:
            data = json.load(f)
    except Exception as e:
        print('⚠ Falha ao carregar jogo:', e)
        return
    phase = data.get('phase',1)
    two_player = data.get('two_player', False)
    p1 = data.get('player1', {})
    player1.rect.centerx = p1.get('x', player1.rect.centerx)
    player1.rect.centery = p1.get('y', player1.rect.centery)
    player1.health = p1.get('health', player1.health)
    player1.score = p1.get('score', player1.score)
    player1.extra_guns = p1.get('extra_guns', player1.extra_guns)
    player1.teleport_ability = p1.get('teleport', player1.teleport_ability)
    p2 = data.get('player2', {})
    player2.rect.centerx = p2.get('x', player2.rect.centerx)
    player2.rect.centery = p2.get('y', player2.rect.centery)
    player2.health = p2.get('health', player2.health)
    player2.score = p2.get('score', player2.score)
    player2.extra_guns = p2.get('extra_guns', player2.extra_guns)
    player2.teleport_ability = p2.get('teleport', player2.teleport_ability)
    meteors.empty()
    for md in data.get('meteors', []):
        m = Meteor(kind=md.get('kind','normal'))
        m.rect.x = md.get('x', m.rect.x)
        m.rect.y = md.get('y', m.rect.y)
        m.speedy = md.get('speedy', m.speedy)
        m.speedx = md.get('speedx', m.speedx)
        meteors.add(m); all_sprites.add(m)


def spawn_special_meteor():
    kind = random.choices(['normal','evil','power','invul','extra_life','teleporter','revive'], [40,15,10,10,15,10,5])[0]
    m = Meteor(kind=kind)
    all_sprites.add(m); meteors.add(m)


# --------- loop principal ---------
running = True
pause_menu = False
phase_last_change = pygame.time.get_ticks()

while running:
    dt = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_state == 'intro':
                if event.key == pygame.K_UP:
                    menu_index = (menu_index - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    menu_index = (menu_index + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    escolha = menu_options[menu_index]
                    if escolha == 'Jogar 1 Jogador':
                        reset_game(two_p=False)
                        game_state = 'playing'
                    elif escolha == 'Jogar 2 Jogadores':
                        reset_game(two_p=True)
                        game_state = 'playing'
                    elif escolha == 'Controles':
                        game_state = 'controls'
                    elif escolha == 'Carregar Jogo':
                        load_game(); game_state = 'playing'
                    elif escolha == 'Sair':
                        running = False
            elif game_state in ['playing','game_over','victory','controls']:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_p:
                    pause_menu = not pause_menu
                if event.key == pygame.K_r:
                    reset_game(two_p=two_player)
                    game_state = 'playing'
                if event.key == pygame.K_f:
                    save_game()
                if event.key == pygame.K_l:
                    load_game(); game_state = 'playing'
                if event.key == pygame.K_m:
                    player1.mouse_control = not player1.mouse_control
                if event.key == pygame.K_t:
                    if player1.teleport_ability:
                        player1.teleport()

    # continuous input for playing
    keys = pygame.key.get_pressed()
    if game_state == 'playing' and not pause_menu:
        if keys[player1.controls['shoot']]:
            bullets_list = player1.shoot()
            if bullets_list:
                for b in bullets_list:
                    all_sprites.add(b); bullets.add(b)
                if shoot_snd: shoot_snd.play()
        if two_player and (keys[player2.controls['shoot']] or keys[pygame.K_KP0] or keys[pygame.K_RCTRL]):
            bullets_list = player2.shoot()
            if bullets_list:
                for b in bullets_list:
                    all_sprites.add(b); bullets.add(b)
                if shoot_snd: shoot_snd.play()

    # update groups
    all_sprites.update()
    meteors.update()
    bullets.update()
    powerups.update()
    explosions.update()

    # collisions only if playing and not paused
    if game_state == 'playing' and not pause_menu:
        # bullets hit meteors: meteor dies on first hit (no life system)
        hits = pygame.sprite.groupcollide(meteors, bullets, False, True)
        for meteor, bullets_hit in hits.items():
            # explosion only if frames exist; Explosion handles absence by not showing animation
            expl = Explosion(meteor.rect.center)
            all_sprites.add(expl); explosions.add(expl)
            if explosion_snd:
                explosion_snd.play()
            # powerup chance
            if random.random() < 0.35:
                pu = Powerup(meteor.rect.center, ptype=random.choice(['revive','invul_gift','upgrade','extra_life','teleporter']))
                all_sprites.add(pu); powerups.add(pu)
            if two_player:
                if player1.score >= player2.score:
                    player1.score += 10
                else:
                    player2.score += 10
            else:
                player1.score += 10
            meteor.respawn()

        # meteors hit players
        if player1 in all_sprites:
            hits_p1 = pygame.sprite.spritecollide(player1, meteors, False)
            for hit in hits_p1:
                if player1.take_damage(hit.damage):
                    e = Explosion(hit.rect.center); all_sprites.add(e); explosions.add(e)
                    if explosion_snd: explosion_snd.play()
                hit.respawn()

        if two_player and player2 in all_sprites:
            hits_p2 = pygame.sprite.spritecollide(player2, meteors, False)
            for hit in hits_p2:
                if player2.take_damage(hit.damage):
                    e = Explosion(hit.rect.center); all_sprites.add(e); explosions.add(e)
                    if explosion_snd: explosion_snd.play()
                hit.respawn()

        # powerup collection handling (inalterado)
        if player1 in all_sprites:
            collected1 = pygame.sprite.spritecollide(player1, powerups, True)
            for pu in collected1:
                if pu.ptype == 'revive':
                    if player2 not in all_sprites or getattr(player2,'health',0) <= 0:
                        player2 = Player(WIDTH//4, HEIGHT-120, controls_p2); player2.health = 50; all_sprites.add(player2)
                    else:
                        player1.health = min(100, player1.health+50)
                elif pu.ptype == 'invul_gift':
                    player1.invulnerable_until = pygame.time.get_ticks()+5000
                elif pu.ptype == 'upgrade':
                    player1.extra_guns = min(3, player1.extra_guns+1)
                elif pu.ptype == 'extra_life':
                    player1.health = min(100, player1.health+30)
                elif pu.ptype == 'teleporter':
                    player1.teleport_ability = True

        if two_player and player2 in all_sprites:
            collected2 = pygame.sprite.spritecollide(player2, powerups, True)
            for pu in collected2:
                if pu.ptype == 'revive':
                    if player1 not in all_sprites or getattr(player1,'health',0) <= 0:
                        player1 = Player(WIDTH//2, HEIGHT-120, controls_p1); player1.health = 50; all_sprites.add(player1)
                    else:
                        player2.health = min(100, player2.health+50)
                elif pu.ptype == 'invul_gift':
                    player2.invulnerable_until = pygame.time.get_ticks()+5000
                elif pu.ptype == 'upgrade':
                    player2.extra_guns = min(3, player2.extra_guns+1)
                elif pu.ptype == 'extra_life':
                    player2.health = min(100, player2.health+30)
                elif pu.ptype == 'teleporter':
                    player2.teleport_ability = True

        # maintain meteor count
        while len(meteors) < MAX_METEORS:
            spawn_special_meteor()

        # end conditions
        if player1.health <= 0 and (not two_player or getattr(player2,'health',0) <= 0):
            game_state = 'game_over'
            if player1.score > 0: add_highscore('PLAYER1', player1.score)
        if two_player and getattr(player1,'health',0) <= 0 and getattr(player2,'health',0) <= 0:
            game_state = 'game_over'
            if player1.score + player2.score > 0: add_highscore('DUO', player1.score + player2.score)
        if player1.score >= VICTORY_SCORE or (two_player and (player1.score + player2.score) >= VICTORY_SCORE):
            game_state = 'victory'
            add_highscore('WINNER', max(getattr(player1,'score',0), getattr(player2,'score',0)))

    # drawing (igual ao anterior)
    if game_state == 'intro':
        background.draw()
        for p in planets:
            p.draw(screen)
        draw_text(screen, 'MENU PRINCIPAL', 60, WIDTH//2, 80)
        draw_text(screen, 'HIGHSCORES', 36, WIDTH//2, 160)
        for i,hs in enumerate(highscores[:8]):
            draw_text(screen, f"{i+1}. {hs['name']} - {hs['score']}", 26, WIDTH//2, 200 + i*28)
        for i,opt in enumerate(menu_options):
            color = (255,255,0) if i == menu_index else (200,200,200)
            draw_text(screen, opt, 40, WIDTH - 300, 220 + i*60, color)
        draw_health_bar(screen, 20, 20, player1.health if player1 in all_sprites else 0)
    elif game_state == 'controls':
        screen.fill((0,0,0))
        draw_text(screen, 'Controles', 64, WIDTH//2, 40)
        draw_text(screen, 'P1: WASD mover, ESPACO atirar, M mouse control, T teleport', 28, WIDTH//2, 140)
        draw_text(screen, 'P2: Setas mover, KP0 atirar, RCTRL alternativa', 28, WIDTH//2, 190)
        draw_text(screen, 'F = salvar | L = carregar | P = pausar | R = reiniciar | ESC = sair', 24, WIDTH//2, 260)
        draw_text(screen, 'Pressione BACKSPACE para voltar', 24, WIDTH//2, HEIGHT-80)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_BACKSPACE]:
            game_state = 'intro'
    elif game_state == 'playing':
        background.draw()
        for p in planets:
            p.draw(screen)
        all_sprites.draw(screen)
        draw_health_bar(screen,20,20, player1.health if player1 in all_sprites else 0)
        draw_text(screen, f'P1 PONTOS: {getattr(player1,"score",0)}', 30, WIDTH//3, 20)
        if two_player and player2 in all_sprites:
            draw_health_bar(screen, WIDTH-270, 20, player2.health)
            draw_text(screen, f'P2 PONTOS: {player2.score}', 30, 2*WIDTH//3, 20)
        draw_text(screen, f'FASE: {phase}', 26, WIDTH-100, 20)
        if pause_menu:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0,0,0,150))
            screen.blit(s, (0,0))
            draw_text(screen, 'PAUSADO', 64, WIDTH//2, HEIGHT//2 - 100)
            draw_text(screen, 'P = continuar | ESC = sair | R = reiniciar', 28, WIDTH//2, HEIGHT//2)
    elif game_state == 'game_over':
        screen.fill((0,0,0))
        draw_text(screen, '💀 GAME OVER - Pressione R para reiniciar', 48, WIDTH//2, HEIGHT//2, (255,0,0))
        draw_text(screen, f'SCORE: {player1.score + (player2.score if two_player else 0)}', 36, WIDTH//2, HEIGHT//2+60)
    elif game_state == 'victory':
        screen.fill((0,0,0))
        draw_text(screen, '🎉 VITÓRIA! Pontuação Alcançada!', 48, WIDTH//2, HEIGHT//2, (0,255,0))
        draw_text(screen, f'SCORE: {player1.score + (player2.score if two_player else 0)}', 36, WIDTH//2, HEIGHT//2+60)

    pygame.display.flip()

pygame.quit()
sys.exit()

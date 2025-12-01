# cosmic_descent_3d.py
# VERSÃO ATUALIZADA COM CONTROLE DE VOLUME

import pygame
import random
import sys
import os
import json
import time
import math

pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🚀 NOVA DESCENT - Controle de Volume")
clock = pygame.time.Clock()

# ---------------- CONFIGURAÇÃO DE VOLUME ----------------
# Arquivo para salvar configurações de volume
VOLUME_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "volume_config.json")

# Configurações padrão de volume
DEFAULT_VOLUMES = {
    "master": 0.7,      # Volume geral
    "music": 0.6,       # Músicas de fase
    "effects": 0.8,     # Efeitos sonoros
    "shoot": 0.7,       # Tiro
    "explosion": 0.8,   # Explosão
    "powerup": 0.4,     # Powerup (reduzido por padrão)
    "respawn": 0.6      # Respawn
}

# Carregar ou criar configuração de volume
def load_volume_config():
    """Carrega as configurações de volume do arquivo, ou cria padrão"""
    try:
        if os.path.exists(VOLUME_CONFIG_FILE):
            with open(VOLUME_CONFIG_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠ Erro ao carregar configuração de volume: {e}")
    
    # Se não existir, cria com valores padrão
    save_volume_config(DEFAULT_VOLUMES)
    return DEFAULT_VOLUMES.copy()

def save_volume_config(volumes):
    """Salva as configurações de volume no arquivo"""
    try:
        with open(VOLUME_CONFIG_FILE, "w") as f:
            json.dump(volumes, f, indent=2)
    except Exception as e:
        print(f"⚠ Erro ao salvar configuração de volume: {e}")

# Carregar configurações de volume
VOLUME_CONFIG = load_volume_config()

# Funções para aplicar volume
def set_sound_volume(sound, sound_type):
    """Define o volume de um efeito sonoro baseado no tipo"""
    if sound and hasattr(sound, 'set_volume'):
        # Aplica volume de efeitos e volume específico do som
        volume = VOLUME_CONFIG.get("master", 1.0) * VOLUME_CONFIG.get("effects", 1.0)
        if sound_type in VOLUME_CONFIG:
            volume *= VOLUME_CONFIG.get(sound_type, 1.0)
        sound.set_volume(min(volume, 1.0))  # Garante que não passe de 1.0

def set_music_volume():
    """Define o volume da música de fundo"""
    volume = VOLUME_CONFIG.get("master", 1.0) * VOLUME_CONFIG.get("music", 1.0)
    pygame.mixer.music.set_volume(min(volume, 1.0))

# ---------------- ASSET CONFIG ----------------
ASSET_CONFIG = {
    "assets_dir": "assets",
    "background_global": "blue-stars.png",

    "planets_phase1": [
        {"image": "saturn.png", "x": WIDTH - 550, "y": 40, "size": 420},
        {"image": "terra.png", "x": 80, "y": HEIGHT - 420, "size": 360},
    ],
    "planets_phase2": [
        {"image": "c3po.png", "x": WIDTH - 400, "y": 100, "size": 300},
        {"image": "marte.png", "x": 150, "y": HEIGHT - 300, "size": 250},
    ],
    "planets_phase3": [
        {"image": "plutao.png", "x": WIDTH//2 - 100, "y": 50, "size": 200},
        {"image": "netuno.png", "x": WIDTH - 200, "y": HEIGHT - 200, "size": 150},
    ],
    "explosion_frames": ["01.png", "02.png", "03.png", "04.png", "05.png", "06.png"],
    "players": {"player": "player.png", "size": (100, 70)},
    "players_dead": {"player_dead": "player_dead.png", "size": (100, 70)},
    "bullets": {"image": "bullert.png", "size": (12, 20)},
    "meteors": {"default": "asteroid-1.png", "evil": "asteroid-2.png"},
    "enemies": {"enemy_small": "skill04.png", "size": (64, 64)},
    "boss": {"image": "skill06.png", "size": (220, 220)},
    "sounds": {
        "shoot": "shoot.mp3",
        "explosion": "explosion.mp3",
        "powerup": "powerup.mp3",
        "respawn": "respawn.wav",
        "music_phase1": "phase1.mp3",
        "music_phase2": "phase2.mp3",
        "music_phase3": "phase3.mp3"
    },
    "explosion_scale": (90, 90),
    "player_default_color": (0, 120, 255),
    "player_dead_color": (100, 100, 100, 150),
    "max_meteors": 8,
    "points_to_next_phase": 1500,
    "respawn_time": 5000,
    "initial_lives": 3
}

ASSETS_DIR = os.path.join(os.path.dirname(__file__), ASSET_CONFIG["assets_dir"])
SAVE_FILE = os.path.join(os.path.dirname(__file__), "savegame.json")
HIGHSCORES_FILE = os.path.join(os.path.dirname(__file__), "highscores.json")

# ---------------- Asset Manager ----------------
class AssetManager:
    def __init__(self, assets_dir):
        self.assets_dir = assets_dir
        self._cache = {}

    def _path(self, name):
        return os.path.join(self.assets_dir, name) if name else None

    def load_image(self, name, scale=None):
        if not name:
            return None
        key = f"img|{name}|{scale}"
        if key in self._cache:
            return self._cache[key]
        p = self._path(name)
        if p and os.path.isfile(p):
            try:
                img = pygame.image.load(p).convert_alpha()
                if scale:
                    img = pygame.transform.scale(img, tuple(scale))
                self._cache[key] = img
                return img
            except Exception:
                return None
        return None

    def load_sound(self, name):
        if not name:
            return None
        key = f"snd|{name}"
        if key in self._cache:
            return self._cache[key]
        p = self._path(name)
        if p and os.path.isfile(p):
            try:
                s = pygame.mixer.Sound(p)
                self._cache[key] = s
                return s
            except Exception:
                return None
        return None

ASSETS = AssetManager(ASSETS_DIR)

# ---------------- Funções de Música ----------------
def change_music(phase_name):
    """Troca a música conforme a fase"""
    try:
        music_map = {
            "asteroids": "music_phase1",
            "phase2": "music_phase2",
            "phase3": "music_phase3"
        }
        
        if phase_name in music_map:
            music_file = ASSET_CONFIG.get("sounds", {}).get(music_map[phase_name])
            if music_file:
                mp = os.path.join(ASSETS_DIR, music_file)
                if os.path.isfile(mp):
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(mp)
                    pygame.mixer.music.play(-1)
                    set_music_volume()  # Aplica volume atual
    except Exception as e:
        print(f"Erro ao trocar música: {e}")

# ---------------- Helpers ----------------
def draw_text(surf, text, size, x, y, color=(255,255,255)):
    font = pygame.font.Font(None, size)
    s = font.render(str(text), True, color)
    r = s.get_rect()
    r.midtop = (x, y)
    surf.blit(s, r)

def draw_health_bar(surf, x, y, pct):
    pct = max(0, pct)
    BAR_LENGTH, BAR_HEIGHT = 250, 25
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    color = (0,200,0) if pct > 50 else (200,50,50)
    pygame.draw.rect(surf, color, fill_rect)
    pygame.draw.rect(surf, (255,255,255), outline_rect, 2)

# ---------------- Background ----------------
class Background:
    def draw(self, surf, phase_state="asteroids"):
        img_name = ASSET_CONFIG.get("background_global", None)
        img = ASSETS.load_image(img_name, scale=(WIDTH, HEIGHT)) if img_name else None

        if img:
            surf.blit(img, (0,0))
        else:
            surf.fill((0,0,0))
        
        if phase_state == "asteroids":
            planets_config = ASSET_CONFIG.get("planets_phase1", [])
        elif phase_state == "phase2":
            planets_config = ASSET_CONFIG.get("planets_phase2", [])
        elif phase_state == "phase3":
            planets_config = ASSET_CONFIG.get("planets_phase3", [])
        else:
            planets_config = []
        
        for p in planets_config:
            pi = ASSETS.load_image(p.get("image"), scale=(p.get("size"), p.get("size")))
            if pi:
                surf.blit(pi, (p.get("x"), p.get("y")))

# ---------------- Sprites ----------------
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, controls, color=None, name="PLAYER", player_num=1):
        super().__init__()
        self.player_num = player_num
        color = color if color is not None else ASSET_CONFIG.get("player_default_color", (0,120,255))
        p_cfg = ASSET_CONFIG.get("players", {})
        dead_cfg = ASSET_CONFIG.get("players_dead", {})
        
        img_name = p_cfg.get("player")
        size = tuple(p_cfg.get("size", (100,70)))
        img = ASSETS.load_image(img_name, scale=size) if img_name else None
        
        dead_img_name = dead_cfg.get("player_dead")
        dead_img = ASSETS.load_image(dead_img_name, scale=size) if dead_img_name else None
        
        if img:
            self.normal_image = img
        else:
            surf = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.polygon(surf, color, [(size[0]//2,0),(size[0]//6,size[1]),(5*size[0]//6,size[1])])
            self.normal_image = surf
        
        if dead_img:
            self.dead_image = dead_img
        else:
            dead_surf = pygame.Surface(size, pygame.SRCALPHA)
            dead_color = ASSET_CONFIG.get("player_dead_color", (100, 100, 100, 150))
            pygame.draw.polygon(dead_surf, dead_color, [(size[0]//2,0),(size[0]//6,size[1]),(5*size[0]//6,size[1])])
            pygame.draw.line(dead_surf, (200, 50, 50, 200), (10, 10), (size[0]-10, size[1]-10), 3)
            pygame.draw.line(dead_surf, (200, 50, 50, 200), (size[0]-10, 10), (10, size[1]-10), 3)
            self.dead_image = dead_surf
        
        self.image = self.normal_image.copy()
        self.rect = self.image.get_rect(center=(x,y))
        self.controls = controls
        self.speed = 6
        self.health = 100
        self.max_health = 100
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
        
        # Sistema de vidas e respawn
        self.lives = ASSET_CONFIG.get("initial_lives", 3)
        self.is_alive = True
        self.respawn_timer = 0
        self.respawn_time = ASSET_CONFIG.get("respawn_time", 5000)
        self.respawn_blink = 0
        self.respawn_blink_speed = 0.1
        
        # Temporizadores para powerups temporários
        self.upgrade_end_time = 0
        self.shield_end_time = 0
        
        # Efeitos visuais
        self.shield_alpha = 0
        self.is_upgraded = False

    def update(self):
        if not self.is_alive:
            now = pygame.time.get_ticks()
            
            self.respawn_blink += self.respawn_blink_speed
            alpha = int((math.sin(self.respawn_blink) + 1) * 127.5)
            
            if self.respawn_timer and now < self.respawn_timer:
                remaining = (self.respawn_timer - now) / 1000
                self.image = self.dead_image.copy()
                self.image.set_alpha(alpha)
            else:
                self.image = self.dead_image.copy()
                self.image.set_alpha(180)
            return
        
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
            self.rect.centerx += int((mx - self.rect.centerx) * 0.35)
            self.rect.centery += int((my - self.rect.centery) * 0.35)
        self.rect.clamp_ip(screen.get_rect())
        
        now = pygame.time.get_ticks()
        
        if self.upgrade_end_time and now > self.upgrade_end_time:
            self.extra_guns = 0
            self.upgrade_end_time = 0
            self.is_upgraded = False
        
        if self.shield_end_time and now > self.shield_end_time:
            self.has_shield = False
            self.shield_end_time = 0
            self.shield_alpha = 0
        
        if self.invulnerable_until and now > self.invulnerable_until:
            self.invulnerable_until = 0
        
        if self.has_shield:
            self.shield_alpha = (self.shield_alpha + 10) % 255
            shield_surf = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (100, 200, 255, int(self.shield_alpha)), 
                              (shield_surf.get_width()//2, shield_surf.get_height()//2), 
                              min(shield_surf.get_width(), shield_surf.get_height())//2, 3)
            
            combined = self.normal_image.copy()
            shield_rect = shield_surf.get_rect(center=(combined.get_width()//2, combined.get_height()//2))
            combined.blit(shield_surf, shield_rect, special_flags=pygame.BLEND_ALPHA_SDL2)
            self.image = combined
        elif self.is_upgraded:
            upgraded = self.normal_image.copy()
            glow = pygame.Surface(upgraded.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 255, 100, 30), glow.get_rect(), border_radius=10)
            upgraded.blit(glow, (0,0), special_flags=pygame.BLEND_ALPHA_SDL2)
            self.image = upgraded
        else:
            self.image = self.normal_image.copy()

    def shoot(self):
        if not self.is_alive:
            return None
            
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.shoot_delay:
            self.last_shot = now
            bullets_out = []
            bullets_out.append(Bullet(self.rect.centerx, self.rect.top, speed=-12, owner="player"))
            
            if self.extra_guns >= 1:
                bullets_out.append(Bullet(self.rect.left+10, self.rect.centery, speed=-12, owner="player"))
                bullets_out.append(Bullet(self.rect.right-10, self.rect.centery, speed=-12, owner="player"))
            return bullets_out
        return None

    def take_damage(self, amount):
        if not self.is_alive:
            return False
            
        now = pygame.time.get_ticks()
        if self.invulnerable_until and now < self.invulnerable_until:
            return False
        if self.has_shield:
            return False
            
        self.health -= amount
        if self.health <= 0:
            self.die()
        return True

    def die(self):
        self.health = 0
        self.is_alive = False
        self.lives -= 1
        
        self.extra_guns = 0
        self.upgrade_end_time = 0
        self.is_upgraded = False
        self.has_shield = False
        self.shield_end_time = 0
        self.invulnerable_until = 0
        self.teleport_ability = False
        
        return True

    def respawn(self):
        """Player ressuscita"""
        self.is_alive = True
        self.health = self.max_health // 2
        self.respawn_timer = 0
        
        safe_x = WIDTH // 2 if self.player_num == 1 else WIDTH // 4
        self.rect.center = (safe_x, HEIGHT - 120)
        
        self.invulnerable_until = pygame.time.get_ticks() + 3000
        
        # Aplica volume no som de respawn
        if respawn_snd:
            set_sound_volume(respawn_snd, "respawn")
            respawn_snd.play()
        return True

    def teleport(self):
        if not self.is_alive or not self.teleport_ability:
            return False
        self.rect.centerx = random.randint(80, WIDTH-80)
        self.rect.centery = random.randint(80, HEIGHT-160)
        self.invulnerable_until = pygame.time.get_ticks() + 3000
        self.teleport_ability = False
        return True
    
    def activate_upgrade(self, duration=15000):
        if not self.is_alive:
            return
        self.extra_guns = 1
        self.upgrade_end_time = pygame.time.get_ticks() + duration
        self.is_upgraded = True
    
    def activate_shield(self, duration=8000):
        if not self.is_alive:
            return
        self.has_shield = True
        self.shield_end_time = pygame.time.get_ticks() + duration
    
    def activate_invulnerability(self, duration=5000):
        if not self.is_alive:
            return
        self.invulnerable_until = pygame.time.get_ticks() + duration

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=-12, owner="player"):
        super().__init__()
        bcfg = ASSET_CONFIG.get("bullets", {})
        img_name = bcfg.get("image")
        size = tuple(bcfg.get("size", (12,20)))
        img = ASSETS.load_image(img_name, scale=size) if img_name else None
        if img:
            self.image = img
        else:
            surf = pygame.Surface(size, pygame.SRCALPHA)
            c = (255,0,0) if owner=="enemy" else (255,255,0)
            pygame.draw.rect(surf, c, (0,0,size[0],size[1]))
            self.image = surf
        self.rect = self.image.get_rect(center=(x,y))
        self.speed = speed
        self.speedx = 0
        self.owner = owner

    def update(self):
        self.rect.y += self.speed
        self.rect.x += self.speedx
        if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, kind="default", x=None, y=None):
        super().__init__()
        mcfg = ASSET_CONFIG.get("meteors", {})
        img_name = mcfg.get(kind, mcfg.get("default"))
        size = (64,64)
        img = ASSETS.load_image(img_name, scale=size) if img_name else None
        if img:
            self.base = img
        else:
            surf = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.circle(surf, (120,120,120), (size[0]//2, size[1]//2), 30)
            self.base = surf
        self.image = self.base.copy()
        
        # CORREÇÃO: Melhor inicialização de posição
        if x is not None and y is not None:
            self.rect = self.image.get_rect(center=(x, y))
        else:
            self.rect = self.image.get_rect(center=(random.randint(40, WIDTH-40), random.randint(-300, -40)))
        
        if kind == "evil":
            self.speedy = random.randint(1,3)
            self.damage = 40
        else:
            self.speedy = random.randint(1,2)
            self.damage = 20
        self.speedx = random.randint(-2,2)
        self.rot = 0
        self.rot_speed = random.randint(-5,5)
        self.kind = kind

    def update(self):
        self.rect.y += int(self.speedy * GLOBAL_SPEED_MULT)
        self.rect.x += self.speedx
        self.rot = (self.rot + self.rot_speed) % 360
        try:
            self.image = pygame.transform.rotate(self.base, self.rot)
        except Exception:
            self.image = self.base
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center
        if self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.respawn()

    def respawn(self):
        self.rect.x = random.randint(0, WIDTH-40)
        self.rect.y = random.randint(-220, -40)
        if self.kind == "evil":
            self.speedy = random.randint(1,3)
        else:
            self.speedy = random.randint(1,2)
        self.speedx = random.randint(-2,2)
        self.rot_speed = random.randint(-5,5)

class EnemyShip(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        enx = ASSET_CONFIG.get("enemies", {})
        img = ASSETS.load_image(enx.get("enemy_small"), scale=tuple(enx.get("size", (64,64)))) if enx.get("enemy_small") else None
        if img:
            self.image = img
        else:
            size = tuple(enx.get("size", (64,64)))
            surf = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.polygon(surf, (180,80,40), [(size[0]//2,0),(0,size[1]),(size[0],size[1])])
            self.image = surf
        self.rect = self.image.get_rect(center=(x,y))
        self.health = 3
        self.last_shot = 0
        self.shoot_delay = 900 + random.randint(-200,200)
        self.fire_speed = 6
        self.move_timer = pygame.time.get_ticks()

    def update(self):
        t = pygame.time.get_ticks()
        if t - self.move_timer > 1200:
            self.move_timer = t
            self.rect.x += random.choice([-40,-20,0,20,40])
            self.rect.clamp_ip(screen.get_rect())

    def aim_and_shoot(self, target):
        if not target:
            return
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.shoot_delay:
            self.last_shot = now
            bx = self.rect.centerx
            by = self.rect.bottom
            b = Bullet(bx, by, speed=self.fire_speed, owner="enemy")
            all_sprites.add(b); bullets.add(b)

    def take_damage(self, amount=1):
        self.health -= amount
        return self.health <= 0

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        bcfg = ASSET_CONFIG.get("boss", {})
        img = ASSETS.load_image(bcfg.get("image"), scale=tuple(bcfg.get("size", (220,220)))) if bcfg.get("image") else None
        if img:
            self.image = img
        else:
            size = tuple(bcfg.get("size", (220,220)))
            surf = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.circle(surf, (150,30,200), (size[0]//2, size[1]//2), min(size)//2)
            pygame.draw.circle(surf, (255,200,255), (size[0]//2, size[1]//2), min(size)//2, 6)
            self.image = surf
        self.rect = self.image.get_rect(center=(x,y))
        self.health = 80
        self.last_shot = 0
        self.shoot_delay = 1500
        self.move_dir = 1
        self.speed = 2
        self.attack_mode = "normal"
        self.attack_timer = pygame.time.get_ticks()
        self.attack_duration = 5000

    def update(self):
        self.rect.x += self.speed * self.move_dir
        if self.rect.right > WIDTH - 100:
            self.move_dir = -1
        elif self.rect.left < 100:
            self.move_dir = 1
        
        now = pygame.time.get_ticks()
        if now - self.attack_timer > self.attack_duration:
            self.attack_timer = now
            modes = ["normal", "spread", "rapid"]
            self.attack_mode = random.choice(modes)

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            
            if self.attack_mode == "normal":
                for off in (-40, 0, 40):
                    b = Bullet(self.rect.centerx + off, self.rect.bottom, speed=8, owner="enemy")
                    all_sprites.add(b); bullets.add(b)
            
            elif self.attack_mode == "spread":
                angles = [-30, -15, 0, 15, 30]
                for angle in angles:
                    b = Bullet(self.rect.centerx, self.rect.bottom, speed=8, owner="enemy")
                    b.speedx = angle * 0.2
                    all_sprites.add(b); bullets.add(b)
            
            elif self.attack_mode == "rapid":
                self.shoot_delay = 300
                b = Bullet(self.rect.centerx, self.rect.bottom, speed=10, owner="enemy")
                all_sprites.add(b); bullets.add(b)
            else:
                self.shoot_delay = 1500

# Explosion frames load
EXPLOSION_FRAMES = []
EXPLOSION_LOADED = False
def load_explosion_frames():
    global EXPLOSION_FRAMES, EXPLOSION_LOADED
    if EXPLOSION_LOADED:
        return
    EXPLOSION_LOADED = True
    frames = []
    for name in ASSET_CONFIG.get("explosion_frames", []):
        img = ASSETS.load_image(name, scale=ASSET_CONFIG.get("explosion_scale"))
        if img:
            frames.append(img)
    EXPLOSION_FRAMES = frames

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        load_explosion_frames()
        if EXPLOSION_FRAMES:
            self.frames = EXPLOSION_FRAMES.copy()
            self.index = 0
            self.image = self.frames[self.index]
            self.rect = self.image.get_rect(center=center)
            self.last = pygame.time.get_ticks()
            self.rate = 60
        else:
            self.image = pygame.Surface((2,2), pygame.SRCALPHA)
            self.rect = self.image.get_rect(center=center)
            self._auto_kill = True

    def update(self):
        if getattr(self, "_auto_kill", False):
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
    def __init__(self, center, ptype="revive"):
        super().__init__()
        self.ptype = ptype
        self.size = 28
        
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        if ptype == "revive": 
            color = (200, 30, 30)
            pygame.draw.circle(self.image, color, (self.size//2, self.size//2), self.size//2)
        elif ptype == "invul_gift": 
            color = (30, 100, 200)
            pygame.draw.rect(self.image, color, (0, 0, self.size, self.size), border_radius=5)
        elif ptype == "upgrade": 
            color = (220, 200, 30)
            points = [(self.size//2, 2), (2, self.size-2), (self.size-2, self.size-2)]
            pygame.draw.polygon(self.image, color, points)
        elif ptype == "extra_life": 
            color = (30, 200, 60)
            pygame.draw.rect(self.image, color, (2, 2, self.size-4, self.size-4))
        elif ptype == "teleporter": 
            color = (180, 80, 180)
            pygame.draw.circle(self.image, color, (self.size//2, self.size//2), self.size//3)
        elif ptype == "shield":
            color = (100, 200, 255)
            pygame.draw.circle(self.image, color, (self.size//2, self.size//2), self.size//2, 3)
        else: 
            color = (255, 255, 255)
            pygame.draw.rect(self.image, color, (0, 0, self.size, self.size))
        
        glow = pygame.Surface((self.size+4, self.size+4), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*color, 100), (0, 0, self.size+4, self.size+4), border_radius=7)
        final_image = pygame.Surface((self.size+4, self.size+4), pygame.SRCALPHA)
        final_image.blit(glow, (0, 0))
        final_image.blit(self.image, (2, 2))
        self.image = final_image
        
        self.rect = self.image.get_rect(center=center)
        self.float_offset = random.random() * 3.14
        self.float_speed = 0.05

    def update(self):
        self.rect.y += 2 + math.sin(pygame.time.get_ticks() * self.float_speed + self.float_offset)
        if self.rect.top > HEIGHT:
            self.kill()

# ---------------- Sounds ----------------
# Carregar sons e aplicar volumes iniciais
shoot_snd = ASSETS.load_sound(ASSET_CONFIG.get("sounds", {}).get("shoot"))
explosion_snd = ASSETS.load_sound(ASSET_CONFIG.get("sounds", {}).get("explosion"))
powerup_snd = ASSETS.load_sound(ASSET_CONFIG.get("sounds", {}).get("powerup"))
respawn_snd = ASSETS.load_sound(ASSET_CONFIG.get("sounds", {}).get("respawn"))

# Aplicar volumes iniciais aos sons
if shoot_snd: set_sound_volume(shoot_snd, "shoot")
if explosion_snd: set_sound_volume(explosion_snd, "explosion")
if powerup_snd: set_sound_volume(powerup_snd, "powerup")  # Volume reduzido por padrão
if respawn_snd: set_sound_volume(respawn_snd, "respawn")

# ---------------- Variáveis Globais ----------------
enemies_total = 0
enemies_killed = 0
current_enemy_wave = 0
TOTAL_ENEMIES_PHASE2 = 15
ENEMIES_PER_WAVE = 5

# ---------------- Funções de Spawn ----------------
def spawn_enemy_wave(count):
    global enemies_total
    
    margin = 120
    if count > 1:
        spacing = max(1, (WIDTH - 2*margin) // max(1, count-1))
    else:
        spacing = 0
    
    for i in range(count):
        x = margin + i*spacing if count > 1 else WIDTH//2
        y = 120 + random.randint(-20,20)
        es = EnemyShip(x,y)
        enemies.add(es)
        all_sprites.add(es)
        enemies_total += 1

def spawn_special_meteor():
    kind = random.choices(["default","evil","power","invul","extra_life","teleporter","revive", "shield"], 
                         [35,15,12,10,15,10,5,3])[0]
    m = Meteor(kind=kind); all_sprites.add(m); meteors.add(m)

def drop_powerup(center, phase):
    if phase == "asteroids":
        pool = ["invul_gift", "upgrade", "extra_life", "teleporter", "shield"]
        if two_player:
            pool.append("revive")  # Só dropa powerup revive em 2 jogadores
    elif phase == "phase2":
        pool = ["upgrade", "extra_life", "shield", "invul_gift"]
        weights = [30, 25, 25, 20]
    elif phase == "phase3":
        pool = ["shield", "extra_life", "upgrade"]
        weights = [40, 35, 25]
    else:
        pool = ["extra_life", "invul_gift", "upgrade"]
        weights = [40, 30, 30]
    
    ptype = random.choices(pool, weights=weights if 'weights' in locals() else None)[0]
    pu = Powerup(center, ptype=ptype)
    all_sprites.add(pu)
    powerups.add(pu)
    return pu

# ---------------- Groups & init ----------------
background = Background()
all_sprites = pygame.sprite.Group()
meteors = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
explosions = pygame.sprite.Group()
enemies = pygame.sprite.Group()

controls_p1 = {'left':pygame.K_a,'right':pygame.K_d,'up':pygame.K_w,'down':pygame.K_s,'shoot':pygame.K_SPACE}
controls_p2 = {'left':pygame.K_LEFT,'right':pygame.K_RIGHT,'up':pygame.K_UP,'down':pygame.K_DOWN,'shoot':pygame.K_KP0}

player1 = Player(WIDTH//2, HEIGHT-120, controls_p1, color=ASSET_CONFIG.get("player_default_color"), player_num=1)
player2 = Player(WIDTH//4, HEIGHT-120, controls_p2, color=(255,100,100), player_num=2)
all_sprites.add(player1)

MAX_METEORS = ASSET_CONFIG.get("max_meteors", 8)
for _ in range(MAX_METEORS):
    m = Meteor(kind=random.choice(["default","default","evil"]))
    all_sprites.add(m); meteors.add(m)

phase = 1
phase_state = "asteroids"
two_player = False
menu_options = ["Jogar 1 Jogador", "Jogar 2 Jogadores", "Controles", "Highscores", "Ajustar Volume", "Carregar Jogo", "Sair"]
menu_index = 0

# Menu de volume
volume_options = ["Volume Geral", "Volume Música", "Volume Efeitos", 
                  "Volume Tiros", "Volume Explosões", "Volume Powerups", 
                  "Volume Respawn", "Restaurar Padrão", "Voltar ao Menu"]
volume_index = 0
volume_adjusting = False
current_volume_type = "master"

# Menu de pausa
pause_options = ["Continuar", "Controles", "Ajustar Volume", "Salvar Jogo", "Carregar Jogo", "Voltar ao Menu", "Sair"]
pause_index = 0

POINTS_TO_NEXT_PHASE = ASSET_CONFIG.get("points_to_next_phase", 1500)
GLOBAL_SPEED_MULT = 1.0

# highscores load com mais informações
try:
    with open(HIGHSCORES_FILE, "r") as f:
        highscores = json.load(f)
except Exception:
    highscores = []

def add_highscore(name, score, phases_completed=1, victory=False):
    """Adiciona highscore com informações detalhadas"""
    global highscores
    
    # Determinar progresso
    progress = ""
    if victory:
        progress = "VITÓRIA (Fase 3)"
    elif phases_completed >= 2:
        progress = f"Fase {phases_completed}"
    else:
        progress = "Fase 1"
    
    highscores.append({
        "name": name, 
        "score": score, 
        "date": time.strftime("%Y-%m-%d %H:%M"),
        "phases": phases_completed,
        "victory": victory,
        "progress": progress
    })
    
    # Manter apenas os 10 melhores
    highscores = sorted(highscores, key=lambda x: x["score"], reverse=True)[:10]
    
    with open(HIGHSCORES_FILE, "w") as f:
        json.dump(highscores, f, indent=2)

# ---------------- Game functions ----------------
def reset_game(two_p=False):
    global player1, player2, all_sprites, meteors, bullets, powerups, explosions, enemies, phase, phase_state, two_player, GLOBAL_SPEED_MULT, boss, last_minion_spawn, enemies_total, enemies_killed, current_enemy_wave
    
    phase = 1
    phase_state = "asteroids"
    two_player = two_p
    GLOBAL_SPEED_MULT = 1.0
    enemies_total = 0
    enemies_killed = 0
    current_enemy_wave = 0
    
    all_sprites.empty(); meteors.empty(); bullets.empty(); powerups.empty(); explosions.empty(); enemies.empty()
    player1 = Player(WIDTH//2, HEIGHT-120, controls_p1, color=ASSET_CONFIG.get("player_default_color"), player_num=1)
    player2 = Player(WIDTH//4, HEIGHT-120, controls_p2, color=(255,100,100), player_num=2)
    all_sprites.add(player1)
    if two_player:
        all_sprites.add(player2)
    for _ in range(MAX_METEORS):
        m = Meteor(kind=random.choice(["default","default","evil"]))
        all_sprites.add(m); meteors.add(m)
    boss = None
    last_minion_spawn = 0
    
    change_music("asteroids")

def save_game():
    """Salva o estado atual do jogo"""
    try:
        # Determinar fases completadas
        phases_completed = 1
        if phase_state == "phase2" or phase_state == "boss_transition":
            phases_completed = 2
        elif phase_state == "phase3" or phase_state == "victory":
            phases_completed = 3
        
        # Coletar dados dos meteors CORRIGIDO
        meteors_data = []
        for m in meteors:
            meteors_data.append({
                "x": m.rect.centerx,
                "y": m.rect.centery,
                "kind": m.kind,
                "speedy": m.speedy,
                "speedx": m.speedx,
                "rot": m.rot,
                "rot_speed": m.rot_speed
            })
        
        data = {
            "phase": phase,
            "phase_state": phase_state,
            "two_player": two_player,
            "phases_completed": phases_completed,
            "player1": {
                "x": player1.rect.centerx,
                "y": player1.rect.centery,
                "health": player1.health,
                "score": player1.score,
                "extra_guns": player1.extra_guns,
                "teleport": player1.teleport_ability,
                "lives": player1.lives,
                "is_alive": player1.is_alive
            },
            "player2": {
                "x": player2.rect.centerx,
                "y": player2.rect.centery,
                "health": player2.health,
                "score": player2.score,
                "extra_guns": player2.extra_guns,
                "teleport": player2.teleport_ability,
                "lives": player2.lives,
                "is_alive": player2.is_alive
            },
            "meteors": meteors_data,
            "global_speed_mult": GLOBAL_SPEED_MULT,
            "enemies_killed": enemies_killed,
            "current_enemy_wave": current_enemy_wave
        }
        
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
        
        print("💾 Jogo salvo com sucesso!")
        return True
    except Exception as e:
        print(f"⚠ Erro ao salvar jogo: {e}")
        return False

def load_game():
    """Carrega um jogo salvo - CORREÇÃO CRÍTICA para meteors"""
    global phase, phase_state, two_player, GLOBAL_SPEED_MULT, enemies_killed, current_enemy_wave
    
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
    except Exception as e:
        print("⚠ Falha ao carregar jogo:", e)
        return False
    
    # Carregar dados básicos
    phase = data.get("phase", 1)
    phase_state = data.get("phase_state", "asteroids")
    two_player = data.get("two_player", False)
    GLOBAL_SPEED_MULT = data.get("global_speed_mult", 1.0)
    enemies_killed = data.get("enemies_killed", 0)
    current_enemy_wave = data.get("current_enemy_wave", 0)
    
    # Limpar grupos
    all_sprites.empty()
    meteors.empty()
    bullets.empty()
    powerups.empty()
    explosions.empty()
    enemies.empty()
    
    # Carregar Player 1
    p1 = data.get("player1", {})
    player1.rect.centerx = p1.get("x", WIDTH//2)
    player1.rect.centery = p1.get("y", HEIGHT-120)
    player1.health = p1.get("health", 100)
    player1.score = p1.get("score", 0)
    player1.extra_guns = p1.get("extra_guns", 0)
    player1.teleport_ability = p1.get("teleport", False)
    player1.lives = p1.get("lives", 3)
    player1.is_alive = p1.get("is_alive", True)
    
    # Atualizar imagem do player 1
    if player1.is_alive:
        player1.image = player1.normal_image.copy()
    else:
        player1.image = player1.dead_image.copy()
    
    all_sprites.add(player1)
    
    # Carregar Player 2 se existir
    if two_player:
        p2 = data.get("player2", {})
        player2.rect.centerx = p2.get("x", WIDTH//4)
        player2.rect.centery = p2.get("y", HEIGHT-120)
        player2.health = p2.get("health", 100)
        player2.score = p2.get("score", 0)
        player2.extra_guns = p2.get("extra_guns", 0)
        player2.teleport_ability = p2.get("teleport", False)
        player2.lives = p2.get("lives", 3)
        player2.is_alive = p2.get("is_alive", True)
        
        # Atualizar imagem do player 2
        if player2.is_alive:
            player2.image = player2.normal_image.copy()
        else:
            player2.image = player2.dead_image.copy()
        
        all_sprites.add(player2)
    
    # CORREÇÃO CRÍTICA: Recriar meteors corretamente
    meteors_data = data.get("meteors", [])
    for md in meteors_data:
        # Usar o construtor corrigido que aceita x e y
        m = Meteor(
            kind=md.get("kind", "default"),
            x=md.get("x", random.randint(40, WIDTH-40)),
            y=md.get("y", random.randint(-300, -40))
        )
        
        # Restaurar atributos adicionais
        m.speedy = md.get("speedy", 1)
        m.speedx = md.get("speedx", 0)
        m.rot = md.get("rot", 0)
        m.rot_speed = md.get("rot_speed", random.randint(-5,5))
        m.damage = 40 if md.get("kind") == "evil" else 20
        
        # Adicionar aos grupos
        meteors.add(m)
        all_sprites.add(m)
    
    # Se não houver meteors no save, criar novos
    if len(meteors) == 0 and phase_state == "asteroids":
        for _ in range(MAX_METEORS):
            m = Meteor(kind=random.choice(["default","default","evil"]))
            all_sprites.add(m)
            meteors.add(m)
    
    print("✅ Jogo carregado com sucesso!")
    return True

# Funções para o menu de volume
def draw_volume_menu(screen):
    """Desenha o menu de ajuste de volume"""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    screen.blit(overlay, (0, 0))
    
    draw_text(screen, "🎵 CONFIGURAÇÃO DE VOLUME", 60, WIDTH//2, 60)
    
    for i, opt in enumerate(volume_options):
        color = (255, 255, 0) if i == volume_index else (200, 200, 200)
        
        if opt == "Restaurar Padrão":
            draw_text(screen, opt, 36, WIDTH//2, 180 + i*55, color)
        elif opt == "Voltar ao Menu":
            draw_text(screen, opt, 36, WIDTH//2, 180 + i*55, color)
        else:
            # Extrair o tipo de volume do texto
            vol_type = ""
            if "Geral" in opt:
                vol_type = "master"
            elif "Música" in opt:
                vol_type = "music"
            elif "Efeitos" in opt:
                vol_type = "effects"
            elif "Tiros" in opt:
                vol_type = "shoot"
            elif "Explosões" in opt:
                vol_type = "explosion"
            elif "Powerups" in opt:
                vol_type = "powerup"
            elif "Respawn" in opt:
                vol_type = "respawn"
            
            current_vol = VOLUME_CONFIG.get(vol_type, 0.5) * 100
            bar_width = 200
            bar_height = 20
            bar_x = WIDTH//2 - bar_width//2
            bar_y = 180 + i*55 + 25
            
            # Barra de volume
            fill_width = int((current_vol / 100) * bar_width)
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))
            pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
            
            # Texto com porcentagem
            display_text = f"{opt}: {current_vol:.0f}%"
            if volume_adjusting and vol_type == current_volume_type:
                display_text = f"> {display_text} <"
            
            draw_text(screen, display_text, 30, WIDTH//2, 180 + i*55, color)
    
    if volume_adjusting:
        draw_text(screen, "Use ← → para ajustar, ENTER para confirmar", 22, WIDTH//2, HEIGHT-80)
    else:
        draw_text(screen, "Use ↑↓ para navegar, ENTER para selecionar", 22, WIDTH//2, HEIGHT-80)
    
    draw_text(screen, "ESC para voltar sem salvar", 20, WIDTH//2, HEIGHT-40)

def update_volume(type_key, delta):
    """Atualiza um tipo específico de volume"""
    global VOLUME_CONFIG
    
    current = VOLUME_CONFIG.get(type_key, 0.5)
    new_volume = max(0.0, min(1.0, current + delta))
    VOLUME_CONFIG[type_key] = new_volume
    
    # Aplicar imediatamente
    if type_key == "master" or type_key == "music":
        set_music_volume()
    
    # Aplicar volumes aos sons existentes
    if shoot_snd and type_key in ["master", "effects", "shoot"]:
        set_sound_volume(shoot_snd, "shoot")
    if explosion_snd and type_key in ["master", "effects", "explosion"]:
        set_sound_volume(explosion_snd, "explosion")
    if powerup_snd and type_key in ["master", "effects", "powerup"]:
        set_sound_volume(powerup_snd, "powerup")
    if respawn_snd and type_key in ["master", "effects", "respawn"]:
        set_sound_volume(respawn_snd, "respawn")
    
    return new_volume

def restore_default_volumes():
    """Restaura os volumes padrão"""
    global VOLUME_CONFIG
    VOLUME_CONFIG = DEFAULT_VOLUMES.copy()
    
    # Aplicar volumes
    set_music_volume()
    if shoot_snd: set_sound_volume(shoot_snd, "shoot")
    if explosion_snd: set_sound_volume(explosion_snd, "explosion")
    if powerup_snd: set_sound_volume(powerup_snd, "powerup")
    if respawn_snd: set_sound_volume(respawn_snd, "respawn")
    
    save_volume_config(VOLUME_CONFIG)

# ---------------- Main loop variables ----------------
running = True
pause_menu = False
transition_start = None
boss = None
last_minion_spawn = 0
game_state = "intro"

# Tocar música inicial
try:
    change_music("asteroids")
except:
    pass

# ---------------- Main Loop ----------------
while running:
    dt = clock.tick(60) / 1000.0

    # --- events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            # MENU PRINCIPAL
            if game_state == "intro":
                if event.key == pygame.K_UP:
                    menu_index = (menu_index - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    menu_index = (menu_index + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    escolha = menu_options[menu_index]
                    if escolha == "Jogar 1 Jogador":
                        reset_game(two_p=False); game_state = "playing"
                    elif escolha == "Jogar 2 Jogadores":
                        reset_game(two_p=True); game_state = "playing"
                    elif escolha == "Controles":
                        game_state = "controls"
                    elif escolha == "Highscores":
                        game_state = "highscores"
                    elif escolha == "Ajustar Volume":
                        game_state = "volume_menu"
                        volume_index = 0
                        volume_adjusting = False
                    elif escolha == "Carregar Jogo":
                        if load_game():
                            game_state = "playing"
                        else:
                            print("❌ Não foi possível carregar o jogo")
                    elif escolha == "Sair":
                        running = False
            
            # MENU DE VOLUME
            elif game_state == "volume_menu":
                if event.key == pygame.K_ESCAPE:
                    # Salvar configurações ao sair
                    save_volume_config(VOLUME_CONFIG)
                    game_state = "intro"
                
                if volume_adjusting:
                    if event.key == pygame.K_LEFT:
                        update_volume(current_volume_type, -0.05)
                    elif event.key == pygame.K_RIGHT:
                        update_volume(current_volume_type, 0.05)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        volume_adjusting = False
                        # Salvar configurações
                        save_volume_config(VOLUME_CONFIG)
                else:
                    if event.key == pygame.K_UP:
                        volume_index = (volume_index - 1) % len(volume_options)
                    elif event.key == pygame.K_DOWN:
                        volume_index = (volume_index + 1) % len(volume_options)
                    elif event.key == pygame.K_RETURN:
                        escolha = volume_options[volume_index]
                        
                        if escolha == "Restaurar Padrão":
                            restore_default_volumes()
                        elif escolha == "Voltar ao Menu":
                            save_volume_config(VOLUME_CONFIG)
                            game_state = "intro"
                        else:
                            # Determinar tipo de volume
                            vol_type = ""
                            if "Geral" in escolha:
                                vol_type = "master"
                            elif "Música" in escolha:
                                vol_type = "music"
                            elif "Efeitos" in escolha:
                                vol_type = "effects"
                            elif "Tiros" in escolha:
                                vol_type = "shoot"
                            elif "Explosões" in escolha:
                                vol_type = "explosion"
                            elif "Powerups" in escolha:
                                vol_type = "powerup"
                            elif "Respawn" in escolha:
                                vol_type = "respawn"
                            
                            if vol_type:
                                volume_adjusting = True
                                current_volume_type = vol_type
            
            # JOGO EM ANDAMENTO
            elif game_state in ["playing","phase3"]:
                if event.key == pygame.K_ESCAPE:
                    if pause_menu:
                        pause_menu = False  # ESC fecha o menu de pausa
                    else:
                        pause_menu = True  # ESC abre o menu de pausa
                
                # Menu de pausa - navegação
                if pause_menu:
                    if event.key == pygame.K_UP:
                        pause_index = (pause_index - 1) % len(pause_options)
                    elif event.key == pygame.K_DOWN:
                        pause_index = (pause_index + 1) % len(pause_options)
                    elif event.key == pygame.K_RETURN:
                        escolha = pause_options[pause_index]
                        
                        if escolha == "Continuar":
                            pause_menu = False
                        elif escolha == "Controles":
                            game_state = "controls"
                            pause_menu = False
                        elif escolha == "Ajustar Volume":
                            game_state = "volume_menu"
                            volume_index = 0
                            volume_adjusting = False
                            pause_menu = False
                        elif escolha == "Salvar Jogo":
                            if save_game():
                                # Mostrar mensagem de sucesso
                                print("✅ Jogo salvo!")
                            pause_menu = False
                        elif escolha == "Carregar Jogo":
                            if load_game():
                                game_state = "playing"
                            pause_menu = False
                        elif escolha == "Voltar ao Menu":
                            game_state = "intro"
                            pause_menu = False
                        elif escolha == "Sair":
                            running = False
                
                # Tecla P ainda funciona para pausar
                if event.key == pygame.K_p:
                    pause_menu = not pause_menu
                
                if event.key == pygame.K_r:
                    if game_state == "game_over":
                        reset_game(two_p=two_player); game_state = "playing"
                
                if event.key == pygame.K_f:
                    save_game()
                
                if event.key == pygame.K_l:
                    if load_game():
                        game_state = "playing"
                
                if event.key == pygame.K_m:
                    player1.mouse_control = not player1.mouse_control
                
                if event.key == pygame.K_t:
                    if player1.teleport_ability and player1.is_alive:
                        player1.teleport()
            
            # OUTROS ESTADOS (controles, highscores, etc)
            elif game_state in ["controls", "highscores", "game_over", "victory"]:
                if event.key == pygame.K_ESCAPE:
                    game_state = "intro"
                elif event.key == pygame.K_RETURN:
                    game_state = "intro"

    # --- continuous input / shooting for player(s) ---
    if game_state in ("playing", "phase3") and not pause_menu and phase_state not in ("transition", "boss_transition"):
        keys = pygame.key.get_pressed()
        if keys[player1.controls["shoot"]] and player1.is_alive:
            bls = player1.shoot()
            if bls:
                for b in bls:
                    all_sprites.add(b); bullets.add(b)
                if shoot_snd: 
                    # Reaplica volume antes de tocar
                    set_sound_volume(shoot_snd, "shoot")
                    shoot_snd.play()
        if two_player and (keys[player2.controls["shoot"]] or keys[pygame.K_KP0] or keys[pygame.K_RCTRL]) and player2.is_alive:
            bls = player2.shoot()
            if bls:
                for b in bls:
                    all_sprites.add(b); bullets.add(b)
                if shoot_snd: 
                    set_sound_volume(shoot_snd, "shoot")
                    shoot_snd.play()

    # --- enemy AI & boss actions ---
    if game_state in ("playing","phase3") and not pause_menu and phase_state not in ("transition", "boss_transition"):
        if phase_state == "phase2" or phase_state == "phase3":
            for es in list(enemies):
                targets = [p for p in (player1, player2) if p in all_sprites and getattr(p, "is_alive", False)]
                if not targets:
                    continue
                target = min(targets, key=lambda t: abs(t.rect.centerx - es.rect.centerx))
                es.aim_and_shoot(target)
        if boss and phase_state == "phase3":
            boss.shoot()

    # --- updates ---
    if game_state in ("playing", "phase3") and not pause_menu and phase_state not in ("transition", "boss_transition"):
        all_sprites.update()
        meteors.update()
        bullets.update()
        powerups.update()
        explosions.update()
        enemies.update()
        if boss:
            boss.update()
        
        # enemy bullets -> players (só players vivos)
        if player1.is_alive:
            hits_from_enemy = [b for b in bullets if getattr(b, "owner", "") == "enemy" and b.rect.colliderect(player1.rect)]
            for b in hits_from_enemy:
                if player1.take_damage(15):
                    ex = Explosion(player1.rect.center); all_sprites.add(ex); explosions.add(ex)
                    if explosion_snd: 
                        set_sound_volume(explosion_snd, "explosion")
                        explosion_snd.play()
                b.kill()

        if two_player and player2.is_alive:
            hits_from_enemy = [b for b in bullets if getattr(b, "owner", "") == "enemy" and b.rect.colliderect(player2.rect)]
            for b in hits_from_enemy:
                if player2.take_damage(15):
                    ex = Explosion(player2.rect.center); all_sprites.add(ex); explosions.add(ex)
                    if explosion_snd: 
                        set_sound_volume(explosion_snd, "explosion")
                        explosion_snd.play()
                b.kill()

    # --- collisions & phase logic ---
    if game_state in ("playing","phase3") and not pause_menu and phase_state not in ("transition", "boss_transition"):
        # ----- PHASE 1: ASTEROIDS -----
        if phase_state == "asteroids":
            hits = pygame.sprite.groupcollide(meteors, bullets, False, True)
            for meteor, bullets_hit in hits.items():
                ex = Explosion(meteor.rect.center); all_sprites.add(ex); explosions.add(ex)
                if explosion_snd: 
                    set_sound_volume(explosion_snd, "explosion")
                    explosion_snd.play()

                credited = False
                for b in bullets_hit:
                    if getattr(b, "owner", "") == "player":
                        player1.score += 10
                        credited = True
                if not credited and two_player:
                    player2.score += 10
                if not credited and not two_player:
                    player1.score += 10

                if random.random() < 0.5:
                    drop_powerup(meteor.rect.center, "asteroids")

                total_score = player1.score + (player2.score if two_player else 0)
                if total_score > 0 and total_score % 500 == 0:
                    GLOBAL_SPEED_MULT += 0.3

                meteor.respawn()

                # check transition to next phase
                if (not two_player and player1.score >= POINTS_TO_NEXT_PHASE) or (two_player and (player1.score + player2.score) >= POINTS_TO_NEXT_PHASE):
                    for m in list(meteors):
                        m.kill()
                    meteors.empty()
                    bullets.empty()
                    powerups.empty()
                    phase_state = "transition"
                    game_state = "next_phase"
                    transition_start = pygame.time.get_ticks()
                    break

            # meteors -> players collisions (só players vivos)
            if player1.is_alive:
                hits_p1 = pygame.sprite.spritecollide(player1, meteors, False)
                for hit in hits_p1:
                    if player1.take_damage(hit.damage):
                        e = Explosion(hit.rect.center); all_sprites.add(e); explosions.add(e)
                        if explosion_snd: 
                            set_sound_volume(explosion_snd, "explosion")
                            explosion_snd.play()
                    hit.respawn()
            if two_player and player2.is_alive:
                hits_p2 = pygame.sprite.spritecollide(player2, meteors, False)
                for hit in hits_p2:
                    if player2.take_damage(hit.damage):
                        e = Explosion(hit.rect.center); all_sprites.add(e); explosions.add(e)
                        if explosion_snd: 
                            set_sound_volume(explosion_snd, "explosion")
                            explosion_snd.play()
                    hit.respawn()

        # ----- PHASE 2: ENEMIES -----
        elif phase_state == "phase2":
            # Detecção de colisão bullets->enemies na fase 2
            hits_en = pygame.sprite.groupcollide(enemies, bullets, False, True)
            for en, bls in hits_en.items():
                dmg = sum(1 for b in bls if getattr(b,"owner","")=="player")
                if dmg > 0:
                    dead = en.take_damage(dmg)
                    if dead:
                        enemies_killed += 1
                        ex = Explosion(en.rect.center); all_sprites.add(ex); explosions.add(ex)
                        
                        drop_chance = 0.6
                        if enemies_killed % 3 == 0:
                            drop_chance = 1.0
                        
                        if random.random() < drop_chance:
                            drop_powerup(en.rect.center, "phase2")
                        
                        en.kill(); enemies.remove(en)
            
            if len(enemies) == 0 and enemies_killed < TOTAL_ENEMIES_PHASE2:
                next_spawn = min(ENEMIES_PER_WAVE, TOTAL_ENEMIES_PHASE2 - enemies_killed)
                if next_spawn > 0:
                    current_enemy_wave += 1
                    spawn_enemy_wave(next_spawn)
            
            elif enemies_killed >= TOTAL_ENEMIES_PHASE2 and len(enemies) == 0:
                bullets.empty()
                powerups.empty()
                phase_state = "boss_transition"
                game_state = "next_phase"
                transition_start = pygame.time.get_ticks()

        # ----- PHASE 3 (boss fight) -----
        elif phase_state == "phase3":
            # Detecção de colisão bullets->enemies também deve funcionar na fase 3
            # Inimigos normais (minions) na fase 3
            hits_enemies_phase3 = pygame.sprite.groupcollide(enemies, bullets, False, True)
            for en, bls in hits_enemies_phase3.items():
                dmg = sum(1 for b in bls if getattr(b,"owner","")=="player")
                if dmg > 0:
                    dead = en.take_damage(dmg)
                    if dead:
                        ex = Explosion(en.rect.center); all_sprites.add(ex); explosions.add(ex)
                        
                        # Chance de drop para minions do boss
                        if random.random() < 0.4:  # 40% de chance
                            drop_powerup(en.rect.center, "phase3")
                        
                        en.kill(); enemies.remove(en)
            
            # Boss específico
            if boss and boss.alive():
                hits_boss = pygame.sprite.spritecollide(boss, bullets, True)
                for b in hits_boss:
                    if getattr(b,"owner","") == "player":
                        boss.health -= 1
                        
                        if boss.health % 10 == 0 and boss.health > 0:
                            drop_powerup((boss.rect.centerx + random.randint(-50, 50), 
                                         boss.rect.centery + random.randint(-50, 50)), "phase3")
                        
                        if boss.health <= 0:
                            ex = Explosion(boss.rect.center); all_sprites.add(ex); explosions.add(ex)
                            if explosion_snd: 
                                set_sound_volume(explosion_snd, "explosion")
                                explosion_snd.play()
                            
                            for _ in range(3):
                                drop_powerup((boss.rect.centerx + random.randint(-100, 100), 
                                           boss.rect.centery + random.randint(-100, 100)), "phase3")
                            
                            boss.kill(); boss = None
                            player1.score += 500
                            if two_player: player2.score += 300
                            phase_state = "victory"
                            game_state = "victory"
                            
                            # Adicionar highscore com vitória
                            total_score = player1.score + (player2.score if two_player else 0)
                            name = "DUO" if two_player else "PLAYER1"
                            add_highscore(name, total_score, phases_completed=3, victory=True)
                
                # Spawn de minions mais lento
                if pygame.time.get_ticks() - last_minion_spawn > random.randint(5000, 6000):
                    last_minion_spawn = pygame.time.get_ticks()
                    
                    mx = random.randint(150, WIDTH-150)
                    m = EnemyShip(mx, boss.rect.bottom + 60)
                    enemies.add(m)
                    all_sprites.add(m)

        # ----- COLISÕES COM POWERUPS (só players vivos) -----
        if player1.is_alive:
            coll1 = pygame.sprite.spritecollide(player1, powerups, True)
            for pu in coll1:
                if pu.ptype == "revive":
                    # CORREÇÃO: Só revive o P2 se estiver jogando com 2 jogadores
                    if two_player and not player2.is_alive and player2.lives > 0:
                        player2.respawn()
                    else:
                        # Se não tem P2 para reviver, cura o P1
                        player1.health = min(100, player1.health+50)
                
                elif pu.ptype == "invul_gift":
                    player1.activate_invulnerability(5000)
                
                elif pu.ptype == "upgrade":
                    player1.activate_upgrade(15000)
                
                elif pu.ptype == "extra_life":
                    player1.health = min(100, player1.health+30)
                    player1.lives += 1
                
                elif pu.ptype == "teleporter":
                    player1.teleport_ability = True
                
                elif pu.ptype == "shield":
                    player1.activate_shield(8000)
                
                if powerup_snd:
                    set_sound_volume(powerup_snd, "powerup")
                    powerup_snd.play()

        if two_player and player2.is_alive:
            coll2 = pygame.sprite.spritecollide(player2, powerups, True)
            for pu in coll2:
                if pu.ptype == "revive":
                    # CORREÇÃO: Só revive o P1 se estiver jogando com 2 jogadores
                    if not player1.is_alive and player1.lives > 0:
                        player1.respawn()
                    else:
                        # Se não tem P1 para reviver, cura o P2
                        player2.health = min(100, player2.health+50)
                
                elif pu.ptype == "invul_gift":
                    player2.activate_invulnerability(5000)
                
                elif pu.ptype == "upgrade":
                    player2.activate_upgrade(15000)
                
                elif pu.ptype == "extra_life":
                    player2.health = min(100, player2.health+30)
                    player2.lives += 1
                
                elif pu.ptype == "teleporter":
                    player2.teleport_ability = True
                
                elif pu.ptype == "shield":
                    player2.activate_shield(8000)
                
                if powerup_snd:
                    set_sound_volume(powerup_snd, "powerup")
                    powerup_snd.play()

        # ensure meteor count
        if phase_state == "asteroids":
            while len(meteors) < MAX_METEORS:
                spawn_special_meteor()

        # ----- Game over check -----
        if not two_player:
            # Modo 1 jogador: morreu = GAME OVER
            if not player1.is_alive or player1.lives <= 0:
                game_state = "game_over"
                phase_state = "game_over"
                if player1.score > 0:
                    # Determinar fases completadas
                    phases_completed = 1
                    if phase_state == "phase2" or phase_state == "boss_transition":
                        phases_completed = 2
                    elif phase_state == "phase3":
                        phases_completed = 3
                    
                    add_highscore("PLAYER1", player1.score, phases_completed=phases_completed, victory=False)
        else:
            # Modo 2 jogadores: ambos mortos = GAME OVER
            game_over = (player1.lives <= 0 and player2.lives <= 0)
            if game_over:
                game_state = "game_over"
                phase_state = "game_over"
                if player1.score + player2.score > 0:
                    # Determinar fases completadas
                    phases_completed = 1
                    if phase_state == "phase2" or phase_state == "boss_transition":
                        phases_completed = 2
                    elif phase_state == "phase3":
                        phases_completed = 3
                    
                    add_highscore("DUO", player1.score + player2.score, phases_completed=phases_completed, victory=False)

    # --- NEXT_PHASE screen handling ---
    if game_state == "next_phase":
        if phase_state == "transition":
            if transition_start and pygame.time.get_ticks() - transition_start > 3000:
                phase_state = "phase2"
                game_state = "playing"
                bullets.empty()
                powerups.empty()
                explosions.empty()
                current_enemy_wave = 1
                spawn_enemy_wave(min(ENEMIES_PER_WAVE, TOTAL_ENEMIES_PHASE2))
                change_music("phase2")
                transition_start = None
                
                # Adicionar highscore parcial ao completar fase 1
                total_score = player1.score + (player2.score if two_player else 0)
                name = "DUO" if two_player else "PLAYER1"
                add_highscore(name, total_score, phases_completed=1, victory=False)
        elif phase_state == "boss_transition":
            if transition_start and pygame.time.get_ticks() - transition_start > 3000:
                bullets.empty()
                powerups.empty()
                explosions.empty()
                boss = Boss(WIDTH//2, 150)
                all_sprites.add(boss)
                phase_state = "phase3"
                game_state = "playing"
                change_music("phase3")
                transition_start = None
                
                # Adicionar highscore parcial ao completar fase 2
                total_score = player1.score + (player2.score if two_player else 0)
                name = "DUO" if two_player else "PLAYER1"
                add_highscore(name, total_score, phases_completed=2, victory=False)

    # --- DRAW SECTION ---
    screen.fill((0,0,0))
    
    if game_state == "intro":
        draw_text(screen, "🚀 NOVA DESCENT 🚀", 72, WIDTH//2, 60)
        draw_text(screen, "MENU PRINCIPAL", 40, WIDTH//2, 140)
        for i, opt in enumerate(menu_options):
            cor = (255,255,0) if i == menu_index else (200,200,200)
            draw_text(screen, opt, 36, WIDTH//2, 220 + i*55, cor)
        draw_text(screen, "Use ↑↓ para navegar, ENTER para selecionar", 22, WIDTH//2, HEIGHT-60)

    elif game_state == "controls":
        draw_text(screen, "📋 CONTROLES", 60, WIDTH//2, 60)
        
        draw_text(screen, "🎮 JOGADOR 1:", 36, WIDTH//2, 150, (100, 200, 255))
        draw_text(screen, "WASD - Movimentar", 28, WIDTH//2, 190)
        draw_text(screen, "ESPAÇO - Atirar", 28, WIDTH//2, 225)
        draw_text(screen, "T - Teleportar (quando disponível)", 28, WIDTH//2, 260)
        draw_text(screen, "M - Ativar/Desativar controle do mouse", 28, WIDTH//2, 295)
        
        draw_text(screen, "🎮 JOGADOR 2:", 36, WIDTH//2, 350, (255, 100, 100))
        draw_text(screen, "SETAS - Movimentar", 28, WIDTH//2, 390)
        draw_text(screen, "KP0 ou RCTRL - Atirar", 28, WIDTH//2, 425)
        
        draw_text(screen, "🔄 COMANDOS GERAIS:", 36, WIDTH//2, 490, (200, 255, 100))
        draw_text(screen, "P - Pausar/Despausar", 28, WIDTH//2, 530)
        draw_text(screen, "ESC - Menu de Pausa/Sair", 28, WIDTH//2, 565)
        draw_text(screen, "R - Reiniciar (apenas no GAME OVER)", 28, WIDTH//2, 600)
        draw_text(screen, "F - Salvar jogo | L - Carregar jogo", 28, WIDTH//2, 635)
        
        draw_text(screen, "Pressione ENTER ou ESC para voltar ao menu", 24, WIDTH//2, HEIGHT-50)

    elif game_state == "highscores":
        draw_text(screen, "🏆 HIGHSCORES", 60, WIDTH//2, 60)
        
        if not highscores:
            draw_text(screen, "Nenhum highscore registrado ainda!", 36, WIDTH//2, HEIGHT//2)
        else:
            for i, hs in enumerate(highscores[:10]):
                name = hs.get("name", "Unknown")
                score = hs.get("score", 0)
                progress = hs.get("progress", "Fase 1")
                date = hs.get("date", "N/A")
                victory = hs.get("victory", False)
                
                # Destaque para os 3 primeiros
                if i == 0:
                    color = (255, 215, 0)  # Ouro
                    medal = "🥇"
                elif i == 1:
                    color = (192, 192, 192)  # Prata
                    medal = "🥈"
                elif i == 2:
                    color = (205, 127, 50)  # Bronze
                    medal = "🥉"
                else:
                    color = (200, 200, 200)
                    medal = f"{i+1}."
                
                y_pos = 150 + i * 50
                
                # Nome e pontuação
                draw_text(screen, f"{medal} {name}: {score} pts", 26, WIDTH//2 - 180, y_pos, color)
                
                # Progresso (com emoji se venceu)
                progress_text = f"✓ {progress}" if victory else f"→ {progress}"
                progress_color = (100, 255, 100) if victory else (200, 200, 100)
                draw_text(screen, progress_text, 22, WIDTH//2 + 100, y_pos, progress_color)
                
                # Data
                draw_text(screen, f"({date})", 18, WIDTH//2 + 100, y_pos + 25, (150, 150, 150))
        
        draw_text(screen, "Pressione ENTER ou ESC para voltar ao menu", 24, WIDTH//2, HEIGHT-50)

    elif game_state == "volume_menu":
        draw_volume_menu(screen)

    elif game_state in ("playing", "phase3"):
        # Desenhar o jogo normalmente
        background.draw(screen, phase_state)
        
        if phase_state not in ("transition", "boss_transition"):
            all_sprites.draw(screen)
        
        # Interface do Player 1
        draw_health_bar(screen, 20, 20, player1.health if player1.is_alive else 0)
        draw_text(screen, f"P1 PONTOS: {player1.score}", 30, 150, 20)
        
        # Vidas do Player 1
        lives_text = f"P1 VIDAS: {player1.lives}"
        if not player1.is_alive:
            if two_player:
                lives_text += " (Aguardando revive do P2)"  # Mensagem para 2 jogadores
            else:
                lives_text += " (GAME OVER)"  # Mensagem para 1 jogador
        draw_text(screen, lives_text, 22, 150, 55, (255, 200, 100) if player1.is_alive else (200, 100, 100))
        
        if two_player:
            # Interface do Player 2
            draw_health_bar(screen, WIDTH-270, 20, player2.health if player2.is_alive else 0)
            draw_text(screen, f"P2 PONTOS: {player2.score}", 30, WIDTH-150, 20)
            
            # Vidas do Player 2
            lives_text = f"P2 VIDAS: {player2.lives}"
            if not player2.is_alive:
                lives_text += " (Aguardando revive do P1)"  # Mensagem para 2 jogadores
            draw_text(screen, lives_text, 22, WIDTH-150, 55, (255, 200, 100) if player2.is_alive else (200, 100, 100))
        
        # Phase-specific UI
        if phase_state == "asteroids":
            draw_text(screen, f"Pontos para fase 2: {POINTS_TO_NEXT_PHASE}", 22, WIDTH-220, 20)
        elif phase_state == "phase2":
            draw_text(screen, f"FASE 2 - INIMIGOS: {enemies_killed}/{TOTAL_ENEMIES_PHASE2}", 26, WIDTH//2, 20)
            draw_text(screen, f"Wave: {current_enemy_wave}", 22, WIDTH//2, 50)
        elif phase_state == "phase3":
            draw_text(screen, "FASE 3 - CHEFÃO FINAL", 36, WIDTH//2, 20)
            if boss and boss.alive():
                draw_text(screen, f"CHEFÃO HP: {boss.health}", 22, WIDTH//2, 60)
        
        # Mostrar powerups ativos
        now = pygame.time.get_ticks()
        y_offset = 100
        
        # Player 1 powerups
        if player1.is_alive:
            if player1.upgrade_end_time and now < player1.upgrade_end_time:
                remaining = (player1.upgrade_end_time - now) / 1000
                draw_text(screen, f"P1 Upgrade: {remaining:.1f}s", 20, 100, y_offset, (255, 255, 100))
                y_offset += 25
            if player1.shield_end_time and now < player1.shield_end_time:
                remaining = (player1.shield_end_time - now) / 1000
                draw_text(screen, f"P1 Escudo: {remaining:.1f}s", 20, 100, y_offset, (100, 200, 255))
                y_offset += 25
            if player1.invulnerable_until and now < player1.invulnerable_until:
                remaining = (player1.invulnerable_until - now) / 1000
                draw_text(screen, f"P1 Invulnerável: {remaining:.1f}s", 20, 100, y_offset, (30, 100, 200))
                y_offset += 25
        
        # Player 2 powerups
        if two_player and player2.is_alive:
            y_offset = 100
            if player2.upgrade_end_time and now < player2.upgrade_end_time:
                remaining = (player2.upgrade_end_time - now) / 1000
                draw_text(screen, f"P2 Upgrade: {remaining:.1f}s", 20, WIDTH-100, y_offset, (255, 255, 100))
                y_offset += 25
            if player2.shield_end_time and now < player2.shield_end_time:
                remaining = (player2.shield_end_time - now) / 1000
                draw_text(screen, f"P2 Escudo: {remaining:.1f}s", 20, WIDTH-100, y_offset, (100, 200, 255))
                y_offset += 25
            if player2.invulnerable_until and now < player2.invulnerable_until:
                remaining = (player2.invulnerable_until - now) / 1000
                draw_text(screen, f"P2 Invulnerável: {remaining:.1f}s", 20, WIDTH-100, y_offset, (30, 100, 200))
                y_offset += 25
        
        # Instruções de revive em 2 jogadores
        if two_player:
            if not player1.is_alive and player2.is_alive:
                draw_text(screen, "🎮 P2: Pegue o powerup VERMELHO para reviver P1!", 24, WIDTH//2, HEIGHT-40, (255, 50, 50))
            elif not player2.is_alive and player1.is_alive:
                draw_text(screen, "🎮 P1: Pegue o powerup VERMELHO para reviver P2!", 24, WIDTH//2, HEIGHT-40, (255, 50, 50))
        
        # Menu de pausa sobreposto
        if pause_menu:
            # Semi-transparência sobre o jogo
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            draw_text(screen, "⏸️ JOGO PAUSADO", 60, WIDTH//2, 120)
            
            for i, opt in enumerate(pause_options):
                cor = (255, 255, 0) if i == pause_index else (200, 200, 200)
                draw_text(screen, opt, 36, WIDTH//2, 220 + i*55, cor)
            
            draw_text(screen, "Use ↑↓ para navegar, ENTER para selecionar", 22, WIDTH//2, HEIGHT-60)

    elif game_state == "next_phase":
        background.draw(screen, "asteroids")
        if phase_state == "transition":
            draw_text(screen, "🔄 PRÓXIMA FASE!", 60, WIDTH//2, HEIGHT//2 - 80)
            draw_text(screen, "Os inimigos chegaram...", 40, WIDTH//2, HEIGHT//2)
            draw_text(screen, "DESTRUAM ELES!" if two_player else "DESTRUA ELES!", 40, WIDTH//2, HEIGHT//2 + 60)
        elif phase_state == "boss_transition":
            draw_text(screen, "⚠️ ALERTA MÁXIMO!", 60, WIDTH//2, HEIGHT//2 - 80)
            draw_text(screen, "CHEFÃO EM BREVE", 40, WIDTH//2, HEIGHT//2)
            draw_text(screen, "Prepare-se para a batalha final!", 40, WIDTH//2, HEIGHT//2 + 60)

    elif game_state == "victory":
        background.draw(screen, "phase3")
        draw_text(screen, "🎉 VITÓRIA!", 72, WIDTH//2, HEIGHT//2 - 100)
        draw_text(screen, "Você derrotou o chefão e salvou a galáxia!", 36, WIDTH//2, HEIGHT//2)
        draw_text(screen, f"Pontuação final: {player1.score + (player2.score if two_player else 0)}", 32, WIDTH//2, HEIGHT//2 + 50)
        draw_text(screen, "Pressione ENTER ou ESC para voltar ao menu", 24, WIDTH//2, HEIGHT-50)

    elif game_state == "game_over":
        background.draw(screen, "asteroids")
        draw_text(screen, "💀 GAME OVER", 72, WIDTH//2, HEIGHT//2 - 100)
        
        if two_player:
            draw_text(screen, f"Pontuação final: {player1.score + player2.score}", 36, WIDTH//2, HEIGHT//2 - 20)
        else:
            draw_text(screen, f"Pontuação final: {player1.score}", 36, WIDTH//2, HEIGHT//2 - 20)
        
        draw_text(screen, "Pressione R para reiniciar ou ESC para sair", 28, WIDTH//2, HEIGHT//2 + 40)

    pygame.display.flip()

pygame.quit()
sys.exit()
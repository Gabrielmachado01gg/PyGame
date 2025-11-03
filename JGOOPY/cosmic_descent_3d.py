import pygame
import random
import sys
import os

# ==================== CONFIGURAÇÕES INICIAIS ====================
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🚀 Cosmic Descent 2D - Pygame Edition")
clock = pygame.time.Clock()

# ==================== CAMINHOS ====================
ASSETS = os.path.join(os.path.dirname(__file__), "assets")

# ==================== FUNÇÕES ====================
def carregar_img(nome, escala=None):
    caminho = os.path.join(ASSETS, nome)
    try:
        img = pygame.image.load(caminho).convert_alpha()
        if escala:
            img = pygame.transform.scale(img, escala)
        return img
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {nome}")
        # Criar uma imagem fallback
        surf = pygame.Surface(escala if escala else (100, 100))
        surf.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        return surf

def draw_text(surf, text, size, x, y, color=(255, 255, 255)):
    font = pygame.font.Font(None, size)
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    rect.topleft = (x, y)
    surf.blit(surface, rect)

def draw_health_bar(surf, x, y, pct):
    pct = max(pct, 0)
    BAR_LENGTH, BAR_HEIGHT = 250, 25
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    cor = (0, 255, 0) if pct > 50 else (255, 0, 0)
    pygame.draw.rect(surf, cor, fill_rect)
    pygame.draw.rect(surf, (255, 255, 255), outline_rect, 2)

# ==================== CLASSES ====================
class Background:
    def __init__(self):
        # Usando os arquivos que você realmente tem
        self.layers = [
            carregar_img("blue-preview.png", (WIDTH, HEIGHT)),
        ]
        self.index = 0
        self.timer = 0
        self.interval = 8  # segundos

    def update(self, dt):
        self.timer += dt
        if self.timer > self.interval:
            self.index = (self.index + 1) % len(self.layers)
            self.timer = 0

    def draw(self):
        screen.blit(self.layers[self.index], (0, 0))

class Planet(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = carregar_img(image, (random.randint(100, 200), random.randint(100, 200)))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH)
        self.rect.y = random.randint(0, HEIGHT // 2)
        self.speed = random.uniform(0.2, 0.6)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.rect.x = WIDTH + random.randint(100, 200)
            self.rect.y = random.randint(0, HEIGHT // 2)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = carregar_img("player.png", (100, 70))
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 120))
        self.speed = 8
        self.health = 100
        self.score = 0
        self.last_shot = 0
        self.shoot_delay = 300

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        self.rect.clamp_ip(screen.get_rect())

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = carregar_img("bullert.png", (15, 25))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Usando os planetas como meteoros (já que você não tem imagens de meteoros específicas)
        img_name = random.choice(["asteroid-1", "asteroid-2"])
        self.image = carregar_img(img_name, (80, 80))
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH-50), random.randint(-100, -40)))
        self.speedy = random.randint(3, 7)
        self.speedx = random.randint(-2, 2)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = random.randint(-100, -40)
            self.speedy = random.randint(3, 7)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        # Usando os frames de explosão que você tem (01, 02, 03, 04, 05, 06)
        self.frames = []
        for i in range(1, 7):
            frame_name = f"0{i}.png" if i < 10 else f"{i}.png"
            self.frames.append(carregar_img(frame_name, (100, 100)))
        
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=center)
        self.frame_rate = 50
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.kill()
            else:   
                self.image = self.frames[self.frame_index]

# ==================== INICIALIZAÇÃO ====================
print("🚀 Iniciando Cosmic Descent 2D...")
print("📁 Carregando assets...")

background = Background()
all_sprites = pygame.sprite.Group()
planets = pygame.sprite.Group()
meteors = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Planetas de fundo (os que se movem lentamente)
planet_names = ["terra.png", "netuno.png", "plutao.png", "saturn.png", "marte.png", "c3po.png"]
for name in planet_names:
    p = Planet(name)
    all_sprites.add(p)
    planets.add(p)

player = Player()
all_sprites.add(player)

# Meteoros (que caem)
for _ in range(6):
    m = Meteor()
    all_sprites.add(m)
    meteors.add(m)

print("✅ Jogo carregado!")
print("🎮 Controles: WASD - Mover | Espaço - Atirar | R - Reiniciar")

# ==================== LOOP PRINCIPAL ====================
game_over = False
victory = False
running = True

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over and not victory:
                player.shoot()
            if event.key == pygame.K_r:
                # Reiniciar jogo
                player.health = 100
                player.score = 0
                
                # Limpar todos os sprites
                all_sprites.empty()
                meteors.empty()
                bullets.empty()
                planets.empty()

                # Recriar planetas de fundo
                for name in planet_names:
                    p = Planet(name)
                    all_sprites.add(p)
                    planets.add(p)

                # Recriar jogador
                player = Player()
                all_sprites.add(player)

                # Recriar meteoros
                for _ in range(6):
                    m = Meteor()
                    all_sprites.add(m)
                    meteors.add(m)

                game_over = False
                victory = False
                print("🔄 Jogo reiniciado!")

    if not game_over and not victory:
        background.update(dt)
        all_sprites.update()

        # colisão balas x meteoros
        hits = pygame.sprite.groupcollide(meteors, bullets, True, True)
        for hit in hits:
            player.score += 5
            explosion = Explosion(hit.rect.center)
            all_sprites.add(explosion)
            m = Meteor()
            all_sprites.add(m)
            meteors.add(m)

        # colisão jogador x meteoros
        hits = pygame.sprite.spritecollide(player, meteors, True)
        for hit in hits:
            player.health -= 20
            explosion = Explosion(hit.rect.center)
            all_sprites.add(explosion)
            m = Meteor()
            all_sprites.add(m)
            meteors.add(m)
            if player.health <= 0:
                game_over = True
                print("💀 Game Over!")

        if player.score >= 100:
            victory = True
            print("🎉 Vitória!")

    # ========== DESENHO ==========
    background.draw()
    all_sprites.draw(screen)
    
    # UI
    draw_health_bar(screen, 20, 20, player.health)
    draw_text(screen, f"PONTOS: {player.score}", 36, 20, 55)
    draw_text(screen, "WASD: Mover | ESPAÇO: Atirar | R: Reiniciar", 24, 20, HEIGHT - 40)

    if game_over:
        draw_text(screen, "💀 GAME OVER - Pressione R para reiniciar", 48, WIDTH//2 - 300, HEIGHT//2, (255, 0, 0))
    elif victory:
        draw_text(screen, "🎉 VITÓRIA! 100 pontos alcançados!", 48, WIDTH//2 - 280, HEIGHT//2, (0, 255, 0))

    pygame.display.flip()

pygame.quit()
sys.exit()
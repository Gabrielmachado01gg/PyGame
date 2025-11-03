from ursina import *
import random
import math

app = Ursina()

# ==================== CONFIGURAÇÃO 2D ====================
window.title = 'Cosmic Descent 2D - Com Todas as Imagens'
window.borderless = False
window.fullscreen = False
window.color = color.black

# Configuração para visão 2D
camera.orthographic = True
camera.fov = 20

# Variável global para controle do jogo
game_paused = False

# ==================== SISTEMA DE BACKGROUND ROTATIVO ====================
class BackgroundSystem:
    def __init__(self):
        self.backgrounds = [
            'pixelat_startield',
            'pixelat_startield_diagonal_diffraction_spi',
            'pixelat_startield_corona'
        ]
        self.current_bg_index = 0
        self.background_entity = None
        self.bg_change_timer = 0
        self.bg_change_interval = 10  # Mudar a cada 10 segundos
        self.load_current_background()
        
    def load_current_background(self):
        try:
            if self.background_entity:
                destroy(self.background_entity)
                
            self.background_entity = Entity(
                model='quad',
                texture=self.backgrounds[self.current_bg_index],
                scale=(60, 40),
                position=(0, 0, 50),
                z=50
            )
            print(f"✅ Background carregado: {self.backgrounds[self.current_bg_index]}")
        except Exception as e:
            print(f"❌ Erro ao carregar background {self.backgrounds[self.current_bg_index]}: {e}")
            # Fallback básico
            self.background_entity = Entity(
                model='quad',
                color=color.dark_blue,
                scale=(60, 40),
                position=(0, 0, 50),
                z=50
            )
    
    def update(self):
        if game_paused:
            return
            
        # Rotação suave do background
        if self.background_entity:
            self.background_entity.rotation_z += 0.1 * time.dt
            
        # Trocar background periodicamente
        self.bg_change_timer += time.dt
        if self.bg_change_timer >= self.bg_change_interval:
            self.current_bg_index = (self.current_bg_index + 1) % len(self.backgrounds)
            self.load_current_background()
            self.bg_change_timer = 0

# ==================== SISTEMA DE PLANETAS NO FUNDO ====================
class PlanetSystem:
    def __init__(self):
        self.planets = []
        self.planet_textures = ['terra', 'netuno', 'plutao', 'saturn', 'marte', 'c3po']
        self.create_planets()
    
    def create_planets(self):
        for texture_name in self.planet_textures:
            try:
                planet = Entity(
                    model='quad',
                    texture=texture_name,
                    scale=random.uniform(4, 7),
                    position=(
                        random.uniform(-35, 35),
                        random.uniform(-20, 20),
                        15  # Camada entre background e jogador
                    ),
                    rotation=(0, 0, random.uniform(0, 360))
                )
                planet.speed = random.uniform(0.03, 0.08)
                planet.rotation_speed = random.uniform(0.05, 0.15)
                self.planets.append(planet)
                print(f"✅ Planeta {texture_name} carregado!")
            except Exception as e:
                print(f"❌ Erro ao carregar planeta {texture_name}: {e}")
                # Planeta fallback
                planet = Entity(
                    model='circle',
                    color=color.random_color(),
                    scale=random.uniform(3, 5),
                    position=(
                        random.uniform(-35, 35),
                        random.uniform(-20, 20),
                        15
                    )
                )
                planet.speed = random.uniform(0.03, 0.08)
                planet.rotation_speed = random.uniform(0.05, 0.15)
                self.planets.append(planet)
    
    def update(self):
        if game_paused:
            return
            
        for planet in self.planets:
            # Movimento suave dos planetas
            planet.rotation_z += planet.rotation_speed * time.dt
            planet.x -= planet.speed * time.dt
            
            # Reposicionar planeta se sair da tela
            if planet.x < -40:
                planet.x = 40
                planet.y = random.uniform(-20, 20)

# ==================== NAVE 2D COM THRUSTER ANIMADO ====================
class SpaceShip(Entity):
    def __init__(self):
        # Carregar nave principal
        try:
            super().__init__(
                model='quad',
                texture='player',
                scale=(2.5, 1.8),
                position=(0, -8, 0),
                rotation=(0, 0, 0),
                collider='box'
            )
            print("✅ Nave player.png carregada!")
        except Exception as e:
            print(f"❌ Erro ao carregar nave: {e}")
            super().__init__(
                model='triangle',
                color=color.blue,
                scale=1.5,
                position=(0, -8, 0),
                rotation=(0, 0, 180),
                collider='box'
            )
        
        self.speed = 8
        self.health = 100
        self.score = 0
        self.bullets = []
        
        # Sistema de thruster animado
        self.setup_thruster_animation()
        self.thruster_timer = 0
        self.current_thruster_frame = 0
        
    def setup_thruster_animation(self):
        # Frames do thruster (p01 (1) até p01 (7))
        self.thruster_frames = []
        for i in range(1, 8):
            try:
                frame_name = f'p01 ({i})'
                self.thruster_frames.append(frame_name)
            except:
                pass
        
        # Criar entidade do thruster
        if self.thruster_frames:
            try:
                self.thruster = Entity(
                    model='quad',
                    texture=self.thruster_frames[0],
                    scale=(1.5, 1.5),
                    position=(0, -1.3, -0.3),
                    parent=self
                )
                print("✅ Thruster animado carregado!")
            except:
                self.thruster = Entity(
                    model='quad',
                    color=color.orange,
                    scale=(1.0, 1.0),
                    position=(0, -1.3, -0.3),
                    parent=self
                )
        else:
            self.thruster = Entity(
                model='quad',
                color=color.orange,
                scale=(1.0, 1.0),
                position=(0, -1.3, -0.3),
                parent=self
            )
    
    def update_thruster_animation(self):
        if not hasattr(self, 'thruster') or not self.thruster:
            return
            
        self.thruster_timer += time.dt
        
        # Animação mais rápida quando se move
        animation_speed = 10 if (held_keys['w'] or held_keys['up']) else 6
        
        if self.thruster_timer >= 1.0 / animation_speed:
            self.thruster_timer = 0
            if self.thruster_frames:
                self.current_thruster_frame = (self.current_thruster_frame + 1) % len(self.thruster_frames)
                try:
                    self.thruster.texture = self.thruster_frames[self.current_thruster_frame]
                except:
                    pass
            
            # Efeito de escala pulsante
            pulse = math.sin(time.time() * 8) * 0.1 + 1.0
            if held_keys['w'] or held_keys['up']:
                self.thruster.scale = (1.5 * pulse, 1.8 * pulse)
                self.thruster.color = color.lerp(color.orange, color.yellow, abs(math.sin(time.time() * 10)))
            else:
                self.thruster.scale = (1.2 * pulse, 1.2 * pulse)
                self.thruster.color = color.orange
    
    def update(self):
        if game_paused:
            return
            
        # Controles
        move_x = (held_keys['d'] or held_keys['right']) - (held_keys['a'] or held_keys['left'])
        move_y = (held_keys['w'] or held_keys['up']) - (held_keys['s'] or held_keys['down'])
        
        self.x += move_x * self.speed * time.dt
        self.y += move_y * self.speed * time.dt
        
        # Limites da tela
        self.x = clamp(self.x, -18, 18)
        self.y = clamp(self.y, -12, 8)
        
        # Atualizar animação do thruster
        self.update_thruster_animation()
    
    def shoot(self):
        if game_paused:
            return
            
        try:
            bullet = Entity(
                model='quad',
                texture='bullet',
                scale=(0.4, 0.4),
                position=(self.x, self.y + 1.0, 0),
                collider='box'
            )
            print("✅ Bala bullet.png criada!")
        except Exception as e:
            print(f"❌ Erro ao carregar bala: {e}")
            bullet = Entity(
                model='quad',
                color=color.yellow,
                scale=(0.3, 0.5),
                position=(self.x, self.y + 1.0, 0),
                collider='box'
            )
        
        self.bullets.append(bullet)
        bullet.animate_position((bullet.x, 25), duration=1.2)
        destroy(bullet, delay=1.2)

# ==================== METEOROS 2D ====================
class Meteor(Entity):
    def __init__(self):
        super().__init__(
            model='circle',
            color=color.gray,
            scale=random.uniform(0.8, 1.5),
            position=(
                random.uniform(-20, 20),
                random.uniform(15, 25),
                0
            ),
            collider='box'
        )
        
        # Adicionar detalhes ao meteoro
        self.detail = Entity(
            model='circle',
            color=color.dark_gray,
            scale=0.6,
            position=(random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2), -0.1),
            parent=self
        )
        
        self.speed = random.uniform(3, 6)
        self.rotation_speed = random.uniform(-40, 40)
    
    def update(self):
        if game_paused:
            return
            
        self.y -= self.speed * time.dt
        self.rotation_z += self.rotation_speed * time.dt
        
        # Verificar colisão com balas
        for bullet in player.bullets[:]:
            if self.intersects(bullet).hit:
                create_explosion(self.position)
                player.score += 5
                player.bullets.remove(bullet)
                destroy(bullet)
                self.reset_position()
                return
        
        # Colisão com jogador
        if self.intersects(player).hit:
            player.health -= 10
            create_explosion(self.position)
            self.reset_position()
        
        # Reposicionar se sair da tela
        if self.y < -20:
            self.reset_position()
    
    def reset_position(self):
        self.y = random.uniform(15, 25)
        self.x = random.uniform(-20, 20)

# ==================== SISTEMA DE EXPLOSÃO ANIMADA ====================
def create_explosion(position):
    if game_paused:
        return
        
    try:
        explosion = Entity(
            model='quad',
            texture='01',  # Primeiro frame
            scale=2.5,
            position=position,
            z=-1
        )
        
        explosion_frames = ['01', '02', '03', '04', '05', '06']
        current_frame = 0
        
        def next_explosion_frame():
            nonlocal current_frame
            if current_frame < len(explosion_frames) and explosion.enabled:
                try:
                    explosion.texture = explosion_frames[current_frame]
                    current_frame += 1
                    # Escala decrescente
                    explosion.scale = 2.5 * (1 - (current_frame / len(explosion_frames) * 0.5))
                    invoke(next_explosion_frame, delay=0.08)
                except Exception as e:
                    destroy(explosion)
            else:
                destroy(explosion)
        
        next_explosion_frame()
        print("✅ Explosão animada criada!")
        
    except Exception as e:
        print(f"❌ Erro na explosão animada: {e}")
        # Explosão básica fallback
        for i in range(8):
            particle = Entity(
                model='circle',
                color=color.orange,
                scale=0.3,
                position=position + (random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), 0)
            )
            particle.animate_scale((0.1, 0.1), duration=0.5)
            destroy(particle, delay=0.5)

# ==================== UI 2D ====================
class GameUI(Entity):
    def __init__(self):
        super().__init__()
        
        # Fundo semi-transparente para UI
        self.ui_background = Entity(
            model='quad',
            color=color.black,
            scale=(0.4, 0.15),
            position=(-0.75, 0.4),
            parent=camera.ui,
            alpha=0.7
        )
        
        self.health_text = Text(
            text='VIDA: 100',
            position=(-0.8, 0.45),
            scale=2,
            color=color.green
        )
        
        self.score_text = Text(
            text='PONTOS: 0', 
            position=(-0.8, 0.35),
            scale=2,
            color=color.yellow
        )
        
        self.controls_text = Text(
            text='WASD: Mover | ESPAÇO: Atirar | R: Reiniciar',
            position=(0, -0.45),
            scale=1.5,
            color=color.light_gray
        )
        
        self.game_over_text = None
        self.victory_text = None
    
    def update(self):
        if game_paused:
            return
            
        self.health_text.text = f'VIDA: {player.health}'
        self.score_text.text = f'PONTOS: {player.score}'
    
    def show_game_over(self):
        self.game_over_text = Text(
            text='GAME OVER!\nPressione R para reiniciar',
            position=(0, 0.1),
            scale=2.5,
            color=color.red
        )
    
    def show_victory(self):
        self.victory_text = Text(
            text='VITÓRIA!\n100 pontos alcançados!',
            position=(0, 0.2),
            scale=2,
            color=color.green
        )
    
    def clear_messages(self):
        if self.game_over_text:
            destroy(self.game_over_text)
            self.game_over_text = None
        if self.victory_text:
            destroy(self.victory_text)
            self.victory_text = None

# ==================== INICIALIZAÇÃO ====================
print("🚀 INICIANDO COSMIC DESCENT 2D...")
print("📁 Carregando recursos...")

background_system = BackgroundSystem()
planet_system = PlanetSystem()
player = SpaceShip()
game_ui = GameUI()
meteors = [Meteor() for _ in range(6)]

print("✅ Todos os sistemas carregados!")
print("🎮 Controles: WASD/Setas - Mover | Espaço - Atirar | R - Reiniciar")

# ==================== GAME LOOP ====================
def update():
    global game_paused
    
    # Atualizar sistemas se o jogo não estiver pausado
    if not game_paused:
        background_system.update()
        planet_system.update()
        
        # Remover balas destruídas
        player.bullets = [bullet for bullet in player.bullets if bullet.enabled]
    
    # Game Over
    if player.health <= 0 and not game_paused:
        player.health = 0
        game_paused = True
        game_ui.show_game_over()
        print("💀 GAME OVER - Pressione R para reiniciar")
    
    # Vitória
    if player.score >= 100 and player.health > 0 and not game_paused:
        game_paused = True
        game_ui.show_victory()
        print("🎉 VITÓRIA - Pressione R para jogar novamente")

def input(key):
    global game_paused
    
    if key == 'r':  # Reiniciar
        game_paused = False
        player.health = 100
        player.score = 0
        player.position = (0, -8, 0)
        
        # Limpar balas
        for bullet in player.bullets:
            destroy(bullet)
        player.bullets = []
        
        # Resetar meteoros
        for meteor in meteors:
            meteor.reset_position()
        
        # Limpar mensagens
        game_ui.clear_messages()
        
        print("🔄 Jogo reiniciado!")
    
    if key == 'space' and not game_paused:  # Atirar
        player.shoot()

app.run()
# Cosmic Descent 3D

**Autores:** Gabriel Machado; Arthur Simioni  

---

## Objetivo
Documentação completa do projeto: instruções para clonar, compilar/rodar, descrição das fases, powerups, efeitos, dinâmica do jogo e instruções de entrega. 

## Como clonar o repositório
```bash
git clone https://github.com/SEU-USUARIO/cosmic-descent-3d.git
cd cosmic-descent-3d
```

> **Obs:** substitua `SEU-USUARIO` pelo usuário do GitHub onde o repositório ficará hospedado.

## Requisitos / Dependências
- Python 3.10 ou superior
- pip
- pygame

Instalação:
```bash
python -m venv venv
source venv/bin/activate    # Linux / macOS
venv\Scripts\activate     # Windows (PowerShell)
pip install --upgrade pip
pip install pygame
```

## Como executar o jogo
Na raiz do repositório, execute:
```bash
python cosmic_descent_3d.py
```
Arquivos importantes:
- `cosmic_descent_3d.py` — código-fonte principal
- `assets/` — pasta com imagens e sons (coloque as imagens listadas no código)
- `savegame.json` — arquivo de save 
- `highscores.json` — arquivo com highscores

## Como jogar (Controles)
### Jogador 1 (P1)
- **WASD** — mover
- **Espaço** — atirar
- **T** — teleporte (se tiver powerup)
- **M** — alternar controle por mouse

### Jogador 2 (P2) — modo cooperativo
- **Setas** — mover
- **Teclado Numérico 0 (KP0)** — atirar

### Controles gerais
- **P** — pausar
- **R** — reiniciar
- **F** — salvar jogo
- **L** — carregar jogo
- **ESC** — sair

## Estrutura do Jogo e Dinâmicas

O jogo possui 3 fases principais: **Fase 1 (Asteroides)**, **Fase 2 (Invasão - waves)** e **Fase 3 (Chefão)**. Abaixo a descrição completa de cada fase, powerups, efeitos e mecânicas observadas no código.

### Fase 1 — Campo de Asteroides
- Meteoros (normais e 'evil') caem verticalmente com rotação.
- Colisão com meteoro causa dano (20 para normais, 40 para 'evil').
- Ao destruir um meteoro ganha-se pontos (10 por destruição).
- Chance de drop de powerup: **50%** (implementado no código).
- Quando a pontuação total (P1 ou P1+P2) alcança `POINTS_TO_NEXT_PHASE` (1500 por padrão), o jogo transita para a Fase 2.
- Dynamical scaling: a cada 500 pontos, a velocidade global aumenta (variável `GLOBAL_SPEED_MULT`).

### Fase 2 — Encastre de Inimigos (Waves)
- Sistema de waves: total de **15 inimigos**, spawnados em waves de até 5 (`ENEMIES_PER_WAVE`).
- Inimigos se movem lateralmente aleatoriamente e atiram no jogador.
- Cada inimigo possui `health = 3` e pode dropar powerups.
- Probabilidade de drop aumentada: ~60%, e a cada 3 inimigos derrotados há uma queda garantida.
- Ao derrotar os 15 inimigos, o jogo entra na transição para a Fase 3 (boss).

### Fase 3 — Chefão Final (Boss Fight)
- Boss implementado com `health = 80` e modos de ataque rotativos: `normal`, `spread`, `rapid`.
- Comportamento do boss:
  - Move horizontalmente entre limites definidos.
  - Alterna de attack_mode a cada `attack_duration` (5000 ms por padrão).
  - Shooting patterns: múltiplos tiros, ângulo spread, ou modo rápido com menor intervalo.
- Ao perder 10 HP, o boss dropa um powerup. Ao morrer, o boss solta 3 powerups e concede pontos de bônus ao jogador.

## Powerups Implementados
- `revive` — revive o parceiro (modo 2 jogadores) ou cura parcial (P1).
- `invul_gift` — invulnerabilidade por 5s.
- `upgrade` — ativação de tiros extras (tiro triplo) por 15s.
- `extra_life` — recupera HP (ex.: +30 ou +50 dependendo do caso).
- `teleporter` — concede habilidade de teleporte (uso único).
- `shield` — escudo temporário (8s) que absorve dano.

## Efeitos Visuais e Sonoros
- Animações de explosão (frames carregados conforme `ASSET_CONFIG["explosion_frames"]`).
- Efeitos de glow nos powerups e efeito visual para upgrade/escudo no sprite do jogador.
- Três trilhas sonoras (fase 1, 2 e 3) e sons para disparo, explosão e powerup (se assets presentes).

## Sistema de Save / Load
- `save_game()` grava um JSON (`savegame.json`) com estado de fase, posição/jogadores, pontuações e meteoro spawns.
- `load_game()` restaura esse estado (tentar carregar o arquivo salvo antes de executar).

## Arquivos no Repositório (sugestão)
```
cosmic-descent-3d/
├─ cosmic_descent_3d.py
├─ README.md
├─ documentation.pdf   # versão final
├─ assets/
│  ├─ player.png
│  ├─ bullert.png
│  ├─ asteroid-1.png
│  ├─ asteroid-2.png
│  ├─ music_phase1.mp3
│  └─ ... (restantes)
├─ savegame.json
├─ highscores.json
└─ .gitignore
```

## LINK para video explicativo 
https://youtu.be/FLZUyv0VQqk


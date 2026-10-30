# NOVA DESCENT — Jogo de nave em Python (Pygame)

[![CI](https://github.com/Gabrielmachado01gg/PyGame/actions/workflows/ci.yml/badge.svg)](https://github.com/Gabrielmachado01gg/PyGame/actions/workflows/ci.yml)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Licença MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-green)

Jogo de nave espacial 2D feito com **Pygame**, com 3 fases, modo para 1 ou 2 jogadores, powerups, chefão final, ranking de pontuações e save/load. Projeto desenvolvido em dupla por **Gabriel Wiedenhoft** e **Arthur Simioni**.

## Fases

1. **Campo de asteroides:** meteoros caem com rotação e causam dano. A velocidade do jogo aumenta conforme a pontuação, e a fase termina ao atingir a meta de pontos.
2. **Invasão:** ondas de naves inimigas que se movem e atiram no jogador, com chance de largar powerups.
3. **Chefão final:** batalha contra o boss.

## Recursos

- Modo 1 jogador ou 2 jogadores cooperativo
- Powerups (incluindo reviver o parceiro no modo cooperativo)
- Ranking com as 10 melhores pontuações (`highscores.json`)
- Salvar e carregar jogo
- Menu de volume com ajuste de geral, música, efeitos, tiros, explosões, powerups e respawn
- Música diferente em cada fase

## Controles

| Ação | Jogador 1 | Jogador 2 |
|---|---|---|
| Mover | W A S D | Setas |
| Atirar | Espaço | Teclado numérico 0 (ou Ctrl direito) |
| Teleporte (com powerup) | T | — |

Geral: **P** pausar · **R** reiniciar · **F** salvar · **L** carregar · **M** alternar controle por mouse · **ESC** voltar/sair.

## Como executar

Requisitos: Python 3.10 ou superior.

```bash
git clone https://github.com/Gabrielmachado01gg/PyGame.git
cd PyGame
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd JGOOPY
python NOVA_DESCENT.py
```

## Estrutura

```
JGOOPY/
├── NOVA_DESCENT.py   # código do jogo
└── assets/           # imagens e sons
```

## Autores

- Gabriel Wiedenhoft — [LinkedIn](https://www.linkedin.com/in/gabriel-wiedenhoft-machado)
- Arthur Simioni

Licença [MIT](LICENSE). Verifique os direitos de uso dos arquivos de imagem e áudio em `JGOOPY/assets` antes de reutilizá-los.

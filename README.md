# NOVA DESCENT — Jogo de nave em Python (Pygame)

[![CI](https://github.com/Gabrielmachado01gg/PyGame/actions/workflows/ci.yml/badge.svg)](https://github.com/Gabrielmachado01gg/PyGame/actions/workflows/ci.yml)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Licença MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-green)

### ▶ [Jogue agora no navegador](https://gabrielmachado01gg.github.io/PyGame/)

Sem instalar nada: funciona no computador (teclado ou mouse) e no celular (toque). A versão web fica na pasta `web/` e é uma reescrita do jogo em HTML5 Canvas + JavaScript, com as mesmas 3 fases e vários ajustes (veja abaixo). A versão original em Pygame continua em `JGOOPY/`.

---

Jogo de nave espacial 2D feito com **Pygame**, com 3 fases, modo para 1 ou 2 jogadores, powerups, chefão final, ranking de pontuações e save/load. Projeto desenvolvido por **Gabriel Wiedenhoft**.

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

## Versão web

Rodando em: https://gabrielmachado01gg.github.io/PyGame/

O que mudou em relação à versão Pygame:

- **Roda no navegador**, com tela que se ajusta ao tamanho da janela e controles por **toque** (arraste para mover; a nave atira sozinha) e por **mouse**
- **Vidas de verdade no modo 1 jogador:** na versão Pygame a primeira morte já encerrava a partida; agora a nave reaparece após 3 s, protegida, até acabarem as vidas
- **Pontuação por quem acertou:** cada tiro leva o dono, então no modo 2 jogadores cada um pontua pelo que destrói (antes tudo ia para o P1). Inimigos e chefão também dão pontos
- **Aceleração dos asteroides corrigida:** antes só acontecia se a pontuação caísse exatamente em múltiplos de 500
- **Chefão:** o tiro rápido não "gruda" mais no atraso curto; entrada animada e barra de vida
- **Placar sem duplicatas:** uma entrada por partida (antes cada fase concluída gravava uma entrada parcial)
- **Sprites com a proporção correta** (a nave era esticada para 100×70), naves inimigas viradas para baixo, nave do P2 com outra cor
- Inimigos entram em cena e miram de leve no jogador; colisões de asteroides circulares
- Efeitos: partículas, tremor de tela, brilho ao levar dano, textos flutuantes, banners de fase
- Save/load e volumes salvos no próprio navegador (`localStorage`); pausa automática ao trocar de aba

Rodar a versão web localmente (qualquer servidor estático serve, pois os módulos ES precisam de `http://`):

```bash
cd web
python -m http.server 8000
# abra http://localhost:8000
```

As imagens e os áudios da pasta `web/assets` são os mesmos de `JGOOPY/assets`, só redimensionados/copiados por `scripts/preparar_assets_web.py`.

## Como executar a versão Pygame

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
├── NOVA_DESCENT.py   # jogo original em Pygame
└── assets/           # imagens e sons
web/                  # versão para navegador
├── index.html
├── css/estilo.css
├── js/               # config, assets, audio, input, entities, game, ui, main
└── assets/           # imagens e áudios otimizados
scripts/preparar_assets_web.py
```

## Autor

- Gabriel Wiedenhoft — [LinkedIn](https://www.linkedin.com/in/gabriel-wiedenhoft-8a3256286)

Licença [MIT](LICENSE). 

## Créditos dos assets

Imagens (como `c3po.png`) e áudio (música) em `JGOOPY/assets` vieram de bancos gratuitos de recursos para jogos. A origem exata de cada arquivo não foi registrada na época. O código do jogo é autoral e está sob a licença MIT; os assets mantêm as licenças de seus autores originais, então verifique os direitos de uso antes de reutilizá-los. Se algum arquivo é seu e você quer crédito ou remoção, abra uma issue.

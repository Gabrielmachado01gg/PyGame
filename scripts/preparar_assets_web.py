"""Gera web/assets a partir de JGOOPY/assets: reduz imagens grandes (sem distorcer) e copia os áudios."""
import shutil
from pathlib import Path
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
ORIGEM = RAIZ / "JGOOPY" / "assets"
DESTINO = RAIZ / "web" / "assets"

# nome -> altura máxima em pixels (proporção preservada); None copia como está
IMAGENS = {
    "blue-stars.png": None, "bullert.png": None, "asteroid-1.png": None, "asteroid-2.png": None,
    "player.png": 192, "skill04.png": 176, "skill06.png": 440,
    "saturn.png": 420, "terra.png": 360, "c3po.png": 300, "marte.png": 250, "plutao.png": 200, "netuno.png": 200,
    "01.png": None, "02.png": None, "03.png": None, "04.png": None, "05.png": None, "06.png": None,
}
AUDIOS = ["shoot.mp3", "explosion.mp3", "powerup.mp3", "phase1.mp3", "phase2.mp3", "phase3.mp3"]

(DESTINO / "img").mkdir(parents=True, exist_ok=True)
(DESTINO / "audio").mkdir(parents=True, exist_ok=True)
for nome, altura in IMAGENS.items():
    im = Image.open(ORIGEM / nome).convert("RGBA")
    if altura and im.height > altura:
        im = im.resize((round(im.width * altura / im.height), altura), Image.LANCZOS)
    im.save(DESTINO / "img" / nome, optimize=True)
for nome in AUDIOS:
    shutil.copy2(ORIGEM / nome, DESTINO / "audio" / nome)
print("ok", sum(p.stat().st_size for p in DESTINO.rglob("*") if p.is_file()) // 1024, "KB")

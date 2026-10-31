import { IMAGES } from "./config.js";

export const imgs = {};

function carregar(nome) {
  return new Promise((resolve) => {
    const im = new Image();
    im.onload = () => resolve([nome, im]);
    im.onerror = () => resolve([nome, null]); // o jogo desenha formas se a imagem faltar
    im.src = `assets/img/${nome}.png`;
  });
}

export async function carregarImagens(onProgresso) {
  let feitas = 0;
  await Promise.all(IMAGES.map(async (n) => {
    const [nome, im] = await carregar(n);
    imgs[nome] = im;
    onProgresso?.(++feitas / IMAGES.length);
  }));
  imgs["player-p2"] = tingir(imgs.player, "hue-rotate(150deg) saturate(1.6)");
  imgs["enemy"] = girar180(imgs.skill04);
}

// Cria uma cópia colorida da imagem (ctx.filter não existe em alguns navegadores: nesse caso, usa a original).
function tingir(im, filtro) {
  if (!im) return null;
  const c = document.createElement("canvas");
  c.width = im.width; c.height = im.height;
  const x = c.getContext("2d");
  if (!("filter" in x)) return im;
  x.filter = filtro;
  x.drawImage(im, 0, 0);
  return c;
}

function girar180(im) {
  if (!im) return null;
  const c = document.createElement("canvas");
  c.width = im.width; c.height = im.height;
  const x = c.getContext("2d");
  x.translate(c.width / 2, c.height / 2);
  x.rotate(Math.PI);
  x.drawImage(im, -im.width / 2, -im.height / 2);
  return c;
}

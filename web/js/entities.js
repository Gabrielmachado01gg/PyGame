import { W, H, CFG, POWERUP_COLORS } from "./config.js";
import { imgs } from "./assets.js";

export const rnd = (a, b) => a + Math.random() * (b - a);
export const rint = (a, b) => Math.floor(rnd(a, b + 1));
export const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
export function weighted(items, weights) {
  const total = weights.reduce((s, w) => s + w, 0);
  let r = Math.random() * total;
  for (let i = 0; i < items.length; i++) { r -= weights[i]; if (r <= 0) return items[i]; }
  return items[items.length - 1];
}
export const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

// Desenha uma imagem centrada em (cx, cy) com altura h, preservando a proporção.
export function drawImg(ctx, img, cx, cy, h, rot = 0, alpha = 1) {
  if (!img) return false;
  const w = (img.width / img.height) * h;
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.translate(cx, cy);
  if (rot) ctx.rotate(rot);
  ctx.drawImage(img, -w / 2, -h / 2, w, h);
  ctx.restore();
  return true;
}

export function hit(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}
function circleBox(cx, cy, r, b) {
  const nx = clamp(cx, b.x, b.x + b.w), ny = clamp(cy, b.y, b.y + b.h);
  return (cx - nx) ** 2 + (cy - ny) ** 2 < r * r;
}
export { circleBox };

// ---------------------------------------------------------------- Jogador
export class Player {
  constructor(n, x, y) {
    this.n = n; this.x = x; this.y = y; this.home = { x, y };
    this.vx = 0; this.alive = true; this.health = 100; this.score = 0;
    this.lives = CFG.initialLives;
    this.lastShot = -1e9; this.tele = false;
    this.invulUntil = 0; this.shieldUntil = 0; this.upgradeUntil = 0;
    this.respawnAt = 0; this.flash = 0; this.thrust = Math.random() * 10;
  }
  get owner() { return "p" + this.n; }
  get box() { return { x: this.x - 17, y: this.y - 32, w: 34, h: 62 }; }
  shielded(t) { return t < this.shieldUntil; }
  invul(t) { return t < this.invulUntil; }
  upgraded(t) { return t < this.upgradeUntil; }

  move(dx, dy, k) {
    this.x = clamp(this.x + dx * CFG.playerSpeed * k, 32, W - 32);
    this.y = clamp(this.y + dy * CFG.playerSpeed * k, 46, H - 46);
    this.vx = dx;
  }
  follow(tx, ty, k) {
    const nx = this.x + clamp((tx - this.x) * 0.22 * k, -16 * k, 16 * k);
    const ny = this.y + clamp((ty - this.y) * 0.22 * k, -16 * k, 16 * k);
    this.vx = clamp((nx - this.x) / (6 * k || 1), -1, 1);
    this.x = clamp(nx, 32, W - 32);
    this.y = clamp(ny, 46, H - 46);
  }

  shoot(g) {
    if (!this.alive || g.t - this.lastShot < CFG.playerShootDelay) return;
    this.lastShot = g.t;
    const o = this.owner;
    g.bullets.push(bullet(this.x, this.y - 40, 0, -CFG.bulletSpeed, o));
    if (this.upgraded(g.t)) {
      g.bullets.push(bullet(this.x - 24, this.y - 6, -0.9, -CFG.bulletSpeed, o));
      g.bullets.push(bullet(this.x + 24, this.y - 6, 0.9, -CFG.bulletSpeed, o));
    }
    g.audio.efeito("shoot");
  }

  damage(amount, g) {
    if (!this.alive || this.invul(g.t) || this.shielded(g.t)) return false;
    this.health -= amount;
    this.flash = 8;
    g.shake = Math.max(g.shake, 8);
    if (this.health <= 0) this.die(g);
    return true;
  }

  die(g) {
    this.health = 0; this.alive = false; this.lives -= 1;
    this.upgradeUntil = this.shieldUntil = this.invulUntil = 0; this.tele = false;
    this.respawnAt = this.lives > 0 ? g.t + CFG.respawnMs : Infinity;
    g.boom(this.x, this.y, true);
    g.text(this.x, this.y - 40, this.lives > 0 ? "−1 vida" : "sem vidas", "#ff6b6b");
  }

  respawn(g) {
    this.alive = true; this.health = 100; this.respawnAt = 0;
    this.x = this.home.x; this.y = this.home.y;
    this.invulUntil = g.t + CFG.invulnAfterRespawnMs;
    g.text(this.x, this.y - 50, "de volta!", "#9be7ff");
  }

  teleport(g) {
    if (!this.alive || !this.tele) return;
    this.x = rnd(80, W - 80); this.y = rnd(160, H - 100);
    this.invulUntil = g.t + 3000; this.tele = false;
    g.spark(this.x, this.y, "#d98cff", 18);
  }

  draw(ctx, g) {
    const t = g.t;
    if (!this.alive) return;
    const blink = this.invul(t) && !this.shielded(t) ? (Math.floor(t / 90) % 2 ? 0.35 : 0.9) : 1;
    // chama do motor
    const f = 14 + Math.sin(t * 0.05 + this.thrust) * 5;
    const grad = ctx.createLinearGradient(0, this.y + 34, 0, this.y + 34 + f * 2);
    grad.addColorStop(0, this.n === 1 ? "rgba(120,200,255,.95)" : "rgba(255,170,110,.95)");
    grad.addColorStop(1, "rgba(255,255,255,0)");
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.moveTo(this.x - 8, this.y + 34); ctx.lineTo(this.x + 8, this.y + 34); ctx.lineTo(this.x, this.y + 34 + f * 2);
    ctx.fill();
    const img = this.n === 2 ? imgs["player-p2"] : imgs.player;
    // halo suave: a nave original é escura e some no fundo
    const halo = ctx.createRadialGradient(this.x, this.y, 8, this.x, this.y, 62);
    halo.addColorStop(0, this.n === 1 ? "rgba(90,180,255,.28)" : "rgba(255,140,100,.28)");
    halo.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = halo; ctx.beginPath(); ctx.arc(this.x, this.y, 62, 0, 6.28); ctx.fill();
    if (!drawImg(ctx, img, this.x, this.y, 92, this.vx * 0.12, blink)) {
      ctx.fillStyle = this.n === 1 ? "#0078ff" : "#ff6464";
      ctx.beginPath(); ctx.moveTo(this.x, this.y - 40); ctx.lineTo(this.x - 28, this.y + 36); ctx.lineTo(this.x + 28, this.y + 36); ctx.fill();
    }
    // realce: soma a própria imagem para clarear o casco escuro
    ctx.globalCompositeOperation = "lighter";
    drawImg(ctx, img, this.x, this.y, 92, this.vx * 0.12, 0.35 * blink);
    ctx.globalCompositeOperation = "source-over";
    if (this.flash > 0) {
      ctx.globalAlpha = this.flash / 12;
      drawImg(ctx, img, this.x, this.y, 92, this.vx * 0.12, 1);
      ctx.globalCompositeOperation = "lighter";
      drawImg(ctx, img, this.x, this.y, 92, this.vx * 0.12, 1);
      ctx.globalCompositeOperation = "source-over";
      ctx.globalAlpha = 1;
    }
    if (this.shielded(t)) {
      const left = this.shieldUntil - t;
      const a = left < 1500 ? (Math.floor(t / 100) % 2 ? 0.3 : 0.9) : 0.9;
      ctx.strokeStyle = `rgba(110,210,255,${a})`; ctx.lineWidth = 3;
      ctx.fillStyle = "rgba(110,210,255,.12)";
      ctx.beginPath(); ctx.arc(this.x, this.y, 58 + Math.sin(t * 0.01) * 2, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
    }
    if (this.upgraded(t)) {
      ctx.strokeStyle = "rgba(255,230,100,.7)"; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(this.x, this.y, 52, -0.6, 0.6); ctx.stroke();
      ctx.beginPath(); ctx.arc(this.x, this.y, 52, Math.PI - 0.6, Math.PI + 0.6); ctx.stroke();
    }
  }
}

// ---------------------------------------------------------------- Tiros
export function bullet(x, y, vx, vy, owner, dmg = 1) {
  return { x, y, vx, vy, owner, dmg };
}
export function drawBullet(ctx, b) {
  if (b.owner === "enemy") {
    ctx.fillStyle = "rgba(255,60,60,.35)";
    ctx.beginPath(); ctx.arc(b.x, b.y, 11, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#ff5a4a";
    ctx.beginPath(); ctx.arc(b.x, b.y, 6, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#ffd2c8";
    ctx.beginPath(); ctx.arc(b.x, b.y, 2.5, 0, Math.PI * 2); ctx.fill();
  } else if (imgs.bullert) {
    drawImg(ctx, imgs.bullert, b.x, b.y, 26);
  } else {
    ctx.fillStyle = "#ffe84a"; ctx.fillRect(b.x - 4, b.y - 10, 8, 20);
  }
}

// ---------------------------------------------------------------- Meteoro
export class Meteor {
  constructor(kind = "default", x, y) {
    this.kind = kind; this.r = 28;
    this.damage = kind === "evil" ? 40 : 20;
    this.x = x ?? rnd(40, W - 40);
    this.y = y ?? rnd(-300, -40);
    this.rot = rnd(0, 6.28);
    this.spawnSpeeds();
  }
  spawnSpeeds() {
    this.vy = this.kind === "evil" ? rnd(1.4, 3.2) : rnd(1.1, 2.2);
    this.vx = rnd(-1.6, 1.6);
    this.rotSpeed = rnd(-0.08, 0.08);
  }
  respawn() { this.x = rnd(40, W - 40); this.y = rnd(-220, -50); this.spawnSpeeds(); }
  update(k, mult) {
    this.y += this.vy * mult * k; this.x += this.vx * k; this.rot += this.rotSpeed * k;
    if (this.y > H + 50 || this.x < -60 || this.x > W + 60) this.respawn();
  }
  draw(ctx) {
    const im = this.kind === "evil" ? imgs["asteroid-2"] : imgs["asteroid-1"];
    if (!drawImg(ctx, im, this.x, this.y, this.kind === "evil" ? 72 : 64, this.rot)) {
      ctx.fillStyle = "#777"; ctx.beginPath(); ctx.arc(this.x, this.y, 30, 0, 6.28); ctx.fill();
    }
  }
}

// ---------------------------------------------------------------- Inimigo
export class Enemy {
  constructor(x, targetY, g) {
    this.x = x; this.y = -60; this.targetY = targetY; this.tx = x;
    this.health = 3; this.flash = 0;
    this.nextShot = g.t + rnd(700, 1500);
    this.shotDelay = 900 + rnd(-200, 200);
    this.nextMove = g.t + 1200;
  }
  get box() { return { x: this.x - 28, y: this.y - 28, w: 56, h: 56 }; }
  update(k, g) {
    if (this.y < this.targetY) this.y += 4 * k;
    if (g.t > this.nextMove) {
      this.nextMove = g.t + 1200;
      this.tx = clamp(this.x + pick([-80, -40, 0, 40, 80]), 60, W - 60);
    }
    this.x += (this.tx - this.x) * 0.06 * k;
    if (this.flash > 0) this.flash -= k;
    if (this.y >= this.targetY - 2 && g.t > this.nextShot) {
      this.nextShot = g.t + this.shotDelay;
      const target = g.nearestAlive(this.x);
      let vx = 0;
      if (target) vx = clamp((target.x - this.x) / 140, -2.2, 2.2); // mira de leve no jogador mais próximo
      g.bullets.push(bullet(this.x, this.y + 30, vx, 6, "enemy"));
    }
  }
  draw(ctx) {
    if (!drawImg(ctx, imgs.enemy, this.x, this.y, 66)) {
      ctx.fillStyle = "#b45028"; ctx.beginPath(); ctx.moveTo(this.x, this.y + 32); ctx.lineTo(this.x - 32, this.y - 32); ctx.lineTo(this.x + 32, this.y - 32); ctx.fill();
    }
    if (this.flash > 0) {
      ctx.globalAlpha = Math.min(1, this.flash / 6) * 0.8;
      ctx.globalCompositeOperation = "lighter";
      drawImg(ctx, imgs.enemy, this.x, this.y, 66);
      ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 1;
    }
  }
}

// ---------------------------------------------------------------- Chefão
export class Boss {
  constructor(g) {
    this.x = W / 2; this.y = -160; this.targetY = 150;
    this.health = CFG.bossHealth; this.maxHealth = CFG.bossHealth;
    this.dir = 1; this.speed = 2; this.mode = "normal"; this.flash = 0;
    this.nextShot = g.t + 1500; this.modeUntil = g.t + 5000; this.t0 = g.t;
  }
  get box() { return { x: this.x - 100, y: this.y - 100, w: 200, h: 200 }; }
  get entering() { return this.y < this.targetY - 1; }
  update(k, g) {
    if (this.entering) { this.y += 2.5 * k; return; }
    this.x += this.speed * this.dir * k;
    this.y = this.targetY + Math.sin((g.t - this.t0) * 0.002) * 12;
    if (this.x + 110 > W - 100) this.dir = -1; else if (this.x - 110 < 100) this.dir = 1;
    if (this.flash > 0) this.flash -= k;
    if (g.t > this.modeUntil) {
      this.modeUntil = g.t + 5000;
      this.mode = pick(["normal", "spread", "rapid"]);
    }
    if (g.t > this.nextShot) {
      const by = this.y + 100;
      if (this.mode === "normal") {
        this.nextShot = g.t + 1500;
        for (const off of [-40, 0, 40]) g.bullets.push(bullet(this.x + off, by, 0, 8, "enemy"));
      } else if (this.mode === "spread") {
        this.nextShot = g.t + 1500;
        for (const a of [-30, -15, 0, 15, 30]) g.bullets.push(bullet(this.x, by, a * 0.1, 8, "enemy"));
      } else {
        this.nextShot = g.t + 300; // tiro rápido: o atraso volta ao normal quando o modo muda
        g.bullets.push(bullet(this.x + rnd(-30, 30), by, 0, 10, "enemy"));
      }
    }
  }
  draw(ctx) {
    if (!drawImg(ctx, imgs.skill06, this.x, this.y, 220)) {
      ctx.fillStyle = "#9628c8"; ctx.beginPath(); ctx.arc(this.x, this.y, 110, 0, 6.28); ctx.fill();
    }
    if (this.flash > 0) {
      ctx.globalAlpha = Math.min(1, this.flash / 6) * 0.7;
      ctx.globalCompositeOperation = "lighter";
      drawImg(ctx, imgs.skill06, this.x, this.y, 220);
      ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 1;
    }
  }
}

// ---------------------------------------------------------------- Explosão
export class Explosion {
  constructor(x, y, size = 90) { this.x = x; this.y = y; this.size = size; this.i = 0; this.acc = 0; this.done = false; }
  update(dt) {
    this.acc += dt;
    while (this.acc > 65) { this.acc -= 65; this.i++; }
    if (this.i >= 6) this.done = true;
  }
  draw(ctx) {
    const im = imgs[["01", "02", "03", "04", "05", "06"][Math.min(5, this.i)]];
    if (im) drawImg(ctx, im, this.x, this.y, this.size);
  }
}

// ---------------------------------------------------------------- Powerup
export class Powerup {
  constructor(x, y, type) { this.x = x; this.y = y; this.type = type; this.off = Math.random() * 6; this.r = 18; }
  update(k, t) {
    this.y += (2 + Math.sin(t * 0.003 + this.off)) * k;
    this.x += Math.cos(t * 0.002 + this.off) * 0.4 * k;
  }
  get dead() { return this.y > H + 30; }
  draw(ctx, t) {
    const c = POWERUP_COLORS[this.type] || "#fff";
    const pulse = 1 + Math.sin(t * 0.008 + this.off) * 0.12;
    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.scale(pulse, pulse);
    const g = ctx.createRadialGradient(0, 0, 4, 0, 0, 26);
    g.addColorStop(0, c + "aa"); g.addColorStop(1, c + "00");
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, 26, 0, 6.28); ctx.fill();
    ctx.fillStyle = c; ctx.strokeStyle = "#fff"; ctx.lineWidth = 2;
    ctx.beginPath();
    switch (this.type) {
      case "revive": ctx.arc(0, 0, 14, 0, 6.28); break;
      case "invul_gift": ctx.roundRect(-13, -13, 26, 26, 5); break;
      case "upgrade": ctx.moveTo(0, -15); ctx.lineTo(-14, 12); ctx.lineTo(14, 12); ctx.closePath(); break;
      case "extra_life": ctx.rect(-12, -12, 24, 24); break;
      case "teleporter": ctx.arc(0, 0, 10, 0, 6.28); break;
      case "shield": ctx.arc(0, 0, 14, 0, 6.28); ctx.fillStyle = "rgba(100,200,255,.15)"; break;
      default: ctx.rect(-12, -12, 24, 24);
    }
    ctx.fill(); ctx.stroke();
    // marca interna para não depender só da cor
    ctx.fillStyle = "#fff"; ctx.strokeStyle = "#fff"; ctx.lineWidth = 2.5;
    ctx.beginPath();
    if (this.type === "extra_life") { ctx.moveTo(-6, 0); ctx.lineTo(6, 0); ctx.moveTo(0, -6); ctx.lineTo(0, 6); ctx.stroke(); }
    else if (this.type === "revive") { ctx.moveTo(-5, 2); ctx.lineTo(0, -4); ctx.lineTo(5, 2); ctx.stroke(); }
    else if (this.type === "upgrade") { ctx.arc(0, 4, 2.2, 0, 6.28); ctx.fill(); }
    else if (this.type === "teleporter") { ctx.arc(0, 0, 3, 0, 6.28); ctx.fill(); }
    ctx.restore();
  }
}

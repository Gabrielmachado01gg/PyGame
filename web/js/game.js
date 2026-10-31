import { W, H, CFG, PLANETS, POWERUP_NAMES } from "./config.js";
import { imgs } from "./assets.js";
import * as store from "./storage.js";
import {
  Player, Meteor, Enemy, Boss, Explosion, Powerup, bullet, drawBullet, drawImg,
  rnd, rint, pick, weighted, hit, circleBox,
} from "./entities.js";

const PHASE_NAMES = { asteroids: "Fase 1", phase2: "Fase 2", phase3: "Fase 3" };

export class Game {
  constructor(audio) {
    this.audio = audio;
    this.stars = Array.from({ length: 90 }, () => ({ x: rnd(0, W), y: rnd(0, H), z: rnd(0.3, 1.4) }));
    this.reset(false);
  }

  reset(two) {
    this.two = two; this.t = 0;
    this.stage = "asteroids"; this.mult = 1; this.nextSpeedStep = 500;
    this.killed = 0; this.wave = 0;
    this.players = [new Player(1, two ? W * 0.62 : W / 2, H - 110)];
    if (two) this.players.push(new Player(2, W * 0.38, H - 110));
    this.meteors = []; this.bullets = []; this.powerups = []; this.enemies = [];
    this.fx = []; this.parts = []; this.texts = [];
    this.boss = null; this.trans = null; this.end = null; this.banner = null;
    this.shake = 0; this.nextMinion = 0; this.recorded = false;
    for (let i = 0; i < CFG.maxMeteors; i++) this.meteors.push(new Meteor(pick(["default", "default", "evil"])));
    this.setBanner("FASE 1", "Destrua asteroides: faltam 1500 pontos", 2600);
    this.audio.tocarMusica("asteroids");
  }

  // ---------- utilidades
  get totalScore() { return this.players.reduce((s, p) => s + p.score, 0); }
  get progressLabel() {
    if (this.end === "victory") return "Vitória";
    return PHASE_NAMES[this.stage] || "Fase 1";
  }
  phasesDone() { return this.end === "victory" ? 3 : this.stage === "asteroids" ? 0 : this.stage === "phase2" ? 1 : 2; }
  alivePlayers() { return this.players.filter((p) => p.alive); }
  nearestAlive(x) {
    let best = null, d = 1e9;
    for (const p of this.players) if (p.alive && Math.abs(p.x - x) < d) { d = Math.abs(p.x - x); best = p; }
    return best;
  }
  playerByOwner(o) { return this.players.find((p) => p.owner === o); }
  setBanner(title, sub, ms) { this.banner = { title, sub, until: this.t + ms, from: this.t }; }
  text(x, y, s, color = "#fff") { this.texts.push({ x, y, s, color, life: 1100, max: 1100 }); }
  spark(x, y, color, n = 10) {
    for (let i = 0; i < n; i++) {
      const a = rnd(0, 6.28), v = rnd(1.5, 5);
      this.parts.push({ x, y, vx: Math.cos(a) * v, vy: Math.sin(a) * v, life: rnd(300, 700), max: 700, c: color, s: rnd(1.5, 3.5) });
    }
  }
  boom(x, y, big = false) {
    this.fx.push(new Explosion(x, y, big ? 150 : 90));
    this.spark(x, y, big ? "#ffb347" : "#ffd98a", big ? 26 : 12);
    if (big) this.shake = Math.max(this.shake, 14);
    this.audio.efeito("explosion");
  }

  // ---------- fases
  spawnWave(n) {
    const margin = 140;
    const spacing = n > 1 ? (W - 2 * margin) / (n - 1) : 0;
    for (let i = 0; i < n; i++) {
      this.enemies.push(new Enemy(n > 1 ? margin + i * spacing : W / 2, 120 + rnd(-20, 20), this));
    }
  }

  drop(x, y, stage) {
    let pool, weights = null;
    if (stage === "asteroids") {
      pool = ["invul_gift", "upgrade", "extra_life", "teleporter", "shield"];
      if (this.two) pool.push("revive");
    } else if (stage === "phase2") { pool = ["upgrade", "extra_life", "shield", "invul_gift"]; weights = [30, 25, 25, 20]; }
    else { pool = ["shield", "extra_life", "upgrade"]; weights = [40, 35, 25]; }
    const type = weights ? weighted(pool, weights) : pick(pool);
    this.powerups.push(new Powerup(x, y, type));
  }

  startTransition(kind) {
    this.bullets.length = 0; this.powerups.length = 0;
    this.meteors.length = 0; this.enemies.length = 0;
    this.trans = {
      kind, until: this.t + CFG.transitionMs, from: this.t,
      title: kind === "phase2" ? "PRÓXIMA FASE!" : "ALERTA MÁXIMO!",
      lines: kind === "phase2"
        ? ["Os inimigos chegaram…", this.two ? "Destruam eles!" : "Destrua eles!"]
        : ["Chefão a caminho", "Prepare-se para a batalha final!"],
    };
  }

  finishTransition() {
    const kind = this.trans.kind;
    this.trans = null;
    this.bullets.length = 0; this.powerups.length = 0; this.fx.length = 0;
    if (kind === "phase2") {
      this.stage = "phase2"; this.wave = 1; this.killed = 0;
      this.spawnWave(CFG.enemiesPerWave);
      this.audio.tocarMusica("phase2");
      this.setBanner("FASE 2", `Derrube ${CFG.totalEnemiesPhase2} naves inimigas`, 2600);
    } else {
      this.stage = "phase3";
      this.boss = new Boss(this);
      this.nextMinion = this.t + 6000;
      this.audio.tocarMusica("phase3");
      this.setBanner("FASE 3", "Chefão final", 2600);
    }
  }

  award(owner, pts) {
    const p = this.playerByOwner(owner) || this.players.find((q) => q.alive) || this.players[0];
    p.score += pts;
    return p;
  }

  // ---------- atualização
  update(dt, ctrls) {
    const k = dt / (1000 / 60);
    this.updateStars(k);
    this.updateFx(dt, k);
    if (this.end) return;
    this.t += dt;

    if (this.trans) {
      if (this.t >= this.trans.until) this.finishTransition();
      return;
    }
    if (this.banner && this.t > this.banner.until) this.banner = null;

    // jogadores
    this.players.forEach((p, i) => {
      const c = ctrls[i] || {};
      if (!p.alive) {
        if (p.respawnAt <= this.t && p.lives > 0) p.respawn(this);
        return;
      }
      p.thrust += k * 0.1;
      if (p.flash > 0) p.flash -= k;
      if (c.follow) p.follow(c.follow.x, c.follow.y, k);
      else p.move(c.dx || 0, c.dy || 0, k);
      if (c.tp) p.teleport(this);
      if (c.shoot) p.shoot(this);
    });

    // projéteis
    for (const b of this.bullets) { b.x += b.vx * k; b.y += b.vy * k; }
    this.bullets = this.bullets.filter((b) => b.y > -30 && b.y < H + 30 && b.x > -30 && b.x < W + 30);
    for (const pu of this.powerups) pu.update(k, this.t);
    this.powerups = this.powerups.filter((pu) => !pu.dead);

    if (this.stage === "asteroids") this.updateAsteroids(k);
    else if (this.stage === "phase2") this.updateEnemies(k);
    else this.updateBoss(k);

    this.hitPlayers();
    this.pickups();
    this.checkEnd();
  }

  updateStars(k) {
    for (const s of this.stars) {
      s.y += s.z * 0.5 * k * (this.stage === "asteroids" ? 1 : 1.4);
      if (s.y > H) { s.y = -4; s.x = rnd(0, W); }
    }
  }
  updateFx(dt, k) {
    for (const e of this.fx) e.update(dt);
    this.fx = this.fx.filter((e) => !e.done);
    for (const p of this.parts) { p.x += p.vx * k; p.y += p.vy * k; p.vx *= 0.97; p.vy *= 0.97; p.life -= dt; }
    this.parts = this.parts.filter((p) => p.life > 0);
    for (const t of this.texts) { t.y -= 0.5 * k; t.life -= dt; }
    this.texts = this.texts.filter((t) => t.life > 0);
    this.shake *= Math.pow(0.9, k);
    if (this.shake < 0.2) this.shake = 0;
  }

  updateAsteroids(k) {
    for (const m of this.meteors) m.update(k, this.mult);
    while (this.meteors.length < CFG.maxMeteors) this.meteors.push(new Meteor(pick(["default", "default", "evil"])));

    for (const b of this.bullets) {
      if (b.owner === "enemy") continue;
      for (const m of this.meteors) {
        if (Math.hypot(b.x - m.x, b.y - m.y) < m.r + 6) {
          b.dead = true;
          this.boom(m.x, m.y);
          const p = this.award(b.owner, 10);
          this.text(m.x, m.y - 20, "+10", "#ffe27a");
          if (Math.random() < 0.5) this.drop(m.x, m.y, "asteroids");
          m.respawn();
          break;
        }
      }
    }
    this.bullets = this.bullets.filter((b) => !b.dead);

    // a cada 500 pontos os asteroides aceleram (a versão original só checava múltiplos exatos)
    while (this.totalScore >= this.nextSpeedStep) {
      this.mult += 0.25; this.nextSpeedStep += 500;
      this.setBanner("ASTEROIDES MAIS RÁPIDOS", "", 1400);
    }

    for (const p of this.players) {
      if (!p.alive) continue;
      for (const m of this.meteors) {
        if (circleBox(m.x, m.y, m.r - 4, p.box)) {
          if (p.damage(m.damage, this)) this.boom(m.x, m.y);
          m.respawn();
        }
      }
    }
    if (this.totalScore >= CFG.pointsToNextPhase) this.startTransition("phase2");
  }

  updateEnemies(k) {
    for (const e of this.enemies) e.update(k, this);
    for (const b of this.bullets) {
      if (b.owner === "enemy") continue;
      for (const e of this.enemies) {
        if (e.health > 0 && hit({ x: b.x - 5, y: b.y - 10, w: 10, h: 20 }, e.box)) {
          b.dead = true; e.health -= b.dmg; e.flash = 8;
          this.spark(b.x, b.y, "#ffd98a", 4);
          if (e.health <= 0) {
            this.killed++;
            this.boom(e.x, e.y);
            this.award(b.owner, 50);
            this.text(e.x, e.y - 24, "+50", "#ffe27a");
            const chance = this.killed % 3 === 0 ? 1 : 0.6;
            if (Math.random() < chance) this.drop(e.x, e.y, "phase2");
          }
          break;
        }
      }
    }
    this.bullets = this.bullets.filter((b) => !b.dead);
    this.enemies = this.enemies.filter((e) => e.health > 0);

    if (this.enemies.length === 0) {
      if (this.killed < CFG.totalEnemiesPhase2) {
        this.wave++;
        const n = Math.min(CFG.enemiesPerWave, CFG.totalEnemiesPhase2 - this.killed);
        this.spawnWave(n);
        this.setBanner(`ONDA ${this.wave}`, "", 1300);
      } else {
        this.startTransition("boss");
      }
    }
  }

  updateBoss(k) {
    const boss = this.boss;
    if (boss) {
      boss.update(k, this);
      if (!boss.entering) {
        for (const b of this.bullets) {
          if (b.owner === "enemy") continue;
          if (hit({ x: b.x - 5, y: b.y - 10, w: 10, h: 20 }, boss.box)) {
            b.dead = true; boss.health -= b.dmg; boss.flash = 6;
            this.spark(b.x, b.y, "#ff9d7a", 4);
            this.award(b.owner, 2);
            if (boss.health > 0 && boss.health % 10 === 0) this.drop(boss.x + rnd(-60, 60), boss.y + rnd(-30, 60), "phase3");
            if (boss.health <= 0) { this.killBoss(b.owner); break; }
          }
        }
      }
      if (this.boss && this.t > this.nextMinion && !boss.entering && this.enemies.length < 3) {
        this.nextMinion = this.t + rnd(5000, 6000);
        this.enemies.push(new Enemy(rnd(150, W - 150), boss.y + 120, this));
      }
    }
    for (const e of this.enemies) e.update(k, this);
    for (const b of this.bullets) {
      if (b.owner === "enemy") continue;
      for (const e of this.enemies) {
        if (e.health > 0 && hit({ x: b.x - 5, y: b.y - 10, w: 10, h: 20 }, e.box)) {
          b.dead = true; e.health -= b.dmg; e.flash = 8;
          if (e.health <= 0) {
            this.boom(e.x, e.y); this.award(b.owner, 50); this.text(e.x, e.y - 24, "+50", "#ffe27a");
            if (Math.random() < 0.4) this.drop(e.x, e.y, "phase3");
          }
          break;
        }
      }
    }
    this.bullets = this.bullets.filter((b) => !b.dead);
    this.enemies = this.enemies.filter((e) => e.health > 0);
  }

  killBoss(owner) {
    const boss = this.boss;
    this.boom(boss.x, boss.y, true);
    for (let i = 0; i < 4; i++) setTimeout(() => this.fx.push(new Explosion(boss.x + rnd(-90, 90), boss.y + rnd(-90, 90), 120)), i * 140);
    this.award(owner, 500);
    this.boss = null; this.enemies.length = 0;
    this.bullets = this.bullets.filter((b) => b.owner !== "enemy");
    this.end = "victory";
    this.endAt = this.t;
  }

  hitPlayers() {
    for (const b of this.bullets) {
      if (b.owner !== "enemy") continue;
      for (const p of this.players) {
        if (!p.alive) continue;
        const bx = p.box;
        if (circleBox(b.x, b.y, 6, bx)) {
          b.dead = true;
          if (p.damage(CFG.enemyBulletDamage, this)) this.spark(b.x, b.y, "#ff7a6a", 6);
          break;
        }
      }
    }
    this.bullets = this.bullets.filter((b) => !b.dead);
  }

  pickups() {
    for (const p of this.players) {
      if (!p.alive) continue;
      const bx = p.box;
      for (const pu of this.powerups) {
        if (pu.taken) continue;
        if (circleBox(pu.x, pu.y, pu.r, bx)) {
          pu.taken = true;
          this.applyPowerup(p, pu.type);
          this.text(pu.x, pu.y - 20, POWERUP_NAMES[pu.type], "#9be7ff");
          this.audio.efeito("powerup");
        }
      }
    }
    this.powerups = this.powerups.filter((pu) => !pu.taken);
  }

  applyPowerup(p, type) {
    const t = this.t;
    switch (type) {
      case "revive": {
        const other = this.players.find((q) => q !== p && !q.alive && q.lives > 0);
        if (other) other.respawn(this); else p.health = Math.min(100, p.health + 50);
        break;
      }
      case "invul_gift": p.invulUntil = t + CFG.invulnMs; break;
      case "upgrade": p.upgradeUntil = t + CFG.upgradeMs; break;
      case "extra_life": p.health = Math.min(100, p.health + 30); p.lives += 1; break;
      case "teleporter": p.tele = true; break;
      case "shield": p.shieldUntil = t + CFG.shieldMs; break;
    }
  }

  checkEnd() {
    if (this.end) return;
    const over = this.players.every((p) => !p.alive && p.lives <= 0);
    if (over) { this.end = "gameover"; this.endAt = this.t; }
  }

  // ---------- salvar / carregar
  snapshot() {
    return {
      v: 1, two: this.two, stage: this.stage, mult: this.mult, nextSpeedStep: this.nextSpeedStep,
      killed: this.killed, wave: this.wave, bossHealth: this.boss ? this.boss.health : null,
      players: this.players.map((p) => ({ score: p.score, lives: p.lives, health: p.alive ? p.health : 100, tele: p.tele, upgraded: p.upgraded(this.t), x: p.x, y: p.y })),
      savedAt: new Date().toISOString(),
    };
  }
  restore(s) {
    if (!s || s.v !== 1) return false;
    this.reset(!!s.two);
    this.stage = s.stage; this.mult = s.mult; this.nextSpeedStep = s.nextSpeedStep; this.killed = s.killed; this.wave = s.wave;
    s.players.forEach((d, i) => {
      const p = this.players[i]; if (!p) return;
      Object.assign(p, { score: d.score, lives: Math.max(1, d.lives), health: d.health, tele: d.tele, x: d.x, y: d.y });
      if (d.upgraded) p.upgradeUntil = this.t + 8000;
      p.invulUntil = this.t + 2000;
    });
    this.meteors.length = 0;
    if (this.stage === "asteroids") for (let i = 0; i < CFG.maxMeteors; i++) this.meteors.push(new Meteor(pick(["default", "default", "evil"])));
    if (this.stage === "phase2") {
      const left = CFG.totalEnemiesPhase2 - this.killed;
      if (left > 0) this.spawnWave(Math.min(CFG.enemiesPerWave, left));
    }
    if (this.stage === "phase3") {
      this.boss = new Boss(this);
      if (s.bossHealth) this.boss.health = s.bossHealth;
      this.nextMinion = this.t + 6000;
    }
    this.audio.tocarMusica(this.stage);
    this.setBanner(PHASE_NAMES[this.stage].toUpperCase(), "Jogo carregado", 1800);
    return true;
  }

  // ---------- desenho
  drawBackground(ctx, stage = this.stage) {
    if (imgs["blue-stars"]) { ctx.imageSmoothingEnabled = true; ctx.drawImage(imgs["blue-stars"], 0, 0, W, H); }
    else { ctx.fillStyle = "#000"; ctx.fillRect(0, 0, W, H); }
    ctx.fillStyle = "rgba(2,4,14,.35)"; ctx.fillRect(0, 0, W, H);
    for (const s of this.stars) {
      ctx.fillStyle = `rgba(200,225,255,${0.25 + s.z * 0.35})`;
      ctx.fillRect(s.x, s.y, s.z * 1.6, s.z * 1.6);
    }
    const list = stage === "phase2" ? PLANETS.phase2 : stage === "phase3" ? PLANETS.phase3 : PLANETS.asteroids;
    for (const p of list) {
      const im = imgs[p.img];
      if (im) ctx.drawImage(im, p.x, p.y + Math.sin(this.t * 0.0004 + p.x) * 6, p.size, p.size);
    }
  }

  draw(ctx) {
    ctx.save();
    if (this.shake > 0) ctx.translate(rnd(-this.shake, this.shake) * 0.5, rnd(-this.shake, this.shake) * 0.5);
    this.drawBackground(ctx, this.trans ? "asteroids" : this.stage);
    if (!this.trans) {
      for (const m of this.meteors) m.draw(ctx);
      for (const pu of this.powerups) pu.draw(ctx, this.t);
      for (const e of this.enemies) e.draw(ctx);
      if (this.boss) this.boss.draw(ctx);
      for (const b of this.bullets) drawBullet(ctx, b);
      for (const p of this.players) p.draw(ctx, this);
    }
    for (const e of this.fx) e.draw(ctx);
    ctx.globalCompositeOperation = "lighter";
    for (const p of this.parts) {
      ctx.globalAlpha = Math.max(0, p.life / p.max);
      ctx.fillStyle = p.c; ctx.fillRect(p.x, p.y, p.s, p.s);
    }
    ctx.globalCompositeOperation = "source-over"; ctx.globalAlpha = 1;
    ctx.restore();
  }
}

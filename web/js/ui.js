import { W, H, CFG, VOLUME_LABELS, POWERUP_NAMES, POWERUP_COLORS } from "./config.js";
import { imgs } from "./assets.js";
import { drawImg } from "./entities.js";

export const FONT_T = '"Orbitron", "Segoe UI", system-ui, sans-serif';
export const FONT_B = '"Rajdhani", "Segoe UI", system-ui, sans-serif';
const CYAN = "#5ad1ff", AMBER = "#ffcf5a", RED = "#ff5a5a", MUTED = "#9db0c9";

export function txt(ctx, s, x, y, size, color = "#fff", align = "center", font = FONT_B, weight = 600) {
  ctx.font = `${weight} ${size}px ${font}`;
  ctx.textAlign = align; ctx.textBaseline = "middle";
  ctx.fillStyle = color;
  ctx.fillText(String(s), x, y);
}
function glowText(ctx, s, x, y, size, color, glow) {
  ctx.save(); ctx.shadowColor = glow; ctx.shadowBlur = 24;
  txt(ctx, s, x, y, size, color, "center", FONT_T, 800);
  ctx.restore();
}
function panel(ctx, x, y, w, h, a = 0.55) {
  ctx.fillStyle = `rgba(6,12,28,${a})`;
  ctx.strokeStyle = "rgba(120,170,255,.25)"; ctx.lineWidth = 1.5;
  ctx.beginPath(); ctx.roundRect(x, y, w, h, 10); ctx.fill(); ctx.stroke();
}

// ---------- menus em lista
export function hitItems(p, n, y0, step) {
  if (p.x < W / 2 - 250 || p.x > W / 2 + 250) return -1;
  const i = Math.floor((p.y - (y0 - step / 2)) / step);
  return i >= 0 && i < n ? i : -1;
}
export function drawItems(ctx, items, idx, y0, step, size = 34) {
  items.forEach((it, i) => {
    const sel = i === idx;
    const y = y0 + i * step;
    if (sel) {
      ctx.fillStyle = "rgba(90,209,255,.12)";
      ctx.strokeStyle = "rgba(90,209,255,.55)"; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.roundRect(W / 2 - 230, y - step / 2 + 5, 460, step - 10, 10); ctx.fill(); ctx.stroke();
    }
    const label = typeof it === "string" ? it : it.label;
    const off = typeof it === "object" && it.disabled;
    txt(ctx, label, W / 2, y, size, off ? "#5d6b82" : sel ? AMBER : "#d7e3f5", "center", FONT_B, sel ? 700 : 600);
    if (typeof it === "object" && it.hint) txt(ctx, it.hint, W / 2 + 215, y, 16, MUTED, "right");
  });
}

// ---------- telas
export function drawTitle(ctx, app, items, idx) {
  const g = app.game;
  g.drawBackground(ctx, "asteroids");
  ctx.fillStyle = "rgba(2,4,14,.45)"; ctx.fillRect(0, 0, W, H);
  const t = performance.now();
  drawImg(ctx, imgs.player, W * 0.16, 520 + Math.sin(t / 700) * 12, 150, -0.1);
  drawImg(ctx, imgs.enemy, W * 0.86, 230 + Math.sin(t / 900) * 10, 90, 0.1);
  glowText(ctx, "NOVA DESCENT", W / 2, 100, 74, "#eaf6ff", "#2a9dff");
  txt(ctx, "SHOOTER ESPACIAL EM 3 FASES", W / 2, 158, 22, CYAN, "center", FONT_B, 700);
  drawItems(ctx, items, idx, 250, 62, 34);
  txt(ctx, "↑ ↓ para navegar · ENTER para escolher · ou toque / clique", W / 2, H - 60, 20, MUTED);
  txt(ctx, "Projeto de Gabriel Wiedenhoft · versão web em HTML5 Canvas", W / 2, H - 30, 17, "#6f819e");
}

export function drawControls(ctx, app) {
  app.game.drawBackground(ctx, "asteroids");
  ctx.fillStyle = "rgba(2,4,14,.7)"; ctx.fillRect(0, 0, W, H);
  txt(ctx, "CONTROLES", W / 2, 70, 44, "#eaf6ff", "center", FONT_T, 800);
  const col = (x, title, color, rows) => {
    panel(ctx, x, 120, 360, 300);
    txt(ctx, title, x + 180, 155, 28, color, "center", FONT_T, 700);
    rows.forEach(([k, d], i) => {
      txt(ctx, k, x + 24, 205 + i * 44, 24, AMBER, "left", FONT_B, 700);
      txt(ctx, d, x + 336, 205 + i * 44, 22, "#d7e3f5", "right");
    });
  };
  col(60, "JOGADOR 1", CYAN, [["W A S D", "mover"], ["ESPAÇO", "atirar"], ["T", "teleportar"], ["M", "mouse liga/desliga"]]);
  col(460, "JOGADOR 2", RED, [["SETAS", "mover"], ["ENTER / CTRL dir.", "atirar"], ["SHIFT dir.", "teleportar"]]);
  col(860, "GERAL", "#b7f08a", [["P / ESC", "pausa"], ["F", "salvar"], ["L", "carregar"], ["R", "reiniciar"]]);
  panel(ctx, 60, 450, 1160, 150);
  txt(ctx, "Celular / tablet", 90, 485, 24, CYAN, "left", FONT_T, 700);
  txt(ctx, "Arraste o dedo para mover a nave — ela atira sozinha enquanto você joga.", 90, 530, 22, "#d7e3f5", "left");
  txt(ctx, "No modo 1 jogador, as setas também movem a nave e o mouse (tecla M) segue o cursor.", 90, 566, 22, "#d7e3f5", "left");
  txt(ctx, "ENTER ou ESC para voltar", W / 2, H - 50, 22, MUTED);
}

export function drawScores(ctx, app, list) {
  app.game.drawBackground(ctx, "asteroids");
  ctx.fillStyle = "rgba(2,4,14,.7)"; ctx.fillRect(0, 0, W, H);
  txt(ctx, "PLACAR", W / 2, 70, 44, "#eaf6ff", "center", FONT_T, 800);
  if (!list.length) {
    txt(ctx, "Nenhuma partida registrada neste navegador ainda.", W / 2, H / 2, 28, MUTED);
  }
  const medal = ["#ffd700", "#c0c0c0", "#cd7f32"];
  list.slice(0, 10).forEach((h, i) => {
    const y = 140 + i * 48;
    panel(ctx, W / 2 - 420, y - 20, 840, 42, 0.4);
    txt(ctx, `${i + 1}.`, W / 2 - 395, y, 24, medal[i] || MUTED, "left", FONT_T, 700);
    txt(ctx, h.name, W / 2 - 340, y, 24, medal[i] || "#d7e3f5", "left");
    txt(ctx, `${h.score} pts`, W / 2 - 100, y, 24, AMBER, "left", FONT_B, 700);
    txt(ctx, h.victory ? "✓ " + h.progress : "→ " + h.progress, W / 2 + 60, y, 22, h.victory ? "#7dff9a" : "#d8d06a", "left");
    txt(ctx, h.date || "", W / 2 + 400, y, 18, "#6f819e", "right");
  });
  txt(ctx, "ENTER ou ESC para voltar", W / 2, H - 40, 22, MUTED);
}

// linhas do menu de volume: 6 barras + restaurar + voltar
export const VOL_KEYS = Object.keys(VOLUME_LABELS);
export function volRow(i) { return { y: 150 + i * 56, barX: W / 2 - 40, barW: 260 }; }
export function drawVolume(ctx, app, idx) {
  app.game.drawBackground(ctx, "asteroids");
  ctx.fillStyle = "rgba(2,4,14,.75)"; ctx.fillRect(0, 0, W, H);
  txt(ctx, "VOLUME", W / 2, 70, 44, "#eaf6ff", "center", FONT_T, 800);
  VOL_KEYS.forEach((k, i) => {
    const { y, barX, barW } = volRow(i);
    const sel = i === idx, v = app.audio.volumes[k];
    if (sel) { ctx.fillStyle = "rgba(90,209,255,.1)"; ctx.beginPath(); ctx.roundRect(W / 2 - 330, y - 24, 660, 48, 10); ctx.fill(); }
    txt(ctx, VOLUME_LABELS[k], W / 2 - 300, y, 26, sel ? AMBER : "#d7e3f5", "left");
    ctx.fillStyle = "#1a2540"; ctx.beginPath(); ctx.roundRect(barX, y - 8, barW, 16, 8); ctx.fill();
    ctx.fillStyle = sel ? AMBER : CYAN; ctx.beginPath(); ctx.roundRect(barX, y - 8, Math.max(8, barW * v), 16, 8); ctx.fill();
    ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.arc(barX + barW * v, y, 9, 0, 6.28); ctx.fill();
    txt(ctx, Math.round(v * 100) + "%", W / 2 + 300, y, 24, "#d7e3f5", "right");
  });
  const rest = VOL_KEYS.length;
  drawItems(ctx, ["Restaurar padrão", "Voltar"], idx - rest, 150 + rest * 56 + 14, 56, 28);
  txt(ctx, "↑ ↓ escolher · ← → ajustar · toque nas barras", W / 2, H - 40, 20, MUTED);
}

export function drawPause(ctx, items, idx) {
  ctx.fillStyle = "rgba(2,4,14,.72)"; ctx.fillRect(0, 0, W, H);
  txt(ctx, "PAUSADO", W / 2, 130, 52, "#eaf6ff", "center", FONT_T, 800);
  drawItems(ctx, items, idx, 235, 62, 32);
  txt(ctx, "ESC / P continua", W / 2, H - 50, 20, MUTED);
}

export function drawTransition(ctx, g) {
  const tr = g.trans;
  const p = Math.min(1, (g.t - tr.from) / 500);
  ctx.fillStyle = "rgba(2,4,14,.55)"; ctx.fillRect(0, 0, W, H);
  ctx.globalAlpha = p;
  glowText(ctx, tr.title, W / 2, H / 2 - 70, 58, tr.kind === "boss" ? "#ff9a8a" : "#eaf6ff", tr.kind === "boss" ? "#ff3b2e" : "#2a9dff");
  txt(ctx, tr.lines[0], W / 2, H / 2 + 10, 32, "#d7e3f5");
  txt(ctx, tr.lines[1], W / 2, H / 2 + 56, 32, AMBER, "center", FONT_B, 700);
  ctx.globalAlpha = 1;
}

export function drawEnd(ctx, app, items, idx, rank) {
  const g = app.game;
  const win = g.end === "victory";
  ctx.fillStyle = "rgba(2,4,14,.7)"; ctx.fillRect(0, 0, W, H);
  glowText(ctx, win ? "VITÓRIA!" : "GAME OVER", W / 2, 150, 70, win ? "#c9ffd8" : "#ffb3b3", win ? "#2cff7a" : "#ff3b3b");
  txt(ctx, win ? "Você derrotou o chefão e salvou a galáxia." : `Você chegou até a ${g.progressLabel.toLowerCase()}.`, W / 2, 220, 28, "#d7e3f5");
  txt(ctx, `PONTUAÇÃO ${g.totalScore}`, W / 2, 285, 38, AMBER, "center", FONT_T, 700);
  if (g.two) txt(ctx, `P1 ${g.players[0].score}  ·  P2 ${g.players[1].score}`, W / 2, 330, 24, MUTED);
  if (rank > 0) txt(ctx, rank === 1 ? "Novo recorde neste navegador!" : `${rank}º lugar no placar`, W / 2, 368, 24, "#7dff9a");
  drawItems(ctx, items, idx, 440, 62, 32);
}

// ---------- HUD
function bar(ctx, x, y, w, h, pct, color) {
  ctx.fillStyle = "rgba(6,12,28,.7)"; ctx.fillRect(x, y, w, h);
  ctx.fillStyle = color; ctx.fillRect(x, y, w * Math.max(0, Math.min(1, pct)), h);
  ctx.strokeStyle = "rgba(255,255,255,.75)"; ctx.lineWidth = 2; ctx.strokeRect(x, y, w, h);
}
function lifeIcons(ctx, x, y, n, dir, img) {
  const shown = Math.min(n, 8);
  for (let i = 0; i < shown; i++) {
    drawImg(ctx, img, x + dir * i * 26, y, 26);
    ctx.globalCompositeOperation = "lighter";
    drawImg(ctx, img, x + dir * i * 26, y, 26, 0, 0.8);
    ctx.globalCompositeOperation = "source-over";
  }
  if (n > 8) txt(ctx, "+" + (n - 8), x + dir * 8 * 26, y, 18, MUTED, dir > 0 ? "left" : "right");
}
function powerChips(ctx, g, p, x, y, dir) {
  const items = [];
  if (p.alive && p.upgraded(g.t)) items.push(["TIRO TRIPLO", p.upgradeUntil - g.t, CFG.upgradeMs, POWERUP_COLORS.upgrade]);
  if (p.alive && p.shielded(g.t)) items.push(["ESCUDO", p.shieldUntil - g.t, CFG.shieldMs, POWERUP_COLORS.shield]);
  if (p.alive && p.invul(g.t) && p.invulUntil - g.t > 0) items.push(["INVULNERÁVEL", p.invulUntil - g.t, 5000, POWERUP_COLORS.invul_gift]);
  items.forEach(([name, left, max, color], i) => {
    const cy = y + i * 26;
    const align = dir > 0 ? "left" : "right";
    txt(ctx, `${name} ${(left / 1000).toFixed(1)}s`, x, cy, 17, color, align, FONT_B, 700);
    const bx = dir > 0 ? x : x - 120;
    ctx.fillStyle = "rgba(255,255,255,.12)"; ctx.fillRect(bx, cy + 10, 120, 3);
    ctx.fillStyle = color; ctx.fillRect(bx, cy + 10, 120 * Math.min(1, left / max), 3);
  });
  if (p.alive && p.tele) {
    txt(ctx, p.n === 1 ? "T · TELEPORTE PRONTO" : "SHIFT · TELEPORTE PRONTO", x, y + items.length * 26, 17, POWERUP_COLORS.teleporter, dir > 0 ? "left" : "right", FONT_B, 700);
  }
}

export function drawHud(ctx, app) {
  const g = app.game;
  g.players.forEach((p, i) => {
    const left = i === 0;
    const x = left ? 20 : W - 270;
    const al = left ? "left" : "right";
    const ax = left ? x : x + 250;
    const hp = p.alive ? p.health : 0;
    bar(ctx, x, 20, 250, 20, hp / 100, hp > 50 ? "#27c25a" : hp > 25 ? "#e0a82a" : "#e04646");
    txt(ctx, `${g.two ? "P" + p.n + "  " : ""}${p.score}`, ax, 58, 28, "#fff", al, FONT_T, 700);
    lifeIcons(ctx, left ? x + 12 : x + 238, 90, p.lives, left ? 1 : -1, p.n === 2 ? imgs["player-p2"] : imgs.player);
    if (!p.alive) {
      const msg = p.lives > 0 ? `reaparece em ${Math.max(0, (p.respawnAt - g.t) / 1000).toFixed(1)}s` : "fora de jogo";
      txt(ctx, msg, ax, 122, 18, p.lives > 0 ? AMBER : RED, al, FONT_B, 700);
    }
    powerChips(ctx, g, p, ax, p.alive ? 122 : 146, left ? 1 : -1);
  });

  // centro: progresso da fase
  if (g.stage === "asteroids") {
    const pct = Math.min(1, g.totalScore / CFG.pointsToNextPhase);
    txt(ctx, "FASE 1 · ASTEROIDES", W / 2, 24, 20, MUTED, "center", FONT_B, 700);
    bar(ctx, W / 2 - 150, 42, 300, 12, pct, CYAN);
    txt(ctx, `${Math.min(g.totalScore, CFG.pointsToNextPhase)} / ${CFG.pointsToNextPhase}`, W / 2, 70, 18, "#d7e3f5");
  } else if (g.stage === "phase2") {
    txt(ctx, "FASE 2 · NAVES INIMIGAS", W / 2, 24, 20, MUTED, "center", FONT_B, 700);
    bar(ctx, W / 2 - 150, 42, 300, 12, g.killed / CFG.totalEnemiesPhase2, AMBER);
    txt(ctx, `${g.killed} / ${CFG.totalEnemiesPhase2} · onda ${g.wave}`, W / 2, 70, 18, "#d7e3f5");
  } else if (g.boss) {
    txt(ctx, "FASE 3 · CHEFÃO FINAL", W / 2, 24, 20, "#ffb0a0", "center", FONT_B, 700);
    bar(ctx, W / 2 - 220, 42, 440, 14, g.boss.health / g.boss.maxHealth, "#e04646");
    txt(ctx, `${Math.max(0, g.boss.health)} / ${g.boss.maxHealth}`, W / 2, 72, 18, "#d7e3f5");
  }

  if (g.two) {
    const a = g.players[0], b = g.players[1];
    if (!a.alive && b.alive && a.lives > 0) txt(ctx, "P2: pegue o powerup vermelho para trazer o P1 de volta", W / 2, H - 36, 22, RED, "center", FONT_B, 700);
    else if (!b.alive && a.alive && b.lives > 0) txt(ctx, "P1: pegue o powerup vermelho para trazer o P2 de volta", W / 2, H - 36, 22, RED, "center", FONT_B, 700);
  }

  // banner de fase
  if (g.banner) {
    const b = g.banner, total = b.until - b.from, e = g.t - b.from;
    const a = Math.min(1, e / 250, (total - e) / 400);
    ctx.globalAlpha = Math.max(0, a);
    glowText(ctx, b.title, W / 2, H * 0.36, 52, "#eaf6ff", "#2a9dff");
    if (b.sub) txt(ctx, b.sub, W / 2, H * 0.36 + 52, 26, AMBER);
    ctx.globalAlpha = 1;
  }

  // toast
  if (app.toast && performance.now() < app.toast.until) {
    panel(ctx, W / 2 - 150, H - 100, 300, 40, 0.8);
    txt(ctx, app.toast.text, W / 2, H - 80, 22, "#d7ffe3", "center", FONT_B, 700);
  }
}

// botões de toque / clique dentro do jogo
export const BTN_PAUSE = { x: W - 44, y: H - 44, r: 28 };
export const BTN_TELE = { x: W - 44, y: H - 112, r: 28 };
export function drawButtons(ctx, app) {
  const g = app.game;
  const round = (b, label, color) => {
    ctx.fillStyle = "rgba(6,12,28,.6)"; ctx.strokeStyle = color; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, 6.28); ctx.fill(); ctx.stroke();
    txt(ctx, label, b.x, b.y + 1, 22, color, "center", FONT_T, 700);
  };
  round(BTN_PAUSE, "II", "#9db0c9");
  const p1 = g.players[0];
  if (p1.alive && p1.tele) round(BTN_TELE, "T", POWERUP_COLORS.teleporter);
  // botão de som
  ctx.globalAlpha = 0.9;
  txt(ctx, app.audio.mudo ? "SOM: OFF" : "SOM: ON", 20, H - 28, 16, "#6f819e", "left", FONT_B, 700);
  ctx.globalAlpha = 1;
}
export const BTN_SOUND = { x: 20, y: H - 46, w: 100, h: 36 };

export function drawLoading(ctx, pct) {
  ctx.fillStyle = "#04060f"; ctx.fillRect(0, 0, W, H);
  txt(ctx, "NOVA DESCENT", W / 2, H / 2 - 50, 48, "#eaf6ff", "center", FONT_T, 800);
  ctx.fillStyle = "#1a2540"; ctx.fillRect(W / 2 - 160, H / 2 + 10, 320, 8);
  ctx.fillStyle = CYAN; ctx.fillRect(W / 2 - 160, H / 2 + 10, 320 * pct, 8);
  txt(ctx, "carregando…", W / 2, H / 2 + 44, 20, MUTED);
}

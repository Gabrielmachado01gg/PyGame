import { W, H, CFG, VOLUME_LABELS } from "./config.js";
import { carregarImagens, imgs } from "./assets.js";
import { Audio } from "./audio.js";
import { Input } from "./input.js";
import { Game } from "./game.js";
import * as store from "./storage.js";
import * as ui from "./ui.js";

const canvas = document.getElementById("jogo");
const ctx = canvas.getContext("2d");
canvas.width = W; canvas.height = H;

const audio = new Audio();
const input = new Input(canvas);
const app = { ctx, input, audio, game: null, toast: null, scene: "loading", mouse: false };

const state = { idx: 0, back: "title", endTimer: 0, rank: 0, loadPct: 0, volDrag: -1 };
const TITLE_BASE = ["Jogar 1 jogador", "Jogar 2 jogadores", "Continuar jogo salvo", "Controles", "Placar", "Volume"];
const PAUSE_ITEMS = ["Continuar", "Salvar jogo", "Carregar jogo", "Controles", "Volume", "Voltar ao menu"];
const END_ITEMS = ["Jogar de novo", "Voltar ao menu"];

function toast(text) { app.toast = { text, until: performance.now() + 1800 }; }
function go(scene, idx = 0) { app.scene = scene; state.idx = idx; }
const hasSave = () => !!store.load("save", null);

function titleItems() {
  return TITLE_BASE.map((l, i) => (i === 2 ? { label: l, disabled: !hasSave() } : l));
}

function startGame(two) {
  app.game.reset(two);
  state.endTimer = 0;
  go("play");
}
function loadGame() {
  const snap = store.load("save", null);
  if (snap && app.game.restore(snap)) { state.endTimer = 0; go("play"); return true; }
  toast("Nenhum jogo salvo");
  return false;
}
function saveGame() {
  toast(store.save("save", app.game.snapshot()) ? "Jogo salvo" : "Não foi possível salvar");
}
function recordRun() {
  const g = app.game;
  if (g.recorded || g.totalScore <= 0) return 0;
  g.recorded = true;
  const entry = {
    name: g.two ? "DUO" : "PLAYER1", score: g.totalScore,
    date: new Date().toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" }),
    progress: g.progressLabel, phases: g.phasesDone(), victory: g.end === "victory",
  };
  const top = store.addHighscore(entry);
  return top.indexOf(entry) + 1;
}

// ---- navegação genérica de listas (teclado + mouse/toque)
function listInput(ev, items, y0, step, onPick) {
  const n = items.length;
  const enabled = (i) => !(typeof items[i] === "object" && items[i].disabled);
  for (const k of ev.teclas) {
    if (k === "ArrowUp" || k === "KeyW") { do { state.idx = (state.idx - 1 + n) % n; } while (!enabled(state.idx)); }
    else if (k === "ArrowDown" || k === "KeyS") { do { state.idx = (state.idx + 1) % n; } while (!enabled(state.idx)); }
    else if (k === "Enter" || k === "NumpadEnter") onPick(state.idx);
  }
  const h = ui.hitItems(input.pointer, n, y0, step);
  if (h >= 0 && enabled(h)) {
    if (ev.moveu && input.pointer.type === "mouse") state.idx = h;
    if (ev.clique) { state.idx = h; onPick(h); }
  }
}

// ---- cenas
function sceneTitle(ev) {
  const items = titleItems();
  if (items[state.idx].disabled) state.idx = 0;
  listInput(ev, items, 250, 62, (i) => {
    if (items[i].disabled) return;
    if (i === 0) startGame(false);
    else if (i === 1) startGame(true);
    else if (i === 2) loadGame();
    else if (i === 3) { state.back = "title"; go("controls"); }
    else if (i === 4) go("scores");
    else if (i === 5) { state.back = "title"; go("volume"); }
  });
  app.game.update(16, []);
  ui.drawTitle(ctx, app, items, state.idx);
}

function sceneInfo(ev, draw, back, idx) {
  if (ev.teclas.some((k) => k === "Escape" || k === "Enter" || k === "NumpadEnter") || ev.clique) { go(back, idx); return; }
  draw();
}

function sceneVolume(ev) {
  const keys = ui.VOL_KEYS, n = keys.length;
  const rest = n; // índice de "Restaurar", rest+1 = "Voltar"
  const total = n + 2;
  for (const k of ev.teclas) {
    if (k === "ArrowUp" || k === "KeyW") state.idx = (state.idx - 1 + total) % total;
    else if (k === "ArrowDown" || k === "KeyS") state.idx = (state.idx + 1) % total;
    else if ((k === "ArrowLeft" || k === "ArrowRight") && state.idx < n) {
      audio.ajustar(keys[state.idx], k === "ArrowLeft" ? -0.05 : 0.05);
      if (["shoot", "explosion", "powerup"].includes(keys[state.idx])) audio.efeito(keys[state.idx]);
    } else if (k === "Enter" || k === "NumpadEnter") {
      if (state.idx === rest) audio.restaurar();
      else if (state.idx === rest + 1) { audio.salvar(); go(state.back, state.back === "pause" ? 4 : 5); return; }
    } else if (k === "Escape") { audio.salvar(); go(state.back, state.back === "pause" ? 4 : 5); return; }
  }
  const p = input.pointer;
  // barras: arrastar com mouse ou dedo
  if (p.down) {
    for (let i = 0; i < n; i++) {
      const r = ui.volRow(i);
      if (Math.abs(p.y - r.y) < 24 && p.x > r.barX - 14 && p.x < r.barX + r.barW + 14 && (state.volDrag < 0 || state.volDrag === i)) {
        state.volDrag = i; state.idx = i;
        audio.definir(keys[i], Math.round(((p.x - r.barX) / r.barW) * 20) / 20);
      }
    }
  } else if (state.volDrag >= 0) {
    const k = keys[state.volDrag];
    if (["shoot", "explosion", "powerup"].includes(k)) audio.efeito(k);
    audio.salvar(); state.volDrag = -1;
  }
  if (ev.clique) {
    const h = ui.hitItems(p, 2, 150 + rest * 56 + 14, 56);
    if (h === 0) audio.restaurar();
    else if (h === 1) { audio.salvar(); go(state.back, state.back === "pause" ? 4 : 5); return; }
  }
  app.game.update(16, []);
  ui.drawVolume(ctx, app, state.idx);
}

function controlsFor(g, ev) {
  const k = (c) => input.tecla(c);
  const c1 = { dx: (k("KeyD") - k("KeyA")) || 0, dy: (k("KeyS") - k("KeyW")) || 0, shoot: k("Space"), tp: ev.teclas.includes("KeyT") };
  const c2 = { dx: k("ArrowRight") - k("ArrowLeft"), dy: k("ArrowDown") - k("ArrowUp"), shoot: k("Enter") || k("ControlRight") || k("Numpad0"), tp: ev.teclas.includes("ShiftRight") };
  if (!g.two) {
    // sozinho: setas também movem e Enter também atira
    c1.dx += c2.dx; c1.dy += c2.dy; c1.shoot = c1.shoot || c2.shoot;
    c1.dx = Math.max(-1, Math.min(1, c1.dx)); c1.dy = Math.max(-1, Math.min(1, c1.dy));
  }
  const p = input.pointer;
  if (input.touchMode || app.mouse) {
    c1.follow = { x: p.x, y: p.y - (input.touchMode ? 70 : 0) };
    if (input.touchMode) c1.shoot = true; // no toque a nave atira sozinha
    else if (p.down) c1.shoot = true;
  } else if (p.down && p.type === "mouse") {
    // clique também atira no modo teclado
    c1.shoot = true;
  }
  return [c1, c2];
}

const inCircle = (p, b) => (p.x - b.x) ** 2 + (p.y - b.y) ** 2 <= (b.r + 6) ** 2;

function scenePlay(ev, dt) {
  const g = app.game;
  const p = input.pointer;
  for (const key of ev.teclas) {
    if (key === "Escape" || key === "KeyP") { go("pause"); return scenePause(ev, 0, true); }
    if (key === "KeyF") saveGame();
    if (key === "KeyL") { loadGame(); return; }
    if (key === "KeyM") { app.mouse = !app.mouse; toast(app.mouse ? "Mouse controla a nave" : "Teclado controla a nave"); }
  }
  if (ev.clique) {
    if (inCircle(p, ui.BTN_PAUSE)) { go("pause"); return scenePause(ev, 0, true); }
    if (g.players[0].alive && g.players[0].tele && inCircle(p, ui.BTN_TELE)) g.players[0].teleport(g);
    const s = ui.BTN_SOUND;
    if (p.x > s.x && p.x < s.x + s.w && p.y > s.y && p.y < s.y + s.h) audio.alternarMudo();
  }
  const ctrls = controlsFor(g, ev);
  g.update(dt, ctrls);
  if (g.end) {
    state.endTimer += dt;
    if (state.endTimer > (g.end === "victory" ? 2200 : 1500)) {
      state.rank = recordRun();
      go("end");
    }
  }
  drawWorld();
}

function drawWorld() {
  const g = app.game;
  g.draw(ctx);
  if (g.trans) ui.drawTransition(ctx, g);
  else { ui.drawHud(ctx, app); ui.drawButtons(ctx, app); }
}

function scenePause(ev, dt, fresh = false) {
  const g = app.game;
  if (!fresh) {
    if (ev.teclas.some((k) => k === "Escape" || k === "KeyP")) { go("play"); return; }
    listInput(ev, PAUSE_ITEMS, 235, 62, (i) => {
      if (i === 0) go("play");
      else if (i === 1) saveGame();
      else if (i === 2) loadGame();
      else if (i === 3) { state.back = "pause"; go("controls"); }
      else if (i === 4) { state.back = "pause"; go("volume"); }
      else if (i === 5) { recordRun(); go("title"); }
    });
  }
  if (app.scene !== "pause") return;
  drawWorld();
  ui.drawPause(ctx, PAUSE_ITEMS, state.idx);
}

function sceneEnd(ev) {
  const g = app.game;
  g.update(16, []);
  for (const k of ev.teclas) {
    if (k === "KeyR") { startGame(g.two); return; }
    if (k === "Escape") { go("title"); return; }
  }
  listInput(ev, END_ITEMS, 440, 62, (i) => { if (i === 0) startGame(g.two); else go("title"); });
  if (app.scene !== "end") return;
  g.draw(ctx);
  ui.drawEnd(ctx, app, END_ITEMS, state.idx, state.rank);
}

// ---- laço principal
let last = performance.now();
function frame(now) {
  const dt = Math.min(50, now - last);
  last = now;
  const ev = input.consumir();
  if (ev.teclas.length || ev.clique) audio.liberar();
  try {
    switch (app.scene) {
      case "loading": ui.drawLoading(ctx, state.loadPct); break;
      case "title": sceneTitle(ev); break;
      case "controls": app.game.update(16, []); sceneInfo(ev, () => ui.drawControls(ctx, app), state.back, state.back === "pause" ? 3 : 3); break;
      case "scores": app.game.update(16, []); sceneInfo(ev, () => ui.drawScores(ctx, app, store.load("highscores", [])), "title", 4); break;
      case "volume": sceneVolume(ev); break;
      case "play": scenePlay(ev, dt); break;
      case "pause": scenePause(ev, dt); break;
      case "end": sceneEnd(ev); break;
    }
  } catch (e) {
    console.error(e);
  }
  requestAnimationFrame(frame);
}

document.addEventListener("visibilitychange", () => {
  if (document.hidden && app.scene === "play") go("pause");
});

async function iniciar() {
  requestAnimationFrame(frame);
  try { await Promise.race([Promise.all([document.fonts.load("800 20px Orbitron"), document.fonts.load("600 20px Rajdhani")]), new Promise((r) => setTimeout(r, 2500))]); } catch {}
  await carregarImagens((p) => { state.loadPct = p * 0.8; });
  await audio.carregar();
  state.loadPct = 1;
  go("title");
  document.getElementById("carregando")?.remove();
}
// o jogo precisa existir antes do primeiro quadro das telas que o usam
app.game = new Game(audio);
iniciar();

if (new URLSearchParams(location.search).has("debug")) {
  window.__nd = { app, state, go, startGame, store, CFG };
}

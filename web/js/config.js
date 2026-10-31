// Constantes do jogo. Velocidades em pixels por frame a 60 fps (o motor converte por tempo).
export const W = 1280;
export const H = 720;

export const CFG = {
  maxMeteors: 8,
  pointsToNextPhase: 1500,
  initialLives: 3,
  totalEnemiesPhase2: 15,
  enemiesPerWave: 5,
  respawnMs: 3000,
  invulnAfterRespawnMs: 3000,
  playerSpeed: 6,
  playerShootDelay: 300,
  bulletSpeed: 12,
  enemyBulletDamage: 15,
  bossHealth: 80,
  upgradeMs: 15000,
  shieldMs: 8000,
  invulnMs: 5000,
  transitionMs: 3000,
};

export const PLANETS = {
  asteroids: [
    { img: "saturn", x: W - 550, y: 40, size: 420 },
    { img: "terra", x: 80, y: H - 420, size: 360 },
  ],
  phase2: [
    { img: "c3po", x: W - 400, y: 100, size: 300 },
    { img: "marte", x: 150, y: H - 300, size: 250 },
  ],
  phase3: [
    { img: "plutao", x: W / 2 - 100, y: 50, size: 200 },
    { img: "netuno", x: W - 200, y: H - 200, size: 150 },
  ],
};

export const IMAGES = ["blue-stars", "saturn", "terra", "c3po", "marte", "plutao", "netuno", "player", "bullert",
  "asteroid-1", "asteroid-2", "skill04", "skill06", "01", "02", "03", "04", "05", "06"];
export const SOUNDS = ["shoot", "explosion", "powerup"];
export const MUSIC = { asteroids: "phase1", phase2: "phase2", phase3: "phase3" };

export const DEFAULT_VOLUMES = { master: 0.7, music: 0.6, effects: 0.8, shoot: 0.7, explosion: 0.8, powerup: 0.4 };
export const VOLUME_LABELS = {
  master: "Volume geral", music: "Música", effects: "Efeitos", shoot: "Tiros", explosion: "Explosões", powerup: "Powerups",
};

export const POWERUP_COLORS = {
  revive: "#c81e1e", invul_gift: "#1e64c8", upgrade: "#dcc81e", extra_life: "#1ec83c", teleporter: "#b450b4", shield: "#64c8ff",
};
export const POWERUP_NAMES = {
  revive: "Reviver parceiro", invul_gift: "Invulnerável", upgrade: "Tiro triplo", extra_life: "Vida extra", teleporter: "Teleporte", shield: "Escudo",
};

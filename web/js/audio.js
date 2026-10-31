import { DEFAULT_VOLUMES, MUSIC, SOUNDS } from "./config.js";
import * as store from "./storage.js";

// Efeitos via Web Audio (sobrepõem sem cortar); música via <audio> em laço.
export class Audio {
  constructor() {
    this.volumes = { ...DEFAULT_VOLUMES, ...store.load("volumes", {}) };
    this.ctx = null;
    this.buffers = {};
    this.musica = null;
    this.faseAtual = null;
    this.liberado = false;
    this.mudo = !!store.load("mudo", false);
  }

  async carregar() {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return;
    this.ctx = new AC();
    await Promise.all(SOUNDS.map(async (nome) => {
      try {
        const resp = await fetch(`assets/audio/${nome}.mp3`);
        this.buffers[nome] = await this.ctx.decodeAudioData(await resp.arrayBuffer());
      } catch {
        this.buffers[nome] = null;
      }
    }));
  }

  // Navegadores só liberam áudio depois de um gesto do usuário.
  liberar() {
    if (this.liberado) return;
    this.liberado = true;
    this.ctx?.resume?.();
    if (this.faseAtual) this.tocarMusica(this.faseAtual);
  }

  volumeEfeito(tipo) {
    const v = this.volumes;
    return Math.min(1, v.master * v.effects * (v[tipo] ?? 1));
  }

  efeito(nome) {
    const buf = this.buffers[nome];
    if (!buf || !this.ctx || !this.liberado || this.mudo) return;
    const src = this.ctx.createBufferSource();
    const ganho = this.ctx.createGain();
    ganho.gain.value = this.volumeEfeito(nome);
    src.buffer = buf;
    src.connect(ganho).connect(this.ctx.destination);
    src.start();
  }

  tocarMusica(fase) {
    this.faseAtual = fase;
    if (!this.liberado) return;
    const arquivo = MUSIC[fase];
    if (!arquivo) return;
    this.musica?.pause();
    if (this.mudo) { this.musica = null; return; }
    this.musica = new window.Audio(`assets/audio/${arquivo}.mp3`);
    this.musica.loop = true;
    this.aplicarMusica();
    this.musica.play().catch(() => {});
  }

  alternarMudo() {
    this.mudo = !this.mudo;
    store.save("mudo", this.mudo);
    if (this.mudo) this.musica?.pause();
    else this.tocarMusica(this.faseAtual);
  }

  pararMusica() {
    this.musica?.pause();
  }

  aplicarMusica() {
    if (this.musica) this.musica.volume = Math.min(1, this.volumes.master * this.volumes.music);
  }

  ajustar(tipo, delta) {
    this.volumes[tipo] = Math.max(0, Math.min(1, Math.round((this.volumes[tipo] + delta) * 100) / 100));
    this.aplicarMusica();
  }

  definir(tipo, valor) {
    this.volumes[tipo] = Math.max(0, Math.min(1, valor));
    this.aplicarMusica();
  }

  restaurar() {
    this.volumes = { ...DEFAULT_VOLUMES };
    this.aplicarMusica();
    this.salvar();
  }

  salvar() {
    store.save("volumes", this.volumes);
  }
}

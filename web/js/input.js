import { W, H } from "./config.js";

// Teclado, mouse e toque. As teclas ficam em um Set para consulta contínua; os "toques" de menu viram eventos.
export class Input {
  constructor(canvas) {
    this.canvas = canvas;
    this.keys = new Set();
    this.pressed = []; // teclas pressionadas desde o último frame
    this.pointer = { x: W / 2, y: H - 120, down: false, type: "mouse", clicked: false, moved: false };
    this.touchMode = false;

    window.addEventListener("keydown", (e) => {
      if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Space"].includes(e.code)) e.preventDefault();
      if (!this.keys.has(e.code)) this.pressed.push(e.code);
      this.keys.add(e.code);
    });
    window.addEventListener("keyup", (e) => this.keys.delete(e.code));
    window.addEventListener("blur", () => this.keys.clear());

    canvas.addEventListener("pointermove", (e) => this.#mover(e));
    canvas.addEventListener("pointerdown", (e) => {
      this.#mover(e);
      this.pointer.down = true;
      this.pointer.clicked = true;
      if (e.pointerType === "touch") this.touchMode = true;
      canvas.setPointerCapture?.(e.pointerId);
    });
    const soltar = () => { this.pointer.down = false; };
    canvas.addEventListener("pointerup", soltar);
    canvas.addEventListener("pointercancel", soltar);
    canvas.addEventListener("contextmenu", (e) => e.preventDefault());
  }

  #mover(e) {
    const r = this.canvas.getBoundingClientRect();
    this.pointer.x = ((e.clientX - r.left) / r.width) * W;
    this.pointer.y = ((e.clientY - r.top) / r.height) * H;
    this.pointer.type = e.pointerType;
    this.pointer.moved = true;
  }

  tecla(code) { return this.keys.has(code); }

  // Consome as teclas pressionadas e o clique deste frame.
  consumir() {
    const teclas = this.pressed;
    const clique = this.pointer.clicked;
    const moveu = this.pointer.moved;
    this.pressed = [];
    this.pointer.clicked = false;
    this.pointer.moved = false;
    return { teclas, clique, moveu };
  }
}

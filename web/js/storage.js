// Persistência em localStorage. Tudo em try/catch: o navegador pode bloquear o armazenamento.
const PREFIX = "novadescent:";

export function load(key, fallback) {
  try {
    const raw = localStorage.getItem(PREFIX + key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

export function save(key, value) {
  try {
    localStorage.setItem(PREFIX + key, JSON.stringify(value));
    return true;
  } catch {
    return false;
  }
}

export function addHighscore(entry) {
  const lista = load("highscores", []);
  lista.push(entry);
  lista.sort((a, b) => b.score - a.score);
  const top = lista.slice(0, 10);
  save("highscores", top);
  return top;
}

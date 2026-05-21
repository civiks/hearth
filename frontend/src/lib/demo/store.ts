import {
  DEMO_STATE_VERSION,
  buildSeedState,
  type DemoState,
} from "./fixtures";

const STORAGE_KEY = "hs.demo.v1";

let state: DemoState = loadInitial();
let persistTimer: ReturnType<typeof setTimeout> | null = null;

function loadInitial(): DemoState {
  if (typeof localStorage === "undefined") return buildSeedState();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return seedAndPersist();
    const parsed = JSON.parse(raw) as DemoState;
    if (parsed.version !== DEMO_STATE_VERSION) return seedAndPersist();
    return parsed;
  } catch {
    return seedAndPersist();
  }
}

function seedAndPersist(): DemoState {
  const fresh = buildSeedState();
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(fresh));
  } catch {
    // ignore quota errors
  }
  return fresh;
}

export function getState(): DemoState {
  return state;
}

export function persist(): void {
  if (persistTimer) clearTimeout(persistTimer);
  persistTimer = setTimeout(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {
      // ignore quota errors
    }
  }, 200);
}

export function resetState(): void {
  state = buildSeedState();
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // ignore
  }
}

export function mutate<T>(fn: (s: DemoState) => T): T {
  const result = fn(state);
  persist();
  return result;
}

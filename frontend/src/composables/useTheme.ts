import { ref } from "vue";

export type Theme = "light" | "dark" | "system";
export type EffectiveTheme = "light" | "dark";

const STORAGE_KEY = "theme";

function readStored(): Theme {
  if (typeof window === "undefined") return "light";
  const stored = window.localStorage.getItem(STORAGE_KEY);
  if (stored === "light" || stored === "dark" || stored === "system") return stored;
  return "light";
}

function resolve(theme: Theme): EffectiveTheme {
  if (theme !== "system") return theme;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function apply(effective: EffectiveTheme) {
  const root = document.documentElement;
  root.classList.toggle("dark", effective === "dark");
  root.style.colorScheme = effective;
}

const theme = ref<Theme>(readStored());
const effectiveTheme = ref<EffectiveTheme>(
  typeof window === "undefined" ? "light" : resolve(theme.value),
);

let initialized = false;

function init() {
  if (initialized || typeof window === "undefined") return;
  initialized = true;
  apply(effectiveTheme.value);
  const media = window.matchMedia("(prefers-color-scheme: dark)");
  media.addEventListener("change", () => {
    if (theme.value !== "system") return;
    effectiveTheme.value = media.matches ? "dark" : "light";
    apply(effectiveTheme.value);
  });
}

function setTheme(next: Theme) {
  theme.value = next;
  window.localStorage.setItem(STORAGE_KEY, next);
  effectiveTheme.value = resolve(next);
  apply(effectiveTheme.value);
}

export function useTheme() {
  init();
  return { theme, effectiveTheme, setTheme };
}

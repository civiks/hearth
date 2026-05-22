function readToken(name: string): string {
  if (typeof window === "undefined") return "";
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return v ? `hsl(${v})` : "";
}

export function sequentialPalette(): string[] {
  return [
    readToken("--chart-1"),
    readToken("--chart-2"),
    readToken("--chart-3"),
    readToken("--chart-4"),
    readToken("--chart-5"),
  ].filter(Boolean);
}

export function categoricalPalette(): string[] {
  return [
    readToken("--chart-cat-1"),
    readToken("--chart-cat-2"),
    readToken("--chart-cat-3"),
    readToken("--chart-cat-4"),
    readToken("--chart-cat-5"),
  ].filter(Boolean);
}

export function paletteFor(kind: "sequential" | "categorical"): string[] {
  return kind === "categorical" ? categoricalPalette() : sequentialPalette();
}

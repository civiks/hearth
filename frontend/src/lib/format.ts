/** Format a backend-issued datetime string into a human-readable local string. */
export function formatDateTime(input: string | null | undefined): string {
  if (!input) return "";
  const d = new Date(input);
  if (Number.isNaN(d.getTime())) return input;
  return d.toLocaleString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

/** Format a backend-issued date string (YYYY-MM-DD) into a readable form. */
export function formatDate(input: string | null | undefined): string {
  if (!input) return "";
  const d = new Date(input);
  if (Number.isNaN(d.getTime())) return input;
  return d.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}

/** Two-letter uppercase initials for an avatar. */
export function initials(name: string | null | undefined): string {
  if (!name) return "";
  const words = name.trim().split(/\s+/);
  if (words.length >= 2) return ((words[0]![0] ?? "") + (words[1]![0] ?? "")).toUpperCase();
  return (words[0]!.slice(0, 2)).toUpperCase();
}

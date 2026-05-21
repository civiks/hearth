import type { components } from "./api-types";
import { ApiError } from "./api-error";
import { DEMO } from "./demo/flag";

export { ApiError };
export type User = components["schemas"]["LoginResponse"];
export type Role = "admin" | "professional" | "user";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  init?: RequestInit,
): Promise<T> {
  if (DEMO) {
    const { demoFetch } = await import("./demo/mockApi");
    return demoFetch<T>(method, path, body);
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    credentials: "include",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
    ...init,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = (await res.json()) as { detail?: string };
      if (data.detail) detail = data.detail;
    } catch {
      // not JSON, swallow
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  get: <T>(path: string, init?: RequestInit) => request<T>("GET", path, undefined, init),
  post: <T>(path: string, body?: unknown, init?: RequestInit) =>
    request<T>("POST", path, body, init),
  put: <T>(path: string, body?: unknown, init?: RequestInit) =>
    request<T>("PUT", path, body, init),
  delete: <T>(path: string, init?: RequestInit) => request<T>("DELETE", path, undefined, init),
};

export function homePathForRole(role: Role | string | null | undefined): string {
  switch (role) {
    case "admin":
      return "/admin/overview";
    case "professional":
      return "/professional/overview";
    case "user":
      return "/home/browse";
    default:
      return "/login";
  }
}

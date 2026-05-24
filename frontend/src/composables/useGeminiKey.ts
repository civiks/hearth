/**
 * Gemini key status — backed by the server, not localStorage.
 *
 * The raw key never leaves the backend after it's set. From the browser's
 * point of view the only observable state is a boolean: "is this user's
 * Gemini key configured?" Setting and clearing are POST/DELETE round trips.
 *
 * One module-level ref so every caller sees the same value. Refreshed when
 * the authenticated user changes (login, account switch) and after any
 * mutation. Pages that care should call `refresh()` on mount — there is no
 * automatic background polling.
 */

import { computed, ref, watch } from "vue";

import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

interface KeyStatus {
  configured: boolean;
}

// `null` until we've talked to the server. We expose this as `loaded` so
// callers can avoid flashing "Not configured" before the round-trip lands.
const _status = ref<KeyStatus | null>(null);
const _inflight = ref<Promise<void> | null>(null);

async function refresh(): Promise<void> {
  // Dedupe concurrent calls — multiple components mounting at once
  // shouldn't hammer the endpoint.
  if (_inflight.value) return _inflight.value;
  const p = (async () => {
    try {
      _status.value = await api.get<KeyStatus>("/api/users/me/gemini-key");
    } catch {
      // 401 (not logged in) or transient failure — treat as unknown.
      _status.value = null;
    } finally {
      _inflight.value = null;
    }
  })();
  _inflight.value = p;
  return p;
}

async function set(apiKey: string): Promise<void> {
  const trimmed = apiKey.trim();
  if (!trimmed) return;
  _status.value = await api.put<KeyStatus>("/api/users/me/gemini-key", {
    api_key: trimmed,
  });
}

async function clear(): Promise<void> {
  await api.delete<void>("/api/users/me/gemini-key");
  _status.value = { configured: false };
}

function reset(): void {
  _status.value = null;
  _inflight.value = null;
}

// Reset whenever the authenticated user changes (incl. logout). Done at
// module level so callers don't need to wire this up.
let _authWatcherInstalled = false;
function ensureAuthWatcher() {
  if (_authWatcherInstalled) return;
  _authWatcherInstalled = true;
  const auth = useAuthStore();
  watch(
    () => auth.user_id,
    () => {
      reset();
    },
  );
}

export function useGeminiKey() {
  ensureAuthWatcher();
  const hasKey = computed(() => _status.value?.configured === true);
  const loaded = computed(() => _status.value !== null);
  return { hasKey, loaded, refresh, set, clear };
}

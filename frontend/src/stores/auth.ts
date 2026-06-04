import { defineStore } from "pinia";

import { api, type User } from "@/lib/api";

interface State {
  user: User | null;
  loaded: boolean;
}

export const useAuthStore = defineStore("auth", {
  state: (): State => ({
    user: null,
    loaded: false,
  }),
  getters: {
    logged_in: (s) => s.user !== null,
    role: (s) => s.user?.role ?? null,
    user_id: (s) => s.user?.id ?? null,
    email: (s) => s.user?.email ?? null,
    full_name: (s) => s.user?.full_name ?? null,
    avatar_url: (s) => s.user?.avatar_url ?? null,
    address: (s) => s.user?.address ?? null,
    pincode: (s) => s.user?.pincode ?? null,
    service_id: (s) => s.user?.service_id ?? null,
    approval_status: (s) => s.user?.approval_status ?? null,
    is_blocked: (s) => s.user?.is_blocked ?? false,
  },
  actions: {
    setUser(user: User) {
      this.user = user;
      this.loaded = true;
    },
    updateUserDetails(patch: Partial<User>) {
      if (!this.user) return;
      this.user = { ...this.user, ...patch };
    },
    async hydrate() {
      try {
        const me = await api.get<User>("/api/auth/me");
        this.user = me;
      } catch {
        this.user = null;
      } finally {
        this.loaded = true;
      }
    },
    async logout() {
      try {
        await api.post<void>("/api/auth/logout");
      } catch {
        // server already cleared the cookie or never had one; safe to ignore
      }
      this.user = null;
    },
  },
});

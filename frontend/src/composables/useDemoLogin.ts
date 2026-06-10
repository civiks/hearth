import {
  Briefcase,
  ShieldCheck,
  UserCircle,
  type LucideIcon,
} from "@lucide/vue";
import { useRouter } from "vue-router";

import { ApiError, api, homePathForRole, type Role, type User } from "@/lib/api";
import { resetState } from "@/lib/demo/store";
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";

export interface DemoRole {
  label: string;
  value: Role;
  email: string;
  icon: LucideIcon;
}

export const DEMO_ROLES: DemoRole[] = [
  { label: "Customer", value: "user", email: "customer@demo.local", icon: UserCircle },
  { label: "Professional", value: "professional", email: "pro@demo.local", icon: Briefcase },
  { label: "Admin", value: "admin", email: "admin@demo.local", icon: ShieldCheck },
];

export function useDemoLogin() {
  const auth = useAuthStore();
  const router = useRouter();
  const toasts = useNotificationsStore();

  async function loginAs(role: Role): Promise<void> {
    const entry = DEMO_ROLES.find((r) => r.value === role);
    if (!entry) return;
    try {
      const user = await api.post<User>("/api/auth/login", {
        email: entry.email,
        password: "demo",
      });
      auth.setUser(user);
      router.push(homePathForRole(role));
    } catch (err) {
      toasts.error(
        "Demo login failed",
        err instanceof ApiError ? err.detail : "Unable to start the demo.",
      );
    }
  }

  async function resetDemoData(): Promise<void> {
    resetState();
    await auth.logout();
    router.push("/");
    setTimeout(() => location.reload(), 100);
  }

  return { DEMO_ROLES, loginAs, resetDemoData };
}

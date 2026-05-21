<template>
  <div class="fixed bottom-4 left-1/2 -translate-x-1/2 z-50">
    <DropdownMenu>
      <DropdownMenuTrigger as-child>
        <button
          type="button"
          class="bg-primary text-primary-foreground inline-flex items-center gap-2 h-10 pl-3 pr-2 text-xs font-medium shadow-lg hover:bg-[#0353e9] transition-colors"
          :aria-label="ariaLabel"
        >
          <span>
            Demo<span v-if="currentRoleLabel" class="font-normal opacity-85">
              · {{ currentRoleLabel }}</span>
          </span>
          <ChevronUp class="size-3.5" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="center" side="top" class="w-64">
        <DropdownMenuLabel>
          <div class="flex flex-col leading-tight">
            <span class="text-sm font-medium">Demo mode</span>
            <span class="text-xs text-muted-foreground">
              State persists in your browser only.
            </span>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuLabel
          class="text-[11px] uppercase tracking-wide text-muted-foreground font-normal"
        >
          Sign in as
        </DropdownMenuLabel>
        <DropdownMenuItem
          v-for="role in roles"
          :key="role.value"
          :class="auth.role === role.value ? 'bg-muted font-medium' : ''"
          @click="switchTo(role.value)"
        >
          <component :is="role.icon" class="mr-2 size-4" />
          {{ role.label }}
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          class="text-destructive focus:text-destructive"
          @click="reset"
        >
          <RotateCcw class="mr-2 size-4" />
          Reset demo data
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  </div>
</template>

<script lang="ts" setup>
import {
  Briefcase,
  ChevronUp,
  RotateCcw,
  ShieldCheck,
  UserCircle,
  type LucideIcon,
} from "lucide-vue-next";
import { computed } from "vue";
import { useRouter } from "vue-router";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { api, homePathForRole, type Role, type User } from "@/lib/api";
import { resetState } from "@/lib/demo/store";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();

interface RoleOption {
  label: string;
  value: Role;
  email: string;
  icon: LucideIcon;
}

const roles: RoleOption[] = [
  { label: "Customer", value: "user", email: "customer@demo.local", icon: UserCircle },
  { label: "Professional", value: "professional", email: "pro@demo.local", icon: Briefcase },
  { label: "Admin", value: "admin", email: "admin@demo.local", icon: ShieldCheck },
];

const currentRoleLabel = computed(() => {
  const r = roles.find((x) => x.value === auth.role);
  return r?.label ?? null;
});

const ariaLabel = computed(() =>
  currentRoleLabel.value
    ? `Demo mode (signed in as ${currentRoleLabel.value}) — click to switch role`
    : "Demo mode — click to sign in",
);

async function switchTo(role: Role) {
  const entry = roles.find((r) => r.value === role);
  if (!entry) return;
  try {
    const user = await api.post<User>("/api/auth/login", {
      email: entry.email,
      password: "demo",
    });
    auth.setUser(user);
    router.push(homePathForRole(role));
  } catch (err) {
    console.error("demo role switch failed", err);
  }
}

async function reset() {
  resetState();
  await auth.logout();
  router.push("/");
  setTimeout(() => location.reload(), 100);
}
</script>

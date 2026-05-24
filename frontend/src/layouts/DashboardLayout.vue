<template>
  <div class="flex h-screen flex-col bg-background">
    <!-- Dark global top bar — brand on the left, user menu on the right -->
    <header
      class="vt-topbar flex h-12 shrink-0 items-center justify-between bg-surface-inverse px-6 text-surface-inverse-foreground relative z-20"
    >
      <RouterLink to="/" class="vt-brand flex items-center gap-2 shrink-0">
        <BrandMark class="h-4 w-auto" />
        <span class="font-semibold text-base tracking-tight">hearth</span>
      </RouterLink>

      <div class="flex items-center gap-2">
        <button
          type="button"
          :aria-pressed="chat.open"
          aria-label="Ask AI"
          class="flex items-center gap-2 h-7 pl-3 pr-2 rounded-full text-xs font-medium text-surface-inverse-foreground transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-surface-inverse-foreground/60 focus-visible:ring-offset-2 focus-visible:ring-offset-surface-inverse"
          :class="
            chat.open
              ? 'bg-surface-inverse-foreground/20'
              : 'bg-surface-inverse-foreground/10 hover:bg-surface-inverse-foreground/20'
          "
          @click="chat.toggle()"
        >
          Ask
          <AiMark class="size-4" />
        </button>

        <DropdownMenu :modal="false">
          <DropdownMenuTrigger as-child>
            <button
              type="button"
              class="flex items-center gap-2 px-2 py-1 transition hover:bg-surface-inverse-foreground/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-surface-inverse-foreground/60 focus-visible:ring-offset-2 focus-visible:ring-offset-surface-inverse"
            >
              <Avatar class="size-6">
                <AvatarFallback class="bg-primary text-primary-foreground text-[10px]">
                  {{ initials(auth.full_name) }}
                </AvatarFallback>
              </Avatar>
              <span class="hidden sm:inline text-xs">{{ auth.email }}</span>
              <span class="sm:hidden text-xs">{{ firstName }}</span>
              <ChevronDown class="size-3.5 opacity-70" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" class="w-56">
            <DropdownMenuLabel>
              <div class="flex flex-col leading-tight">
                <span class="text-sm font-medium">{{ auth.full_name }}</span>
                <span class="text-xs text-muted-foreground">{{ auth.email }}</span>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem @click="$router.push('/account')">
              <UserCircle class="mr-2 size-4" />
              Account
            </DropdownMenuItem>
            <DropdownMenuItem @click="$router.push('/settings')">
              <Settings class="mr-2 size-4" />
              Settings
            </DropdownMenuItem>
            <DropdownMenuSub>
              <DropdownMenuSubTrigger>
                <component :is="themeIcon" class="mr-2 size-4" />
                Theme
              </DropdownMenuSubTrigger>
              <DropdownMenuSubContent class="w-40">
                <DropdownMenuRadioGroup
                  :model-value="theme"
                  @update:model-value="(v) => setTheme(v as Theme)"
                >
                  <DropdownMenuRadioItem value="light">
                    <Sun class="mr-2 size-4" />
                    Light
                  </DropdownMenuRadioItem>
                  <DropdownMenuRadioItem value="dark">
                    <Moon class="mr-2 size-4" />
                    Dark
                  </DropdownMenuRadioItem>
                  <DropdownMenuRadioItem value="system">
                    <Monitor class="mr-2 size-4" />
                    System
                  </DropdownMenuRadioItem>
                </DropdownMenuRadioGroup>
              </DropdownMenuSubContent>
            </DropdownMenuSub>
            <DropdownMenuSub v-if="DEMO">
              <DropdownMenuSubTrigger>
                <Repeat class="mr-2 size-4" />
                Switch role
              </DropdownMenuSubTrigger>
              <DropdownMenuSubContent class="w-44">
                <DropdownMenuRadioGroup
                  :model-value="auth.role ?? ''"
                  @update:model-value="(v) => loginAs(v as Role)"
                >
                  <DropdownMenuRadioItem
                    v-for="r in DEMO_ROLES"
                    :key="r.value"
                    :value="r.value"
                  >
                    <component :is="r.icon" class="mr-2 size-4" />
                    {{ r.label }}
                  </DropdownMenuRadioItem>
                </DropdownMenuRadioGroup>
              </DropdownMenuSubContent>
            </DropdownMenuSub>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              v-if="DEMO"
              @click="resetDemoData"
            >
              <RotateCcw class="mr-2 size-4" />
              Reset demo data
            </DropdownMenuItem>
            <DropdownMenuItem
              variant="destructive"
              @click="handleLogout"
            >
              <LogOut class="mr-2 size-4" />
              Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
    <main class="flex-1 min-h-0 overflow-y-auto">
      <slot />
    </main>
    <ChatWidget />
  </div>
</template>

<script lang="ts" setup>
import {
  ChevronDown,
  LogOut,
  Monitor,
  Moon,
  Repeat,
  RotateCcw,
  Settings,
  Sun,
  UserCircle,
} from "lucide-vue-next";
import { computed } from "vue";
import { RouterLink, useRouter } from "vue-router";

import AiMark from "@/components/AiMark.vue";
import BrandMark from "@/components/BrandMark.vue";
import ChatWidget from "@/components/ChatWidget.vue";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useDemoLogin, DEMO_ROLES } from "@/composables/useDemoLogin";
import { useTheme, type Theme } from "@/composables/useTheme";
import { type Role } from "@/lib/api";
import { DEMO } from "@/lib/demo/flag";
import { initials } from "@/lib/format";
import { useAuthStore } from "@/stores/auth";
import { useChatStore } from "@/stores/chat";

const router = useRouter();
const auth = useAuthStore();
const chat = useChatStore();
const { theme, effectiveTheme, setTheme } = useTheme();
const { loginAs, resetDemoData } = useDemoLogin();

const firstName = computed(() => auth.full_name?.split(" ")[0] ?? "");

const themeIcon = computed(() => {
  if (theme.value === "system") return Monitor;
  return effectiveTheme.value === "dark" ? Moon : Sun;
});

async function handleLogout() {
  await auth.logout();
  router.push("/");
}
</script>

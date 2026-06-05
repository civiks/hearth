<template>
  <header
    :class="[
      'vt-topbar shrink-0 bg-surface-inverse text-surface-inverse-foreground border-b border-surface-inverse-foreground/10 sm:border-b-0 z-30',
      isDesktop ? 'relative' : 'sticky top-0 transition-transform duration-300 ease-out will-change-transform',
      !isDesktop && headerHidden && '-translate-y-full',
    ]"
  >
    <div class="mx-auto w-full max-w-[1440px] flex h-14 items-center justify-between px-6">
    <RouterLink to="/" class="vt-brand flex items-center gap-2.5 shrink-0">
      <BrandMark class="h-5 w-auto" />
      <span class="brand-wordmark font-semibold text-lg tracking-tight">hearth</span>
    </RouterLink>

    <div class="flex items-center gap-2">
      <button
        type="button"
        aria-label="Ask AI"
        class="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-inverse-foreground/10 hover:bg-surface-inverse-foreground/20 active:bg-surface-inverse-foreground/30 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-surface-inverse-foreground/60 focus-visible:ring-offset-2 focus-visible:ring-offset-surface-inverse text-xs font-medium"
        @click="chat.toggle()"
      >
        <span>Ask</span>
        <AiMark class="size-3.5" />
      </button>

      <DropdownMenu v-if="isDesktop" :modal="false">
        <DropdownMenuTrigger as-child>
          <button
            type="button"
            class="flex items-center gap-2 px-2 py-1 rounded-full transition hover:bg-surface-inverse-foreground/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-surface-inverse-foreground/60 focus-visible:ring-offset-2 focus-visible:ring-offset-surface-inverse"
          >
            <Avatar :name="auth.full_name ?? ''" :src="auth.avatar_url" size="size-6" fallback-class="text-[10px]" />
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
          <DropdownMenuItem @click="settingsDrawer.show()">
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
          <DropdownMenuItem v-if="DEMO" @click="resetDemoData">
            <RotateCcw class="mr-2 size-4" />
            Reset demo data
          </DropdownMenuItem>
          <DropdownMenuItem variant="destructive" @click="handleLogout">
            <LogOut class="mr-2 size-4" />
            Sign out
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <div class="flex items-center gap-1.5 px-2 py-1.5 text-[11px] text-muted-foreground">
            <button class="hover:text-foreground transition-colors" @click="$router.push('/privacy')">Privacy policy</button>
            <span>·</span>
            <button class="hover:text-foreground transition-colors" @click="$router.push('/terms')">Terms of service</button>
          </div>
        </DropdownMenuContent>
      </DropdownMenu>

      <template v-else>
        <button
          type="button"
          class="flex items-center gap-2 px-2 py-1 rounded-full transition hover:bg-surface-inverse-foreground/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-surface-inverse-foreground/60 focus-visible:ring-offset-2 focus-visible:ring-offset-surface-inverse"
          @click="menuOpen = true"
        >
          <Avatar :name="auth.full_name ?? ''" :src="auth.avatar_url" size="size-6" fallback-class="text-[10px]" />
          <ChevronDown class="size-3.5 opacity-70" />
        </button>

        <Drawer v-model:open="menuOpen" should-scale-background>
          <DrawerContent>
            <div class="flex items-center gap-2.5 px-4 pt-4 pb-3">
              <button class="flex items-center gap-2.5 min-w-0 flex-1 text-left" @click="navigate('/account')">
                <Avatar :name="auth.full_name ?? ''" :src="auth.avatar_url" size="size-8 shrink-0" fallback-class="text-xs" />
                <div class="flex flex-col leading-tight min-w-0">
                  <span class="text-sm font-semibold tracking-tight truncate">{{ auth.full_name }}</span>
                  <span class="text-xs tracking-tight text-muted-foreground truncate">{{ auth.email }}</span>
                </div>
              </button>
              <div class="flex items-center gap-0.5 shrink-0">
                <button
                  class="p-2 rounded-md text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
                  aria-label="Account"
                  @click="navigate('/account')"
                >
                  <UserCircle class="size-5" />
                </button>
                <button
                  class="p-2 rounded-md text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
                  aria-label="Settings"
                  @click="menuOpen = false; settingsDrawer.show()"
                >
                  <Settings class="size-5" />
                </button>
                <button
                  v-if="auth.role === 'admin'"
                  class="p-2 rounded-md text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
                  aria-label="Tools"
                  @click="navigate('/admin/tools')"
                >
                  <Hammer class="size-5" />
                </button>
              </div>
            </div>

            <div class="overflow-y-auto p-1.5 pb-3">
              <div class="h-px bg-border -mx-1.5 mb-1.5" />

              <div class="text-muted-foreground px-3 pt-2 pb-1.5 text-[11px] font-medium uppercase tracking-wider">Theme</div>
              <button
                v-for="t in themeOptions"
                :key="t.value"
                class="w-full flex items-center gap-2.5 rounded-md px-3 py-2.5 text-sm font-medium tracking-tight hover:bg-accent transition-colors"
                :class="theme === t.value ? 'bg-accent/60 text-accent-foreground' : ''"
                @click="setTheme(t.value as Theme)"
              >
                <component :is="t.icon" class="size-4" :class="theme === t.value ? '' : 'text-muted-foreground'" />
                {{ t.label }}
                <Check v-if="theme === t.value" class="ml-auto size-3.5 text-primary" />
              </button>

              <template v-if="DEMO">
                <div class="text-muted-foreground px-3 pt-3 pb-1.5 text-[11px] font-medium uppercase tracking-wider">Switch role</div>
                <button
                  v-for="r in DEMO_ROLES"
                  :key="r.value"
                  class="w-full flex items-center gap-2.5 rounded-md px-3 py-2.5 text-sm font-medium tracking-tight hover:bg-accent transition-colors"
                  :class="auth.role === r.value ? 'bg-accent/60 text-accent-foreground' : ''"
                  @click="menuOpen = false; loginAs(r.value as Role)"
                >
                  <component :is="r.icon" class="size-4" :class="auth.role === r.value ? '' : 'text-muted-foreground'" />
                  {{ r.label }}
                  <Check v-if="auth.role === r.value" class="ml-auto size-3.5 text-primary" />
                </button>
              </template>

              <div class="h-px bg-border -mx-1.5 mt-1.5 mb-1.5" />

              <button
                v-if="DEMO"
                class="w-full flex items-center gap-2.5 rounded-md px-3 py-2.5 text-sm font-medium tracking-tight hover:bg-accent transition-colors"
                @click="resetDemoData"
              >
                <RotateCcw class="size-4 text-muted-foreground" />
                Reset demo data
              </button>
              <button
                class="w-full flex items-center gap-2.5 rounded-md px-3 py-2.5 text-sm font-medium tracking-tight text-destructive hover:bg-destructive/10 transition-colors"
                @click="handleLogout"
              >
                <LogOut class="size-4" />
                Sign out
              </button>

              <div class="h-px bg-border -mx-1.5 mt-1.5 mb-1.5" />

              <div class="flex items-center gap-1.5 px-3 py-2 text-xs text-muted-foreground">
                <button class="hover:text-foreground transition-colors" @click="navigate('/privacy')">Privacy policy</button>
                <span>·</span>
                <button class="hover:text-foreground transition-colors" @click="navigate('/terms')">Terms of service</button>
              </div>
            </div>
          </DrawerContent>
        </Drawer>
      </template>
    </div>
    </div>
  </header>
</template>

<script lang="ts" setup>
import { useMediaQuery, useScroll } from "@vueuse/core";
import {
  Check,
  ChevronDown,
  Hammer,
  LogOut,
  Monitor,
  Moon,
  Repeat,
  RotateCcw,
  Settings,
  Sun,
  UserCircle,
} from "lucide-vue-next";
import { computed, ref, watch } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

import AiMark from "@/components/AiMark.vue";
import Avatar from "@/components/Avatar.vue";
import BrandMark from "@/components/BrandMark.vue";
import { Drawer, DrawerContent } from "@/components/ui/drawer";
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
import { DEMO_ROLES, useDemoLogin } from "@/composables/useDemoLogin";
import { useSettingsDrawer } from "@/composables/useSettingsDrawer";
import { useTheme, type Theme } from "@/composables/useTheme";
import { type Role } from "@/lib/api";
import { DEMO } from "@/lib/demo/flag";
import { useAuthStore } from "@/stores/auth";
import { useChatStore } from "@/stores/chat";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();
const chat = useChatStore();
const { theme, effectiveTheme, setTheme } = useTheme();
const { loginAs, resetDemoData } = useDemoLogin();
const settingsDrawer = useSettingsDrawer();

const isDesktop = useMediaQuery("(min-width: 640px)");
const menuOpen = ref(false);

const { y: windowY } = useScroll(window, { throttle: 80 });
const headerHidden = ref(false);
let lastScrollY = 0;
watch(windowY, (y) => {
  if (isDesktop.value || y < 64) {
    headerHidden.value = false;
    lastScrollY = y;
    return;
  }
  const delta = y - lastScrollY;
  if (Math.abs(delta) < 6) return;
  headerHidden.value = delta > 0;
  lastScrollY = y;
});

watch(
  () => route.path,
  () => {
    headerHidden.value = false;
    lastScrollY = 0;
  },
);

const themeIcon = computed(() => {
  if (theme.value === "system") return Monitor;
  return effectiveTheme.value === "dark" ? Moon : Sun;
});

const themeOptions = [
  { value: "light", label: "Light", icon: Sun },
  { value: "dark", label: "Dark", icon: Moon },
  { value: "system", label: "System", icon: Monitor },
] as const;

function navigate(path: string) {
  menuOpen.value = false;
  router.push(path);
}

async function handleLogout() {
  menuOpen.value = false;
  await auth.logout();
  router.push("/");
}
</script>

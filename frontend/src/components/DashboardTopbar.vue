<template>
  <header
    :class="[
      'vt-topbar shrink-0 bg-background bg-gradient-to-b from-primary/8 to-background border-b border-border sm:border-b-0 text-foreground z-30',
      isDesktop ? 'relative' : 'sticky top-0 transition-transform duration-300 ease-out will-change-transform',
      !isDesktop && headerHidden && '-translate-y-full',
    ]"
  >
    <div class="relative mx-auto w-full max-w-[1440px] flex h-14 items-center justify-between gap-3 px-6">
    <RouterLink to="/" class="flex items-center gap-2.5 shrink-0">
      <BrandMark class="vt-brand h-6 w-auto" />
      <span class="font-display font-semibold text-lg tracking-tight" :class="isCustomer ? 'hidden sm:inline' : ''">hearth</span>
    </RouterLink>

    <ServiceSearch v-if="isCustomer" />

    <div class="flex items-center gap-2 shrink-0">
      <button
        type="button"
        aria-label="Ask AI"
        class="hidden sm:flex items-center gap-1.5 h-9 px-4 rounded-full bg-foreground/8 hover:bg-foreground/12 active:bg-foreground/18 press transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background text-sm font-medium"
        @click="chat.toggle()"
      >
        <span>Ask</span>
        <AiMark class="size-4" />
      </button>

      <DropdownMenu v-if="isDesktop" :modal="false">
        <DropdownMenuTrigger as-child>
          <button
            type="button"
            class="flex items-center gap-2 px-2 py-1 rounded-full press transition hover:bg-foreground/8 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
          >
            <Avatar :name="auth.full_name ?? ''" :src="auth.avatar_url" size="size-8" fallback-class="text-xs" />
            <PhCaretDown class="size-3.5 opacity-70" weight="bold" />
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
            <PhUserCircle class="mr-2 size-4" weight="bold" />
            Account
          </DropdownMenuItem>
          <DropdownMenuItem @click="settingsDrawer.show()">
            <PhGear class="mr-2 size-4" weight="bold" />
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
                  <PhSun class="mr-2 size-4" weight="bold" />
                  Light
                </DropdownMenuRadioItem>
                <DropdownMenuRadioItem value="dark">
                  <PhMoon class="mr-2 size-4" weight="bold" />
                  Dark
                </DropdownMenuRadioItem>
                <DropdownMenuRadioItem value="system">
                  <PhMonitor class="mr-2 size-4" weight="bold" />
                  System
                </DropdownMenuRadioItem>
              </DropdownMenuRadioGroup>
            </DropdownMenuSubContent>
          </DropdownMenuSub>
          <DropdownMenuSub v-if="DEMO">
            <DropdownMenuSubTrigger>
              <PhRepeat class="mr-2 size-4" weight="bold" />
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
          <DropdownMenuItem v-if="DEMO" @click="handleResetDemo">
            <PhArrowCounterClockwise class="mr-2 size-4" weight="bold" />
            Reset demo data
          </DropdownMenuItem>
          <DropdownMenuItem variant="destructive" @click="handleLogout">
            <PhSignOut class="mr-2 size-4" weight="bold" />
            Sign out
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <div class="flex items-center gap-1.5 px-2 py-1.5 text-[11px] text-muted-foreground">
            <button class="hover:text-foreground press transition-colors" @click="$router.push('/privacy')">Privacy policy</button>
            <span>·</span>
            <button class="hover:text-foreground press transition-colors" @click="$router.push('/terms')">Terms of service</button>
          </div>
        </DropdownMenuContent>
      </DropdownMenu>

      <template v-else>
        <button
          type="button"
          class="flex items-center gap-2 px-2 py-1 rounded-full press transition hover:bg-foreground/8 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
          @click="menuOpen = true"
        >
          <Avatar :name="auth.full_name ?? ''" :src="auth.avatar_url" size="size-8" fallback-class="text-xs" />
        </button>

        <Drawer v-model:open="menuOpen">
          <DrawerContent>
            <div class="flex items-center gap-3 px-5 pt-3 pb-3 pr-14 shrink-0">
              <button class="flex items-center gap-3 min-w-0 flex-1 text-left press" @click="navigate('/account')">
                <Avatar :name="auth.full_name ?? ''" :src="auth.avatar_url" size="size-10 shrink-0" fallback-class="text-sm" />
                <div class="flex flex-col leading-tight min-w-0">
                  <span class="flex items-center gap-1 text-base font-semibold tracking-tight min-w-0">
                    <span class="truncate">{{ auth.full_name }}</span>
                    <PhCaretDown class="size-3.5 shrink-0 text-muted-foreground" weight="bold" />
                  </span>
                  <span class="text-sm tracking-tight text-muted-foreground truncate">{{ auth.email }}</span>
                </div>
              </button>
            </div>

            <div class="flex-1 min-h-0 overflow-y-auto px-2.5 pb-3 scroll-fade-y">
              <div class="h-px bg-border/50 mx-3 mb-2" />

              <div class="flex items-center justify-between gap-3 px-3 py-2">
                <span class="text-[15px] font-medium tracking-tight">Theme</span>
                <div class="flex items-center gap-0.5 rounded-full bg-foreground/6 p-1">
                  <button
                    v-for="t in themeOptions"
                    :key="t.value"
                    :aria-label="t.label"
                    :aria-pressed="theme === t.value"
                    class="flex h-8 items-center justify-center gap-1.5 rounded-full text-[13px] font-medium tracking-tight press transition-colors"
                    :class="theme === t.value ? 'bg-card text-foreground soft-card px-3 dark:bg-foreground/10 dark:shadow-none' : 'text-muted-foreground hover:text-foreground w-8'"
                    @click="setTheme(t.value as Theme)"
                  >
                    <component :is="t.icon" class="size-[1.1rem] shrink-0" weight="bold" />
                    <span v-if="theme === t.value">{{ t.label }}</span>
                  </button>
                </div>
              </div>

              <div v-if="DEMO" class="flex items-center justify-between gap-3 px-3 py-2">
                <span class="text-[15px] font-medium tracking-tight shrink-0">Role</span>
                <div class="flex items-center gap-0.5 rounded-full bg-foreground/6 p-1">
                  <button
                    v-for="r in DEMO_ROLES"
                    :key="r.value"
                    :aria-label="r.label"
                    :aria-pressed="auth.role === r.value"
                    class="flex h-8 items-center justify-center gap-1.5 rounded-full text-[13px] font-medium tracking-tight press transition-colors"
                    :class="auth.role === r.value ? 'bg-card text-foreground soft-card px-3 dark:bg-foreground/10 dark:shadow-none' : 'text-muted-foreground hover:text-foreground w-8'"
                    @click="menuOpen = false; loginAs(r.value as Role)"
                  >
                    <component :is="r.icon" class="size-[1.1rem] shrink-0" weight="bold" />
                    <span v-if="auth.role === r.value">{{ r.label }}</span>
                  </button>
                </div>
              </div>

              <div class="h-px bg-border/50 mx-3 my-2" />

              <button
                v-if="DEMO"
                class="w-full flex items-center gap-3 rounded-xl px-3 py-3 text-[15px] font-medium tracking-tight hover:bg-accent press transition-colors"
                @click="handleResetDemo"
              >
                <PhArrowCounterClockwise class="size-5 text-muted-foreground" weight="bold" />
                Reset demo data
              </button>
              <button
                v-if="auth.role === 'admin'"
                class="w-full flex items-center gap-3 rounded-xl px-3 py-3 text-[15px] font-medium tracking-tight hover:bg-accent press transition-colors"
                @click="navigate('/admin/tools')"
              >
                <PhHammer class="size-5 text-muted-foreground" weight="bold" />
                Tools
              </button>
              <button
                class="w-full flex items-center gap-3 rounded-xl px-3 py-3 text-[15px] font-medium tracking-tight hover:bg-accent press transition-colors"
                @click="menuOpen = false; settingsDrawer.show()"
              >
                <PhGear class="size-5 text-muted-foreground" weight="bold" />
                Settings
              </button>
              <button
                class="w-full flex items-center gap-3 rounded-xl px-3 py-3 text-[15px] font-medium tracking-tight text-destructive hover:bg-destructive/10 press transition-colors"
                @click="handleLogout"
              >
                <PhSignOut class="size-5" weight="bold" />
                Sign out
              </button>

              <div class="h-px bg-border/50 mx-3 my-2" />

              <div class="flex items-center gap-1.5 px-3 py-2 text-xs text-muted-foreground">
                <button class="hover:text-foreground press transition-colors" @click="navigate('/privacy')">Privacy policy</button>
                <span>·</span>
                <button class="hover:text-foreground press transition-colors" @click="navigate('/terms')">Terms of service</button>
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
  PhCaretDown,
  PhHammer,
  PhSignOut,
  PhMonitor,
  PhMoon,
  PhRepeat,
  PhArrowCounterClockwise,
  PhGear,
  PhSun,
  PhUserCircle,
} from '@phosphor-icons/vue';
import { computed, ref, watch } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

import AiMark from "@/components/AiMark.vue";
import Avatar from "@/components/Avatar.vue";
import BrandMark from "@/components/BrandMark.vue";
import ServiceSearch from "@/components/marketplace/ServiceSearch.vue";
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
import { useConfirm } from "@/composables/useConfirm";
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
const { confirm, pending, settle } = useConfirm();
const settingsDrawer = useSettingsDrawer();

const isDesktop = useMediaQuery("(min-width: 640px)");
const menuOpen = ref(false);

watch(menuOpen, (open) => {
  if (!open && pending.value) settle(false);
});

const isCustomer = computed(() => auth.role === "user");

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
  if (theme.value === "system") return PhMonitor;
  return effectiveTheme.value === "dark" ? PhMoon : PhSun;
});

const themeOptions = [
  { value: "light", label: "Light", icon: PhSun },
  { value: "dark", label: "Dark", icon: PhMoon },
  { value: "system", label: "System", icon: PhMonitor },
] as const;

function navigate(path: string) {
  menuOpen.value = false;
  router.push(path);
}

async function handleLogout() {
  if (!await confirm({
    title: "Sign out?",
    description: "You'll be signed out of your account. You can sign back in anytime.",
    confirmLabel: "Sign out",
  })) return;
  menuOpen.value = false;
  await auth.logout();
  router.push("/");
}

async function handleResetDemo() {
  if (!await confirm({
    title: "Reset demo data?",
    description: "This restores the demo to its original state — any bookings, edits, or accounts you changed will be discarded.",
    variant: "destructive",
    confirmLabel: "Reset demo",
  })) return;
  menuOpen.value = false;
  resetDemoData();
}
</script>

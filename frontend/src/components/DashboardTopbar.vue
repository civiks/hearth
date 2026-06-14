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

    <form
      v-if="isCustomer"
      class="flex flex-1 min-w-0 max-w-md sm:mx-6 items-center gap-2 h-9 px-3 rounded-full bg-foreground/6 focus-within:bg-foreground/8 focus-within:ring-2 focus-within:ring-ring transition-colors"
      role="search"
      @submit.prevent="submitSearch"
    >
      <PhMagnifyingGlass class="size-4 shrink-0 text-muted-foreground" weight="bold" />
      <input
        v-model="searchText"
        type="search"
        placeholder="Search services"
        aria-label="Search services"
        class="min-w-0 flex-1 bg-transparent text-sm placeholder:text-muted-foreground focus:outline-none"
        @keydown.enter.prevent="submitSearch"
      />
    </form>

    <div class="flex items-center gap-2 shrink-0">
      <button
        type="button"
        aria-label="Ask AI"
        class="hidden sm:flex items-center gap-1.5 h-9 px-4 rounded-full bg-foreground/8 hover:bg-foreground/12 active:bg-foreground/18 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background text-sm font-medium"
        @click="chat.toggle()"
      >
        <span>Ask</span>
        <AiMark class="size-4" />
      </button>

      <DropdownMenu v-if="isDesktop" :modal="false">
        <DropdownMenuTrigger as-child>
          <button
            type="button"
            class="flex items-center gap-2 px-2 py-1 rounded-full transition hover:bg-foreground/8 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
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
            <button class="hover:text-foreground transition-colors" @click="$router.push('/privacy')">Privacy policy</button>
            <span>·</span>
            <button class="hover:text-foreground transition-colors" @click="$router.push('/terms')">Terms of service</button>
          </div>
        </DropdownMenuContent>
      </DropdownMenu>

      <template v-else>
        <button
          type="button"
          class="flex items-center gap-2 px-2 py-1 rounded-full transition hover:bg-foreground/8 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
          @click="menuOpen = true"
        >
          <Avatar :name="auth.full_name ?? ''" :src="auth.avatar_url" size="size-8" fallback-class="text-xs" />
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
                  <PhUserCircle class="size-5" weight="bold" />
                </button>
                <button
                  class="p-2 rounded-md text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
                  aria-label="Settings"
                  @click="menuOpen = false; settingsDrawer.show()"
                >
                  <PhGear class="size-5" weight="bold" />
                </button>
                <button
                  v-if="auth.role === 'admin'"
                  class="p-2 rounded-md text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
                  aria-label="Tools"
                  @click="navigate('/admin/tools')"
                >
                  <PhHammer class="size-5" weight="bold" />
                </button>
              </div>
            </div>

            <div class="overflow-y-auto p-1.5 pb-3 scroll-fade-y">
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
                <PhCheck v-if="theme === t.value" class="ml-auto size-3.5 text-primary" weight="bold" />
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
                  <PhCheck v-if="auth.role === r.value" class="ml-auto size-3.5 text-primary" weight="bold" />
                </button>
              </template>

              <div class="h-px bg-border -mx-1.5 mt-1.5 mb-1.5" />

              <button
                v-if="DEMO"
                class="w-full flex items-center gap-2.5 rounded-md px-3 py-2.5 text-sm font-medium tracking-tight hover:bg-accent transition-colors"
                @click="handleResetDemo"
              >
                <PhArrowCounterClockwise class="size-4 text-muted-foreground" weight="bold" />
                Reset demo data
              </button>
              <button
                class="w-full flex items-center gap-2.5 rounded-md px-3 py-2.5 text-sm font-medium tracking-tight text-destructive hover:bg-destructive/10 transition-colors"
                @click="handleLogout"
              >
                <PhSignOut class="size-4" weight="bold" />
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
  PhCheck,
  PhCaretDown,
  PhHammer,
  PhMagnifyingGlass,
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
const { confirm } = useConfirm();
const settingsDrawer = useSettingsDrawer();

const isDesktop = useMediaQuery("(min-width: 640px)");
const menuOpen = ref(false);

const isCustomer = computed(() => auth.role === "user");
const searchText = ref(typeof route.query.search === "string" ? route.query.search : "");

watch(
  () => route.query.search,
  (s) => {
    if (route.path === "/home/services") searchText.value = typeof s === "string" ? s : "";
  },
);

function submitSearch() {
  const q = searchText.value.trim();
  router.push({ path: "/home/services", query: q ? { search: q } : {} });
}

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
  menuOpen.value = false;
  if (!await confirm({
    title: "Sign out?",
    description: "You'll be signed out of your account. You can sign back in anytime.",
    confirmLabel: "Sign out",
  })) return;
  await auth.logout();
  router.push("/");
}

async function handleResetDemo() {
  menuOpen.value = false;
  if (!await confirm({
    title: "Reset demo data?",
    description: "This restores the demo to its original state — any bookings, edits, or accounts you changed will be discarded.",
    variant: "destructive",
    confirmLabel: "Reset demo",
  })) return;
  resetDemoData();
}
</script>

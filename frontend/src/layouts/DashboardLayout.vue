<template>
  <div class="flex h-screen flex-col bg-background">
    <!-- Dark global top bar — brand on the left, user menu on the right -->
    <header
      class="vt-topbar flex h-12 shrink-0 items-center justify-between bg-[#161616] px-6 text-white relative z-20"
    >
      <RouterLink to="/" class="vt-brand flex items-center gap-2 shrink-0">
        <BrandMark class="h-4 w-auto" />
        <span class="font-serif font-semibold text-base tracking-tight">hearth</span>
      </RouterLink>

      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <button
            type="button"
            class="flex items-center gap-2 px-2 py-1 transition hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/60 focus-visible:ring-offset-2 focus-visible:ring-offset-[#161616]"
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
          <DropdownMenuSeparator />
          <DropdownMenuItem
            class="text-destructive focus:text-destructive"
            @click="handleLogout"
          >
            <LogOut class="mr-2 size-4" />
            Sign out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
    <main class="flex-1 min-h-0 overflow-y-auto">
      <slot />
    </main>
  </div>
</template>

<script lang="ts" setup>
import { ChevronDown, LogOut, Settings, UserCircle } from "lucide-vue-next";
import { computed } from "vue";
import { RouterLink, useRouter } from "vue-router";

import BrandMark from "@/components/BrandMark.vue";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { initials } from "@/lib/format";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const auth = useAuthStore();

const firstName = computed(() => auth.full_name?.split(" ")[0] ?? "");

async function handleLogout() {
  await auth.logout();
  router.push("/");
}
</script>

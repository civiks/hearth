<template>
  <Card class="w-full max-w-md ring-0 p-8 sm:p-10 gap-0">
    <RouterLink
      to="/"
      class="self-start mb-8 hover:opacity-80 transition-opacity"
      aria-label="hearth — back to home"
    >
      <BrandMark class="h-8 w-auto" />
    </RouterLink>

    <h1 class="text-3xl font-light tracking-tight">
      Welcome back to <span class="font-medium">hearth</span>
    </h1>
    <p class="mt-1 text-sm text-muted-foreground">Sign in to continue</p>

    <form class="space-y-6 mt-8" @submit.prevent="submit">
      <div class="space-y-1.5">
        <Label for="email">Email</Label>
        <Input
          id="email"
          v-model="email"
          type="email"
          autocomplete="email"
          required
        />
      </div>
      <div class="space-y-1.5">
        <div class="flex items-baseline justify-between">
          <Label for="password">Password</Label>
          <button
            type="button"
            class="text-xs text-primary hover:underline cursor-pointer"
            @click="onForgotPassword"
          >
            Forgot password?
          </button>
        </div>
        <div class="relative">
          <Input
            id="password"
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            autocomplete="current-password"
            class="pr-10"
            required
          />
          <button
            type="button"
            class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-muted-foreground hover:text-foreground cursor-pointer"
            :aria-label="showPassword ? 'Hide password' : 'Show password'"
            :aria-pressed="showPassword"
            tabindex="-1"
            @click="showPassword = !showPassword"
          >
            <EyeOff v-if="showPassword" class="size-4" />
            <Eye v-else class="size-4" />
          </button>
        </div>
      </div>

      <div class="flex items-center gap-2 pt-2">
        <Button type="submit" :disabled="loading">
          {{ loading ? "Signing in…" : "Sign in" }}
        </Button>
        <Button
          type="button"
          variant="outline"
          @click="$router.push('/register')"
        >
          Create account
        </Button>
      </div>

      <p class="pt-2 text-xs leading-relaxed text-muted-foreground">
        By signing in you agree to hearth's
        <RouterLink
          to="/terms"
          target="_blank"
          class="text-primary hover:underline"
        >
          Terms of Service
        </RouterLink>
        and
        <RouterLink
          to="/privacy"
          target="_blank"
          class="text-primary hover:underline"
        >
          Privacy Policy</RouterLink>.
      </p>
    </form>
  </Card>
</template>

<script lang="ts" setup>
import { Eye, EyeOff } from "lucide-vue-next";
import { ref } from "vue";
import { RouterLink, useRouter } from "vue-router";

import BrandMark from "@/components/BrandMark.vue";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ApiError, api, homePathForRole, type User } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";

const router = useRouter();
const auth = useAuthStore();
const toasts = useNotificationsStore();

const email = ref("");
const password = ref("");
const showPassword = ref(false);
const loading = ref(false);

function onForgotPassword() {
  toasts.info(
    "Password recovery isn't wired up in this demo",
    "Try one of the seed accounts (admin@email.com / admin) or use the Demo button.",
  );
}

async function submit() {
  loading.value = true;
  try {
    const user = await api.post<User>("/api/auth/login", {
      email: email.value,
      password: password.value,
    });
    auth.setUser(user);
    router.push(homePathForRole(user.role));
  } catch (err) {
    toasts.error(
      "Sign in failed",
      err instanceof ApiError ? err.detail : "Unable to connect to the server.",
    );
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="w-full max-w-md flex flex-col">
    <RouterLink
      to="/"
      class="self-center mb-8 hover:opacity-80 transition-opacity"
      aria-label="hearth — back to home"
    >
      <BrandMark class="h-8 w-auto" />
    </RouterLink>

    <h1 class="text-center text-2xl font-light tracking-tight">
      Welcome back to <span class="font-medium">hearth</span>
    </h1>
    <p class="mt-2 text-center text-xs text-muted-foreground">
      Don't have an account?
      <RouterLink to="/register" class="text-primary underline underline-offset-2">
        Sign up
      </RouterLink>
    </p>

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
            class="text-xs text-primary hover:underline cursor-pointer focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
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
            class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-muted-foreground hover:text-foreground cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1"
            :aria-label="showPassword ? 'Hide password' : 'Show password'"
            :aria-pressed="showPassword"
            @click="showPassword = !showPassword"
          >
            <EyeOff v-if="showPassword" class="size-3.5" />
            <Eye v-else class="size-3.5" />
          </button>
        </div>
      </div>

      <div class="pt-2">
        <Button type="submit" class="w-full" :disabled="loading">
          {{ loading ? "Signing in…" : "Sign in" }}
        </Button>
      </div>

      <p class="pt-2 text-xs leading-relaxed text-muted-foreground">
        By signing in you agree to hearth's
        <RouterLink
          to="/terms"
          target="_blank"
          class="text-primary underline underline-offset-2"
        >
          Terms of Service
        </RouterLink>
        and
        <RouterLink
          to="/privacy"
          target="_blank"
          class="text-primary underline underline-offset-2"
        >
          Privacy Policy</RouterLink>.
      </p>
    </form>
  </div>
</template>

<script lang="ts" setup>
import { Eye, EyeOff } from "lucide-vue-next";
import { ref } from "vue";
import { RouterLink, useRouter } from "vue-router";

import BrandMark from "@/components/BrandMark.vue";
import { Button } from "@/components/ui/button";
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
  if (!email.value.trim()) {
    toasts.info("Enter your email above first.");
    return;
  }
  toasts.success(
    "Check your inbox",
    `If an account exists for ${email.value}, a reset link is on its way.`,
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

<template>
  <div class="w-full max-w-sm flex flex-col">
    <RouterLink
      to="/"
      class="self-center mb-6 hover:opacity-80 transition-opacity"
      aria-label="hearth — back to home"
    >
      <BrandMark class="h-10 w-auto" />
    </RouterLink>

    <h1 class="font-display text-center text-3xl font-bold tracking-tight mb-6">
      Welcome back
    </h1>

    <form class="space-y-3" @submit.prevent="submit">
      <Input
        v-model="email"
        type="email"
        placeholder="Email address"
        autocomplete="email"
        required
        class="bg-muted border-transparent h-12 px-5 rounded-full"
      />

      <div class="space-y-1.5">
        <div class="relative">
          <Input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="Password"
            autocomplete="current-password"
            class="bg-muted border-transparent h-12 px-5 pr-12 rounded-full"
            required
          />
          <button
            type="button"
            class="absolute right-4 top-1/2 -translate-y-1/2 p-1 text-muted-foreground hover:text-foreground cursor-pointer focus-visible:outline-none"
            :aria-label="showPassword ? 'Hide password' : 'Show password'"
            :aria-pressed="showPassword"
            @click="showPassword = !showPassword"
          >
            <PhEyeSlash v-if="showPassword" class="size-4" />
            <PhEye v-else class="size-4" />
          </button>
        </div>
        <div class="flex justify-end px-1">
          <button
            type="button"
            class="text-xs text-muted-foreground hover:text-foreground cursor-pointer focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
            @click="onForgotPassword"
          >
            Forgot password?
          </button>
        </div>
      </div>

      <Button type="submit" class="w-full rounded-full h-12 font-semibold" :disabled="loading">
        {{ loading ? "Signing in…" : "Sign in" }}
      </Button>
    </form>

    <p class="mt-5 text-center text-sm text-muted-foreground">
      Don't have an account?
      <RouterLink to="/register" class="text-primary font-semibold hover:underline underline-offset-2">Sign up</RouterLink>
    </p>

    <p class="mt-4 text-[11px] text-center text-muted-foreground/60">
      By signing in you agree to hearth's
      <RouterLink to="/terms" target="_blank" class="underline underline-offset-2 hover:text-muted-foreground">Terms of Service</RouterLink>
      and
      <RouterLink to="/privacy" target="_blank" class="underline underline-offset-2 hover:text-muted-foreground">Privacy Policy</RouterLink>.
    </p>
  </div>
</template>

<script lang="ts" setup>
import {
  PhEye,
  PhEyeSlash,
} from '@phosphor-icons/vue';
import { ref } from "vue";
import { RouterLink, useRouter } from "vue-router";

import BrandMark from "@/components/BrandMark.vue";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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

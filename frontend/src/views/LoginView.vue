<template>
  <div class="w-full max-w-sm flex flex-col">
    <RouterLink
      to="/"
      class="self-center mb-6 hover:opacity-80 transition-opacity"
      aria-label="hearth — back to home"
    >
      <BrandMark class="h-10 w-auto" />
    </RouterLink>

    <h1 class="font-display text-center text-3xl font-bold tracking-tight mb-6 text-transparent bg-clip-text bg-gradient-to-b from-zinc-900 via-zinc-800 to-zinc-500 dark:from-zinc-100 dark:via-zinc-300 dark:to-zinc-500">
      Welcome back
    </h1>

    <form class="space-y-3" novalidate @submit.prevent="submit">
      <Input
        v-model="email"
        type="email"
        placeholder="Email address"
        autocomplete="email"
        required
        :aria-invalid="invalid.email || undefined"
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
            :aria-invalid="invalid.password || undefined"
          />
          <button
            type="button"
            class="absolute right-4 top-1/2 -translate-y-1/2 p-1 text-muted-foreground hover:text-foreground cursor-pointer focus-visible:outline-none"
            :aria-label="showPassword ? 'Hide password' : 'Show password'"
            :aria-pressed="showPassword"
            @click="showPassword = !showPassword"
          >
            <PhEyeSlash v-if="showPassword" class="size-4" weight="bold" />
            <PhEye v-else class="size-4" weight="bold" />
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

      <Button type="submit" class="w-full rounded-full h-12 font-semibold" :disabled="loading || !email.trim() || !password">
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
import { nextTick, reactive, ref, watch } from "vue";
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
const invalid = reactive({ email: false, password: false });

watch(email, (v) => { if (v.trim()) invalid.email = false; });
watch(password, (v) => { if (v) invalid.password = false; });

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
  const emailMissing = !email.value.trim();
  const passwordMissing = !password.value;
  if (emailMissing || passwordMissing) {
    toasts.error("Check the form", "Enter your email and password.");
    invalid.email = false;
    invalid.password = false;
    // Re-flag next tick so the shake animation replays on a repeat submit.
    void nextTick(() => {
      invalid.email = emailMissing;
      invalid.password = passwordMissing;
    });
    return;
  }
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

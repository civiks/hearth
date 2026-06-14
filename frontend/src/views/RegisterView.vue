<template>
  <div class="w-full max-w-sm flex flex-col">
    <button
      v-if="step === 'form'"
      type="button"
      class="fixed top-5 left-5 z-10 grid place-items-center size-10 rounded-full bg-muted text-foreground hover:bg-muted/70 cursor-pointer press"
      aria-label="Back"
      @click="step = 'role'"
    >
      <PhArrowLeft class="size-4" weight="bold" />
    </button>

    <RouterLink
      to="/"
      class="self-center mb-6 hover:opacity-80 transition-opacity"
      aria-label="hearth — back to home"
    >
      <BrandMark class="h-10 w-auto" />
    </RouterLink>

    <template v-if="step === 'role'">
      <div class="text-center mb-7">
        <h1 class="font-display text-3xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-b from-zinc-900 via-zinc-800 to-zinc-500 dark:from-zinc-100 dark:via-zinc-300 dark:to-zinc-500">
          Join hearth
        </h1>
        <p class="mt-1.5 text-sm text-muted-foreground">
          See how hearth gets verified pros to your doorstep within hours
        </p>
      </div>

      <div class="rounded-3xl bg-card soft-card p-2">
        <div class="px-3 pt-2 pb-2.5 text-sm text-muted-foreground">I want to…</div>
        <div class="grid grid-cols-2 gap-1.5">
          <button
            type="button"
            :class="[
              'group/role relative flex aspect-[5/6] flex-col justify-between rounded-2xl p-4 text-left cursor-pointer press transition-colors',
              role === 'user'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary hover:bg-secondary-hover',
            ]"
            :aria-pressed="role === 'user'"
            @click="role = 'user'"
          >
            <PhHouseLine
              :class="['size-7', role === 'user' ? 'text-primary-foreground' : 'text-muted-foreground/60']"
              :weight="role === 'user' ? 'fill' : 'bold'"
            />
            <div class="font-medium leading-snug">Book a service</div>
          </button>
          <button
            type="button"
            :class="[
              'group/role relative flex aspect-[5/6] flex-col justify-between rounded-2xl p-4 text-left cursor-pointer press transition-colors',
              role === 'professional'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary hover:bg-secondary-hover',
            ]"
            :aria-pressed="role === 'professional'"
            @click="role = 'professional'"
          >
            <PhWrench
              :class="['size-7', role === 'professional' ? 'text-primary-foreground' : 'text-muted-foreground/60']"
              :weight="role === 'professional' ? 'fill' : 'bold'"
            />
            <div class="font-medium leading-snug">Offer my services</div>
          </button>
        </div>
      </div>

      <Button variant="secondary" :disabled="!role" class="mt-4 w-full rounded-full h-12 font-semibold justify-center" @click="step = 'form'">
        Continue
        <PhArrowRight class="size-4" weight="bold" />
      </Button>

      <p class="mt-5 text-center text-sm text-muted-foreground">
        Already have an account?
        <RouterLink to="/login" class="text-primary font-semibold hover:underline underline-offset-2">Sign in</RouterLink>
      </p>
    </template>

    <template v-else>
      <h1 class="font-display text-center text-3xl font-bold tracking-tight mb-1 text-transparent bg-clip-text bg-gradient-to-b from-zinc-900 via-zinc-800 to-zinc-500 dark:from-zinc-100 dark:via-zinc-300 dark:to-zinc-500">
        {{ role === "user" ? "Create account" : "Sign up as Pro" }}
      </h1>
      <p class="mb-6 text-center text-sm text-muted-foreground">
        {{ role === "user" ? "A few details and you're set" : "We'll review your profile before going live" }}
      </p>

      <form id="register-form" class="space-y-3 pb-24 sm:pb-0" @submit.prevent="submit">
        <Input
          v-model="email"
          type="email"
          placeholder="Email address"
          autocomplete="email"
          required
          class="bg-muted border-transparent h-12 px-5 rounded-full"
        />

        <div class="relative">
          <Input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="Password"
            autocomplete="new-password"
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
            <PhEyeSlash v-if="showPassword" class="size-4" weight="bold" />
            <PhEye v-else class="size-4" weight="bold" />
          </button>
        </div>

        <Input
          v-model="full_name"
          placeholder="Full name"
          autocomplete="name"
          required
          class="bg-muted border-transparent h-12 px-5 rounded-full"
        />

        <Input
          v-model="address"
          placeholder="Address"
          autocomplete="street-address"
          required
          class="bg-muted border-transparent h-12 px-5 rounded-full"
        />

        <Input
          v-model="pincode"
          placeholder="Pincode"
          autocomplete="postal-code"
          required
          class="bg-muted border-transparent h-12 px-5 rounded-full"
        />

        <div v-if="role === 'professional'" class="space-y-3 pt-1">
          <Select v-model="serviceId">
            <SelectTrigger class="bg-muted border-transparent h-12 px-5 rounded-full">
              <SelectValue placeholder="Service category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem
                v-for="s in services"
                :key="s.id"
                :value="String(s.id)"
              >
                {{ s.name }}
              </SelectItem>
            </SelectContent>
          </Select>

          <Input
            v-model="experienceStr"
            type="number"
            min="0"
            max="60"
            placeholder="Years of experience"
            class="bg-muted border-transparent h-12 px-5 rounded-full"
          />

          <Textarea
            v-model="description"
            placeholder="Professional description"
            rows="3"
            class="bg-muted border-transparent px-5 py-3 resize-none rounded-2xl"
          />
        </div>

        <div class="flex items-start gap-2.5 pt-1">
          <Checkbox id="tos" v-model:checked="agreedToTos" class="mt-0.5" />
          <label for="tos" class="text-[11px] leading-relaxed text-muted-foreground/60 cursor-pointer">
            I agree to hearth's
            <RouterLink to="/terms" target="_blank" class="underline underline-offset-2 hover:text-muted-foreground">Terms of Service</RouterLink>
            and
            <RouterLink to="/privacy" target="_blank" class="underline underline-offset-2 hover:text-muted-foreground">Privacy Policy</RouterLink>.
            <span v-if="role === 'professional'">Professional profiles are reviewed before going live.</span>
          </label>
        </div>

        <Button type="submit" class="hidden sm:flex w-full rounded-full h-12 font-semibold justify-center" :disabled="loading || !agreedToTos">
          {{ loading ? "Creating…" : "Create account" }}
        </Button>
      </form>
    </template>

    <div v-if="step === 'form'" class="page-footer sm:hidden">
      <Button form="register-form" type="submit" class="w-full rounded-full h-12 font-semibold justify-center" :disabled="loading || !agreedToTos">
        {{ loading ? "Creating…" : "Create account" }}
      </Button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {
  PhArrowLeft,
  PhArrowRight,
  PhEye,
  PhEyeSlash,
  PhHouseLine,
  PhWrench,
} from '@phosphor-icons/vue';
import { computed, ref, watch } from "vue";
import { RouterLink, useRouter } from "vue-router";

import BrandMark from "@/components/BrandMark.vue";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { ApiError, api, homePathForRole, type User as ApiUser } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";

interface Service {
  id: number;
  name: string;
}

const router = useRouter();
const auth = useAuthStore();
const toasts = useNotificationsStore();

const step = ref<"role" | "form">("role");
const role = ref<"user" | "professional" | null>(null);
const email = ref("");
const password = ref("");
const showPassword = ref(false);
const full_name = ref("");
const address = ref("");
const pincode = ref("");
const serviceId = ref<string | undefined>(undefined);
const experience = ref<number | null>(null);
const experienceStr = computed<string>({
  get: () => (experience.value === null ? "" : String(experience.value)),
  set: (v: string) => {
    const n = Number(v);
    experience.value = Number.isFinite(n) ? n : null;
  },
});
const description = ref("");

const agreedToTos = ref(false);
const services = ref<Service[]>([]);
const loading = ref(false);

watch(
  [step, role],
  ([s, r]) => {
    if (s === "form" && r === "professional" && services.value.length === 0) {
      loadServices();
    }
  },
  { immediate: true },
);

async function loadServices() {
  try {
    services.value = await api.get<Service[]>("/api/services");
  } catch {
    // ignore — only matters if user picks "professional"
  }
}

async function submit() {
  loading.value = true;
  try {
    const payload: Record<string, unknown> = {
      email: email.value,
      password: password.value,
      role: role.value,
      full_name: full_name.value,
      address: address.value,
      pincode: pincode.value,
    };
    if (role.value === "professional") {
      payload.service_id = serviceId.value ? Number(serviceId.value) : undefined;
      payload.experience = experience.value;
      payload.description = description.value;
    }
    const user = await api.post<ApiUser>("/api/auth/register", payload);
    auth.setUser(user);
    router.push(homePathForRole(user.role));
  } catch (err) {
    toasts.error(
      "Could not create account",
      err instanceof ApiError ? err.detail : "Registration failed.",
    );
  } finally {
    loading.value = false;
  }
}
</script>

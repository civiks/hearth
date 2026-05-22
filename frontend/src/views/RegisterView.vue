<template>
  <Card class="w-full max-w-md ring-0 p-8 sm:p-10 gap-0">
    <RouterLink
      to="/"
      class="self-start mb-8 hover:opacity-80 transition-opacity"
      aria-label="hearth — back to home"
    >
      <BrandMark class="h-8 w-auto" />
    </RouterLink>

    <!-- Step 1: pick role -->
    <template v-if="step === 'role'">
      <h1 class="text-2xl font-light tracking-tight">
        Join <span class="font-medium">hearth</span>
      </h1>
      <p class="mt-1 text-sm text-muted-foreground">
        First, tell us why you're here
      </p>

      <div class="mt-8 space-y-3">
        <button
          type="button"
          class="w-full flex items-start gap-3 border bg-card p-4 text-left transition hover:border-primary cursor-pointer"
          @click="selectRole('user')"
        >
          <User class="mt-0.5 size-5 text-primary shrink-0" />
          <div>
            <div class="text-sm font-medium">Customer</div>
            <div class="text-xs text-muted-foreground">
              Book and manage home services
            </div>
          </div>
        </button>
        <button
          type="button"
          class="w-full flex items-start gap-3 border bg-card p-4 text-left transition hover:border-primary cursor-pointer"
          @click="selectRole('professional')"
        >
          <Briefcase class="mt-0.5 size-5 text-primary shrink-0" />
          <div>
            <div class="text-sm font-medium">Service Professional</div>
            <div class="text-xs text-muted-foreground">
              Offer services and accept bookings
            </div>
          </div>
        </button>
      </div>

      <p class="mt-8 text-sm text-muted-foreground">
        Already have an account?
        <RouterLink to="/login" class="text-primary hover:underline">
          Sign in
        </RouterLink>
      </p>
    </template>

    <!-- Step 2: form -->
    <template v-else>
      <button
        type="button"
        class="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-4 cursor-pointer"
        @click="step = 'role'"
      >
        <ArrowLeft class="size-3.5" /> Back
      </button>

      <h1 class="text-2xl font-light tracking-tight">
        {{ role === "user" ? "Sign up as Customer" : "Sign up as Professional" }}
      </h1>
      <p class="mt-1 text-sm text-muted-foreground">
        {{
          role === "user"
            ? "A few details and you're set"
            : "We'll review your profile before going live"
        }}
      </p>

      <form class="space-y-5 mt-8" @submit.prevent="submit">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
            <Label for="password">Password</Label>
            <div class="relative">
              <Input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="new-password"
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
                <EyeOff v-if="showPassword" class="size-4" />
                <Eye v-else class="size-4" />
              </button>
            </div>
          </div>
        </div>

        <div class="space-y-1.5">
          <Label for="full_name">Full name</Label>
          <Input
            id="full_name"
            v-model="full_name"
            autocomplete="name"
            required
          />
        </div>

        <div class="space-y-1.5">
          <Label for="address">Address</Label>
          <Input
            id="address"
            v-model="address"
            autocomplete="street-address"
            required
          />
        </div>

        <div class="space-y-1.5">
          <Label for="pincode">Pincode</Label>
          <Input
            id="pincode"
            v-model="pincode"
            autocomplete="postal-code"
            required
          />
        </div>

        <div v-if="role === 'professional'" class="space-y-4 border-t pt-5">
          <div class="space-y-1.5">
            <Label for="service">Service category</Label>
            <Select v-model="serviceId">
              <SelectTrigger id="service">
                <SelectValue placeholder="Choose a service" />
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
          </div>
          <div class="space-y-1.5">
            <Label for="experience">Years of experience</Label>
            <Input
              id="experience"
              v-model="experienceStr"
              type="number"
              min="0"
              max="60"
            />
          </div>
          <div class="space-y-1.5">
            <Label for="description">Professional description</Label>
            <Textarea id="description" v-model="description" rows="3" />
          </div>
        </div>

        <p class="pt-2 text-xs leading-relaxed text-muted-foreground">
          By creating an account you agree to hearth's
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
          {{
            role === "professional"
              ? "Professional profiles are reviewed before going live."
              : ""
          }}
        </p>

        <div class="flex items-center gap-2 pt-2">
          <Button type="submit" :disabled="loading">
            {{ loading ? "Creating…" : "Create account" }}
          </Button>
          <Button type="button" variant="outline" @click="step = 'role'">
            Back
          </Button>
        </div>
      </form>
    </template>
  </Card>
</template>

<script lang="ts" setup>
import { ArrowLeft, Briefcase, Eye, EyeOff, User } from "lucide-vue-next";
import { computed, ref, watch } from "vue";
import { RouterLink, useRouter } from "vue-router";

import BrandMark from "@/components/BrandMark.vue";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
const role = ref<"user" | "professional">("user");
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

const services = ref<Service[]>([]);
const loading = ref(false);

function selectRole(r: "user" | "professional") {
  role.value = r;
  step.value = "form";
}

// Only fetch services when the professional form is actually about to render.
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

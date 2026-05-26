<template>
  <section class="border-b bg-card">
    <div class="mx-auto w-full max-w-[1440px] px-6 py-6 space-y-3">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div class="flex items-center gap-1.5 text-xs text-muted-foreground">
            <MapPin class="size-3.5" />
            {{ locationLabel }}
            <button
              class="underline underline-offset-2 hover:text-foreground ml-1"
              @click="openPicker"
            >
              {{ auth.pincode ? "change" : "set location" }}
            </button>
          </div>
          <h1 class="text-2xl font-light tracking-tight mt-1">
            Trusted home services on demand
          </h1>
          <p class="text-xs text-muted-foreground mt-0.5">
            {{ bookedToday }} services booked in your area this week.
          </p>
        </div>
        <div class="relative w-full sm:w-80">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            :model-value="modelValue"
            placeholder="Search for plumbing, AC repair, cleaning…"
            class="pl-9 h-10"
            @update:model-value="$emit('update:modelValue', String($event))"
            @keyup.enter="$emit('submit', modelValue)"
          />
        </div>
      </div>
    </div>
  </section>

  <Dialog v-model:open="dialogOpen">
    <DialogContent class="sm:max-w-sm">
      <DialogHeader>
        <DialogTitle>Service location</DialogTitle>
        <DialogDescription>
          We use this to show relevant professionals near you.
        </DialogDescription>
      </DialogHeader>
      <form class="space-y-4" @submit.prevent="save">
        <div class="space-y-2">
          <Label for="loc_address">Address</Label>
          <Input id="loc_address" v-model="form.address" placeholder="Street address" />
        </div>
        <div class="space-y-2">
          <Label for="loc_pincode">Pincode</Label>
          <Input
            id="loc_pincode"
            v-model="form.pincode"
            placeholder="6-digit pincode"
            pattern="[0-9]{6}"
          />
        </div>
        <Alert v-if="error" variant="destructive">
          <AlertCircle class="size-4" />
          <AlertDescription>{{ error }}</AlertDescription>
        </Alert>
      </form>
      <DialogFooter>
        <Button variant="outline" type="button" @click="dialogOpen = false">Cancel</Button>
        <Button type="button" :disabled="saving" @click="save">
          {{ saving ? "Saving…" : "Save" }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<script lang="ts" setup>
import { AlertCircle, MapPin, Search } from "lucide-vue-next";
import { computed, reactive, ref } from "vue";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ApiError, api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

const props = defineProps<{ modelValue: string; bookingsThisWeek?: number }>();
defineEmits<{
  "update:modelValue": [value: string];
  submit: [value: string];
}>();

const auth = useAuthStore();

const locationLabel = computed(() => {
  if (auth.pincode) return `Bangalore — ${auth.pincode}`;
  if (auth.address) return auth.address;
  return "Bangalore";
});

const bookedToday = computed(() => props.bookingsThisWeek ?? 147);

const dialogOpen = ref(false);
const saving = ref(false);
const error = ref("");

const form = reactive({ address: "", pincode: "" });

function openPicker() {
  form.address = auth.address ?? "";
  form.pincode = auth.pincode ?? "";
  error.value = "";
  dialogOpen.value = true;
}

async function save() {
  saving.value = true;
  error.value = "";
  try {
    await api.put("/api/users/me", { address: form.address, pincode: form.pincode });
    auth.updateUserDetails({ address: form.address, pincode: form.pincode });
    dialogOpen.value = false;
  } catch (err) {
    error.value = err instanceof ApiError ? err.detail : "Failed to save location.";
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <section class="border-b bg-card">
    <div class="mx-auto w-full max-w-[1440px] px-6 py-3 sm:py-5 space-y-3">
      <button
        type="button"
        class="inline-flex items-center gap-1.5 text-xs tracking-tight tabular-nums text-muted-foreground hover:text-foreground transition-colors"
        @click="openPicker"
      >
        <MapPin class="size-3.5" />
        {{ locationLabel }}
        <ChevronDown class="size-3.5" />
      </button>

      <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3">
        <div class="relative w-full sm:w-72 shrink-0">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 size-3.5 text-muted-foreground" />
          <Input
            :model-value="search"
            placeholder="Search for services"
            class="pl-9 h-10"
            @update:model-value="$emit('update:search', String($event))"
            @keyup.enter="$emit('submit', search)"
          />
        </div>

        <ul
          v-if="categories.length"
          class="flex gap-2 overflow-x-auto scrollbar-hide scroll-x-mask sm:flex-1 min-w-0"
        >
          <li>
            <button
              type="button"
              class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs transition-colors whitespace-nowrap"
              :class="category === null ? activeChip : inactiveChip"
              @click="$emit('update:category', null)"
            >
              All
              <span
                v-if="totalCount"
                class="inline-flex items-center justify-center min-w-[18px] rounded-full px-1 text-[10px] font-medium tabular-nums"
                :class="category === null ? 'bg-primary-foreground/20 text-primary-foreground' : 'bg-muted text-muted-foreground'"
              >
                {{ totalCount }}
              </span>
            </button>
          </li>
          <li v-for="entry in categories" :key="entry.name">
            <button
              type="button"
              class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs transition-colors whitespace-nowrap"
              :class="category === entry.name ? activeChip : inactiveChip"
              @click="$emit('update:category', entry.name)"
            >
              {{ entry.name }}
              <span
                class="inline-flex items-center justify-center min-w-[18px] rounded-full px-1 text-[10px] font-medium tabular-nums"
                :class="category === entry.name ? 'bg-primary-foreground/20 text-primary-foreground' : 'bg-muted text-muted-foreground'"
              >
                {{ entry.count }}
              </span>
            </button>
          </li>
        </ul>
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
          <AlertCircle class="size-3.5" />
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
import {
  AlertCircle,
  ChevronDown,
  MapPin,
  Search,
} from "lucide-vue-next";
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

interface ServiceLike {
  category?: string | null;
}

const props = defineProps<{
  search: string;
  category: string | null;
  services: ServiceLike[];
}>();

defineEmits<{
  "update:search": [value: string];
  "update:category": [value: string | null];
  submit: [value: string];
}>();

const auth = useAuthStore();

const locationLabel = computed(() => {
  if (auth.pincode) return auth.pincode;
  if (auth.address) return auth.address;
  return "Set location";
});

const activeChip = "bg-primary text-primary-foreground border-primary";
const inactiveChip = "bg-card text-foreground border-border hover:bg-muted";

const categories = computed(() => {
  const map = new Map<string, number>();
  for (const s of props.services) {
    if (!s.category) continue;
    map.set(s.category, (map.get(s.category) ?? 0) + 1);
  }
  return [...map.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => a.name.localeCompare(b.name));
});
const totalCount = computed(() => props.services.length);

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

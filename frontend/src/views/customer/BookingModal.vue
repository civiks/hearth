<template>
  <Drawer :open="true" @update:open="(v) => !v && $emit('close')">
    <DrawerContent>
      <DrawerHeader>
        <DrawerTitle>Book {{ service.name }}</DrawerTitle>
        <DrawerDescription>
          <span v-if="step === 'pro'">Choose a professional for this job.</span>
          <span v-else>{{ service.description }}</span>
        </DrawerDescription>
      </DrawerHeader>

      <!-- scrollable body -->
      <div class="flex-1 overflow-y-auto px-5 py-5 space-y-4">
        <Alert v-if="auth.is_blocked" variant="destructive">
          <AlertCircle class="size-4" />
          <AlertTitle>Account blocked</AlertTitle>
          <AlertDescription>Please contact support to resolve this.</AlertDescription>
        </Alert>

        <!-- Step 1: Pick a professional -->
        <div v-if="step === 'pro'" class="space-y-3">
          <button
            type="button"
            class="w-full text-left rounded-lg p-3 flex items-center gap-3 transition-colors border"
            :class="selectedProId === null ? 'border-primary/50 bg-primary/5' : 'border-border hover:bg-muted/50'"
            @click="selectedProId = null"
          >
            <span class="size-12 shrink-0 rounded-full bg-primary/10 flex items-center justify-center">
              <Sparkles class="size-5 text-primary" />
            </span>
            <div class="flex-1">
              <div class="text-sm font-medium">Any available professional</div>
              <p class="text-xs text-muted-foreground">We'll assign the best-rated pro near you.</p>
            </div>
          </button>
          <ProfessionalPickCard
            v-for="pro in professionals"
            :key="pro.id"
            :professional="pro"
            :selected="selectedProId === pro.id"
            @select="selectedProId = pro.id"
          />
          <div v-if="professionals.length === 0" class="text-xs text-muted-foreground text-center py-4">
            No specific pros listed — we'll match you with the best available.
          </div>
        </div>

        <!-- Step 2: schedule + address -->
        <form v-else class="space-y-4" @submit.prevent="onSubmit">
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div class="border rounded-md bg-muted/50 p-3">
              <div class="text-xs text-muted-foreground mb-1">Duration</div>
              <div class="flex items-center gap-1 font-medium">
                <Clock class="size-3.5 text-primary opacity-70" />
                {{ service.time_required }} min
              </div>
            </div>
            <div class="border rounded-md bg-muted/50 p-3">
              <div class="text-xs text-muted-foreground mb-1">Price</div>
              <div class="flex items-center gap-1 font-medium">
                <IndianRupee class="size-3.5 text-primary opacity-70" />
                {{ service.base_price }}
              </div>
            </div>
          </div>

          <div
            v-if="selectedProName"
            class="border rounded-md bg-muted/30 p-3 flex items-center gap-3 text-sm"
          >
            <UserCheck class="size-4 text-primary" />
            <div>
              <div class="font-medium">{{ selectedProName }}</div>
              <div class="text-xs text-muted-foreground">Your chosen professional</div>
            </div>
            <button
              type="button"
              class="ml-auto text-xs text-primary underline underline-offset-2"
              @click="step = 'pro'"
            >
              change
            </button>
          </div>

          <div class="space-y-2">
            <Label for="scheduled_time">Preferred time</Label>
            <Input
              id="scheduled_time"
              v-model="form.scheduled_time"
              type="datetime-local"
              required
            />
          </div>

          <div class="space-y-2">
            <Label>Service location</Label>
            <div class="flex gap-2">
              <Input v-model="form.address" placeholder="Address" required />
              <Input
                v-model="form.pincode"
                placeholder="Pincode"
                pattern="[0-9]{6}"
                class="max-w-[140px]"
                required
              />
            </div>
            <Button
              v-if="hasDefault"
              type="button"
              variant="link"
              size="sm"
              class="px-0 text-xs"
              @click="useDefault"
            >
              Use my default address
            </Button>
          </div>

          <div class="space-y-2">
            <Label for="remarks">Additional notes</Label>
            <Textarea
              id="remarks"
              v-model="form.remarks"
              rows="3"
              placeholder="Any specific requirements…"
            />
          </div>

          <Alert v-if="errorMessage" variant="destructive">
            <AlertCircle class="size-4" />
            <AlertDescription>{{ errorMessage }}</AlertDescription>
          </Alert>
        </form>
      </div>

      <DrawerFooter>
        <Button
          v-if="step === 'schedule'"
          type="button"
          variant="outline"
          @click="step = 'pro'"
        >
          Back
        </Button>
        <Button type="button" variant="secondary" @click="$emit('close')">Cancel</Button>
        <Button
          v-if="step === 'pro'"
          type="button"
          @click="step = 'schedule'"
        >
          Continue
          <ChevronRight class="size-3.5 ml-1" />
        </Button>
        <Button
          v-else
          type="button"
          :disabled="submitting || auth.is_blocked"
          @click="onSubmit"
        >
          {{ submitting ? "Booking…" : "Confirm booking" }}
        </Button>
      </DrawerFooter>
    </DrawerContent>
  </Drawer>
</template>

<script lang="ts" setup>
import {
  AlertCircle,
  ChevronRight,
  Clock,
  IndianRupee,
  Sparkles,
  UserCheck,
} from "lucide-vue-next";
import { computed, reactive, ref } from "vue";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ApiError, api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import ProfessionalPickCard from "@/views/customer/ProfessionalPickCard.vue";
import type { Service } from "./ServicesGrid.vue";

export interface ProfessionalOption {
  id: number;
  full_name: string;
  service_id: number | null;
  avatar_url?: string;
  rating?: number | null;
  review_count?: number | null;
  experience?: number | null;
  description?: string | null;
  approval_status?: string | null;
  is_blocked?: boolean;
}

const props = defineProps<{
  service: Service;
  professionals?: ProfessionalOption[];
}>();
const emit = defineEmits<{ close: []; booked: [] }>();

const auth = useAuthStore();
const professionals = computed(() => props.professionals ?? []);

const step = ref<"pro" | "schedule">(professionals.value.length > 0 ? "pro" : "schedule");
const selectedProId = ref<number | null>(null);
const selectedProName = computed(() => {
  if (selectedProId.value == null) return null;
  return professionals.value.find((p) => p.id === selectedProId.value)?.full_name ?? null;
});

const submitting = ref(false);
const errorMessage = ref("");

function defaultScheduledTime(): string {
  const t = new Date();
  t.setDate(t.getDate() + 1);
  t.setHours(10, 0, 0, 0);
  return t.toISOString().slice(0, 16);
}

const form = reactive({
  scheduled_time: defaultScheduledTime(),
  address: auth.address ?? "",
  pincode: auth.pincode ?? "",
  remarks: "",
});

const hasDefault = computed(() => !!(auth.address && auth.pincode));

function useDefault() {
  form.address = auth.address ?? "";
  form.pincode = auth.pincode ?? "";
}

async function onSubmit() {
  if (auth.is_blocked) {
    errorMessage.value = "Account is blocked.";
    return;
  }
  submitting.value = true;
  errorMessage.value = "";
  try {
    await api.post("/api/requests", {
      service_id: props.service.id,
      scheduled_time: form.scheduled_time,
      address: form.address,
      pincode: form.pincode,
      remarks: form.remarks,
      professional_id: selectedProId.value ?? undefined,
    });
    emit("booked");
  } catch (err) {
    errorMessage.value =
      err instanceof ApiError ? err.detail : "Failed to book service.";
  } finally {
    submitting.value = false;
  }
}
</script>

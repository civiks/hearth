<template>
  <component
    :is="isDesktop ? Sheet : Drawer"
    :open="true"
    v-bind="isDesktop ? {} : { shouldScaleBackground: true }"
    @update:open="(v: boolean) => !v && $emit('close')"
  >
    <component
      :is="isDesktop ? SheetContent : DrawerContent"
    >
      <DrawerHeader>
        <DrawerTitle>Book {{ service.name }}</DrawerTitle>
        <DrawerDescription>
          <span v-if="step === 'pro'">Choose a professional for this job.</span>
          <span v-else>{{ service.description }}</span>
        </DrawerDescription>
      </DrawerHeader>

      <div class="flex-1 overflow-y-auto px-5 py-5 space-y-4">
        <Alert v-if="auth.is_blocked" variant="destructive">
          <AlertCircle class="size-4" />
          <AlertTitle>Account blocked</AlertTitle>
          <AlertDescription>Please contact support to resolve this.</AlertDescription>
        </Alert>

        <!-- Step 1: Pick a professional -->
        <div v-if="step === 'pro'" class="space-y-3">
          <AiSurface
            as="button"
            type="button"
            class="w-full text-left p-3 flex items-center gap-3 transition"
            :class="selectedProId === null ? 'bg-primary/5' : 'hover:bg-muted/50'"
            @click="selectedProId = null"
          >
            <AiMark class="size-12 shrink-0" />
            <div class="flex-1">
              <div class="text-sm font-medium">Any available professional</div>
              <p class="text-xs text-muted-foreground">We'll assign the best-rated pro near you.</p>
            </div>
          </AiSurface>
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
        <form v-else class="space-y-6" @submit.prevent="onSubmit">
          <!-- Summary strip -->
          <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm pb-4 border-b">
            <span class="flex items-center gap-1 text-muted-foreground">
              <Clock class="size-3" />
              <span class="text-foreground font-medium">{{ service.time_required }} min</span>
            </span>
            <span class="text-muted-foreground/30">·</span>
            <span class="inline-flex items-end gap-0.5 font-medium">
              <span class="text-[11px] font-normal leading-none text-muted-foreground mb-px">Rs</span>
              <span class="leading-none">{{ service.base_price }}</span>
            </span>
            <template v-if="selectedProName">
              <span class="text-muted-foreground/30">·</span>
              <span class="flex items-center gap-1.5">
                <UserCheck class="size-3.5 text-primary" />
                <span>{{ selectedProName }}</span>
                <button type="button" class="text-xs text-primary underline underline-offset-2" @click="step = 'pro'">change</button>
              </span>
            </template>
          </div>

          <!-- When -->
          <div class="space-y-2">
            <Label for="scheduled_time" class="text-sm font-semibold">When</Label>
            <Input id="scheduled_time" v-model="form.scheduled_time" type="datetime-local" :min="nowLocal()" required />
          </div>

          <!-- Where -->
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <Label class="text-sm font-semibold">Where</Label>
              <Button v-if="hasDefault" type="button" variant="link" size="sm" class="h-auto px-0 text-xs" @click="useDefault">
                Use saved address
              </Button>
            </div>
            <Input v-model="form.address" placeholder="Street address" required />
            <div class="flex gap-2 mt-2">
              <Input v-model="form.pincode" placeholder="Pincode" pattern="[0-9]{6}" required class="w-32" />
            </div>
          </div>

          <!-- Notes -->
          <div class="space-y-2">
            <Label for="remarks" class="text-sm font-semibold">
              Notes
              <span class="font-normal text-muted-foreground">(optional)</span>
            </Label>
            <Textarea id="remarks" v-model="form.remarks" rows="3" placeholder="Any specific requirements…" />
          </div>

          <Alert v-if="errorMessage" variant="destructive">
            <AlertCircle class="size-4" />
            <AlertDescription>{{ errorMessage }}</AlertDescription>
          </Alert>
        </form>
      </div>

      <DrawerFooter>
        <Button v-if="step === 'schedule'" type="button" variant="primary-soft" size="icon" class="rounded-full" @click="step = 'pro'">
          <ArrowLeft class="size-4" />
        </Button>
        <Button v-if="step === 'pro'" type="button" class="flex-1" @click="step = 'schedule'">
          Continue
          <ChevronRight class="size-3.5 ml-1" />
        </Button>
        <Button v-else type="button" class="flex-1" :disabled="submitting || auth.is_blocked" @click="onSubmit">
          {{ submitting ? "Booking…" : "Confirm booking" }}
        </Button>
      </DrawerFooter>
    </component>
  </component>
</template>

<script lang="ts" setup>
import {
  AlertCircle,
  ArrowLeft,
  ChevronRight,
  Clock,
  UserCheck,
} from "lucide-vue-next";
import { computed, reactive, ref } from "vue";
import { useMediaQuery } from "@vueuse/core";

import AiMark from "@/components/AiMark.vue";
import AiSurface from "@/components/AiSurface.vue";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Drawer, DrawerContent, DrawerDescription, DrawerFooter, DrawerHeader, DrawerTitle } from "@/components/ui/drawer";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Sheet, SheetContent } from "@/components/ui/sheet";
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

const isDesktop = useMediaQuery("(min-width: 640px)");
const auth = useAuthStore();
const professionals = computed(() => props.professionals ?? []);

const step = ref<"pro" | "schedule">(professionals.value.length > 0 ? "pro" : "schedule");
const selectedProId = ref<number | null>(null);
const selectedProName = computed(() =>
  selectedProId.value == null ? null : professionals.value.find((p) => p.id === selectedProId.value)?.full_name ?? null,
);

const submitting = ref(false);
const errorMessage = ref("");

function nowLocal(): string {
  const now = new Date();
  return new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}

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
  if (auth.is_blocked) { errorMessage.value = "Account is blocked."; return; }
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
    errorMessage.value = err instanceof ApiError ? err.detail : "Failed to book service.";
  } finally {
    submitting.value = false;
  }
}
</script>

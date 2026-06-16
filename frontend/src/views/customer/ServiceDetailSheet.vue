<template>
  <ResponsiveSheet
    :open="true"
    :title="step === 'schedule' ? `Book ${service.name}` : service.name"
    :description="step === 'schedule' ? 'Choose a time and address.' : (service.category ?? undefined)"
    :morph-key="step"
    body-class="space-y-6"
    @close="$emit('close')"
  >
    <Alert v-if="auth.is_blocked" variant="destructive">
      <PhWarningCircle class="size-4" />
      <AlertTitle>Account blocked</AlertTitle>
      <AlertDescription>Please contact support to resolve this.</AlertDescription>
    </Alert>

    <!-- ============================ Details step ============================ -->
    <template v-if="step === 'details'">
      <!-- Price / duration / rating strip -->
      <div class="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm tracking-tight">
        <span class="inline-flex items-end gap-0.5 text-lg font-semibold tabular-nums">
          <span class="text-[11px] font-normal leading-none text-muted-foreground mb-px">Rs</span>
          <span class="leading-none">{{ service.base_price }}</span>
        </span>
        <span class="text-muted-foreground/30">·</span>
        <span class="inline-flex items-center gap-1 text-muted-foreground tabular-nums">
          <PhClock class="size-3.5" />
          {{ service.time_required }} min
        </span>
        <span v-if="service.rating != null" class="text-muted-foreground/30">·</span>
        <span v-if="service.rating != null" class="inline-flex items-center gap-1 tabular-nums">
          <PhStar weight="fill" class="size-3.5 text-amber-400" />
          <span class="font-medium">{{ service.rating.toFixed(1) }}</span>
          <span v-if="service.review_count != null" class="text-muted-foreground">
            ({{ service.review_count }} reviews)
          </span>
        </span>
      </div>

      <!-- Description -->
      <p v-if="service.description" class="text-sm tracking-tight leading-relaxed text-muted-foreground">
        {{ service.description }}
      </p>

      <!-- Professionals (selectable) -->
      <section class="space-y-3">
        <h3 class="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
          Choose a professional
        </h3>
        <div v-if="loadingPros" class="space-y-2">
          <div v-for="i in 2" :key="i" class="h-16 rounded-lg bg-muted animate-pulse" />
        </div>
        <template v-else>
          <AiSurface
            as="button"
            type="button"
            class="w-full text-left p-3 flex items-center gap-3 transition-shadow"
            :class="selectedProId === null ? 'ring-2 ring-inset ring-primary/60 dark:ring-primary/70' : 'hover:soft-card-hover'"
            @click="selectedProId = null"
          >
            <AiMark class="size-11 shrink-0" />
            <div class="flex-1">
              <div class="text-sm font-medium tracking-tight">Any available professional</div>
              <p class="text-xs tracking-tight text-muted-foreground">We'll assign the best-rated pro near you.</p>
            </div>
          </AiSurface>
          <ProfessionalPickCard
            v-for="pro in professionals"
            :key="pro.id"
            :professional="pro"
            :selected="selectedProId === pro.id"
            @select="selectedProId = pro.id"
          />
        </template>
      </section>

      <!-- Reviews -->
      <section class="space-y-4">
        <h3 class="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
          Reviews
        </h3>
        <div v-if="loadingReviews" class="space-y-3">
          <div v-for="i in 3" :key="i" class="h-16 rounded-lg bg-muted animate-pulse" />
        </div>
        <template v-else>
          <div v-for="review in reviews" :key="review.id" class="flex gap-3">
            <ProfessionalAvatar
              :name="review.author_name ?? 'Customer'"
              :src="review.author_avatar_url"
              class="size-8 shrink-0"
            />
            <div class="min-w-0 flex-1 space-y-1">
              <div class="flex items-center justify-between gap-2">
                <span class="text-sm font-medium tracking-tight truncate">{{ review.author_name ?? "Customer" }}</span>
                <span class="text-xs tracking-tight tabular-nums text-muted-foreground shrink-0">
                  {{ formatSmartDate(review.date_created) }}
                </span>
              </div>
              <div class="flex items-center gap-0.5">
                <PhStar
                  v-for="n in 5"
                  :key="n"
                  class="size-3"
                  :weight="n <= Math.round(review.rating) ? 'fill' : 'regular'"
                  :class="n <= Math.round(review.rating) ? 'text-amber-400' : 'text-muted-foreground/30'"
                />
              </div>
              <p v-if="review.comment" class="text-sm tracking-tight leading-relaxed text-muted-foreground">
                {{ review.comment }}
              </p>
            </div>
          </div>
          <p v-if="!reviews.length" class="text-sm text-muted-foreground tracking-tight">
            No reviews yet — be the first to book and rate this service.
          </p>
        </template>
      </section>
    </template>

    <!-- ============================ Schedule step ============================ -->
    <form v-else class="space-y-6" @submit.prevent="onSubmit">
      <!-- Summary strip -->
      <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm tracking-tight pb-4 border-b">
        <span class="flex items-center gap-1 text-muted-foreground">
          <PhClock class="size-3" />
          <span class="text-foreground font-medium tabular-nums">{{ service.time_required }} min</span>
        </span>
        <span class="text-muted-foreground/30">·</span>
        <span class="inline-flex items-end gap-0.5 font-medium tabular-nums">
          <span class="text-[11px] font-normal leading-none text-muted-foreground mb-px">Rs</span>
          <span class="leading-none">{{ service.base_price }}</span>
        </span>
        <span class="text-muted-foreground/30">·</span>
        <span class="flex items-center gap-1.5">
          <PhUserCheck class="size-3.5 text-primary" />
          <span>{{ selectedProName ?? "Any available pro" }}</span>
          <button type="button" class="text-xs tracking-tight text-primary underline underline-offset-2" @click="step = 'details'">change</button>
        </span>
      </div>

      <!-- When -->
      <div class="space-y-2">
        <Label for="scheduled_time" class="text-sm font-semibold tracking-tight">When</Label>
        <Input id="scheduled_time" v-model="form.scheduled_time" type="datetime-local" :min="nowLocal()" required />
      </div>

      <!-- Where -->
      <div class="space-y-2">
        <div class="flex items-center justify-between">
          <Label class="text-sm font-semibold tracking-tight">Where</Label>
          <Button v-if="hasDefault" type="button" variant="link" size="sm" class="h-auto px-0 text-xs tracking-tight" @click="useDefault">
            Use saved address
          </Button>
        </div>
        <Input v-model="form.address" placeholder="Street address" required />
        <div class="flex gap-2 mt-2">
          <Input v-model="form.pincode" placeholder="Pincode" pattern="[0-9]{6}" required class="w-32 tabular-nums" />
        </div>
      </div>

      <!-- Notes -->
      <div class="space-y-2">
        <Label for="remarks" class="text-sm font-semibold tracking-tight">
          Notes
          <span class="font-normal tracking-tight text-muted-foreground">(optional)</span>
        </Label>
        <Textarea id="remarks" v-model="form.remarks" rows="3" placeholder="Any specific requirements…" />
      </div>

    </form>

    <template #footer>
      <template v-if="step === 'details'">
        <Button type="button" class="flex-1" :disabled="auth.is_blocked" @click="step = 'schedule'">
          Book now
        </Button>
      </template>
      <template v-else>
        <Button type="button" variant="primary-soft" size="icon" class="size-12 rounded-full" @click="step = 'details'">
          <PhArrowLeft class="size-4" />
        </Button>
        <Button type="button" class="flex-1" :disabled="submitting || auth.is_blocked" @click="onSubmit">
          {{ submitting ? "Booking…" : "Confirm booking" }}
        </Button>
      </template>
    </template>
  </ResponsiveSheet>
</template>

<script lang="ts" setup>
import {
  PhWarningCircle,
  PhArrowLeft,
  PhClock,
  PhStar,
  PhUserCheck,
} from '@phosphor-icons/vue';
import { computed, onMounted, reactive, ref } from "vue";

import AiMark from "@/components/AiMark.vue";
import AiSurface from "@/components/AiSurface.vue";
import ProfessionalAvatar from "@/components/marketplace/ProfessionalAvatar.vue";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import ResponsiveSheet from "@/components/ui/ResponsiveSheet.vue";
import { Textarea } from "@/components/ui/textarea";
import { ApiError, api } from "@/lib/api";
import { formatSmartDate } from "@/lib/format";
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";
import ProfessionalPickCard from "@/views/customer/ProfessionalPickCard.vue";
import type { Service } from "@/views/customer/ServicesGrid.vue";

interface ProfessionalDetail {
  id: number;
  full_name: string;
  service_id: number;
  avatar_url?: string | null;
  rating?: number | null;
  review_count?: number | null;
  experience?: number | null;
  description?: string | null;
}

interface ServiceReview {
  id: number;
  author_name?: string | null;
  author_avatar_url?: string | null;
  rating: number;
  comment?: string | null;
  date_created: string;
}

const props = defineProps<{ service: Service }>();
const emit = defineEmits<{ close: []; booked: [] }>();

const auth = useAuthStore();

const step = ref<"details" | "schedule">("details");

const professionals = ref<ProfessionalDetail[]>([]);
const reviews = ref<ServiceReview[]>([]);
const loadingPros = ref(true);
const loadingReviews = ref(true);

const selectedProId = ref<number | null>(null);
const selectedProName = computed(() =>
  selectedProId.value == null
    ? null
    : professionals.value.find((p) => p.id === selectedProId.value)?.full_name ?? null,
);

const toasts = useNotificationsStore();
const submitting = ref(false);

const form = reactive({
  scheduled_time: defaultScheduledTime(),
  address: auth.address ?? "",
  pincode: auth.pincode ?? "",
  remarks: "",
});

const hasDefault = computed(() => !!(auth.address && auth.pincode));

onMounted(() => {
  void fetchProfessionals();
  void fetchReviews();
});

async function fetchProfessionals() {
  loadingPros.value = true;
  try {
    professionals.value = await api.get<ProfessionalDetail[]>(
      `/api/services/${props.service.id}/professionals`,
    );
  } catch {
    professionals.value = [];
  } finally {
    loadingPros.value = false;
  }
}

async function fetchReviews() {
  loadingReviews.value = true;
  try {
    reviews.value = await api.get<ServiceReview[]>(
      `/api/services/${props.service.id}/reviews`,
    );
  } catch {
    reviews.value = [];
  } finally {
    loadingReviews.value = false;
  }
}

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

function useDefault() {
  form.address = auth.address ?? "";
  form.pincode = auth.pincode ?? "";
}

async function onSubmit() {
  if (auth.is_blocked) {
    toasts.error("Account blocked", "Please contact support to resolve this.");
    return;
  }
  submitting.value = true;
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
    toasts.error("Couldn't book service", err instanceof ApiError ? err.detail : "Please try again.");
  } finally {
    submitting.value = false;
  }
}
</script>

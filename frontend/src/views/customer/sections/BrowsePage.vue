<template>
  <div class="mx-auto w-full max-w-[1440px] px-6 pt-4 sm:pt-5 pb-4 sm:pb-8 space-y-8">
    <Alert v-if="auth.is_blocked" variant="destructive">
      <AlertCircle class="size-3.5" />
      <AlertTitle>Account blocked</AlertTitle>
      <AlertDescription>
        Your account has been blocked. Please contact support for assistance.
      </AlertDescription>
    </Alert>

    <template v-else>
      <AiSurface
        as="button"
        class="w-full p-4 flex items-center gap-4 text-left transition group hover:brightness-105"
        @click="nlOpen = true"
      >
        <AiMark class="size-7" />
        <span class="flex-1 min-w-0">
          <span class="block text-sm font-medium tracking-tight">Tell us what you need</span>
          <span class="block text-xs tracking-tight text-muted-foreground">
            Describe it and we'll match the right service for you.
          </span>
        </span>
        <ChevronRight class="size-3.5 text-muted-foreground group-hover:text-primary" />
      </AiSurface>

      <section v-if="loading" class="space-y-4">
        <header>
          <div class="h-5 w-40 bg-muted animate-pulse" />
          <div class="h-3 w-56 bg-muted animate-pulse mt-2" />
        </header>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          <ServiceCardSkeleton v-for="i in 3" :key="i" />
        </div>
      </section>

      <template v-else>
        <FeaturedRow
          v-if="reorderServices.length"
          :services="reorderServices"
          title="Order again"
          subtitle="Services you've booked before"
          :icon="History"
          sort-by="as-is"
          :limit="3"
          view-all-to="/home/requests"
          @select="openBooking"
        />

        <FeaturedRow
          :services="services"
          title="Most booked this week"
          subtitle="Top picks from your neighbors"
          :icon="TrendingUp"
          sort-by="popular"
          :limit="3"
          view-all-to="/home/services"
          @select="openBooking"
        />

        <FeaturedRow
          :services="services"
          title="Top rated"
          subtitle="Highest-reviewed pros, by your neighbors"
          :icon="Star"
          icon-class="fill-amber-400 text-amber-400"
          sort-by="top-rated"
          :limit="3"
          view-all-to="/home/services"
          @select="openBooking"
        />
      </template>
    </template>

    <BookingModal
      v-if="bookingFor"
      :service="bookingFor"
      :professionals="professionalsForService"
      @close="bookingFor = null"
      @booked="onBooked"
    />

    <NlBookingDialog
      v-if="nlOpen"
      @close="nlOpen = false"
      @booked="onNlBooked"
    />
  </div>
</template>

<script lang="ts" setup>
import { AlertCircle, ChevronRight, History, Star, TrendingUp } from "lucide-vue-next";
import { computed, onMounted, ref } from "vue";

import AiMark from "@/components/AiMark.vue";
import AiSurface from "@/components/AiSurface.vue";
import NlBookingDialog from "@/components/genai/NlBookingDialog.vue";
import FeaturedRow from "@/components/marketplace/FeaturedRow.vue";
import ServiceCardSkeleton from "@/components/marketplace/ServiceCardSkeleton.vue";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";
import BookingModal, {
  type ProfessionalOption,
} from "@/views/customer/BookingModal.vue";
import { type CustomerRequest } from "@/views/customer/RequestCard.vue";
import { type Service } from "@/views/customer/ServicesGrid.vue";

const auth = useAuthStore();
const toasts = useNotificationsStore();

const services = ref<Service[]>([]);
const professionals = ref<ProfessionalOption[]>([]);
const requests = ref<CustomerRequest[]>([]);
const bookingFor = ref<Service | null>(null);
const nlOpen = ref(false);
const loading = ref(true);

const professionalsForService = computed(() =>
  bookingFor.value
    ? professionals.value.filter(
        (p) =>
          p.service_id === bookingFor.value!.id &&
          p.approval_status === "approved" &&
          !p.is_blocked,
      )
    : [],
);

// "Order again" — unique services the customer has booked before, most recent
// first. Dedupes by service_id; assumes /api/requests row ids are monotonically
// increasing so the highest id is the latest booking.
const reorderServices = computed<Service[]>(() => {
  if (!requests.value.length || !services.value.length) return [];
  const byId = new Map(services.value.map((s) => [s.id, s]));
  const sorted = [...requests.value].sort((a, b) => b.id - a.id);
  const seen = new Set<number>();
  const out: Service[] = [];
  for (const r of sorted) {
    if (seen.has(r.service_id)) continue;
    seen.add(r.service_id);
    const svc = byId.get(r.service_id);
    if (svc) out.push(svc);
  }
  return out;
});

onMounted(async () => {
  loading.value = true;
  try {
    await Promise.all([fetchServices(), fetchProfessionals(), fetchRequests()]);
  } finally {
    loading.value = false;
  }
});

async function fetchServices() {
  try {
    services.value = await api.get<Service[]>("/api/services");
  } catch {
    toasts.error("Failed to load services");
  }
}

async function fetchProfessionals() {
  try {
    professionals.value = await api.get<ProfessionalOption[]>(
      "/api/users?role=professional",
    );
  } catch {
    professionals.value = [];
  }
}

async function fetchRequests() {
  try {
    requests.value = await api.get<CustomerRequest[]>("/api/requests");
  } catch {
    requests.value = [];
  }
}

function openBooking(service: Service) {
  if (auth.is_blocked) {
    toasts.error("Account is blocked. Contact support to book services.");
    return;
  }
  bookingFor.value = service;
}

function onBooked() {
  bookingFor.value = null;
  toasts.success("Service booked — track it under My Requests");
}

function onNlBooked() {
  nlOpen.value = false;
  toasts.success("Service booked — track it under My Requests");
}
</script>

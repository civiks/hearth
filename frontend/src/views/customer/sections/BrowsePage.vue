<template>
  <div class="mx-auto w-full max-w-[1440px] px-6 py-8 space-y-8">
    <Alert v-if="auth.is_blocked" variant="destructive">
      <AlertCircle class="size-4" />
      <AlertTitle>Account blocked</AlertTitle>
      <AlertDescription>
        Your account has been blocked. Please contact support for assistance.
      </AlertDescription>
    </Alert>

    <template v-else>
      <section v-if="loading" class="space-y-4">
        <header>
          <div class="h-5 w-40 bg-muted animate-pulse" />
          <div class="h-3 w-56 bg-muted animate-pulse mt-2" />
        </header>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <ServiceCardSkeleton v-for="i in 3" :key="i" />
        </div>
      </section>

      <template v-else>
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
  </div>
</template>

<script lang="ts" setup>
import { AlertCircle, Star, TrendingUp } from "lucide-vue-next";
import { computed, onMounted, ref } from "vue";

import FeaturedRow from "@/components/marketplace/FeaturedRow.vue";
import ServiceCardSkeleton from "@/components/marketplace/ServiceCardSkeleton.vue";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";
import BookingModal, {
  type ProfessionalOption,
} from "@/views/customer/BookingModal.vue";
import { type Service } from "@/views/customer/ServicesGrid.vue";

const auth = useAuthStore();
const toasts = useNotificationsStore();

const services = ref<Service[]>([]);
const professionals = ref<ProfessionalOption[]>([]);
const bookingFor = ref<Service | null>(null);
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

onMounted(async () => {
  loading.value = true;
  try {
    await Promise.all([fetchServices(), fetchProfessionals()]);
  } finally {
    loading.value = false;
  }
});

async function fetchServices() {
  try {
    services.value = await api.get<Service[]>("/api/services");
  } catch (err) {
    console.error("services fetch failed", err);
  }
}

async function fetchProfessionals() {
  try {
    professionals.value = await api.get<ProfessionalOption[]>(
      "/api/users?role=professional",
    );
  } catch (err) {
    if (import.meta.env.DEV) {
      console.warn("professionals list unavailable to customers", err);
    }
    professionals.value = [];
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
</script>

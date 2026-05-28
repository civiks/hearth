<template>
  <div>
    <Alert v-if="auth.is_blocked" variant="destructive" class="mx-6 mt-6">
      <AlertCircle class="size-3.5" />
      <AlertTitle>Account blocked</AlertTitle>
      <AlertDescription>
        Your account has been blocked. Please contact support for assistance.
      </AlertDescription>
    </Alert>

    <template v-else>
      <div class="mx-auto w-full max-w-[1440px] px-6 pt-4 sm:pt-8 [&_header]:mb-0">
        <PageHeader title="Services">
          <LocationPicker />
        </PageHeader>
      </div>

      <MarketplaceHero
        v-model:search="search"
        v-model:category="category"
        :services="services"
      />

      <div class="mx-auto w-full max-w-[1440px] px-6 pt-3 sm:pt-4 pb-10">
        <section v-if="loading" class="space-y-4">
          <div class="grid gap-3 [grid-template-columns:repeat(auto-fill,minmax(220px,1fr))]">
            <ServiceCardSkeleton v-for="i in 8" :key="i" />
          </div>
        </section>

        <ServicesGrid
          v-else
          :services="services"
          :category="category"
          :search="search"
          @select="openBooking"
        />
      </div>
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
import { AlertCircle } from "lucide-vue-next";
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import PageHeader from "@/components/PageHeader.vue";
import LocationPicker from "@/components/marketplace/LocationPicker.vue";
import MarketplaceHero from "@/components/marketplace/MarketplaceHero.vue";
import ServiceCardSkeleton from "@/components/marketplace/ServiceCardSkeleton.vue";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";
import BookingModal, {
  type ProfessionalOption,
} from "@/views/customer/BookingModal.vue";
import ServicesGrid, { type Service } from "@/views/customer/ServicesGrid.vue";

const auth = useAuthStore();
const toasts = useNotificationsStore();
const route = useRoute();
const router = useRouter();

const services = ref<Service[]>([]);
const professionals = ref<ProfessionalOption[]>([]);
const bookingFor = ref<Service | null>(null);
const search = ref(String(route.query.search ?? ""));
const category = ref<string | null>(
  typeof route.query.category === "string" ? route.query.category : null,
);
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

// Keep the URL query in sync so the page is deep-linkable / shareable.
watch([search, category], ([s, c]) => {
  const query: Record<string, string> = {};
  if (s.trim()) query.search = s.trim();
  if (c) query.category = c;
  router.replace({ path: route.path, query });
});

// React to query changes from other pages (e.g., navigation from Browse).
watch(
  () => route.query,
  (q) => {
    const s = typeof q.search === "string" ? q.search : "";
    const c = typeof q.category === "string" ? q.category : null;
    if (s !== search.value) search.value = s;
    if (c !== category.value) category.value = c;
  },
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

<template>
  <div>
    <Alert v-if="auth.is_blocked" variant="destructive" class="mx-6 mt-6">
      <PhWarningCircle class="size-3.5" weight="bold" />
      <AlertTitle>Account blocked</AlertTitle>
      <AlertDescription>
        Your account has been blocked. Please contact support for assistance.
      </AlertDescription>
    </Alert>

    <template v-else>
      <div class="mx-auto w-full max-w-[1440px] px-6 pt-4 sm:pt-5 [&_header]:mb-0">
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
          <div class="grid gap-x-3 gap-y-6 [grid-template-columns:repeat(auto-fill,minmax(220px,1fr))]">
            <ServiceCardSkeleton v-for="i in 8" :key="i" />
          </div>
        </section>

        <ServicesGrid
          v-else
          :services="services"
          :category="category"
          :search="search"
          @select="openDetail"
        />
      </div>
    </template>

    <ServiceDetailSheet
      v-if="detailFor"
      :service="detailFor"
      @close="detailFor = null"
      @booked="onBooked"
    />
  </div>
</template>

<script lang="ts" setup>
import {
  PhWarningCircle,
} from '@phosphor-icons/vue';
import { onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import PageHeader from "@/components/PageHeader.vue";
import LocationPicker from "@/components/marketplace/LocationPicker.vue";
import MarketplaceHero from "@/components/marketplace/MarketplaceHero.vue";
import ServiceCardSkeleton from "@/components/marketplace/ServiceCardSkeleton.vue";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";
import ServiceDetailSheet from "@/views/customer/ServiceDetailSheet.vue";
import ServicesGrid, { type Service } from "@/views/customer/ServicesGrid.vue";

const auth = useAuthStore();
const toasts = useNotificationsStore();
const route = useRoute();
const router = useRouter();

const services = ref<Service[]>([]);
const detailFor = ref<Service | null>(null);
const search = ref(String(route.query.search ?? ""));
const category = ref<string | null>(
  typeof route.query.category === "string" ? route.query.category : null,
);
const loading = ref(true);

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
    await fetchServices();
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

function openDetail(service: Service) {
  if (auth.is_blocked) {
    toasts.error("Account is blocked. Contact support to book services.");
    return;
  }
  detailFor.value = service;
}

function onBooked() {
  detailFor.value = null;
  toasts.success("Service booked — track it under My Requests");
}
</script>

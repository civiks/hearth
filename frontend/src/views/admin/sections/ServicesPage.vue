<template>
  <div class="px-4 py-4 sm:px-6 sm:py-8">
    <PageHeader title="Services" description="Catalog of services available to customers." />
    <ServicesTable
      :services="services"
      :loading="servicesLoading"
      @delete="deleteService"
      @changed="onChanged"
    />
  </div>
</template>

<script lang="ts" setup>
import { onMounted } from "vue";

import PageHeader from "@/components/PageHeader.vue";
import { useAdminData } from "@/composables/useAdminData";
import { useConfirm } from "@/composables/useConfirm";
import { ApiError, api } from "@/lib/api";
import { useNotificationsStore } from "@/stores/notifications";
import ServicesTable from "@/views/admin/ServicesTable.vue";

const { services, fetchServices, servicesLoading } = useAdminData();
const toasts = useNotificationsStore();
const { confirm } = useConfirm();

onMounted(fetchServices);

function onChanged() {
  toasts.success("Service saved");
  fetchServices();
}

async function deleteService(id: number) {
  if (!await confirm({
    title: "Delete this service?",
    description: "Customers won't be able to find or book this service anymore. Active bookings stay intact, but no new requests will come in. This can't be undone.",
    variant: "destructive",
    confirmLabel: "Delete service",
  })) return;
  try {
    await api.delete(`/api/services/${id}`);
    toasts.success("Service deleted");
    fetchServices();
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to delete service");
  }
}
</script>

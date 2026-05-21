<template>
  <div class="px-6 py-8">
    <ServicesTable
      :services="services"
      @delete="deleteService"
      @changed="onChanged"
    />
  </div>
</template>

<script lang="ts" setup>
import { onMounted } from "vue";

import { useAdminData } from "@/composables/useAdminData";
import { ApiError, api } from "@/lib/api";
import { useNotificationsStore } from "@/stores/notifications";
import ServicesTable from "@/views/admin/ServicesTable.vue";

const { services, fetchServices } = useAdminData();
const toasts = useNotificationsStore();

onMounted(fetchServices);

function onChanged() {
  toasts.success("Service saved");
  fetchServices();
}

async function deleteService(id: number) {
  if (!confirm("Delete this service?")) return;
  try {
    await api.delete(`/api/services/${id}`);
    toasts.success("Service deleted");
    fetchServices();
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to delete service");
  }
}
</script>

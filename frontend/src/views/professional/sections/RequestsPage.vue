<template>
  <div class="px-4 py-4 sm:px-6 sm:py-8">
    <ApprovalNotice
      v-if="auth.approval_status === 'pending' || auth.approval_status === 'rejected'"
      :kind="auth.approval_status as 'pending' | 'rejected'"
    />
    <RequestsTable
      v-else
      :requests="requests"
      :loading="loading"
      @update-status="updateRequestStatus"
    />
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from "vue";

import { ApiError, api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";
import ApprovalNotice from "@/views/professional/ApprovalNotice.vue";
import RequestsTable, { type ProRequest } from "@/views/professional/RequestsTable.vue";

const auth = useAuthStore();
const toasts = useNotificationsStore();

const requests = ref<ProRequest[]>([]);
const loading = ref(false);

onMounted(fetchData);

async function fetchData() {
  if (auth.approval_status !== "approved") return;
  loading.value = true;
  try {
    const all = await api.get<ProRequest[]>("/api/requests");
    requests.value = all.filter((r) => r.service_id === auth.service_id);
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to load data");
  } finally {
    loading.value = false;
  }
}

async function updateRequestStatus(requestId: number, status: string) {
  try {
    await api.put(`/api/requests/${requestId}`, { service_status: status });
    await fetchData();
    toasts.success("Status updated");
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to update status");
  }
}
</script>

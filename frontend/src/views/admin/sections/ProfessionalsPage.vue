<template>
  <div class="px-6 py-8">
    <ProfessionalsTable
      :professionals="professionals"
      @approve="(id) => updateApproval(id, 'approved')"
      @reject="(id) => updateApproval(id, 'rejected')"
      @delete="deleteUser"
    />
  </div>
</template>

<script lang="ts" setup>
import { onMounted } from "vue";

import { useAdminData } from "@/composables/useAdminData";
import { ApiError, api } from "@/lib/api";
import { useNotificationsStore } from "@/stores/notifications";
import ProfessionalsTable from "@/views/admin/ProfessionalsTable.vue";

const { professionals, fetchProfessionals } = useAdminData();
const toasts = useNotificationsStore();

onMounted(fetchProfessionals);

async function updateApproval(userId: number, status: string) {
  try {
    await api.put(`/api/users/${userId}`, { approval_status: status });
    const i = professionals.value.findIndex((u) => u.id === userId);
    if (i !== -1) professionals.value[i]!.approval_status = status;
    toasts.success(`User ${status}`);
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to update user");
  }
}

async function deleteUser(userId: number) {
  if (!confirm("Delete this user?")) return;
  try {
    await api.delete(`/api/users/${userId}`);
    professionals.value = professionals.value.filter((u) => u.id !== userId);
    toasts.success("User deleted");
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to delete user");
  }
}
</script>

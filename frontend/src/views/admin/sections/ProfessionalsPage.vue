<template>
  <div class="px-4 py-4 sm:px-6 sm:py-5">
    <PageHeader title="Professionals" description="Service providers registered on the platform." />
    <ProfessionalsTable
      :professionals="professionals"
      :loading="professionalsLoading"
      @approve="(id) => updateApproval(id, 'approved')"
      @reject="(id) => updateApproval(id, 'rejected')"
      @delete="deleteUser"
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
import ProfessionalsTable from "@/views/admin/ProfessionalsTable.vue";

const { professionals, fetchProfessionals, professionalsLoading } = useAdminData();
const toasts = useNotificationsStore();
const { confirm } = useConfirm();

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
  if (!await confirm({
    title: "Remove this professional?",
    description: "Their account, service history, and approval record will be permanently erased. Any open requests assigned to them will need to be reassigned. This can't be undone.",
    variant: "destructive",
    confirmLabel: "Remove professional",
  })) return;
  try {
    await api.delete(`/api/users/${userId}`);
    professionals.value = professionals.value.filter((u) => u.id !== userId);
    toasts.success("User deleted");
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to delete user");
  }
}
</script>

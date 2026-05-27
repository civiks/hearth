<template>
  <div class="px-4 py-4 sm:px-6 sm:py-8">
    <PageHeader title="Users" description="Registered customers on the platform." />
    <UsersTable :users="users" :loading="usersLoading" @toggle-block="toggleBlock" @delete="deleteUser" />
  </div>
</template>

<script lang="ts" setup>
import { onMounted } from "vue";

import PageHeader from "@/components/PageHeader.vue";
import { useAdminData } from "@/composables/useAdminData";
import { useConfirm } from "@/composables/useConfirm";
import { ApiError, api } from "@/lib/api";
import { useNotificationsStore } from "@/stores/notifications";
import type { AdminUser } from "@/views/admin/ProfessionalsTable.vue";
import UsersTable from "@/views/admin/UsersTable.vue";

const { users, fetchUsers, usersLoading } = useAdminData();
const toasts = useNotificationsStore();
const { confirm } = useConfirm();

onMounted(fetchUsers);

async function toggleBlock(user: AdminUser) {
  const next = !user.is_blocked;
  if (!await confirm({
    title: next ? "Block this user?" : "Unblock this user?",
    description: next
      ? "They'll be signed out immediately and won't be able to log in, place new requests, or contact professionals until you unblock them. Existing requests are preserved."
      : "They'll regain full access to the platform and can sign in and place bookings right away.",
    confirmLabel: next ? "Block user" : "Unblock user",
  })) return;
  try {
    await api.put(`/api/users/${user.id}`, { is_blocked: next });
    user.is_blocked = next;
    toasts.success(`User ${next ? "blocked" : "unblocked"}`);
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to update user");
  }
}

async function deleteUser(userId: number) {
  if (!await confirm({
    title: "Delete this user?",
    description: "Their account, booking history, saved addresses, and personal details will be permanently erased. This can't be undone.",
    variant: "destructive",
    confirmLabel: "Delete user",
  })) return;
  try {
    await api.delete(`/api/users/${userId}`);
    users.value = users.value.filter((u) => u.id !== userId);
    toasts.success("User deleted");
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to delete user");
  }
}
</script>

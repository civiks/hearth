<template>
  <div class="px-6 py-8">
    <UsersTable :users="users" @toggle-block="toggleBlock" @delete="deleteUser" />
  </div>
</template>

<script lang="ts" setup>
import { onMounted } from "vue";

import { useAdminData } from "@/composables/useAdminData";
import { ApiError, api } from "@/lib/api";
import { useNotificationsStore } from "@/stores/notifications";
import type { AdminUser } from "@/views/admin/ProfessionalsTable.vue";
import UsersTable from "@/views/admin/UsersTable.vue";

const { users, fetchUsers } = useAdminData();
const toasts = useNotificationsStore();

onMounted(fetchUsers);

async function toggleBlock(user: AdminUser) {
  const next = !user.is_blocked;
  if (!confirm(`${next ? "Block" : "Unblock"} this user?`)) return;
  try {
    await api.put(`/api/users/${user.id}`, { is_blocked: next });
    user.is_blocked = next;
    toasts.success(`User ${next ? "blocked" : "unblocked"}`);
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to update user");
  }
}

async function deleteUser(userId: number) {
  if (!confirm("Delete this user?")) return;
  try {
    await api.delete(`/api/users/${userId}`);
    users.value = users.value.filter((u) => u.id !== userId);
    toasts.success("User deleted");
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to delete user");
  }
}
</script>

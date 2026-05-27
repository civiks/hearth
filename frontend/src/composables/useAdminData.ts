import { ref } from "vue";

import { api } from "@/lib/api";
import { useNotificationsStore } from "@/stores/notifications";
import type { AdminService } from "@/views/admin/ServicesTable.vue";
import type { AdminUser } from "@/views/admin/ProfessionalsTable.vue";

const services = ref<AdminService[]>([]);
const professionals = ref<AdminUser[]>([]);
const users = ref<AdminUser[]>([]);
const servicesLoading = ref(false);
const professionalsLoading = ref(false);
const usersLoading = ref(false);

/**
 * Shared admin data store. Each section page can call `refresh()` for the slice
 * it needs without re-implementing fetchers.
 */
export function useAdminData() {
  const toasts = useNotificationsStore();

  async function fetchServices() {
    servicesLoading.value = true;
    try {
      services.value = await api.get<AdminService[]>("/api/services/all");
    } catch {
      toasts.error("Failed to load services");
    } finally {
      servicesLoading.value = false;
    }
  }

  async function fetchProfessionals() {
    professionalsLoading.value = true;
    try {
      professionals.value = await api.get<AdminUser[]>("/api/users?role=professional");
    } catch {
      toasts.error("Failed to load professionals");
    } finally {
      professionalsLoading.value = false;
    }
  }

  async function fetchUsers() {
    usersLoading.value = true;
    try {
      users.value = await api.get<AdminUser[]>("/api/users?role=user");
    } catch {
      toasts.error("Failed to load users");
    } finally {
      usersLoading.value = false;
    }
  }

  async function refreshAll() {
    await Promise.all([fetchServices(), fetchProfessionals(), fetchUsers()]);
  }

  return {
    services,
    professionals,
    users,
    servicesLoading,
    professionalsLoading,
    usersLoading,
    fetchServices,
    fetchProfessionals,
    fetchUsers,
    refreshAll,
  };
}

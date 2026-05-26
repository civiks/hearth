import { ref } from "vue";

import { api } from "@/lib/api";
import type { AdminService } from "@/views/admin/ServicesTable.vue";
import type { AdminUser } from "@/views/admin/ProfessionalsTable.vue";

const services = ref<AdminService[]>([]);
const professionals = ref<AdminUser[]>([]);
const users = ref<AdminUser[]>([]);

/**
 * Shared admin data store. Each section page can call `refresh()` for the slice
 * it needs without re-implementing fetchers.
 */
export function useAdminData() {
  async function fetchServices() {
    try {
      services.value = await api.get<AdminService[]>("/api/services/all");
    } catch (err) {
      console.error("services fetch failed", err);
    }
  }

  async function fetchProfessionals() {
    try {
      professionals.value = await api.get<AdminUser[]>("/api/users?role=professional");
    } catch (err) {
      console.error("professionals fetch failed", err);
    }
  }

  async function fetchUsers() {
    try {
      users.value = await api.get<AdminUser[]>("/api/users?role=user");
    } catch (err) {
      console.error("users fetch failed", err);
    }
  }

  async function refreshAll() {
    await Promise.all([fetchServices(), fetchProfessionals(), fetchUsers()]);
  }

  return {
    services,
    professionals,
    users,
    fetchServices,
    fetchProfessionals,
    fetchUsers,
    refreshAll,
  };
}

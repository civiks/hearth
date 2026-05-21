import { defineStore } from "pinia";
import { toast } from "vue-sonner";

export type ToastType = "success" | "error" | "info";

/**
 * Thin wrapper around vue-sonner so views can `useNotificationsStore().error(...)`
 * without importing sonner directly. The `<Toaster />` mounted in App.vue is
 * what actually renders the popups.
 */
export const useNotificationsStore = defineStore("notifications", {
  state: () => ({}),
  actions: {
    success(message: string, description?: string) {
      toast.success(message, { description });
    },
    error(message: string, description?: string) {
      toast.error(message, { description });
    },
    info(message: string, description?: string) {
      toast.info(message, { description });
    },
    push(message: string, type: ToastType = "success") {
      this[type](message);
    },
  },
});

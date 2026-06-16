import { computed, ref } from "vue";

interface ConfirmOptions {
  title: string;
  description?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: "destructive" | "default";
}

interface PendingConfirm extends ConfirmOptions {
  resolve: (value: boolean) => void;
}

const pending = ref<PendingConfirm | null>(null);

const hostCount = ref(0);
const hasHost = computed(() => hostCount.value > 0);

export function useConfirm() {
  function confirm(opts: ConfirmOptions): Promise<boolean> {
    return new Promise((resolve) => {
      pending.value = { ...opts, resolve };
    });
  }

  function settle(value: boolean) {
    pending.value?.resolve(value);
    pending.value = null;
  }

  function registerHost() {
    hostCount.value++;
  }

  function unregisterHost() {
    hostCount.value = Math.max(0, hostCount.value - 1);
  }

  return { confirm, pending, settle, hasHost, registerHost, unregisterHost };
}

import { ref } from "vue";

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

  return { confirm, pending, settle };
}

<template>
  <!-- Desktop: centered modal -->
  <Dialog v-if="isDesktop" :open="!!pending" @update:open="(v) => !v && settle(false)">
    <DialogContent :show-close-button="false" class="sm:max-w-sm gap-0 p-0 overflow-hidden rounded-[2.5rem]">
      <div class="space-y-2.5 px-7 pt-7 pb-3">
        <component :is="icon" :class="['size-12 mb-3', iconClass]" weight="bold" />
        <DialogTitle class="text-2xl leading-tight">{{ pending?.title }}</DialogTitle>
        <DialogDescription v-if="pending?.description" class="text-base leading-relaxed">
          {{ pending.description }}
        </DialogDescription>
      </div>
      <div class="px-7 pt-4 pb-7 flex gap-2.5">
        <Button variant="secondary" halo class="flex-1 rounded-full h-11" @click="settle(false)">
          {{ pending?.cancelLabel ?? "Cancel" }}
        </Button>
        <Button
          :variant="pending?.variant === 'destructive' ? 'destructive' : 'default'"
          halo
          class="flex-1 rounded-full h-11"
          @click="settle(true)"
        >
          {{ pending?.confirmLabel ?? "Confirm" }}
        </Button>
      </div>
    </DialogContent>
  </Dialog>

  <Drawer
    v-else-if="!hasHost"
    :open="!!pending"
    @update:open="(v) => !v && settle(false)"
  >
    <DrawerContent :host-confirm="false" :show-close="false">
      <ConfirmContent />
    </DrawerContent>
  </Drawer>
</template>

<script lang="ts" setup>
import { PhQuestion, PhWarning } from "@phosphor-icons/vue";
import { useMediaQuery } from "@vueuse/core";
import { computed } from "vue";

import ConfirmContent from "@/components/ConfirmContent.vue";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "@/components/ui/dialog";
import { Drawer, DrawerContent } from "@/components/ui/drawer";
import { useConfirm } from "@/composables/useConfirm";

const { pending, settle, hasHost } = useConfirm();
const isDesktop = useMediaQuery("(min-width: 640px)");

const isDestructive = computed(() => pending.value?.variant === "destructive");
const icon = computed(() => (isDestructive.value ? PhWarning : PhQuestion));
const iconClass = computed(() =>
  isDestructive.value ? "text-destructive" : "text-primary",
);
</script>

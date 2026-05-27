<template>
  <!-- Desktop: compact centered modal -->
  <Dialog v-if="isDesktop" :open="!!pending" @update:open="(v) => !v && settle(false)">
    <DialogContent :show-close-button="false" class="sm:max-w-xs gap-0 p-0 overflow-hidden">
      <div class="space-y-1 px-5 pt-5 pb-3">
        <DialogTitle>{{ pending?.title }}</DialogTitle>
        <DialogDescription v-if="pending?.description">
          {{ pending.description }}
        </DialogDescription>
      </div>
      <div class="px-5 pt-3 pb-5 flex gap-2">
        <Button variant="secondary" @click="settle(false)">
          {{ pending?.cancelLabel ?? "Cancel" }}
        </Button>
        <Button
          :variant="pending?.variant === 'destructive' ? 'destructive' : 'default'"
          class="flex-1"
          @click="settle(true)"
        >
          {{ pending?.confirmLabel ?? "Confirm" }}
        </Button>
      </div>
    </DialogContent>
  </Dialog>

  <Drawer
    v-else
    :open="!!pending"
    @update:open="(v) => !v && settle(false)"
  >
    <DrawerContent>
      <DrawerHeader>
        <DrawerTitle>{{ pending?.title }}</DrawerTitle>
        <DrawerDescription v-if="pending?.description">
          {{ pending.description }}
        </DrawerDescription>
      </DrawerHeader>
      <DrawerFooter>
        <Button variant="secondary" @click="settle(false)">
          {{ pending?.cancelLabel ?? "Cancel" }}
        </Button>
        <Button
          :variant="pending?.variant === 'destructive' ? 'destructive' : 'default'"
          class="flex-1"
          @click="settle(true)"
        >
          {{ pending?.confirmLabel ?? "Confirm" }}
        </Button>
      </DrawerFooter>
    </DrawerContent>
  </Drawer>
</template>

<script lang="ts" setup>
import { useMediaQuery } from "@vueuse/core";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer";
import { useConfirm } from "@/composables/useConfirm";

const { pending, settle } = useConfirm();
const isDesktop = useMediaQuery("(min-width: 640px)");
</script>

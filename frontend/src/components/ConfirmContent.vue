<template>
  <div class="flex flex-col">
    <div class="flex flex-col gap-1.5 px-5 pt-5 pb-3">
      <component :is="icon" :class="['size-12 mb-2 self-start', iconClass]" weight="bold" />
      <DrawerTitle class="text-2xl leading-tight font-display font-semibold tracking-tight">
        {{ pending?.title }}
      </DrawerTitle>
      <DrawerDescription
        v-if="pending?.description"
        class="text-muted-foreground text-base leading-relaxed"
      >
        {{ pending.description }}
      </DrawerDescription>
    </div>
    <div class="flex flex-row gap-2 px-5 pt-3 pb-5 [&>*]:min-h-12">
      <Button variant="secondary" class="flex-1 rounded-[2.5rem]!" @click="settle(false)">
        {{ pending?.cancelLabel ?? "Cancel" }}
      </Button>
      <Button
        :variant="pending?.variant === 'destructive' ? 'destructive' : 'default'"
        class="flex-1 rounded-[2.5rem]!"
        @click="settle(true)"
      >
        {{ pending?.confirmLabel ?? "Confirm" }}
      </Button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PhQuestion, PhWarning } from "@phosphor-icons/vue";
import { computed } from "vue";
import {
  DrawerDescription,
  DrawerTitle,
} from "vaul-vue";

import { Button } from "@/components/ui/button";
import { useConfirm } from "@/composables/useConfirm";

const { pending, settle } = useConfirm();

const isDestructive = computed(() => pending.value?.variant === "destructive");
const icon = computed(() => (isDestructive.value ? PhWarning : PhQuestion));
const iconClass = computed(() =>
  isDestructive.value ? "text-destructive" : "text-primary",
);
</script>

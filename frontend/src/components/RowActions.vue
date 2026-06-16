<template>
  <!-- Desktop: compact dropdown -->
  <DropdownMenu v-if="isDesktop">
    <DropdownMenuTrigger as-child>
      <Button variant="ghost" size="icon" aria-label="Open menu">
        <PhDotsThreeVertical class="size-4" weight="bold" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end">
      <DropdownMenuItem
        v-for="action in actions"
        :key="action.label"
        :variant="action.variant"
        @click="action.onClick"
      >
        <component :is="action.icon" class="mr-2 size-4" />
        {{ action.label }}
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>

  <!-- Mobile: bottom drawer with large tap targets -->
  <template v-else>
    <Button variant="ghost" size="icon" aria-label="Open menu" @click="open = true">
      <PhDotsThreeVertical class="size-4" weight="bold" />
    </Button>
    <Drawer :open="open" :should-scale-background="false" @update:open="(v) => !v && (open = false)">
      <DrawerContent class="p-0 gap-0" :show-close="false">
        <DrawerTitle class="sr-only">Actions</DrawerTitle>
        <div class="px-4 pt-5 pb-[max(1.25rem,env(safe-area-inset-bottom))] space-y-2.5">
          <Button
            v-for="action in actions"
            :key="action.label"
            :variant="action.variant === 'destructive' ? 'destructive-soft' : 'secondary'"
            class="w-full h-12"
            @click="onAction(action)"
          >
            <component :is="action.icon" class="size-4 shrink-0" />
            {{ action.label }}
          </Button>
        </div>
      </DrawerContent>
    </Drawer>
  </template>
</template>

<script lang="ts" setup>
import {
  PhDotsThreeVertical,
} from '@phosphor-icons/vue';
import { ref, watch, type Component } from "vue";
import { useMediaQuery } from "@vueuse/core";

import { Button } from "@/components/ui/button";
import { Drawer, DrawerContent, DrawerTitle } from "@/components/ui/drawer";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { useConfirm } from "@/composables/useConfirm";

export interface RowAction {
  label: string;
  icon: Component;
  onClick: () => void;
  variant?: "destructive";
  morphsInPlace?: boolean;
}

defineProps<{ actions: RowAction[] }>();

const isDesktop = useMediaQuery("(min-width: 640px)");
const open = ref(false);
const awaitingConfirm = ref(false);

const { pending, settle } = useConfirm();

function onAction(action: RowAction) {
  action.onClick();
  if (action.morphsInPlace) awaitingConfirm.value = true;
  else open.value = false;
}

watch(pending, (value) => {
  if (awaitingConfirm.value && value === null) {
    awaitingConfirm.value = false;
    open.value = false;
  }
});

watch(open, (value) => {
  if (!value && pending.value) settle(false);
});
</script>

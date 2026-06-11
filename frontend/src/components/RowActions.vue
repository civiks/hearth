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
    <Drawer :open="open" :should-scale-background="true" @update:open="(v) => !v && (open = false)">
      <DrawerContent class="p-0 gap-0">
        <DrawerTitle class="sr-only">Actions</DrawerTitle>
        <div class="px-4 pt-3 pb-4 space-y-3">
          <Button
            v-for="action in actions"
            :key="action.label"
            :variant="action.variant === 'destructive' ? 'destructive-soft' : 'secondary'"
            class="w-full h-12"
            @click="action.onClick(); open = false"
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
import { ref, type Component } from "vue";
import { useMediaQuery } from "@vueuse/core";

import { Button } from "@/components/ui/button";
import { Drawer, DrawerContent, DrawerTitle } from "@/components/ui/drawer";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";

export interface RowAction {
  label: string;
  icon: Component;
  onClick: () => void;
  variant?: "destructive";
}

defineProps<{ actions: RowAction[] }>();

const isDesktop = useMediaQuery("(min-width: 640px)");
const open = ref(false);
</script>

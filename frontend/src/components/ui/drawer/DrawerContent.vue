<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { DrawerContent, DrawerHandle, DrawerOverlay, DrawerPortal } from 'vaul-vue'
import { cn } from '@/lib/utils'

const props = defineProps<{ class?: HTMLAttributes['class'] }>()
</script>

<template>
  <DrawerPortal>
    <DrawerOverlay class="fixed inset-0 z-50 bg-black/40" />
    <DrawerContent data-slot="drawer-content" :class="cn('[--sheet-surface:hsl(var(--card))] bg-card dark:bg-card/88 dark:backdrop-blur-2xl text-card-foreground fixed inset-x-2 bottom-[max(0.5rem,env(safe-area-inset-bottom))] z-50 flex flex-col rounded-3xl outline-none max-h-[92svh] overflow-hidden shadow-2xl', props.class)">
      <DrawerHandle class="mx-auto mt-3 mb-1 h-1.5 w-10 shrink-0 rounded-full" />
      <slot />
    </DrawerContent>
  </DrawerPortal>
</template>

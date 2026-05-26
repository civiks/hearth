<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { DrawerContent, DrawerHandle, DrawerOverlay, DrawerPortal } from 'vaul-vue'
import { cn } from '@/lib/utils'

const props = defineProps<{ class?: HTMLAttributes['class'] }>()
</script>

<template>
  <DrawerPortal>
    <DrawerOverlay class="fixed inset-0 z-50 bg-black/40" />
    <DrawerContent :class="cn('bg-popover text-popover-foreground ring-foreground/10 fixed inset-x-2 bottom-2 z-50 flex flex-col rounded-3xl ring-1 outline-none max-h-[92svh] overflow-hidden shadow-2xl', props.class)">
      <DrawerHandle class="mx-auto mt-3 mb-1 h-1.5 w-10 shrink-0 rounded-full bg-muted-foreground/25" />
      <slot />
    </DrawerContent>
  </DrawerPortal>
</template>

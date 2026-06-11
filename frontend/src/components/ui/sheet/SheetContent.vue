<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { DialogContent, DialogOverlay, DialogPortal } from 'reka-ui'
import { cn } from '@/lib/utils'

const props = defineProps<{ class?: HTMLAttributes['class'] }>()
</script>

<template>
  <DialogPortal>
    <DialogOverlay class="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 duration-200" />
    <DialogContent :class="cn('[--sheet-surface:hsl(var(--popover))] bg-popover text-popover-foreground ring-foreground/10 fixed inset-y-0 right-0 z-50 flex flex-col ring-1 outline-none w-full max-w-lg data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:slide-out-to-right data-[state=open]:slide-in-from-right duration-200', props.class)">
      <slot />
    </DialogContent>
  </DialogPortal>
</template>

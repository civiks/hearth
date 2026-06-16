<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { onMounted, onUnmounted } from 'vue'
import { DrawerContent, DrawerHandle, DrawerOverlay, DrawerPortal } from 'vaul-vue'
import ConfirmContent from '@/components/ConfirmContent.vue'
import DrawerMorph from '@/components/ui/DrawerMorph.vue'
import { useConfirm } from '@/composables/useConfirm'
import { cn } from '@/lib/utils'

const props = withDefaults(
  defineProps<{ class?: HTMLAttributes['class']; hostConfirm?: boolean }>(),
  { hostConfirm: true },
)

const { pending, registerHost, unregisterHost } = useConfirm()
onMounted(() => { if (props.hostConfirm) registerHost() })
onUnmounted(() => { if (props.hostConfirm) unregisterHost() })
</script>

<template>
  <DrawerPortal>
    <DrawerOverlay class="fixed inset-0 z-50 bg-black/40" />
    <DrawerContent data-slot="drawer-content" :class="cn('[--sheet-surface:hsl(var(--card))] bg-card dark:bg-card/88 dark:backdrop-blur-2xl text-card-foreground fixed inset-x-2 bottom-[max(0.5rem,env(safe-area-inset-bottom))] z-50 flex flex-col rounded-[2.5rem] outline-none max-h-[92svh] overflow-hidden shadow-2xl', props.class)">
      <DrawerHandle class="mx-auto mt-3 mb-1 h-1.5 w-10 shrink-0 rounded-full" />
      <DrawerMorph v-if="hostConfirm">
        <ConfirmContent v-if="pending" key="confirm" />
        <div v-else key="content" class="flex min-h-0 max-h-[85svh] flex-col">
          <slot />
        </div>
      </DrawerMorph>
      <slot v-else />
    </DrawerContent>
  </DrawerPortal>
</template>

<script setup lang="ts">
import type { PrimitiveProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import type { ButtonVariants } from '.'
import { Primitive } from 'reka-ui'
import { cn } from '@/lib/utils'
import { buttonVariants } from '.'

interface Props extends PrimitiveProps {
  variant?: ButtonVariants['variant']
  size?: ButtonVariants['size']
  /** Variant-matched focus/active halo (via `--halo`), for emphasised CTAs. */
  halo?: boolean
  class?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<Props>(), {
  as: 'button',
})

// Ring shown on focus/active, tinted to the variant's `--halo`; swaps the inset focus shadow.
const haloClass
  = 'focus-visible:shadow-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-[hsl(var(--popover))] focus-visible:ring-[hsl(var(--halo,var(--primary))_/_0.55)] '
    + 'active:ring-2 active:ring-offset-2 active:ring-offset-[hsl(var(--popover))] active:ring-[hsl(var(--halo,var(--primary))_/_0.55)]'
</script>

<template>
  <Primitive
    data-slot="button"
    :data-variant="variant"
    :data-size="size"
    :as="as"
    :as-child="asChild"
    :class="cn(buttonVariants({ variant, size }), halo && haloClass, props.class)"
  >
    <slot />
  </Primitive>
</template>

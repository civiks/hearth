import { type HTMLAttributes, defineComponent, h } from 'vue'
import {
  DrawerClose as VaulClose,
  DrawerDescription as VaulDescription,
  DrawerTitle as VaulTitle,
} from 'vaul-vue'
import { cn } from '@/lib/utils'

export { DrawerRoot as Drawer } from 'vaul-vue'
export { VaulClose as DrawerClose }
export { default as DrawerContent } from './DrawerContent.vue'

export const DrawerHeader = defineComponent({
  props: { class: String as () => HTMLAttributes['class'] },
  setup: (p, { slots }) => () => h('div', { class: cn('flex flex-col gap-1 px-5 pt-5 pb-3', p.class) }, slots.default?.()),
})

export const DrawerFooter = defineComponent({
  props: { class: String as () => HTMLAttributes['class'] },
  setup: (p, { slots }) => () => h('div', { class: cn('flex flex-row gap-2 px-5 pt-3 pb-5', p.class) }, slots.default?.()),
})

export const DrawerTitle = defineComponent({
  setup: (_, { slots, attrs }) => () => h(VaulTitle, { class: cn('text-base font-medium leading-none', attrs.class as string) }, slots),
})

export const DrawerDescription = defineComponent({
  setup: (_, { slots, attrs }) => () => h(VaulDescription, { class: cn('text-muted-foreground text-sm', attrs.class as string) }, slots),
})

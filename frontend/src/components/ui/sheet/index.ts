import { type HTMLAttributes, defineComponent, h } from 'vue'
import { DialogTitle, DialogDescription } from 'reka-ui'
import { cn } from '@/lib/utils'

export { DialogRoot as Sheet, DialogClose as SheetClose } from 'reka-ui'
export { default as SheetContent } from './SheetContent.vue'

export const SheetHeader = defineComponent({
  props: { class: String as () => HTMLAttributes['class'] },
  setup: (p, { slots }) =>
    () => h('div', { class: cn('flex flex-col gap-1.5 px-5 pt-5 pb-4 border-b', p.class) }, slots.default?.()),
})

export const SheetTitle = defineComponent({
  setup: (_, { slots, attrs }) =>
    () => h(DialogTitle, { class: cn('text-lg font-semibold leading-snug tracking-tight font-display', attrs.class as string) }, slots),
})

export const SheetDescription = defineComponent({
  setup: (_, { slots, attrs }) =>
    () => h(DialogDescription, { class: cn('text-muted-foreground text-sm leading-relaxed', attrs.class as string) }, slots),
})

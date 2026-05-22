import type { VariantProps } from 'class-variance-authority'
import { cva } from 'class-variance-authority'

export { default as Button } from './Button.vue'

export const buttonVariants = cva(
  // -style focus: 2px solid inset primary outline (drawn inside the button bounds, never clipped).
  // Hover/active per-variant. Click also briefly compresses via active:scale-[0.98] on icon buttons for tactile feedback.
  'group/button inline-flex shrink-0 items-center justify-center whitespace-nowrap text-sm font-normal cursor-pointer transition-colors outline-none select-none border border-transparent [&_svg:not([class*=size-])]:size-4 [&_svg]:pointer-events-none [&_svg]:shrink-0 focus-visible:outline-none focus-visible:shadow-[inset_0_0_0_2px_hsl(var(--primary))] disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 aria-invalid:border-destructive',
  {
    variants: {
      variant: {
        // Primary —  blue-60, hover blue-70, active blue-80.
        default: 'bg-primary text-primary-foreground hover:bg-[#0353e9] active:bg-[#002d9c]',
        outline: 'border-primary text-primary bg-transparent hover:bg-primary hover:text-primary-foreground active:bg-[#002d9c] active:text-primary-foreground aria-expanded:bg-primary aria-expanded:text-primary-foreground',
        // Secondary —  gray-80 fill + white text, hover gray-70, active gray-60.
        secondary: 'bg-[#393939] text-white hover:bg-[#4c4c4c] active:bg-[#6f6f6f] aria-expanded:bg-[#4c4c4c]',
        // Ghost — for low-emphasis actions inside cards/menus.
        ghost: 'hover:bg-foreground/10 hover:text-foreground active:shadow-[inset_0_0_0_2px_hsl(var(--primary))] aria-expanded:shadow-[inset_0_0_0_2px_hsl(var(--primary))]',
        // Danger —  red-60 fill, hover red-70, active red-80, inset destructive focus.
        destructive: 'bg-destructive text-destructive-foreground hover:bg-[#b81921] active:bg-[#750e13] focus-visible:shadow-[inset_0_0_0_2px_hsl(var(--destructive))]',
        link: 'text-primary underline-offset-4 hover:underline border-transparent focus-visible:shadow-none focus-visible:underline',
      },
      size: {
        'default': 'h-10 gap-1.5 px-4 has-data-[icon=inline-end]:pr-3 has-data-[icon=inline-start]:pl-3',
        'xs': 'h-6 gap-1 px-2 text-xs [&_svg:not([class*=size-])]:size-3',
        'sm': 'h-8 gap-1 px-3 text-[0.8rem] [&_svg:not([class*=size-])]:size-3.5',
        'lg': 'h-11 gap-1.5 px-5',
        'icon': 'size-10',
        'icon-xs': 'size-6 [&_svg:not([class*=size-])]:size-3',
        'icon-sm': 'size-8',
        'icon-lg': 'size-11',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)
export type ButtonVariants = VariantProps<typeof buttonVariants>

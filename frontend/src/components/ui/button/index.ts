import type { VariantProps } from 'class-variance-authority'
import { cva } from 'class-variance-authority'

export { default as Button } from './Button.vue'

export const buttonVariants = cva(
  'group/button inline-flex shrink-0 items-center justify-center whitespace-nowrap text-sm font-normal cursor-pointer transition-colors outline-none select-none border border-transparent [&_svg:not([class*=size-])]:size-4 [&_svg]:pointer-events-none [&_svg]:shrink-0 focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-primary disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 aria-invalid:border-destructive',
  {
    variants: {
      variant: {
        // Primary — Carbon blue-60, hover blue-70.
        default: 'bg-primary text-primary-foreground hover:bg-[#0353e9]',
        // Tertiary — Carbon outline button (transparent fill, primary border + text, fills on hover).
        outline: 'border-primary text-primary bg-transparent hover:bg-primary hover:text-primary-foreground aria-expanded:bg-primary aria-expanded:text-primary-foreground',
        // Secondary — Carbon gray-80 fill + white text, hover gray-70.
        secondary: 'bg-[#393939] text-white hover:bg-[#4c4c4c] aria-expanded:bg-[#4c4c4c]',
        // Ghost — for low-emphasis actions inside cards/menus.
        ghost: 'hover:bg-muted hover:text-foreground aria-expanded:bg-muted aria-expanded:text-foreground',
        // Danger — Carbon red-60 fill, hover red-70.
        destructive: 'bg-destructive text-destructive-foreground hover:bg-[#b81921] focus-visible:outline-destructive',
        link: 'text-primary underline-offset-4 hover:underline border-transparent',
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

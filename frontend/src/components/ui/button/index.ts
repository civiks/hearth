import type { VariantProps } from 'class-variance-authority'
import { cva } from 'class-variance-authority'

export { default as Button } from './Button.vue'

export const buttonVariants = cva(
  // -style focus: 2px solid inset primary outline (drawn inside the button bounds, never clipped).
  // `press` carries the color/shadow transitions and the scale-on-active feedback.
  'group/button inline-flex shrink-0 items-center justify-center whitespace-nowrap text-sm font-normal cursor-pointer press outline-none select-none rounded-md border border-transparent [&_svg:not([class*=size-])]:size-4 [&_svg]:pointer-events-none [&_svg]:shrink-0 focus-visible:outline-none focus-visible:shadow-[inset_0_0_0_2px_hsl(var(--primary))] disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 aria-invalid:border-destructive',
  {
    variants: {
      variant: {
        // `--halo` tints the optional Button `halo` ring to match each variant's fill.
        default: '[--halo:var(--primary)] bg-button-primary text-primary-foreground hover:bg-button-primary-hover active:bg-button-primary-active btn-glow',
        outline: '[--halo:var(--primary)] border-primary text-primary bg-transparent hover:bg-primary hover:text-primary-foreground active:bg-primary-active active:text-primary-foreground aria-expanded:bg-primary aria-expanded:text-primary-foreground',
        // Secondary — theme-aware: dark theme inherits gray-80 hover→gray-70; light theme uses gray-20 hover→gray-30.
        secondary: '[--halo:var(--muted-foreground)] bg-secondary text-secondary-foreground hover:bg-secondary-hover active:bg-secondary-active aria-expanded:bg-secondary-hover',
        // Ghost — for low-emphasis actions inside cards/menus.
        ghost: '[--halo:var(--muted-foreground)] hover:bg-foreground/10 hover:text-foreground active:shadow-[inset_0_0_0_2px_hsl(var(--primary))] aria-expanded:shadow-[inset_0_0_0_2px_hsl(var(--primary))]',
        // Danger — red-60 fill, hover red-70, active red-80, inset destructive focus.
        destructive: '[--halo:var(--destructive)] bg-destructive text-destructive-foreground hover:bg-destructive-hover active:bg-destructive-active focus-visible:shadow-[inset_0_0_0_2px_hsl(var(--destructive))]',
        // Soft danger — tinted background, works on both light and dark surfaces without being too bright.
        'destructive-soft': '[--halo:var(--destructive)] bg-destructive/12 text-destructive hover:bg-destructive/20 active:bg-destructive/25 focus-visible:shadow-[inset_0_0_0_2px_hsl(var(--destructive))]',
        // Soft primary — tinted background for low-emphasis primary actions (e.g. back buttons).
        'primary-soft': '[--halo:var(--primary)] bg-primary/10 text-primary hover:bg-primary/18 active:bg-primary/25',
        link: '[--press-scale:1] text-primary underline-offset-4 hover:underline border-transparent focus-visible:shadow-none focus-visible:underline',
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

<template>
  <main
    class="relative min-h-dvh bg-background flex items-center justify-center px-8 py-12 sm:px-12 overflow-hidden"
  >
    <div
      class="pointer-events-none absolute inset-x-0 bottom-0 h-64 bg-gradient-to-t from-blue-500/15 via-blue-500/5 to-transparent dark:from-blue-400/20 dark:via-blue-400/5"
      aria-hidden="true"
    />

    <slot />

    <footer
      class="pointer-events-none absolute bottom-4 left-0 right-0 text-center text-xs text-muted-foreground"
    >
</footer>
  </main>
</template>

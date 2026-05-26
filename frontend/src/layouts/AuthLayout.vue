<template>
  <main
    class="relative min-h-svh bg-background flex items-center justify-center px-6 py-10"
  >
    <slot />

    <footer
      class="pointer-events-none absolute bottom-4 left-0 right-0 text-center text-xs text-muted-foreground"
    >
      <!-- © 2026 hearth · Delhi, India -->
    </footer>
  </main>
</template>

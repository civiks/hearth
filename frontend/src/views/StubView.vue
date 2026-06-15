<template>
  <div class="mx-auto max-w-2xl px-6 py-16">
    <span class="inline-flex items-center rounded-full bg-muted px-3 py-1 text-xs font-medium tracking-tight text-muted-foreground">
      Coming soon
    </span>
    <h1 class="mt-5 font-display text-3xl font-light tracking-tight">{{ $route.meta.heading }}</h1>
    <p class="mt-4 text-sm leading-relaxed text-muted-foreground">{{ $route.meta.body }}</p>

    <div class="mt-8 flex flex-wrap gap-3">
      <Button as-child class="rounded-full"><RouterLink to="/register">Get started</RouterLink></Button>
      <Button as-child variant="ghost" class="rounded-full"><RouterLink to="/">Back home</RouterLink></Button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { RouterLink } from "vue-router";

import { Button } from "@/components/ui/button";
</script>

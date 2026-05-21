<template>
  <section class="mx-auto max-w-7xl px-6 py-16 border-t">
    <h2 class="text-2xl font-light tracking-tight text-center mb-10">How it works</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div v-for="(step, i) in steps" :key="step.title" class="text-center space-y-3">
        <div
          class="size-12 mx-auto bg-primary/10 flex items-center justify-center"
        >
          <component :is="step.icon" class="size-5 text-primary" />
        </div>
        <div class="text-xs text-primary font-medium tracking-wide">
          STEP {{ i + 1 }}
        </div>
        <h3 class="text-base font-medium">{{ step.title }}</h3>
        <p class="text-sm text-muted-foreground max-w-xs mx-auto">{{ step.body }}</p>
      </div>
    </div>
  </section>
</template>

<script lang="ts" setup>
import { CalendarCheck, MousePointerClick, Sparkles } from "lucide-vue-next";

const steps = [
  {
    icon: MousePointerClick,
    title: "Choose a service",
    body: "Browse 18+ verified household services and pick one that fits your need.",
  },
  {
    icon: CalendarCheck,
    title: "Book in seconds",
    body: "Choose a pro, lock in your time slot, and add any specific notes for the job.",
  },
  {
    icon: Sparkles,
    title: "Sit back",
    body: "Your professional arrives on time with the right tools. Pay after the job is done.",
  },
];
</script>

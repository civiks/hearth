<template>
  <section class="mx-auto max-w-7xl px-6 py-10 sm:py-16">
    <h2 class="text-2xl font-medium tracking-tight mb-8 sm:mb-10">How it works</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-5">
      <div
        v-for="step in steps"
        :key="step.title"
        class="bg-card rounded-xl soft-card p-6 sm:p-7 space-y-3"
      >
        <div
          class="inline-flex size-10 items-center justify-center rounded-full text-white"
          :class="step.iconBg"
        >
          <component :is="step.icon" class="size-5" :stroke-width="2" />
        </div>
        <h3 class="text-base font-semibold">{{ step.title }}</h3>
        <p class="text-sm text-muted-foreground leading-relaxed">
          {{ step.body }}
        </p>
      </div>
    </div>
  </section>
</template>

<script lang="ts" setup>
import { CalendarCheck, MousePointerClick, Sparkles } from "lucide-vue-next";

const steps = [
  {
    icon: MousePointerClick,
    iconBg: "bg-blue-500",
    title: "Choose a service",
    body: "Browse 18+ verified household services and pick one that fits your need.",
  },
  {
    icon: CalendarCheck,
    iconBg: "bg-violet-500",
    title: "Book in seconds",
    body: "Choose a pro, lock in your time slot, and add any specific notes for the job.",
  },
  {
    icon: Sparkles,
    iconBg: "bg-emerald-500",
    title: "Sit back",
    body: "Your professional arrives on time with the right tools. Pay after the job is done.",
  },
];
</script>

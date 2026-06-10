<template>
  <section class="mx-auto max-w-7xl px-6 py-10 sm:py-16">
    <h2 class="font-display text-2xl sm:text-3xl font-semibold tracking-[-0.02em] text-balance mb-8 sm:mb-10">
      How it works
    </h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-5">
      <div
        v-for="step in steps"
        :key="step.title"
        class="bg-card rounded-xl soft-card card-tilt p-6 sm:p-7 space-y-3"
      >
        <div
          class="inline-flex size-10 items-center justify-center rounded-full text-white"
          :class="step.iconBg"
        >
          <component :is="step.icon" class="size-5" :stroke-width="2" />
        </div>
        <h3 class="text-base font-semibold tracking-tight">{{ step.title }}</h3>
        <p class="text-sm tracking-tight leading-relaxed text-muted-foreground">
          {{ step.body }}
        </p>
      </div>
    </div>
  </section>
</template>

<script lang="ts" setup>
import { BadgeCheck, CalendarCheck, MousePointerClick } from "@lucide/vue";

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
    icon: BadgeCheck,
    iconBg: "bg-emerald-500",
    title: "Sit back",
    body: "Your professional arrives on time with the right tools. Pay after the job is done.",
  },
];
</script>

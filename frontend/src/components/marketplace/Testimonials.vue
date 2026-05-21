<template>
  <section class="mx-auto max-w-7xl px-6 py-16 border-t">
    <h2 class="text-2xl font-light tracking-tight text-center mb-10">
      What our customers say
    </h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <article
        v-for="t in testimonials"
        :key="t.name"
        class="bg-card p-6 space-y-4"
      >
        <div class="flex items-center gap-1">
          <Star
            v-for="i in 5"
            :key="i"
            class="size-4 fill-amber-400 text-amber-400"
          />
        </div>
        <p class="text-sm leading-relaxed">"{{ t.quote }}"</p>
        <div class="flex items-center gap-3 pt-2 border-t">
          <ProfessionalAvatar :name="t.name" class="size-9" />
          <div>
            <div class="text-sm font-medium">{{ t.name }}</div>
            <div class="text-xs text-muted-foreground">{{ t.role }}</div>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script lang="ts" setup>
import { Star } from "lucide-vue-next";

import ProfessionalAvatar from "@/components/marketplace/ProfessionalAvatar.vue";

const testimonials = [
  {
    name: "Anitha Bose",
    role: "Customer in HSR Layout",
    quote:
      "Booked an AC service at 9 AM. Technician was at my door before noon with the right gas and a new filter. Will use again.",
  },
  {
    name: "Karan Vyas",
    role: "Customer in Indiranagar",
    quote:
      "I picked the carpenter I wanted from the list. Loved being able to see ratings and years of experience before booking.",
  },
  {
    name: "Priya Iyer",
    role: "Customer in Koramangala",
    quote:
      "Their cleaning team handled my move-out spotlessly. Honest pricing, no last-minute surprises on the invoice.",
  },
];
</script>

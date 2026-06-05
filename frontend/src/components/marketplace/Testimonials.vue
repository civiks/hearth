<template>
  <section class="mx-auto max-w-7xl px-6 py-10 sm:py-16">
    <div class="max-w-2xl mb-10 sm:mb-12">
      <h2 class="font-display text-2xl sm:text-3xl font-semibold tracking-[-0.02em] text-balance">
        What our customers say
      </h2>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
      <article
        v-for="t in testimonials"
        :key="t.name"
        class="bg-card rounded-xl soft-card hover:soft-card-hover transition-shadow p-7 sm:p-8 flex flex-col gap-6"
      >
        <div class="flex items-center gap-0.5">
          <Star
            v-for="i in 5"
            :key="i"
            class="size-3 fill-amber-400 text-amber-400"
          />
        </div>
        <p class="text-lg leading-[1.7] tracking-tight text-muted-foreground flex-1">
          <template v-for="(part, i) in t.parts" :key="i"
            ><span v-if="part.highlight" class="font-medium text-foreground">{{
              part.text
            }}</span
            ><template v-else>{{ part.text }}</template></template
          >
        </p>
        <div class="flex items-center gap-3 pt-5 border-t">
          <ProfessionalAvatar :name="t.name" class="size-9" />
          <div>
            <div class="text-sm font-medium tracking-tight text-foreground">{{ t.name }}</div>
            <div class="text-xs tracking-tight text-muted-foreground">{{ t.role }}</div>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script lang="ts" setup>
import { Star } from "lucide-vue-next";

import ProfessionalAvatar from "@/components/marketplace/ProfessionalAvatar.vue";

type QuotePart = { text: string; highlight?: boolean };

const testimonials: {
  name: string;
  role: string;
  parts: QuotePart[];
}[] = [
  {
    name: "Anitha Bose",
    role: "Mahipalpur",
    parts: [
      { text: "Booked an AC service at 9 AM. Technician was at my door " },
      { text: "before noon", highlight: true },
      { text: " with the right gas and a new filter. Will use again." },
    ],
  },
  {
    name: "Karan Vyas",
    role: "Indiranagar",
    parts: [
      { text: "I picked the carpenter I wanted from the list. Loved being able to see " },
      { text: "ratings and years of experience", highlight: true },
      { text: " before booking." },
    ],
  },
  {
    name: "Priya Iyer",
    role: "Koramangala",
    parts: [
      { text: "Their cleaning team handled my move-out spotlessly. " },
      { text: "Honest pricing", highlight: true },
      { text: ", no last-minute surprises on the invoice." },
    ],
  },
];
</script>

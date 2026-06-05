<template>
  <Avatar :class="size">
    <AvatarImage v-if="src" :src="src" :alt="name" />
    <AvatarFallback :class="cn(variantClass, fallbackClass)">{{ initialsText }}</AvatarFallback>
  </Avatar>
</template>

<script lang="ts" setup>
import { computed } from "vue";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { initials } from "@/lib/format";
import { cn } from "@/lib/utils";

export type AvatarVariant = "primary" | "success" | "warning" | "danger" | "info";

const props = withDefaults(
  defineProps<{
    name?: string;
    src?: string | null;
    variant?: AvatarVariant;
    size?: string;
    fallbackClass?: string;
  }>(),
  { name: "", src: null, variant: "primary", size: "size-9", fallbackClass: "" },
);

const initialsText = computed(() => initials(props.name));
const variantClass = computed(() => {
  switch (props.variant) {
    case "success":
      return "bg-success/15 text-success";
    case "warning":
      return "bg-warning/20 text-foreground";
    case "danger":
      return "bg-destructive/15 text-destructive";
    case "info":
      return "bg-info/15 text-info";
    default:
      return "bg-primary text-primary-foreground";
  }
});
</script>

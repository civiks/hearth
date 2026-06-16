<template>
  <component
    :is="isDesktop ? Sheet : Drawer"
    :open="open"
    v-bind="isDesktop ? {} : { shouldScaleBackground: false }"
    @update:open="(v: boolean) => !v && $emit('close')"
  >
    <component
      :is="isDesktop ? SheetContent : DrawerContent"
      :class="contentClass"
    >
      <slot name="header">
        <div v-if="hasHeader" :class="headerClasses">
          <component :is="TitleComp">
            <slot name="title">{{ title }}</slot>
          </component>
          <component v-if="hasDescription" :is="DescriptionComp">
            <slot name="description">{{ description }}</slot>
          </component>
        </div>
      </slot>

      <div :class="bodyClasses" data-vaul-no-drag>
        <slot />
      </div>

      <div v-if="$slots.footer" class="sheet-footer">
        <slot name="footer" />
      </div>
    </component>
  </component>
</template>

<script lang="ts" setup>
import { computed, useSlots } from "vue";
import { useMediaQuery } from "@vueuse/core";

import { Drawer, DrawerContent, DrawerDescription, DrawerTitle } from "@/components/ui/drawer";
import { Sheet, SheetContent, SheetDescription, SheetTitle } from "@/components/ui/sheet";
import { cn } from "@/lib/utils";

interface Props {
  open: boolean;
  title?: string | null;
  description?: string | null;
  contentClass?: string;
  bodyClass?: string;
}

const props = defineProps<Props>();
defineEmits<{ close: [] }>();

const slots = useSlots();
const isDesktop = useMediaQuery("(min-width: 640px)");

const TitleComp = computed(() => (isDesktop.value ? SheetTitle : DrawerTitle));
const DescriptionComp = computed(() =>
  isDesktop.value ? SheetDescription : DrawerDescription,
);

const hasHeader = computed(
  () => !!(props.title || slots.title || props.description || slots.description),
);
const hasDescription = computed(() => !!(props.description || slots.description));

const headerClasses = computed(() =>
  isDesktop.value
    ? "flex flex-col gap-1.5 px-5 pt-5 pb-4 pr-14"
    : "flex flex-col gap-1.5 px-5 pt-5 pr-14",
);

const bodyClasses = computed(() =>
  cn(
    "flex-1 overflow-y-auto min-h-0 px-5 pt-5 space-y-4",
    slots.footer ? "pb-24" : "pb-5",
    props.bodyClass,
  ),
);
</script>

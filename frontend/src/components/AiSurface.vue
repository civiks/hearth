<template>
  <!--
    Wraps any AI-feature container with the AI surface gradient
    + blue outline. Polymorphic via `as` so it can render as div, button, etc.
    Consumer classes are merged onto the root element.
  -->
  <component
    :is="as"
    v-bind="$attrs"
    :class="['ai-surface ai-outline rounded-lg', $attrs.class]"
  >
    <slot />
  </component>
</template>

<script lang="ts" setup>
withDefaults(defineProps<{ as?: string }>(), { as: "div" });
defineOptions({ inheritAttrs: false });
</script>

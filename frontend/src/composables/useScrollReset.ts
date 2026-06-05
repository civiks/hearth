import { watch, type Ref } from "vue";
import { useRoute } from "vue-router";

export function useScrollReset(el: Ref<HTMLElement | null>) {
  const route = useRoute();
  watch(
    () => route.path,
    () => {
      el.value?.scrollTo({ top: 0 });
      window.scrollTo({ top: 0 });
    },
  );
}

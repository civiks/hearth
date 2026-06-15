import type { Directive } from "vue";

const REVEAL_IN = "reveal-in";

let observer: IntersectionObserver | null = null;

function getObserver(): IntersectionObserver | null {
  if (typeof IntersectionObserver === "undefined") return null;
  observer ??= new IntersectionObserver(
    (entries, obs) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add(REVEAL_IN);
          obs.unobserve(entry.target);
        }
      }
    },
    { rootMargin: "0px 0px -10% 0px", threshold: 0.05 },
  );
  return observer;
}

export const vReveal: Directive<HTMLElement, number | undefined> = {
  mounted(el, binding) {
    el.classList.add("reveal");
    if (binding.value) {
      el.style.setProperty("--reveal-delay", `${binding.value}ms`);
    }

    const obs = getObserver();
    if (!obs) {
      el.classList.add(REVEAL_IN);
      return;
    }
    obs.observe(el);
  },
  unmounted(el) {
    observer?.unobserve(el);
  },
};

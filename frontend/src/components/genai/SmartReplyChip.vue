<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <button
        type="button"
        class="inline-flex items-center gap-1.5 px-2 py-1 text-[11px] text-foreground ai-surface ai-outline hover:brightness-105 transition"
        :aria-label="`AI reply suggestions for request ${requestId}`"
      >
        <AiMark class="size-3" />
        Suggest reply
      </button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end" class="w-72">
      <DropdownMenuLabel class="text-xs font-normal text-muted-foreground">
        Pick a reply to send
      </DropdownMenuLabel>
      <DropdownMenuSeparator />
      <DropdownMenuItem
        v-for="(s, i) in suggestions"
        :key="i"
        class="text-xs whitespace-normal items-start gap-2 cursor-pointer"
        @click="onPick(s)"
      >
        <Send class="size-3 shrink-0 mt-0.5 text-primary" />
        <span>{{ s }}</span>
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>

<script lang="ts" setup>
import { Send } from "@lucide/vue";
import { computed } from "vue";

import AiMark from "@/components/AiMark.vue";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const props = defineProps<{
  requestId: number;
  remarks?: string | null;
  basePrice?: number | null;
  customerName?: string | null;
}>();

const emit = defineEmits<{ pick: [reply: string] }>();

const suggestions = computed(() => {
  const name = props.customerName ?? "there";
  const price = props.basePrice ? `₹${props.basePrice}` : "the quoted rate";
  const remarks = (props.remarks ?? "").toLowerCase();
  const complex = /\b(broken|replace|install|new|leak|stop|short|smoke|burn)\b/.test(remarks);
  const fast = /\b(urgent|asap|today|emergency|now)\b/.test(remarks);

  const base = [
    `Hi ${name}, I can be there in about 30 minutes — quoting ${price} to start.`,
  ];
  if (complex) {
    base.push(
      `Hi ${name}, this likely needs a quick inspection first. Can swing by today afternoon to scope it out.`,
    );
  }
  if (fast) {
    base.push(
      `On my way — should reach you within the hour. I'll confirm the final quote on-site.`,
    );
  }
  if (base.length < 3) {
    base.push(
      `Hi ${name}, fully booked today — can take this first thing tomorrow morning if that works.`,
    );
  }
  return base.slice(0, 3);
});

function onPick(text: string) {
  emit("pick", text);
}
</script>

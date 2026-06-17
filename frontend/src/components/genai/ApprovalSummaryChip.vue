<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <button
        type="button"
        class="inline-flex items-center gap-1.5 px-2 py-1 text-[11px] text-foreground ai-surface ai-outline hover:brightness-105 press transition"
        :aria-label="`AI summary for ${professional.full_name}`"
      >
        <AiMark class="size-3" />
        Summary
      </button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end" class="w-80 p-3 space-y-3">
      <div class="space-y-1">
        <div class="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Synthesis
        </div>
        <p class="text-sm leading-snug">{{ synthesis }}</p>
      </div>

      <div v-if="flags.length" class="space-y-1.5">
        <div class="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Risk flags
        </div>
        <div class="flex flex-wrap gap-1">
          <Badge
            v-for="f in flags"
            :key="f.label"
            :variant="f.severity === 'high' ? 'destructive' : 'secondary'"
            class="text-[10px] font-normal"
          >
            <PhWarning v-if="f.severity === 'high'" class="size-3 mr-1" weight="bold" />
            {{ f.label }}
          </Badge>
        </div>
      </div>

      <div class="border-t pt-2 flex items-center justify-between gap-2 text-xs">
        <span class="text-muted-foreground">Recommend</span>
        <span class="font-medium" :class="recColor">
          {{ recommendation }}
        </span>
      </div>
    </DropdownMenuContent>
  </DropdownMenu>
</template>

<script lang="ts" setup>
import {
  PhWarning,
} from '@phosphor-icons/vue';
import { computed } from "vue";

import AiMark from "@/components/AiMark.vue";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface ProSummaryInput {
  id: number;
  full_name: string;
  email: string;
  experience?: number | null;
  description?: string | null;
  service_name?: string | null;
  pincode?: string | null;
}

interface Flag {
  label: string;
  severity: "low" | "high";
}

const props = defineProps<{
  professional: ProSummaryInput;
  /** Other professionals used to derive cohort-relative flags (same pincode etc). */
  cohort?: ProSummaryInput[];
}>();

const synthesis = computed(() => {
  const p = props.professional;
  const yrs = p.experience ?? 0;
  const seniority =
    yrs >= 8 ? "Veteran" : yrs >= 4 ? "Experienced" : yrs >= 1 ? "Junior" : "New";
  const trade = p.service_name ?? "general services";
  const area = p.pincode ? ` in ${p.pincode}` : "";
  return `${seniority} ${trade.toLowerCase()} professional${area}, ${yrs} year(s) on record.`;
});

const flags = computed<Flag[]>(() => {
  const p = props.professional;
  const list: Flag[] = [];
  if (!p.description || p.description.trim().length < 30) {
    list.push({ label: "Thin bio", severity: "high" });
  }
  const yrs = p.experience ?? 0;
  if (yrs === 0) list.push({ label: "No experience listed", severity: "high" });
  if (yrs >= 8) list.push({ label: "Senior", severity: "low" });

  if (props.cohort?.length) {
    const sharedPincode = props.cohort.filter(
      (c) => c.id !== p.id && c.pincode && c.pincode === p.pincode,
    );
    if (sharedPincode.length >= 3) {
      list.push({ label: `Shared pincode (${sharedPincode.length})`, severity: "low" });
    }
  }

  const domain = p.email.split("@")[1] ?? "";
  if (!/(demo|email|gmail|yahoo|outlook|hotmail)\.(com|local)/.test(domain)) {
    list.push({ label: "Unusual email domain", severity: "low" });
  }
  return list;
});

const recommendation = computed(() => {
  const highRisk = flags.value.filter((f) => f.severity === "high").length;
  if (highRisk >= 2) return "Reject";
  if (highRisk === 1) return "Request more info";
  return "Approve";
});

const recColor = computed(() => {
  switch (recommendation.value) {
    case "Approve":
      return "text-success";
    case "Reject":
      return "text-destructive";
    default:
      return "text-warning";
  }
});
</script>

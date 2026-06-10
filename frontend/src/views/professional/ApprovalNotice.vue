<template>
  <Alert :variant="kind === 'pending' ? 'default' : 'destructive'" class="border-l-4">
    <component :is="iconFor" class="size-3.5" />
    <AlertTitle>{{ config.title }}</AlertTitle>
    <AlertDescription>
      <p class="mb-3">{{ config.lead }}</p>
      <ul class="list-disc pl-5 space-y-1 mb-3">
        <li v-for="point in config.points" :key="point">{{ point }}</li>
      </ul>
      <div class="border-t pt-3 text-sm">
        <p v-if="config.eta" class="text-muted-foreground mb-1">{{ config.eta }}</p>
        <p>
          {{ config.contactLead }}
          <a href="mailto:support@household.com" class="text-primary underline">
            support@household.com
          </a>
        </p>
      </div>
    </AlertDescription>
  </Alert>
</template>

<script lang="ts" setup>
import { AlertTriangle, XCircle } from "@lucide/vue";
import { computed } from "vue";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

type Kind = "pending" | "rejected";

const CONFIG: Record<Kind, {
  title: string;
  lead: string;
  points: string[];
  eta: string;
  contactLead: string;
}> = {
  pending: {
    title: "Account under review",
    lead: "Your professional account is currently being reviewed:",
    points: [
      "You won't be able to view or accept service requests",
      "Your profile will not be visible to potential customers",
      "We'll notify you via email once your account is approved",
    ],
    eta: "Expected review time: 1–2 business days",
    contactLead: "For urgent inquiries, please contact",
  },
  rejected: {
    title: "Account rejected",
    lead: "Your professional account has been rejected.",
    points: [
      "You won't be able to view or accept service requests",
      "Your profile will not be visible to potential customers",
      "We'll notify you via email with the reason for rejection",
    ],
    eta: "",
    contactLead: "For any queries, please contact",
  },
};

const props = defineProps<{ kind: Kind }>();

const config = computed(() => CONFIG[props.kind]);
const iconFor = computed(() => (props.kind === "pending" ? AlertTriangle : XCircle));
</script>

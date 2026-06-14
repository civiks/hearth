<template>
  <ResponsiveSheet :open="true" @close="$emit('close')">
    <template #title>
      <span class="flex items-center gap-2">
        <AiMark class="size-4" />
        Tell us what you need
      </span>
    </template>
    <template #description>
      <template v-if="stage === 'compose'">Describe it — we'll match a service and pre-fill the booking.</template>
      <template v-else-if="stage === 'review'">Reviewing your request…</template>
      <template v-else>Fill in the booking details.</template>
    </template>

    <form v-if="stage === 'compose'" class="space-y-3" @submit.prevent="onParse">
      <Textarea
        v-model="prompt"
        rows="3"
        autofocus
        placeholder="e.g. my kitchen sink is leaking, urgent — tomorrow morning if possible"
      />
      <div class="flex flex-wrap gap-1.5">
        <button
          v-for="ex in EXAMPLES"
          :key="ex"
          type="button"
          class="text-xs bg-muted hover:bg-muted/70 px-2 py-1 rounded transition"
          @click="prompt = ex"
        >
          {{ ex }}
        </button>
      </div>
    </form>

    <div v-else-if="stage === 'review'" class="space-y-4">
      <AiSurface class="px-3 py-2 text-sm whitespace-pre-wrap">
        <span v-if="narrative || streaming" v-html="renderMarkdownish(narrative)" />
        <span
          v-if="streaming"
          class="inline-block size-2 bg-muted-foreground/60 align-middle ml-1 animate-pulse"
          aria-hidden="true"
        />
      </AiSurface>

      <AiSurface v-if="matchedService && !streaming" class="p-3 space-y-1.5 text-sm">
        <div class="flex items-center justify-between gap-2">
          <div class="flex items-center gap-2 min-w-0">
            <AiMark class="size-3" />
            <span class="font-medium truncate">{{ matchedService.name }}</span>
          </div>
          <Badge variant="secondary" class="text-[10px]">
            {{ matchedService.category }}
          </Badge>
        </div>
        <div class="text-xs text-muted-foreground">
          ₹{{ matchedService.base_price }} · ~{{ matchedService.time_required }} min · matched from your description
        </div>
      </AiSurface>
    </div>

    <div v-else class="space-y-4 text-sm">
      <div class="space-y-2">
        <Label for="nl-time">Preferred time</Label>
        <Input id="nl-time" v-model="form.scheduled_time" type="datetime-local" :min="nowLocal()" required />
      </div>
      <div class="space-y-2">
        <Label>Service location</Label>
        <div class="flex gap-2">
          <Input v-model="form.address" placeholder="Address" required />
          <Input
            v-model="form.pincode"
            placeholder="Pincode"
            pattern="[0-9]{6}"
            class="max-w-[140px]"
            required
          />
        </div>
      </div>
      <div class="space-y-2">
        <Label for="nl-remarks">
          Notes
          <span class="font-normal text-muted-foreground">(optional)</span>
        </Label>
        <Textarea id="nl-remarks" v-model="form.remarks" rows="2" />
      </div>
      <Alert v-if="errorMessage" variant="destructive">
        <PhWarningCircle class="size-4" weight="bold" />
        <AlertDescription>{{ errorMessage }}</AlertDescription>
      </Alert>
    </div>

    <template #footer>
      <template v-if="stage === 'compose'">
        <Button type="button" variant="secondary" class="rounded-xl" @click="$emit('close')">Cancel</Button>
        <Button type="button" class="flex-1 rounded-xl" :disabled="!prompt.trim()" @click="onParse">
          Parse
        </Button>
      </template>
      <template v-else-if="stage === 'review'">
        <Button type="button" variant="secondary" class="rounded-xl" @click="restart">Start over</Button>
        <Button type="button" class="flex-1 rounded-xl" :disabled="streaming || !matchedService" @click="stage = 'form'">
          Looks good
          <PhCaretRight class="size-3.5 ml-1" weight="bold" />
        </Button>
      </template>
      <template v-else>
        <Button type="button" variant="primary-soft" size="icon" class="rounded-full" @click="stage = 'review'">
          <PhArrowLeft class="size-4" weight="bold" />
        </Button>
        <Button type="button" class="flex-1 rounded-xl" :disabled="submitting" @click="onSubmit">
          {{ submitting ? "Booking…" : "Confirm booking" }}
        </Button>
      </template>
    </template>
  </ResponsiveSheet>
</template>

<script lang="ts" setup>
import {
  PhWarningCircle,
  PhArrowLeft,
  PhCaretRight,
} from '@phosphor-icons/vue';
import { reactive, ref } from "vue";

import AiMark from "@/components/AiMark.vue";
import AiSurface from "@/components/AiSurface.vue";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import ResponsiveSheet from "@/components/ui/ResponsiveSheet.vue";
import { Textarea } from "@/components/ui/textarea";
import { ApiError, api } from "@/lib/api";
import { parseRequestIntent, streamScript, tokenize, type AgentEvent } from "@/lib/genai";
import { useAuthStore } from "@/stores/auth";

interface ServiceLite {
  id: number;
  name: string;
  category: string;
  base_price: number;
  time_required: number;
  is_active: boolean;
}

const emit = defineEmits<{ close: []; booked: [] }>();

const EXAMPLES = [
  "my kitchen sink is leaking, urgent",
  "need deep cleaning before guests arrive saturday",
  "ceiling fan stopped working, can wait till tomorrow",
];

const auth = useAuthStore();

const stage = ref<"compose" | "review" | "form">("compose");
const prompt = ref("");
const narrative = ref("");
const streaming = ref(false);
const matchedService = ref<ServiceLite | null>(null);
const submitting = ref(false);
const errorMessage = ref("");

const form = reactive({
  scheduled_time: "",
  address: auth.address ?? "",
  pincode: auth.pincode ?? "",
  remarks: "",
});

function nowLocal(): string {
  const now = new Date();
  return new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}

async function onParse() {
  if (!prompt.value.trim()) return;
  stage.value = "review";
  narrative.value = "";
  matchedService.value = null;
  streaming.value = true;

  const intent = parseRequestIntent(prompt.value);
  form.scheduled_time = intent.scheduledTime;
  form.remarks = intent.summary;

  let services: ServiceLite[] = [];
  try {
    services = await api.get<ServiceLite[]>("/api/services");
  } catch {
    // non-fatal: AI flow continues without service matching
  }

  const candidates = services.filter(
    (s) =>
      s.is_active &&
      (s.category === intent.category ||
        s.name.toLowerCase().includes(intent.category.toLowerCase())),
  );
  const chosen = candidates[0] ?? services.find((s) => s.is_active) ?? null;
  matchedService.value = chosen;

  const script: AgentEvent[] = [
    ...tokenize(`Matching to **${intent.category}**`),
    ...tokenize(` · urgency **${intent.urgency}**`),
    ...tokenize(` · ${intent.scheduledLabel}.`),
  ];
  if (chosen) {
    script.push(...tokenize(`\n\nClosest service: **${chosen.name}** (₹${chosen.base_price}).`));
  } else {
    script.push(...tokenize("\n\nNo exact match — pick a category from the browse page."));
  }
  script.push(...tokenize("\n\nReview the details below and confirm."));

  await consume(streamScript(script));
  streaming.value = false;
}

async function consume(stream: ReadableStream<AgentEvent>) {
  const reader = stream.getReader();
  // eslint-disable-next-line no-constant-condition
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    if (value.type === "text") narrative.value += value.delta;
  }
}

function restart() {
  stage.value = "compose";
  narrative.value = "";
  matchedService.value = null;
  errorMessage.value = "";
}

async function onSubmit() {
  if (!matchedService.value) return;
  submitting.value = true;
  errorMessage.value = "";
  try {
    await api.post("/api/requests", {
      service_id: matchedService.value.id,
      scheduled_time: form.scheduled_time,
      address: form.address,
      pincode: form.pincode,
      remarks: form.remarks,
    });
    emit("booked");
  } catch (err) {
    errorMessage.value =
      err instanceof ApiError ? err.detail : "Failed to book service.";
  } finally {
    submitting.value = false;
  }
}

function renderMarkdownish(text: string): string {
  const escaped = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  return escaped
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br />");
}
</script>

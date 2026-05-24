<template>
  <Dialog :open="true" @update:open="(v) => !v && $emit('close')">
    <DialogContent class="sm:max-w-lg">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <AiMark class="size-4" />
          Tell us what you need
        </DialogTitle>
        <DialogDescription>
          Describe it — we'll match a service and pre-fill the booking.
        </DialogDescription>
      </DialogHeader>

      <!-- Step 1: free-form prompt -->
      <form
        v-if="stage === 'compose'"
        class="space-y-3"
        @submit.prevent="onParse"
      >
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
            class="text-xs bg-muted hover:bg-muted/70 px-2 py-1 transition"
            @click="prompt = ex"
          >
            {{ ex }}
          </button>
        </div>
      </form>

      <!-- Step 2: streaming narrative + parsed form -->
      <div v-else class="space-y-4">
        <AiSurface class="px-3 py-2 text-sm whitespace-pre-wrap">
          <span
            v-if="narrative || streaming"
            v-html="renderMarkdownish(narrative)"
          />
          <span
            v-if="streaming"
            class="inline-block size-2 bg-muted-foreground/60 align-middle ml-1 animate-pulse"
            aria-hidden="true"
          />
        </AiSurface>

        <div v-if="matchedService && !streaming" class="space-y-3 text-sm">
          <AiSurface class="p-3 space-y-1.5">
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

          <div class="space-y-2">
            <Label for="nl-time">Preferred time</Label>
            <Input
              id="nl-time"
              v-model="form.scheduled_time"
              type="datetime-local"
              required
            />
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
            <Label for="nl-remarks">Notes for the professional</Label>
            <Textarea
              id="nl-remarks"
              v-model="form.remarks"
              rows="2"
            />
          </div>

          <Alert v-if="errorMessage" variant="destructive">
            <AlertCircle class="size-4" />
            <AlertDescription>{{ errorMessage }}</AlertDescription>
          </Alert>
        </div>
      </div>

      <DialogFooter>
        <Button
          v-if="stage === 'compose'"
          type="button"
          variant="secondary"
          @click="$emit('close')"
        >
          Cancel
        </Button>
        <Button
          v-if="stage === 'compose'"
          type="button"
          :disabled="!prompt.trim()"
          @click="onParse"
        >
          <AiMark class="size-3 mr-1.5" />
          Parse
        </Button>
        <Button
          v-if="stage === 'review'"
          type="button"
          variant="ghost"
          @click="restart"
        >
          Start over
        </Button>
        <Button
          v-if="stage === 'review'"
          type="button"
          :disabled="streaming || !matchedService || submitting"
          @click="onSubmit"
        >
          {{ submitting ? "Booking…" : "Confirm booking" }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<script lang="ts" setup>
import { AlertCircle } from "lucide-vue-next";
import { reactive, ref } from "vue";

import AiMark from "@/components/AiMark.vue";
import AiSurface from "@/components/AiSurface.vue";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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

const stage = ref<"compose" | "review">("compose");
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

async function onParse() {
  if (!prompt.value.trim()) return;
  stage.value = "review";
  narrative.value = "";
  matchedService.value = null;
  streaming.value = true;

  const intent = parseRequestIntent(prompt.value);
  form.scheduled_time = intent.scheduledTime;
  form.remarks = intent.summary;

  // Look up services up front so we can compose the scripted narrative with
  // real data (mirrors how the chatbot agent uses tool results).
  let services: ServiceLite[] = [];
  try {
    services = await api.get<ServiceLite[]>("/api/services");
  } catch (err) {
    if (import.meta.env.DEV) console.warn("services lookup failed", err);
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
    script.push(
      ...tokenize(`\n\nClosest service: **${chosen.name}** (₹${chosen.base_price}).`),
    );
  } else {
    script.push(
      ...tokenize("\n\nNo exact match — pick a category from the browse page."),
    );
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

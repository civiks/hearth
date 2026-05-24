<template>
  <div class="px-6 py-8 max-w-3xl mx-auto space-y-10">
    <header>
      <h1 class="text-2xl font-light tracking-tight">Settings</h1>
      <p class="text-sm text-muted-foreground mt-1">
        Appearance and AI.
      </p>
    </header>

    <section class="space-y-1">
      <h2 class="text-xs font-medium uppercase tracking-wide text-muted-foreground pb-3 border-b">
        Appearance
      </h2>
      <Row label="Theme" hint="Used everywhere in the app.">
        <Select :model-value="theme" @update:model-value="(v) => setTheme(v as Theme)">
          <SelectTrigger class="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="light">Light</SelectItem>
            <SelectItem value="dark">Dark</SelectItem>
            <SelectItem value="system">Match system</SelectItem>
          </SelectContent>
        </Select>
      </Row>
    </section>

    <section class="space-y-1">
      <h2 class="text-xs font-medium uppercase tracking-wide text-muted-foreground pb-3 border-b">
        AI
      </h2>
      <Row label="Gemini API key">
        <template #hint>
          <template v-if="DEMO">
            Not needed in demo mode.
          </template>
          <template v-else>
            Get a free key at
            <a
              href="https://aistudio.google.com/apikey"
              target="_blank"
              rel="noopener"
              class="text-primary hover:underline"
            >aistudio.google.com/apikey</a>.
          </template>
        </template>
        <div class="flex items-center gap-2">
          <span
            v-if="DEMO"
            class="text-xs text-muted-foreground italic"
          >
            Demo mode
          </span>
          <span
            v-else-if="gemini.loaded.value"
            class="text-xs"
            :class="gemini.hasKey.value ? 'text-emerald-600' : 'text-muted-foreground'"
          >
            {{ gemini.hasKey.value ? "Configured" : "Not configured" }}
          </span>
          <Button
            size="sm"
            variant="outline"
            :disabled="DEMO"
            @click="keyDialogOpen = true"
          >
            {{ gemini.hasKey.value ? "Replace" : "Set up" }}
          </Button>
        </div>
      </Row>
    </section>

    <AiKeyDialog v-if="!DEMO" v-model:open="keyDialogOpen" />
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from "vue";

import AiKeyDialog from "@/components/AiKeyDialog.vue";
import { Button } from "@/components/ui/button";
import { DEMO } from "@/lib/demo/flag";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useGeminiKey } from "@/composables/useGeminiKey";
import { useTheme, type Theme } from "@/composables/useTheme";
import Row from "@/views/settings/Row.vue";

const { theme, setTheme } = useTheme();

const gemini = useGeminiKey();
const keyDialogOpen = ref(false);

onMounted(() => {
  if (!DEMO) void gemini.refresh();
});
</script>

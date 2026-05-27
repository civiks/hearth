<template>
  <ResponsiveSheet
    :open="settings.open.value"
    title="Settings"
    content-class="sm:max-w-sm"
    body-class="space-y-0"
    @close="settings.open.value = false"
  >
    <SettingsRow label="AI model" hint="Used for hearth AI.">
      <Select :model-value="chat.modelId" @update:model-value="(v) => chat.setModel(v as string)">
        <SelectTrigger class="w-44">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem v-for="m in CHAT_MODELS" :key="m.id" :value="m.id">
            {{ m.name }}
          </SelectItem>
        </SelectContent>
      </Select>
    </SettingsRow>
    <SettingsRow label="Gemini API key">
      <template #hint>
        <template v-if="DEMO">Not needed in demo mode.</template>
        <template v-else>
          Get a free key at
          <a
            href="https://aistudio.google.com/apikey"
            target="_blank"
            rel="noopener"
            class="text-primary hover:underline"
          >aistudio.google.com</a>.
        </template>
      </template>
      <div class="flex items-center gap-2">
        <span v-if="DEMO" class="text-xs text-muted-foreground italic">Demo mode</span>
        <span
          v-else-if="gemini.loaded.value"
          class="text-xs"
          :class="gemini.hasKey.value ? 'text-success' : 'text-muted-foreground'"
        >
          {{ gemini.hasKey.value ? "Configured" : "Not configured" }}
        </span>
        <Button size="sm" variant="outline" :disabled="DEMO" @click="keyDialogOpen = true">
          {{ gemini.hasKey.value ? "Replace" : "Set up" }}
        </Button>
      </div>
    </SettingsRow>
  </ResponsiveSheet>

  <AiKeyDialog v-if="!DEMO" v-model:open="keyDialogOpen" />
</template>

<script lang="ts" setup>
import { ref, watch } from "vue";

import AiKeyDialog from "@/components/AiKeyDialog.vue";
import SettingsRow from "@/components/SettingsRow.vue";
import { Button } from "@/components/ui/button";
import ResponsiveSheet from "@/components/ui/ResponsiveSheet.vue";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useSettingsDrawer } from "@/composables/useSettingsDrawer";
import { useGeminiKey } from "@/composables/useGeminiKey";
import { DEMO } from "@/lib/demo/flag";
import { CHAT_MODELS, useChatStore } from "@/stores/chat";

const settings = useSettingsDrawer();

const chat = useChatStore();
const gemini = useGeminiKey();
const keyDialogOpen = ref(false);

watch(
  () => settings.open.value,
  (v) => { if (v && !DEMO) void gemini.refresh(); },
);
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="sm:max-w-md">
      <DialogHeader>
        <DialogTitle>Add your Gemini key</DialogTitle>
        <DialogDescription>
          Paste your Gemini key to start chatting.
        </DialogDescription>
      </DialogHeader>

      <form class="space-y-3 pt-1" @submit.prevent="onSave">
        <div class="space-y-1.5">
          <Label for="gemini-key" class="text-xs">API key</Label>
          <Input
            id="gemini-key"
            v-model="draft"
            type="password"
            placeholder="AIza..."
            autocomplete="off"
            spellcheck="false"
            class="font-mono text-xs"
            autofocus
            :disabled="saving"
          />
          <p class="text-[11px] text-muted-foreground">
            Get one at
            <a
              href="https://aistudio.google.com/apikey"
              target="_blank"
              rel="noopener"
              class="text-primary hover:underline"
            >aistudio.google.com/apikey</a>.
          </p>
        </div>

        <DialogFooter>
          <Button
            v-if="gemini.hasKey.value"
            type="button"
            variant="ghost"
            size="sm"
            :disabled="saving"
            @click="onClear"
          >
            Remove saved key
          </Button>
          <Button type="submit" size="sm" :disabled="!canSave || saving">
            {{ gemini.hasKey.value ? "Update" : "Save" }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>

<script lang="ts" setup>
import { computed, ref, watch } from "vue";

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
import { useGeminiKey } from "@/composables/useGeminiKey";
import { useNotificationsStore } from "@/stores/notifications";

const open = defineModel<boolean>("open", { default: false });

const gemini = useGeminiKey();
const toasts = useNotificationsStore();

// The backend never returns the existing key, so the input always starts
// empty. Cleared again whenever the dialog reopens.
const draft = ref("");
const saving = ref(false);

watch(open, (v) => {
  if (v) {
    draft.value = "";
    // Refresh status so the Update/Save label and the Remove button reflect
    // whether the user already has a key on file.
    void gemini.refresh();
  }
});

// Real Gemini keys are ~39 chars; 20 catches obvious garbage without
// rejecting valid future formats.
const canSave = computed(() => draft.value.trim().length >= 20);

async function onSave() {
  const v = draft.value.trim();
  if (v.length < 20) return;
  saving.value = true;
  try {
    await gemini.set(v);
    toasts.success("Gemini key saved");
    open.value = false;
  } catch (err) {
    toasts.error(err instanceof Error ? err.message : "Couldn't save key");
  } finally {
    saving.value = false;
  }
}

async function onClear() {
  saving.value = true;
  try {
    await gemini.clear();
    toasts.info("Gemini key removed");
    open.value = false;
  } catch (err) {
    toasts.error(err instanceof Error ? err.message : "Couldn't remove key");
  } finally {
    saving.value = false;
  }
}
</script>

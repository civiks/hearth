<template>
  <Dialog v-if="isDesktop" v-model:open="open">
    <DialogContent :show-close-button="false" class="sm:max-w-md gap-0 p-0 overflow-hidden rounded-3xl">
      <div class="space-y-2 px-6 pt-6 pb-2">
        <DialogTitle>Add your Gemini key</DialogTitle>
        <DialogDescription>
          Paste your Gemini key to start chatting.
        </DialogDescription>
      </div>

      <form class="px-6 pt-4" @submit.prevent="onSave">
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

        <div class="pt-5 pb-6 flex gap-2 justify-end">
          <Button
            v-if="gemini.hasKey.value"
            type="button"
            variant="secondary"
            halo
            class="rounded-full px-5"
            :disabled="saving"
            @click="onClear"
          >
            Remove saved key
          </Button>
          <Button type="submit" halo class="rounded-full px-5" :disabled="!canSave || saving">
            {{ gemini.hasKey.value ? "Update" : "Save" }}
          </Button>
        </div>
      </form>
    </DialogContent>
  </Dialog>

  <Drawer v-else v-model:open="open">
    <DrawerContent>
      <DrawerHeader>
        <DrawerTitle>Add your Gemini key</DrawerTitle>
        <DrawerDescription>
          Paste your Gemini key to start chatting.
        </DrawerDescription>
      </DrawerHeader>

      <form class="px-4" @submit.prevent="onSave">
        <div class="space-y-1.5">
          <Label for="gemini-key-m" class="text-xs">API key</Label>
          <Input
            id="gemini-key-m"
            v-model="draft"
            type="password"
            placeholder="AIza..."
            autocomplete="off"
            spellcheck="false"
            class="font-mono text-xs"
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

        <DrawerFooter class="px-0">
          <Button
            v-if="gemini.hasKey.value"
            type="button"
            variant="secondary"
            halo
            class="rounded-full"
            :disabled="saving"
            @click="onClear"
          >
            Remove saved key
          </Button>
          <Button type="submit" halo class="flex-1 rounded-full" :disabled="!canSave || saving">
            {{ gemini.hasKey.value ? "Update" : "Save" }}
          </Button>
        </DrawerFooter>
      </form>
    </DrawerContent>
  </Drawer>
</template>

<script lang="ts" setup>
import { useMediaQuery } from "@vueuse/core";
import { computed, ref, watch } from "vue";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useGeminiKey } from "@/composables/useGeminiKey";
import { useNotificationsStore } from "@/stores/notifications";

const open = defineModel<boolean>("open", { default: false });

const isDesktop = useMediaQuery("(min-width: 640px)");

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

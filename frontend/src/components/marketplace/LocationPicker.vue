<template>
  <div>
    <button
      type="button"
      class="inline-flex items-center gap-1.5 text-xs tracking-tight tabular-nums text-muted-foreground hover:text-foreground transition-colors"
      @click="openPicker"
    >
      <PhMapPin class="size-3.5" weight="bold" />
      {{ locationLabel }}
      <PhCaretDown class="size-3.5" weight="bold" />
    </button>

    <Dialog v-if="isDesktop" v-model:open="dialogOpen">
      <DialogContent :show-close-button="false" class="sm:max-w-sm gap-0 p-0 overflow-hidden rounded-3xl">
        <div class="space-y-2 px-6 pt-6 pb-2">
          <DialogTitle>Service location</DialogTitle>
          <DialogDescription>
            We use this to show relevant professionals near you.
          </DialogDescription>
        </div>
        <form class="px-6 pt-4 space-y-4" @submit.prevent="save">
          <div class="space-y-2">
            <Label for="loc_address">Address</Label>
            <Input id="loc_address" v-model="form.address" placeholder="Street address" />
          </div>
          <div class="space-y-2">
            <Label for="loc_pincode">Pincode</Label>
            <Input
              id="loc_pincode"
              v-model="form.pincode"
              placeholder="6-digit pincode"
              pattern="[0-9]{6}"
            />
          </div>
          <Alert v-if="error" variant="destructive">
            <PhWarningCircle class="size-3.5" weight="bold" />
            <AlertDescription>{{ error }}</AlertDescription>
          </Alert>
        </form>
        <div class="px-6 pt-5 pb-6 flex gap-2 justify-end">
          <Button variant="secondary" halo class="rounded-full px-5" @click="dialogOpen = false">Cancel</Button>
          <Button halo class="rounded-full px-5" :disabled="saving" @click="save">
            {{ saving ? "Saving…" : "Save" }}
          </Button>
        </div>
      </DialogContent>
    </Dialog>

    <Drawer v-else v-model:open="dialogOpen">
      <DrawerContent>
        <DrawerHeader>
          <DrawerTitle>Service location</DrawerTitle>
          <DrawerDescription>
            We use this to show relevant professionals near you.
          </DrawerDescription>
        </DrawerHeader>
        <form class="px-4 space-y-4" @submit.prevent="save">
          <div class="space-y-2">
            <Label for="loc_address_m">Address</Label>
            <Input id="loc_address_m" v-model="form.address" placeholder="Street address" />
          </div>
          <div class="space-y-2">
            <Label for="loc_pincode_m">Pincode</Label>
            <Input
              id="loc_pincode_m"
              v-model="form.pincode"
              placeholder="6-digit pincode"
              pattern="[0-9]{6}"
            />
          </div>
          <Alert v-if="error" variant="destructive">
            <PhWarningCircle class="size-3.5" weight="bold" />
            <AlertDescription>{{ error }}</AlertDescription>
          </Alert>
        </form>
        <DrawerFooter>
          <Button variant="secondary" halo class="rounded-full" @click="dialogOpen = false">Cancel</Button>
          <Button halo class="flex-1 rounded-full" :disabled="saving" @click="save">
            {{ saving ? "Saving…" : "Save" }}
          </Button>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  </div>
</template>

<script lang="ts" setup>
import { useMediaQuery } from "@vueuse/core";
import {
  PhWarningCircle,
  PhCaretDown,
  PhMapPin,
} from '@phosphor-icons/vue';
import { computed, reactive, ref } from "vue";

import { Alert, AlertDescription } from "@/components/ui/alert";
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
import { ApiError, api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const isDesktop = useMediaQuery("(min-width: 640px)");

const locationLabel = computed(() => {
  if (auth.pincode) return auth.pincode;
  if (auth.address) return auth.address;
  return "Set location";
});

const dialogOpen = ref(false);
const saving = ref(false);
const error = ref("");
const form = reactive({ address: "", pincode: "" });

function openPicker() {
  form.address = auth.address ?? "";
  form.pincode = auth.pincode ?? "";
  error.value = "";
  dialogOpen.value = true;
}

async function save() {
  saving.value = true;
  error.value = "";
  try {
    await api.put("/api/users/me", { address: form.address, pincode: form.pincode });
    auth.updateUserDetails({ address: form.address, pincode: form.pincode });
    dialogOpen.value = false;
  } catch (err) {
    error.value = err instanceof ApiError ? err.detail : "Failed to save location.";
  } finally {
    saving.value = false;
  }
}
</script>

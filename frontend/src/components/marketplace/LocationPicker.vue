<template>
  <div>
    <button
      type="button"
      class="inline-flex items-center gap-1.5 text-xs tracking-tight tabular-nums text-muted-foreground hover:text-foreground transition-colors"
      @click="openPicker"
    >
      <MapPin class="size-3.5" />
      {{ locationLabel }}
      <ChevronDown class="size-3.5" />
    </button>

    <Dialog v-model:open="dialogOpen">
      <DialogContent class="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle>Service location</DialogTitle>
          <DialogDescription>
            We use this to show relevant professionals near you.
          </DialogDescription>
        </DialogHeader>
        <form class="space-y-4" @submit.prevent="save">
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
            <AlertCircle class="size-3.5" />
            <AlertDescription>{{ error }}</AlertDescription>
          </Alert>
        </form>
        <DialogFooter>
          <Button variant="outline" type="button" @click="dialogOpen = false">Cancel</Button>
          <Button type="button" :disabled="saving" @click="save">
            {{ saving ? "Saving…" : "Save" }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script lang="ts" setup>
import { AlertCircle, ChevronDown, MapPin } from "lucide-vue-next";
import { computed, reactive, ref } from "vue";

import { Alert, AlertDescription } from "@/components/ui/alert";
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
import { ApiError, api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();

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

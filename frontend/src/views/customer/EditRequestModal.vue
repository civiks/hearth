<template>
  <ResponsiveSheet
    :open="true"
    title="Edit service request"
    :description="request.service_name"
    @close="$emit('close')"
  >
    <div class="space-y-2">
      <Label for="edit_scheduled_time">Scheduled time</Label>
      <Input
        id="edit_scheduled_time"
        v-model="form.scheduled_time"
        type="datetime-local"
        :min="nowLocal()"
        required
      />
    </div>
    <div class="space-y-2">
      <Label for="edit_address">Address</Label>
      <Input id="edit_address" v-model="form.address" required />
    </div>
    <div class="space-y-2">
      <Label for="edit_pincode">Pincode</Label>
      <Input id="edit_pincode" v-model="form.pincode" required />
    </div>
    <div class="space-y-2">
      <Label for="edit_remarks">
        Remarks
        <span class="font-normal text-muted-foreground">(optional)</span>
      </Label>
      <Textarea id="edit_remarks" v-model="form.remarks" />
    </div>

    <Alert v-if="errorMessage" variant="destructive">
      <PhWarningCircle class="size-4" weight="bold" />
      <AlertDescription>{{ errorMessage }}</AlertDescription>
    </Alert>

    <template #footer>
      <Button type="button" variant="secondary" class="rounded-xl" @click="$emit('close')">Cancel</Button>
      <Button type="button" class="flex-1 rounded-xl" :disabled="submitting" @click="onSubmit">
        {{ submitting ? "Updating…" : "Update" }}
      </Button>
    </template>
  </ResponsiveSheet>
</template>

<script lang="ts" setup>
import {
  PhWarningCircle,
} from '@phosphor-icons/vue';
import { reactive, ref } from "vue";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import ResponsiveSheet from "@/components/ui/ResponsiveSheet.vue";
import { Textarea } from "@/components/ui/textarea";
import { ApiError, api } from "@/lib/api";
import type { CustomerRequest } from "./RequestCard.vue";

const props = defineProps<{ request: CustomerRequest }>();
const emit = defineEmits<{ close: []; updated: [] }>();

const submitting = ref(false);
const errorMessage = ref("");

const initialDate = props.request.scheduled_time
  ? new Date(props.request.scheduled_time)
  : new Date();

const form = reactive({
  scheduled_time: initialDate.toISOString().slice(0, 16),
  address: props.request.address ?? "",
  pincode: props.request.pincode ?? "",
  remarks: props.request.remarks ?? "",
});

function nowLocal(): string {
  const now = new Date();
  return new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}

async function onSubmit() {
  submitting.value = true;
  errorMessage.value = "";
  try {
    await api.put(`/api/requests/${props.request.id}`, {
      scheduled_time: form.scheduled_time,
      address: form.address,
      pincode: form.pincode,
      remarks: form.remarks,
    });
    emit("updated");
  } catch (err) {
    errorMessage.value =
      err instanceof ApiError ? err.detail : "Failed to update service request.";
  } finally {
    submitting.value = false;
  }
}
</script>

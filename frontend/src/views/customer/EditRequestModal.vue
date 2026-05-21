<template>
  <Dialog :open="true" @update:open="(v) => !v && $emit('close')">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Edit service request</DialogTitle>
        <DialogDescription>{{ request.service_name }}</DialogDescription>
      </DialogHeader>
      <form class="space-y-4" @submit.prevent="onSubmit">
        <div class="space-y-2">
          <Label for="edit_scheduled_time">Scheduled time</Label>
          <Input
            id="edit_scheduled_time"
            v-model="form.scheduled_time"
            type="datetime-local"
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
          <Label for="edit_remarks">Remarks</Label>
          <Textarea id="edit_remarks" v-model="form.remarks" />
        </div>

        <Alert v-if="errorMessage" variant="destructive">
          <AlertCircle class="size-4" />
          <AlertDescription>{{ errorMessage }}</AlertDescription>
        </Alert>

        <DialogFooter>
          <Button type="button" variant="secondary" @click="$emit('close')">Cancel</Button>
          <Button type="submit" :disabled="submitting">
            {{ submitting ? "Updating…" : "Update" }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>

<script lang="ts" setup>
import { AlertCircle } from "lucide-vue-next";
import { reactive, ref } from "vue";

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
import { Textarea } from "@/components/ui/textarea";
import { ApiError, api } from "@/lib/api";
import type { CustomerRequest } from "./HistoryTable.vue";

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

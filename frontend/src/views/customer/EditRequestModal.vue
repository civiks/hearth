<template>
  <component
    :is="isDesktop ? Sheet : Drawer"
    :open="true"
    v-bind="isDesktop ? {} : { shouldScaleBackground: true }"
    @update:open="(v: boolean) => !v && $emit('close')"
  >
    <component :is="isDesktop ? SheetContent : DrawerContent">
      <DrawerHeader>
        <DrawerTitle>Edit service request</DrawerTitle>
        <DrawerDescription>{{ request.service_name }}</DrawerDescription>
      </DrawerHeader>

      <div class="flex-1 overflow-y-auto px-5 py-5 space-y-4" data-vaul-no-drag>
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
          <AlertCircle class="size-4" />
          <AlertDescription>{{ errorMessage }}</AlertDescription>
        </Alert>
      </div>

      <DrawerFooter>
        <Button type="button" variant="outline" @click="$emit('close')">Cancel</Button>
        <Button type="button" class="flex-1" :disabled="submitting" @click="onSubmit">
          {{ submitting ? "Updating…" : "Update" }}
        </Button>
      </DrawerFooter>
    </component>
  </component>
</template>

<script lang="ts" setup>
import { AlertCircle } from "lucide-vue-next";
import { reactive, ref } from "vue";
import { useMediaQuery } from "@vueuse/core";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Drawer, DrawerContent, DrawerDescription, DrawerFooter, DrawerHeader, DrawerTitle } from "@/components/ui/drawer";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Sheet, SheetContent } from "@/components/ui/sheet";
import { Textarea } from "@/components/ui/textarea";
import { ApiError, api } from "@/lib/api";
import type { CustomerRequest } from "./RequestCard.vue";

const props = defineProps<{ request: CustomerRequest }>();
const emit = defineEmits<{ close: []; updated: [] }>();

const isDesktop = useMediaQuery("(min-width: 640px)");
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

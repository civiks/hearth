<template>
  <Card>
    <CardHeader>
      <CardTitle class="text-base font-medium">Export service requests</CardTitle>
      <CardDescription>
        Generate a CSV file containing all service requests. Useful for offline analysis.
      </CardDescription>
    </CardHeader>
    <CardContent>
      <Button :disabled="busy" @click="run">
        <Download class="mr-2 size-4" />
        {{ busy ? "Generating export…" : "Export service requests" }}
      </Button>
    </CardContent>
  </Card>
</template>

<script lang="ts" setup>
import { Download } from "lucide-vue-next";
import { onBeforeUnmount, ref } from "vue";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ApiError, api } from "@/lib/api";
import { useNotificationsStore } from "@/stores/notifications";

interface ExportStatus {
  status: string;
  filename?: string;
  error?: string;
}

const toasts = useNotificationsStore();
const busy = ref(false);
const pollHandle = ref<ReturnType<typeof setInterval> | null>(null);

onBeforeUnmount(() => {
  if (pollHandle.value) clearInterval(pollHandle.value);
});

async function run() {
  try {
    busy.value = true;
    toasts.info("Starting export…");
    const { task_id } = await api.post<{ task_id: string }>(
      "/api/export-service-requests",
    );
    poll(task_id);
  } catch (err) {
    busy.value = false;
    toasts.error(err instanceof ApiError ? err.detail : "Failed to start export");
  }
}

function poll(taskId: string) {
  if (pollHandle.value) clearInterval(pollHandle.value);
  pollHandle.value = setInterval(async () => {
    try {
      const data = await api.get<ExportStatus>(`/api/export-status/${taskId}`);
      if (data.status === "SUCCESS" && data.filename) {
        if (pollHandle.value) clearInterval(pollHandle.value);
        busy.value = false;
        toasts.success("Export ready. Downloading…");
        const base = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
        window.location.href = `${base}/api/download-export/${data.filename}`;
      } else if (data.status === "FAILURE") {
        if (pollHandle.value) clearInterval(pollHandle.value);
        busy.value = false;
        toasts.error(`Export failed: ${data.error ?? "unknown error"}`);
      }
    } catch (err) {
      if (pollHandle.value) clearInterval(pollHandle.value);
      busy.value = false;
      toasts.error(err instanceof ApiError ? err.detail : "Status check failed");
    }
  }, 2000);
}
</script>

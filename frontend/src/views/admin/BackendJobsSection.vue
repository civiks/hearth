<template>
  <Card>
    <CardHeader>
      <CardTitle class="text-base font-medium">Background jobs</CardTitle>
      <CardDescription>
        Manually trigger Celery jobs for testing. Emails land in MailHog.
      </CardDescription>
    </CardHeader>
    <CardContent class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <Button
          variant="outline"
          :disabled="loading.daily"
          @click="trigger('daily-reminders', 'daily', 'Daily reminders sent.')"
        >
          <PhBell class="mr-2 size-3.5" weight="bold" />
          {{ loading.daily ? "Sending…" : "Daily reminders" }}
        </Button>
        <Button
          variant="outline"
          :disabled="loading.monthly"
          @click="trigger('monthly-reports', 'monthly', 'Monthly reports generated.')"
        >
          <PhFileText class="mr-2 size-3.5" weight="bold" />
          {{ loading.monthly ? "Generating…" : "Monthly reports" }}
        </Button>
        <Button
          variant="outline"
          :disabled="loading.activity"
          @click="trigger('activity-reports', 'activity', 'Activity reports generated.')"
        >
          <PhActivity class="mr-2 size-3.5" weight="bold" />
          {{ loading.activity ? "Generating…" : "Activity reports" }}
        </Button>
      </div>
      <Button variant="ghost" size="sm" @click="openMailHog">
        <PhArrowSquareOut class="mr-2 size-3.5" weight="bold" />
        Open MailHog
      </Button>
    </CardContent>
  </Card>
</template>

<script lang="ts" setup>
import {
  PhActivity,
  PhBell,
  PhArrowSquareOut,
  PhFileText,
} from '@phosphor-icons/vue';
import { reactive } from "vue";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ApiError, api } from "@/lib/api";
import { DEMO } from "@/lib/demo/flag";
import { useNotificationsStore } from "@/stores/notifications";

type JobKey = "daily" | "monthly" | "activity";
type JobPath = "daily-reminders" | "monthly-reports" | "activity-reports";

const toasts = useNotificationsStore();

const loading = reactive<Record<JobKey, boolean>>({
  daily: false,
  monthly: false,
  activity: false,
});

async function trigger(path: JobPath, key: JobKey, successMsg: string) {
  loading[key] = true;
  try {
    await api.post(`/api/trigger-${path}`);
    toasts.success(`${successMsg} PhCheck MailHog.`);
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : `Failed to trigger ${path}`);
  } finally {
    loading[key] = false;
  }
}

function openMailHog() {
  if (DEMO) {
    toasts.info(
      "MailHog runs in local dev only",
      "Clone the repo and run `make dev` — MailHog catches outbound mail at :8025.",
    );
    return;
  }
  window.open("http://localhost:8025", "_blank");
}
</script>

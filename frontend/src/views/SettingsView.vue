<template>
  <div class="px-6 py-8 max-w-3xl mx-auto space-y-10">
    <header>
      <h1 class="text-2xl font-light tracking-tight">Settings</h1>
      <p class="text-sm text-muted-foreground mt-1">
        Manage notifications, appearance, and account preferences.
      </p>
    </header>

    <section class="space-y-1">
      <h2 class="text-xs font-medium uppercase tracking-wide text-muted-foreground pb-3 border-b">
        Notifications
      </h2>
      <Row label="Booking updates" hint="Status changes for your service requests.">
        <Switch v-model="prefs.bookingUpdates" />
      </Row>
      <Row label="Promotional emails" hint="Occasional offers and feature announcements.">
        <Switch v-model="prefs.promotions" />
      </Row>
      <Row label="Weekly digest" hint="Summary of activity across your account, every Monday.">
        <Switch v-model="prefs.weeklyDigest" />
      </Row>
      <Row label="In-app sounds" hint="Audible cue when a toast appears.">
        <Switch v-model="prefs.sounds" />
      </Row>
    </section>

    <section class="space-y-1">
      <h2 class="text-xs font-medium uppercase tracking-wide text-muted-foreground pb-3 border-b">
        Appearance
      </h2>
      <Row label="Theme" hint="Light follows the IBM  palette; dark mirrors  g100.">
        <Select v-model="prefs.theme">
          <SelectTrigger class="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="light">Light</SelectItem>
            <SelectItem value="dark">Dark</SelectItem>
            <SelectItem value="system">Match system</SelectItem>
          </SelectContent>
        </Select>
      </Row>
      <Row label="Density" hint="Comfortable padding for desks, compact for dashboards.">
        <Select v-model="prefs.density">
          <SelectTrigger class="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="comfortable">Comfortable</SelectItem>
            <SelectItem value="compact">Compact</SelectItem>
          </SelectContent>
        </Select>
      </Row>
      <Row label="Reduce motion" hint="Disable view-transitions and other animations.">
        <Switch v-model="prefs.reduceMotion" />
      </Row>
    </section>

    <section class="space-y-1">
      <h2 class="text-xs font-medium uppercase tracking-wide text-muted-foreground pb-3 border-b">
        Security
      </h2>
      <Row label="Change password" hint="You'll be signed out of other sessions.">
        <Button variant="outline" size="sm" @click="onChangePassword">Update</Button>
      </Row>
      <Row label="Two-factor authentication" hint="Add an authenticator app for sign-in.">
        <Button variant="outline" size="sm" @click="onEnable2FA">Set up</Button>
      </Row>
      <Row label="Active sessions" hint="Sign out of other devices currently signed in.">
        <Button variant="outline" size="sm" @click="onViewSessions">Manage</Button>
      </Row>
    </section>

    <div class="flex items-center justify-end gap-2 pt-4">
      <Button variant="secondary" size="sm" @click="onReset">Reset</Button>
      <Button size="sm" @click="onSave">Save changes</Button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { reactive } from "vue";

import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { useNotificationsStore } from "@/stores/notifications";
import Row from "@/views/settings/Row.vue";

const toasts = useNotificationsStore();

const defaults = {
  bookingUpdates: true,
  promotions: false,
  weeklyDigest: true,
  sounds: false,
  theme: "light",
  density: "comfortable",
  reduceMotion: false,
};

const prefs = reactive({ ...defaults });

function onSave() {
  toasts.success("Preferences saved");
}

function onReset() {
  Object.assign(prefs, defaults);
  toasts.info("Preferences reset to defaults");
}

function onChangePassword() {
  toasts.info("TODO");
}

function onEnable2FA() {
  toasts.info("TODO");
}

function onViewSessions() {
  toasts.info("TODO");
}
</script>

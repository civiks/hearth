<template>
  <div class="px-6 py-8 max-w-5xl">
    <div v-if="loading" class="flex justify-center py-16">
      <Loader2 class="size-6 animate-spin text-muted-foreground" />
    </div>

    <Alert v-else-if="error" variant="destructive">
      <AlertCircle class="size-4" />
      <AlertDescription>{{ error }}</AlertDescription>
    </Alert>

    <div v-else-if="userData" class="space-y-6">
      <header class="flex items-center gap-4">
        <Avatar class="size-12">
          <AvatarFallback :class="avatarFallbackClass">
            {{ initials(userData.full_name) }}
          </AvatarFallback>
        </Avatar>
        <div>
          <h1 class="text-2xl font-light tracking-tight">
            {{ isOwnProfile ? "My Profile" : `${userData.full_name}'s Profile` }}
          </h1>
          <p class="text-sm text-muted-foreground">
            {{ userData.email }}
          </p>
        </div>
      </header>

      <Card>
        <CardHeader>
          <CardTitle class="text-base font-medium">Basic information</CardTitle>
        </CardHeader>
        <CardContent class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5">
          <Field label="Full name" :value="userData.full_name" />
          <Field label="Email" :value="userData.email" />
          <Field label="Role" :value="userData.role" class="capitalize" />
          <Field label="Account status">
            <StatusPill :status="accountStatus" />
          </Field>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle class="text-base font-medium">Contact</CardTitle>
        </CardHeader>
        <CardContent class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5">
          <Field label="Address" :value="userData.address || 'Not provided'" />
          <Field label="Pincode" :value="userData.pincode || 'Not provided'" />
        </CardContent>
      </Card>

      <Card v-if="userData.role === 'professional'">
        <CardHeader>
          <CardTitle class="text-base font-medium">Professional details</CardTitle>
        </CardHeader>
        <CardContent class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5">
          <Field label="Service" :value="userData.service_name ?? ''" />
          <Field label="Experience" :value="`${userData.experience ?? 0} years`" />
          <Field label="Approval status">
            <StatusPill :status="userData.approval_status ?? 'pending'" />
          </Field>
        </CardContent>
      </Card>

      <div v-if="isOwnProfile && !isAdmin" class="flex flex-wrap gap-2">
        <Button @click="openEdit">
          <Edit2 class="mr-2 size-4" />
          Edit details
        </Button>
        <Button variant="destructive" @click="confirmDelete">
          <Trash2 class="mr-2 size-4" />
          Delete account
        </Button>
      </div>

      <div
        v-if="auth.role === 'admin' && !isOwnProfile"
        class="flex flex-wrap gap-2"
      >
        <Button
          :variant="userData.is_blocked ? 'default' : 'destructive'"
          @click="toggleBlock"
        >
          <component :is="userData.is_blocked ? Unlock : Lock" class="mr-2 size-4" />
          {{ userData.is_blocked ? "Unblock" : "Block" }} user
        </Button>
        <template
          v-if="userData.role === 'professional' && userData.approval_status === 'pending'"
        >
          <Button @click="updateApproval('approved')">
            <CheckCircle class="mr-2 size-4" />
            Approve
          </Button>
          <Button variant="secondary" @click="updateApproval('rejected')">
            <XCircle class="mr-2 size-4" />
            Reject
          </Button>
        </template>
        <Button variant="destructive" @click="deleteUserAccount">
          <Trash2 class="mr-2 size-4" />
          Delete user
        </Button>
      </div>
    </div>

    <Dialog :open="showEdit" @update:open="(v) => !v && closeEdit()">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit profile</DialogTitle>
          <DialogDescription>Update your personal details</DialogDescription>
        </DialogHeader>
        <form class="space-y-4" @submit.prevent="saveChanges">
          <div class="space-y-2">
            <Label for="edit_name">Full name</Label>
            <Input id="edit_name" v-model="editForm.full_name" required />
          </div>
          <div class="space-y-2">
            <Label for="edit_address">Address</Label>
            <Input id="edit_address" v-model="editForm.address" />
          </div>
          <div class="space-y-2">
            <Label for="edit_pincode">Pincode</Label>
            <Input id="edit_pincode" v-model="editForm.pincode" pattern="[0-9]{6}" />
          </div>
          <DialogFooter>
            <Button type="button" variant="secondary" @click="closeEdit">Cancel</Button>
            <Button type="submit" :disabled="loading">Save changes</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script lang="ts" setup>
import { AlertCircle, CheckCircle, Edit2, Loader2, Lock, Trash2, Unlock, XCircle } from "lucide-vue-next";
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import StatusPill from "@/components/StatusBadge.vue";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
import { initials } from "@/lib/format";
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";
import Field from "@/views/account/Field.vue";

interface UserData {
  id: number;
  email: string;
  role: string | null;
  full_name: string;
  address: string | null;
  pincode: string | null;
  is_blocked: boolean;
  service_id?: number | null;
  service_name?: string | null;
  experience?: number | null;
  approval_status?: string | null;
}

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const toasts = useNotificationsStore();

const userData = ref<UserData | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);
const showEdit = ref(false);
const editForm = ref({ full_name: "", address: "", pincode: "" });

const userId = computed(() => route.params.id as string | undefined);
const isOwnProfile = computed(() => !userId.value || userId.value === String(auth.user_id));
const isAdmin = computed(() => auth.role === "admin");

const accountStatus = computed(() => {
  if (!userData.value) return "active";
  if (userData.value.is_blocked) return "blocked";
  if (userData.value.role === "professional")
    return userData.value.approval_status ?? "pending";
  return "active";
});

const avatarFallbackClass = computed(() => {
  if (!userData.value) return "bg-primary text-primary-foreground";
  if (userData.value.is_blocked) return "bg-destructive text-destructive-foreground";
  if (userData.value.approval_status === "pending") return "bg-warning text-foreground";
  if (userData.value.approval_status === "approved") return "bg-success text-foreground";
  return "bg-primary text-primary-foreground";
});

onMounted(fetchUser);
watch(() => route.params.id, fetchUser);

async function fetchUser() {
  loading.value = true;
  error.value = null;
  try {
    const path = isOwnProfile.value ? "/api/users/me" : `/api/users/${userId.value}`;
    userData.value = await api.get<UserData>(path);
    if (isOwnProfile.value && userData.value) {
      auth.updateUserDetails({
        full_name: userData.value.full_name,
        address: userData.value.address,
        pincode: userData.value.pincode,
      });
    }
  } catch (err) {
    error.value = err instanceof ApiError ? err.detail : "Error loading user data.";
  } finally {
    loading.value = false;
  }
}

function openEdit() {
  if (!userData.value) return;
  editForm.value = {
    full_name: userData.value.full_name,
    address: userData.value.address ?? "",
    pincode: userData.value.pincode ?? "",
  };
  showEdit.value = true;
}
function closeEdit() {
  showEdit.value = false;
}

async function saveChanges() {
  loading.value = true;
  try {
    await api.put("/api/users/me", editForm.value);
    auth.updateUserDetails(editForm.value);
    await fetchUser();
    toasts.success("Profile updated");
    closeEdit();
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to update profile.");
  } finally {
    loading.value = false;
  }
}

async function confirmDelete() {
  if (!confirm("Delete your account? This cannot be undone.")) return;
  try {
    await api.delete("/api/users/me");
    await auth.logout();
    router.push("/");
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to delete account.");
  }
}

async function toggleBlock() {
  if (!userData.value) return;
  const next = !userData.value.is_blocked;
  if (!confirm(`${next ? "Block" : "Unblock"} this user?`)) return;
  try {
    await api.put(`/api/users/${userId.value}`, { is_blocked: next });
    await fetchUser();
    toasts.success(`User ${next ? "blocked" : "unblocked"}`);
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to update user.");
  }
}

async function updateApproval(status: string) {
  if (!confirm(`${status} this professional?`)) return;
  try {
    await api.put(`/api/users/${userId.value}`, { approval_status: status });
    await fetchUser();
    toasts.success(`Marked as ${status}`);
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to update status.");
  }
}

async function deleteUserAccount() {
  if (!confirm("Delete this user? This cannot be undone.")) return;
  try {
    await api.delete(`/api/users/${userId.value}`);
    router.push("/admin/users");
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to delete user.");
  }
}
</script>

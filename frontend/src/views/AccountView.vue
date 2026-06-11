<template>
  <div class="px-6 py-8 max-w-2xl mx-auto">
    <div v-if="loading" class="flex justify-center py-16">
      <PhCircleNotch class="size-6 animate-spin text-muted-foreground" />
    </div>

    <Alert v-else-if="error" variant="destructive">
      <PhWarningCircle class="size-4" />
      <AlertDescription>{{ error }}</AlertDescription>
    </Alert>

    <div v-else-if="userData" class="space-y-8">
      <!-- Hero -->
      <header class="flex items-center gap-5">
        <Avatar class="size-16 shrink-0">
          <AvatarFallback :class="avatarFallbackClass" class="text-xl font-medium">
            {{ initials(userData.full_name) }}
          </AvatarFallback>
        </Avatar>
        <div class="min-w-0">
          <h1 class="font-display text-2xl font-semibold tracking-tight truncate">{{ userData.full_name }}</h1>
          <p class="text-sm tracking-tight text-muted-foreground mt-1 flex items-center gap-2 flex-wrap">
            <span class="capitalize">{{ userData.role }}</span>
            <span class="text-muted-foreground/30">·</span>
            <StatusBadge :status="accountStatus" />
          </p>
        </div>
      </header>

      <!-- Contact -->
      <section class="bg-card rounded-xl soft-card p-6 space-y-5">
        <p class="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Contact</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-5">
          <Field label="Email" :value="userData.email" />
          <Field label="Address" :value="userData.address || '—'" />
          <Field label="Pincode" :value="userData.pincode || '—'" />
        </div>
      </section>

      <!-- Professional details -->
      <section v-if="userData.role === 'professional'" class="bg-card rounded-xl soft-card p-6 space-y-5">
        <p class="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Professional</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-5">
          <Field label="Service" :value="userData.service_name || '—'" />
          <Field label="Experience" :value="userData.experience ? `${userData.experience} yrs` : '—'" />
          <Field label="Approval status">
            <StatusBadge :status="userData.approval_status ?? 'pending'" />
          </Field>
        </div>
      </section>

      <!-- Own profile actions -->
      <div v-if="isOwnProfile && !isAdmin" class="flex flex-wrap gap-2">
        <Button @click="openEdit">
          <PhPencilSimple class="mr-2 size-4" />
          Edit details
        </Button>
        <Button variant="destructive" @click="confirmDelete">
          <PhTrash class="mr-2 size-4" />
          Delete account
        </Button>
      </div>

      <!-- Admin actions -->
      <div v-if="auth.role === 'admin' && !isOwnProfile" class="flex flex-wrap gap-2">
        <Button :variant="userData.is_blocked ? 'default' : 'destructive'" @click="toggleBlock">
          <component :is="userData.is_blocked ? PhLockOpen : PhLock" class="mr-2 size-4" />
          {{ userData.is_blocked ? "Unblock" : "Block" }} user
        </Button>
        <template v-if="userData.role === 'professional' && userData.approval_status === 'pending'">
          <Button @click="updateApproval('approved')">
            <PhCheckCircle class="mr-2 size-4" />
            Approve
          </Button>
          <Button variant="secondary" @click="updateApproval('rejected')">
            <PhXCircle class="mr-2 size-4" />
            Reject
          </Button>
        </template>
        <Button variant="destructive" @click="deleteUserAccount">
          <PhTrash class="mr-2 size-4" />
          Delete user
        </Button>
      </div>
    </div>

    <!-- Edit drawer -->
    <ResponsiveSheet
      v-if="showEdit"
      :open="true"
      title="Edit profile"
      description="Update your personal details"
      @close="closeEdit"
    >
      <div class="space-y-2">
        <Label for="edit_name" class="text-sm font-semibold tracking-tight">Full name</Label>
        <Input id="edit_name" v-model="editForm.full_name" required />
      </div>
      <div class="space-y-2">
        <Label for="edit_address" class="text-sm font-semibold tracking-tight">Address</Label>
        <Input id="edit_address" v-model="editForm.address" />
      </div>
      <div class="space-y-2">
        <Label for="edit_pincode" class="text-sm font-semibold tracking-tight">Pincode</Label>
        <Input id="edit_pincode" v-model="editForm.pincode" pattern="[0-9]{6}" class="tabular-nums" />
      </div>

      <template #footer>
        <Button type="button" variant="outline" @click="closeEdit">Cancel</Button>
        <Button type="button" class="flex-1" :disabled="loading" @click="saveChanges">Save changes</Button>
      </template>
    </ResponsiveSheet>
  </div>
</template>

<script lang="ts" setup>
import {
  PhWarningCircle,
  PhCheckCircle,
  PhPencilSimple,
  PhCircleNotch,
  PhLock,
  PhTrash,
  PhLockOpen,
  PhXCircle,
} from '@phosphor-icons/vue';
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import StatusBadge from "@/components/StatusBadge.vue";
import { useConfirm } from "@/composables/useConfirm";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import ResponsiveSheet from "@/components/ui/ResponsiveSheet.vue";
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
const { confirm } = useConfirm();

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

watch(
  [userData, isOwnProfile],
  ([u, own]) => {
    if (!u) return;
    document.title = own ? "Account — hearth" : `${u.full_name} — hearth`;
  },
);

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
  if (!await confirm({
    title: "Delete your account?",
    description: "All your bookings, saved addresses, and personal details will be permanently erased. You'll be signed out immediately and this account can't be recovered.",
    variant: "destructive",
    confirmLabel: "Delete my account",
  })) return;
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
  if (!await confirm({
    title: next ? "Block this user?" : "Unblock this user?",
    description: next
      ? "They'll be signed out immediately and won't be able to log in, place new requests, or contact professionals until you unblock them. Existing requests are preserved."
      : "They'll regain full access to the platform and can sign in and place bookings right away.",
    confirmLabel: next ? "Block user" : "Unblock user",
  })) return;
  try {
    await api.put(`/api/users/${userId.value}`, { is_blocked: next });
    await fetchUser();
    toasts.success(`User ${next ? "blocked" : "unblocked"}`);
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to update user.");
  }
}

async function updateApproval(status: string) {
  if (!await confirm({
    title: status === "approved" ? "Approve this professional?" : "Reject this professional?",
    description: status === "approved"
      ? "They'll be able to accept service requests and start appearing in customer search results right away. You can revoke approval later if needed."
      : "They won't be able to accept requests on the platform. They'll keep their account but stay invisible to customers. You can revisit this decision from their profile.",
    confirmLabel: status === "approved" ? "Approve" : "Reject",
  })) return;
  try {
    await api.put(`/api/users/${userId.value}`, { approval_status: status });
    await fetchUser();
    toasts.success(`Marked as ${status}`);
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to update status.");
  }
}

async function deleteUserAccount() {
  if (!await confirm({
    title: "Delete this user?",
    description: "Their account, booking history, saved addresses, and any associated records will be permanently erased. This can't be undone.",
    variant: "destructive",
    confirmLabel: "Delete user",
  })) return;
  try {
    await api.delete(`/api/users/${userId.value}`);
    router.push("/admin/users");
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to delete user.");
  }
}
</script>

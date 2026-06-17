<template>
  <div class="px-6 py-8 max-w-lg mx-auto">
    <div v-if="loading" class="flex justify-center py-16">
      <PhCircleNotch class="size-6 animate-spin text-muted-foreground" />
    </div>

    <Alert v-else-if="error" variant="destructive">
      <PhWarningCircle class="size-4" weight="bold" />
      <AlertDescription>{{ error }}</AlertDescription>
    </Alert>

    <div v-else-if="userData" class="space-y-7">
      <!-- Hero -->
      <header class="flex flex-col items-center gap-4 text-center">
        <component
          :is="canEditSelf ? 'button' : 'div'"
          :type="canEditSelf ? 'button' : undefined"
          class="relative inline-block rounded-full"
          :class="canEditSelf && 'press'"
          :disabled="canEditSelf ? uploadingAvatar : undefined"
          @click="canEditSelf && pickAvatar()"
        >
          <UserAvatar
            :name="userData.full_name"
            :src="userData.avatar_url"
            size="size-24"
            :fallback-class="cn(avatarFallbackClass, 'text-2xl font-medium')"
          />
          <span
            v-if="uploadingAvatar"
            class="absolute inset-0 flex items-center justify-center rounded-full bg-black/45"
          >
            <PhCircleNotch class="size-6 animate-spin text-white" weight="bold" />
          </span>
          <span
            v-if="canEditSelf"
            class="absolute -bottom-0.5 -right-0.5 flex size-7 items-center justify-center rounded-full bg-foreground text-background ring-2 ring-card"
          >
            <PhCamera class="size-3.5" weight="bold" />
          </span>
          <input
            ref="avatarInput"
            type="file"
            accept="image/*"
            class="hidden"
            @change="onAvatarSelected"
          />
        </component>
        <div class="min-w-0">
          <h1 class="font-display text-2xl font-semibold tracking-tight">{{ userData.full_name }}</h1>
          <p class="mt-2 flex items-center justify-center gap-2 text-sm tracking-tight text-muted-foreground">
            <span class="capitalize">{{ userData.role }}</span>
            <span class="text-muted-foreground/30">·</span>
            <StatusBadge :status="accountStatus" pill />
          </p>
        </div>
      </header>

      <!-- Edit details -->
      <Button
        v-if="isOwnProfile && !isAdmin"
        variant="secondary"
        class="h-12 w-full rounded-full text-[0.95rem] font-medium"
        @click="openEdit"
      >
        <PhPencilSimple class="mr-2 size-4" weight="bold" />
        Edit details
      </Button>

      <!-- Contact -->
      <section class="space-y-2">
        <p class="px-1 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Contact</p>
        <div class="divide-y divide-border overflow-hidden rounded-xl bg-card soft-card">
          <AccountRow :icon="PhEnvelopeSimple" label="Email" :value="userData.email" />
          <AccountRow
            :icon="PhMapPin"
            label="Address"
            :value="userData.address || 'Not set'"
            :interactive="canEditSelf"
            @click="openEdit"
          />
          <AccountRow
            :icon="PhNavigationArrow"
            label="Pincode"
            :value="userData.pincode || 'Not set'"
            :interactive="canEditSelf"
            @click="openEdit"
          />
        </div>
      </section>

      <!-- Professional details -->
      <section v-if="userData.role === 'professional'" class="space-y-2">
        <p class="px-1 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Professional</p>
        <div class="divide-y divide-border overflow-hidden rounded-xl bg-card soft-card">
          <AccountRow :icon="PhBriefcase" label="Service" :value="userData.service_name || '—'" />
          <AccountRow
            :icon="PhMedal"
            label="Experience"
            :value="userData.experience ? `${userData.experience} yrs` : '—'"
          />
          <AccountRow :icon="PhSealCheck" label="Approval">
            <template #value>
              <StatusBadge :status="userData.approval_status ?? 'pending'" pill />
            </template>
          </AccountRow>
        </div>
      </section>

      <!-- Advanced (own profile) -->
      <section v-if="canEditSelf" class="space-y-2">
        <p class="px-1 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Advanced</p>
        <div class="overflow-hidden rounded-xl bg-card soft-card">
          <AccountRow
            :icon="PhTrash"
            label="Delete account"
            description="Permanently erase this account and all its data."
            interactive
            danger
            @click="confirmDelete"
          />
        </div>
      </section>

      <!-- Admin actions -->
      <section v-if="isAdmin && !isOwnProfile" class="space-y-2">
        <p class="px-1 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Manage user</p>
        <div class="divide-y divide-border overflow-hidden rounded-xl bg-card soft-card">
          <template v-if="userData.role === 'professional' && userData.approval_status === 'pending'">
            <AccountRow
              :icon="PhCheckCircle"
              label="Approve professional"
              description="Let them accept requests and appear in search."
              interactive
              @click="updateApproval('approved')"
            />
            <AccountRow
              :icon="PhXCircle"
              label="Reject professional"
              description="Keep their account but hide them from customers."
              interactive
              @click="updateApproval('rejected')"
            />
          </template>
          <AccountRow
            :icon="userData.is_blocked ? PhLockOpen : PhLock"
            :label="userData.is_blocked ? 'Unblock user' : 'Block user'"
            :description="userData.is_blocked ? 'Restore full access to the platform.' : 'Sign them out and prevent new sign-ins.'"
            interactive
            @click="toggleBlock"
          />
          <AccountRow
            :icon="PhTrash"
            label="Delete user"
            description="Permanently erase this account and all its data."
            interactive
            danger
            @click="deleteUserAccount"
          />
        </div>
      </section>
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
        <Button type="button" variant="secondary" class="rounded-[1rem]" @click="closeEdit">Cancel</Button>
        <Button type="button" class="flex-1 rounded-[1rem]" :disabled="loading" @click="saveChanges">Save changes</Button>
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
  PhEnvelopeSimple,
  PhMapPin,
  PhNavigationArrow,
  PhBriefcase,
  PhMedal,
  PhSealCheck,
  PhCamera,
} from '@phosphor-icons/vue';
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import StatusBadge from "@/components/StatusBadge.vue";
import { useConfirm } from "@/composables/useConfirm";
import UserAvatar from "@/components/Avatar.vue";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import ResponsiveSheet from "@/components/ui/ResponsiveSheet.vue";
import { ApiError, api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";
import { useNotificationsStore } from "@/stores/notifications";
import AccountRow from "@/views/account/AccountRow.vue";

interface UserData {
  id: number;
  email: string;
  role: string | null;
  full_name: string;
  address: string | null;
  pincode: string | null;
  is_blocked: boolean;
  avatar_url?: string | null;
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
const avatarInput = ref<HTMLInputElement | null>(null);
const uploadingAvatar = ref(false);

const userId = computed(() => route.params.id as string | undefined);
const isOwnProfile = computed(() => !userId.value || userId.value === String(auth.user_id));
const isAdmin = computed(() => auth.role === "admin");
const canEditSelf = computed(() => isOwnProfile.value && !isAdmin.value);

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

function pickAvatar() {
  if (!uploadingAvatar.value) avatarInput.value?.click();
}

async function onAvatarSelected(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  input.value = "";
  if (!file) return;
  if (!file.type.startsWith("image/")) {
    toasts.error("Please choose an image file.");
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    toasts.error("Image must be 5 MB or smaller.");
    return;
  }
  uploadingAvatar.value = true;
  try {
    const updated = await api.upload<UserData>("/api/users/me/avatar", file);
    userData.value = updated;
    auth.updateUserDetails({ avatar_url: updated.avatar_url });
    toasts.success("Photo updated");
  } catch (err) {
    toasts.error(err instanceof ApiError ? err.detail : "Failed to upload photo.");
  } finally {
    uploadingAvatar.value = false;
  }
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

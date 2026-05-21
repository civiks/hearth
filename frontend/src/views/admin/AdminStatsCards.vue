<template>
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
    <StatCard label="Services" :value="servicesCount" />
    <StatCard label="Professionals" :value="professionalsCount" />
    <StatCard label="Users" :value="usersCount" />
    <StatCard label="Pending approvals" :value="pendingApprovals" />
  </div>
</template>

<script lang="ts" setup>
import StatCard from "@/components/StatCard.vue";

defineProps<{
  servicesCount: number;
  professionalsCount: number;
  usersCount: number;
  pendingApprovals: number;
}>();
</script>

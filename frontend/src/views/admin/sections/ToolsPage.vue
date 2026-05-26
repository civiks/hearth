<template>
  <div class="px-6 py-8 max-w-3xl mx-auto space-y-6">
    <PageHeader title="Tools" description="CSV exports and Celery job triggers for testing the backend pipelines." />
    <ExportSection />
    <BackendJobsSection />
  </div>
</template>

<script lang="ts" setup>
import PageHeader from "@/components/PageHeader.vue";
import BackendJobsSection from "@/views/admin/BackendJobsSection.vue";
import ExportSection from "@/views/admin/ExportSection.vue";
</script>

<template>
  <div class="px-4 py-4 sm:px-6 sm:py-5 max-w-3xl mx-auto space-y-6">
    <PageHeader
      title="Tools"
      description="CSV exports and Celery job triggers for testing the backend pipelines."
    />
    <ExportSection />
    <BackendJobsSection />
  </div>
</template>

<script lang="ts" setup>
import PageHeader from "@/components/PageHeader.vue";
import BackendJobsSection from "@/views/admin/BackendJobsSection.vue";
import ExportSection from "@/views/admin/ExportSection.vue";
</script>

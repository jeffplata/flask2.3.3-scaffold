<script>
import DataTable from "./components/dataTable.vue";

export default {
  components: {
    "data-table": DataTable,
  },
  setup() {
    return {
    }
  },
};
</script>

<template>
  <div>
    <data-table :apiEndpoint="'/api_v1/'"></data-table>
  </div>
</template>

<style></style>

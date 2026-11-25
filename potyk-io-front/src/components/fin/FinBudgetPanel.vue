<script setup lang="ts">
import Button from "primevue/button";
import InputNumber from "primevue/inputnumber";
import { ref, watch } from "vue";

const props = defineProps<{
  dailyBudget: number;
  busy?: boolean;
}>();

const emit = defineEmits<{
  save: [value: number];
}>();

const value = ref<number | null>(props.dailyBudget);

watch(
  () => props.dailyBudget,
  (v) => {
    value.value = v;
  },
);

function submit(): void {
  if (value.value != null && value.value >= 1) emit("save", value.value);
}
</script>

<template>
  <details class="panel">
    <summary>Изменить бюджет на день</summary>
    <form class="form" @submit.prevent="submit">
      <label>
        <span>Новый бюджет (₽)</span>
        <InputNumber v-model="value" :min="1" :use-grouping="false" />
      </label>
      <Button type="submit" label="Сохранить" :loading="busy" />
    </form>
  </details>
</template>

<style scoped>
.panel {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  margin-bottom: 0.75rem;
}

summary {
  cursor: pointer;
  font-weight: 600;
}

.form {
  display: grid;
  gap: 0.75rem;
  margin-top: 0.75rem;
}

label {
  display: grid;
  gap: 0.35rem;
  font-size: 0.9rem;
}
</style>

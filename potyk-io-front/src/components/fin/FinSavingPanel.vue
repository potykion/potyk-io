<script setup lang="ts">
import Button from "primevue/button";
import DatePicker from "primevue/datepicker";
import InputText from "primevue/inputtext";
import { computed, reactive, watch } from "vue";
import type { Saving, SavingPayload } from "@/api/fin";
import AmountField from "@/components/fin/AmountField.vue";

const props = defineProps<{
  defaultDate: string;
  editing: Saving | null;
  todayClosed: boolean;
  pickMode: boolean;
  busy?: boolean;
}>();

const emit = defineEmits<{
  create: [payload: SavingPayload];
  update: [id: number, payload: SavingPayload];
  cancel: [];
  togglePick: [];
  confirmPick: [];
  cancelPick: [];
}>();

const form = reactive({
  date: null as Date | null,
  amount: null as number | null,
  formula: "",
  note: "",
});

const title = computed(() => (props.editing ? "Изменить сейв" : "Зафиксировать сейв"));
const canShow = computed(() => !props.todayClosed || Boolean(props.editing));

function parseIso(iso: string): Date {
  return new Date(`${iso}T12:00:00`);
}

function toIso(d: Date | null): string {
  if (!d) return "";
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

watch(
  () => props.editing,
  (saving) => {
    if (!saving) return;
    form.date = parseIso(saving.date);
    form.amount = saving.amount;
    form.formula = String(saving.amount);
    form.note = saving.note;
  },
);

watch(
  () => props.defaultDate,
  (iso) => {
    if (!props.editing) form.date = parseIso(iso);
  },
  { immediate: true },
);

function setAmount(value: number): void {
  form.amount = value;
  form.formula = String(value);
}

defineExpose({ setAmount });

function submit(): void {
  const date = toIso(form.date);
  if (!date || form.amount == null || form.amount < 1) return;
  const payload: SavingPayload = {
    date,
    amount: form.amount,
    note: form.note.trim(),
  };
  if (props.editing) {
    emit("update", props.editing.id, payload);
  } else {
    emit("create", payload);
    form.amount = null;
    form.formula = "";
    form.note = "";
  }
}
</script>

<template>
  <details v-if="canShow" class="panel" :open="Boolean(editing) || pickMode">
    <summary>{{ title }}</summary>
    <p v-if="!editing" class="muted">Когда реально перевёл на накопительный в банке</p>
    <form class="form" @submit.prevent="submit">
      <label>
        <span>Сумма</span>
        <AmountField v-model:amount="form.amount" v-model:formula="form.formula" />
      </label>
      <label>
        <span>Дата</span>
        <DatePicker v-model="form.date" date-format="yy-mm-dd" show-icon />
      </label>
      <label>
        <span>Заметка</span>
        <InputText v-model="form.note" placeholder="необязательно" />
      </label>

      <div v-if="!editing" class="pick-row">
        <Button
          type="button"
          label="Выбор остатков"
          severity="secondary"
          @click="emit('togglePick')"
        />
        <template v-if="pickMode">
          <Button
            type="button"
            icon="pi pi-check"
            severity="success"
            rounded
            aria-label="Подтвердить остатки"
            @click="emit('confirmPick')"
          />
          <Button
            type="button"
            icon="pi pi-times"
            severity="danger"
            rounded
            aria-label="Отменить выбор"
            @click="emit('cancelPick')"
          />
        </template>
      </div>

      <div class="actions">
        <Button
          type="submit"
          :label="editing ? 'Сохранить' : 'Зафиксировать'"
          :loading="busy"
        />
        <Button
          v-if="editing"
          type="button"
          label="Отмена"
          severity="secondary"
          text
          @click="emit('cancel')"
        />
      </div>
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

.muted {
  color: #64748b;
  margin: 0.5rem 0 0;
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

.pick-row,
.actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  align-items: center;
}
</style>

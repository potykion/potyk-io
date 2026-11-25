<script setup lang="ts">
import AutoComplete from "primevue/autocomplete";
import Button from "primevue/button";
import Checkbox from "primevue/checkbox";
import DatePicker from "primevue/datepicker";
import InputText from "primevue/inputtext";
import SelectButton from "primevue/selectbutton";
import { computed, reactive, ref, watch } from "vue";
import type { Expense, ExpensePayload } from "@/api/fin";
import AmountField from "@/components/fin/AmountField.vue";
import { evalAmountExpression } from "@/utils/calc";

const props = defineProps<{
  categories: string[];
  defaultDate: string;
  editing: Expense | null;
  todayClosed: boolean;
  busy?: boolean;
}>();

const emit = defineEmits<{
  create: [payload: ExpensePayload];
  createBulk: [payloads: ExpensePayload[]];
  update: [id: number, payload: ExpensePayload];
  cancel: [];
}>();

type Mode = "single" | "multi";
const mode = ref<Mode>("single");
const modeOptions = [
  { label: "Одна", value: "single" },
  { label: "Мульти", value: "multi" },
];

type Row = {
  date: Date | null;
  amount: number | null;
  formula: string;
  category: string;
  description: string;
  optional: boolean;
};

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

function emptyRow(dateIso = props.defaultDate): Row {
  return {
    date: parseIso(dateIso),
    amount: null,
    formula: "",
    category: "",
    description: "",
    optional: false,
  };
}

const single = reactive<Row>(emptyRow());
const rows = ref<Row[]>([emptyRow()]);
const categorySuggestions = ref<string[]>([]);

const title = computed(() => (props.editing ? "Изменить трату" : "Добавить трату"));
const canShow = computed(() => !props.todayClosed || Boolean(props.editing));

watch(
  () => props.editing,
  (expense) => {
    if (!expense) return;
    mode.value = "single";
    single.date = parseIso(expense.date);
    single.amount = expense.amount;
    single.formula = String(expense.amount);
    single.category = expense.category;
    single.description = expense.description;
    single.optional = expense.optional;
  },
);

watch(
  () => props.defaultDate,
  (iso) => {
    if (props.editing) return;
    single.date = parseIso(iso);
    for (const row of rows.value) {
      if (!row.amount && !row.category) row.date = parseIso(iso);
    }
  },
);

function searchCategory(event: { query: string }): void {
  const q = event.query.trim().toLowerCase();
  categorySuggestions.value = props.categories.filter((c) => c.toLowerCase().includes(q));
  if (q && !categorySuggestions.value.some((c) => c.toLowerCase() === q)) {
    categorySuggestions.value = [event.query.trim(), ...categorySuggestions.value];
  }
}

function toPayload(row: Row): ExpensePayload | null {
  const date = toIso(row.date);
  let amount = row.amount;
  if (amount == null && row.formula) {
    amount = evalAmountExpression(row.formula);
  }
  const category = String(row.category || "").trim();
  if (!date || amount == null || amount < 1 || !category) return null;
  return {
    date,
    amount,
    category,
    description: row.description.trim(),
    optional: row.optional,
  };
}

function submitSingle(): void {
  const payload = toPayload(single);
  if (!payload) return;
  if (props.editing) {
    emit("update", props.editing.id, payload);
  } else {
    emit("create", payload);
    single.amount = null;
    single.formula = "";
    single.description = "";
    single.optional = false;
  }
}

function submitMulti(): void {
  const payloads = rows.value.map(toPayload).filter(Boolean) as ExpensePayload[];
  if (!payloads.length) return;
  emit("createBulk", payloads);
  rows.value = [emptyRow()];
}

function addRow(): void {
  rows.value.push(emptyRow());
}

function removeRow(index: number): void {
  if (rows.value.length <= 1) return;
  rows.value.splice(index, 1);
}
</script>

<template>
  <details v-if="canShow" class="panel" :open="Boolean(editing)">
    <summary>{{ title }}</summary>

    <SelectButton
      v-if="!editing"
      v-model="mode"
      :options="modeOptions"
      option-label="label"
      option-value="value"
      class="mode-tabs"
      :allow-empty="false"
    />

    <form v-if="editing || mode === 'single'" class="form" @submit.prevent="submitSingle">
      <label>
        <span>Дата</span>
        <DatePicker v-model="single.date" date-format="yy-mm-dd" show-icon />
      </label>
      <label>
        <span>Сумма</span>
        <AmountField v-model:amount="single.amount" v-model:formula="single.formula" />
      </label>
      <label>
        <span>Категория</span>
        <AutoComplete
          v-model="single.category"
          :suggestions="categorySuggestions"
          dropdown
          :force-selection="false"
          placeholder="еда, быт..."
          @complete="searchCategory"
        />
      </label>
      <label>
        <span>Описание</span>
        <InputText v-model="single.description" placeholder="необязательно" />
      </label>
      <label class="check">
        <Checkbox v-model="single.optional" binary />
        <span>Необязательный расход</span>
      </label>
      <div class="actions">
        <Button
          type="submit"
          :label="editing ? 'Сохранить' : 'Добавить трату'"
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

    <div v-else class="multi">
      <div v-for="(row, index) in rows" :key="index" class="multi-row">
        <DatePicker v-model="row.date" date-format="yy-mm-dd" show-icon />
        <AmountField
          v-model:amount="row.amount"
          v-model:formula="row.formula"
          allow-formula
        />
        <AutoComplete
          v-model="row.category"
          :suggestions="categorySuggestions"
          dropdown
          :force-selection="false"
          placeholder="кат."
          @complete="searchCategory"
        />
        <InputText v-model="row.description" placeholder="описание" />
        <label class="check">
          <Checkbox v-model="row.optional" binary />
          <span>Необяз.</span>
        </label>
        <Button
          type="button"
          icon="pi pi-minus"
          severity="danger"
          text
          rounded
          :disabled="rows.length <= 1"
          @click="removeRow(index)"
        />
      </div>
      <div class="actions">
        <Button type="button" icon="pi pi-plus" severity="secondary" @click="addRow" />
        <Button
          type="button"
          label="Добавить траты"
          :loading="busy"
          @click="submitMulti"
        />
      </div>
    </div>
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

.mode-tabs {
  margin: 0.75rem 0;
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

.check {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.multi {
  display: grid;
  gap: 0.75rem;
  margin-top: 0.75rem;
}

.multi-row {
  display: grid;
  gap: 0.4rem;
  grid-template-columns: 1fr;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
}

@media (min-width: 900px) {
  .multi-row {
    grid-template-columns: 10rem 8rem 8rem 1fr auto auto;
    align-items: center;
  }
}
</style>

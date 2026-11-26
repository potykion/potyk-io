<script setup lang="ts">
import AutoComplete from "primevue/autocomplete";
import Button from "primevue/button";
import DatePicker from "primevue/datepicker";
import InputText from "primevue/inputtext";
import SelectButton from "primevue/selectbutton";
import { reactive, ref, watch } from "vue";
import type { ExpensePayload, SavingPayload } from "@/api/fin";
import AmountField from "@/components/fin/AmountField.vue";
import { evalAmountExpression } from "@/utils/calc";

const props = defineProps<{
  categories: string[];
  expenseDefaultDate: string;
  savingDefaultDate: string;
  todayClosed: boolean;
  busy?: boolean;
}>();

const emit = defineEmits<{
  createExpense: [payload: ExpensePayload];
  createSaving: [payload: SavingPayload];
}>();

type Mode = "expense" | "saving";
const mode = ref<Mode>("expense");
const modeOptions = [
  { label: "Трата", value: "expense" as const },
  { label: "Сейф", value: "saving" as const },
];
const categorySuggestions = ref<string[]>([]);

const expense = reactive({
  date: null as Date | null,
  amount: null as number | null,
  formula: "",
  category: "",
  description: "",
});

const saving = reactive({
  amount: null as number | null,
  formula: "",
});

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
  () => props.expenseDefaultDate,
  (iso) => {
    if (iso) expense.date = parseIso(iso);
  },
  { immediate: true },
);

function searchCategory(event: { query: string }): void {
  const q = event.query.trim().toLowerCase();
  categorySuggestions.value = props.categories.filter((c) => c.toLowerCase().includes(q));
  if (q && !categorySuggestions.value.some((c) => c.toLowerCase() === q)) {
    categorySuggestions.value = [event.query.trim(), ...categorySuggestions.value];
  }
}

function resolveAmount(amount: number | null, formula: string): number | null {
  if (amount != null) return amount;
  if (formula) return evalAmountExpression(formula);
  return null;
}

function submitExpense(): void {
  const date = toIso(expense.date);
  const amount = resolveAmount(expense.amount, expense.formula);
  const category = expense.category.trim();
  if (!date || amount == null || amount < 1 || !category) return;
  emit("createExpense", {
    date,
    amount,
    category,
    description: expense.description.trim(),
    optional: false,
  });
  expense.amount = null;
  expense.formula = "";
  expense.description = "";
}

function submitSaving(): void {
  const amount = resolveAmount(saving.amount, saving.formula);
  if (!props.savingDefaultDate || amount == null || amount < 1) return;
  emit("createSaving", {
    date: props.savingDefaultDate,
    amount,
    note: "",
  });
  saving.amount = null;
  saving.formula = "";
}
</script>

<template>
  <div v-if="!todayClosed" class="quick-card">
    <a
      class="ops-link"
      href="https://www.tbank.ru/mybank/operations/"
      target="_blank"
      rel="noopener noreferrer"
      title="где смотреть траты"
      aria-label="где смотреть траты"
    >
      <i class="pi pi-external-link" aria-hidden="true" />
    </a>
    <div class="mode-wrap">
      <SelectButton
        v-model="mode"
        :options="modeOptions"
        option-label="label"
        option-value="value"
        :allow-empty="false"
      />
    </div>

    <form v-if="mode === 'expense'" class="form" @submit.prevent="submitExpense">
      <AmountField
        v-model:amount="expense.amount"
        v-model:formula="expense.formula"
        allow-formula
        large
        placeholder="Сумма, ₽"
      />
      <AutoComplete
        v-model="expense.category"
        class="category"
        :suggestions="categorySuggestions"
        dropdown
        :force-selection="false"
        placeholder="категория"
        @complete="searchCategory"
      />
      <div class="row">
        <DatePicker v-model="expense.date" date-format="yy-mm-dd" show-icon class="date" />
        <InputText v-model="expense.description" class="description" placeholder="описание" />
      </div>
      <Button type="submit" label="Добавить трату" :loading="busy" />
    </form>

    <form v-else class="form" @submit.prevent="submitSaving">
      <AmountField
        v-model:amount="saving.amount"
        v-model:formula="saving.formula"
        allow-formula
        large
        placeholder="Сумма, ₽"
      />
      <Button type="submit" label="Зафиксировать" :loading="busy" />
    </form>
  </div>
</template>

<style scoped>
.quick-card {
  position: relative;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 0.75rem;
  margin-top: 25vh;
  margin-bottom: 0.75rem;
}

.ops-link {
  position: absolute;
  top: 0.65rem;
  right: 0.65rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  color: #64748b;
  text-decoration: none;
  border-radius: 0.4rem;
}

.ops-link:hover {
  color: #0f172a;
  background: #f1f5f9;
}

.mode-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 0.75rem;
}

.form {
  display: grid;
  gap: 0.65rem;
}

.row {
  display: grid;
  gap: 0.5rem;
  grid-template-columns: minmax(9rem, 11rem) 1fr;
}

.category,
.row :deep(.date),
.row :deep(.description),
.row :deep(.p-datepicker),
.row :deep(.p-autocomplete),
.row :deep(.p-inputtext) {
  width: 100%;
}
</style>

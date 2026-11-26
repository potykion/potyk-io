<script setup lang="ts">
import AutoComplete from "primevue/autocomplete";
import Button from "primevue/button";
import DatePicker from "primevue/datepicker";
import InputText from "primevue/inputtext";
import SelectButton from "primevue/selectbutton";
import { reactive, ref, watch } from "vue";
import type { ExpensePayload, FinDay, SavingPayload } from "@/api/fin";
import AmountField from "@/components/fin/AmountField.vue";
import { evalAmountExpression } from "@/utils/calc";
import { formatRub } from "@/utils/money";
import { calcSavingFromRemainders, type SavingCalcPart } from "@/utils/savingCalc";

const props = defineProps<{
  categories: string[];
  expenseDefaultDate: string;
  savingDefaultDate: string;
  today: string;
  days: FinDay[];
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
  date: null as Date | null,
  amount: null as number | null,
  formula: "",
});
const savingCalcParts = ref<SavingCalcPart[]>([]);
const savingCalcSum = ref<number | null>(null);
const savingCalcRounded = ref<number | null>(null);

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

watch(
  () => props.savingDefaultDate,
  (iso) => {
    if (iso) saving.date = parseIso(iso);
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
  expense.category = "";
  expense.description = "";
}

function submitSaving(): void {
  const date = toIso(saving.date);
  const amount = resolveAmount(saving.amount, saving.formula);
  if (!date || amount == null || amount < 1) return;
  emit("createSaving", {
    date,
    amount,
    note: "",
  });
  saving.amount = null;
  saving.formula = "";
  savingCalcParts.value = [];
  savingCalcSum.value = null;
  savingCalcRounded.value = null;
}

/** Остатки после последнего сейфа → сумма в инпут, разбивка по датам ниже. */
function calcSaving(): void {
  const result = calcSavingFromRemainders(props.days, props.today);
  if (!result) {
    savingCalcParts.value = [];
    savingCalcSum.value = null;
    savingCalcRounded.value = null;
    return;
  }
  saving.amount = result.rounded;
  saving.formula = String(result.rounded);
  savingCalcParts.value = result.parts;
  savingCalcSum.value = result.sum;
  savingCalcRounded.value = result.rounded;
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
      <DatePicker v-model="saving.date" date-format="yy-mm-dd" show-icon class="saving-date" />
      <div class="actions">
        <Button type="button" label="Посчитать" severity="secondary" @click="calcSaving" />
        <Button type="submit" class="submit-wide" label="Зафиксировать" :loading="busy" />
      </div>
      <details v-if="savingCalcParts.length" class="calc-spoiler">
        <summary>Как считал</summary>
        <ul class="calc-breakdown">
          <li v-for="p in savingCalcParts" :key="p.date">
            <span class="calc-date">{{ p.date }}</span>
            <span class="calc-amount" :class="{ debt: p.amount < 0 }">{{ formatRub(p.amount) }}</span>
          </li>
          <li class="calc-total">
            <span>сумма</span>
            <span>{{ formatRub(savingCalcSum ?? 0) }}</span>
          </li>
          <li
            v-if="savingCalcRounded != null && savingCalcRounded !== savingCalcSum"
            class="calc-total"
          >
            <span>округл.</span>
            <span>{{ formatRub(savingCalcRounded) }}</span>
          </li>
        </ul>
      </details>
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

.actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  align-items: stretch;
}

.actions .submit-wide {
  flex: 1 1 auto;
  min-width: 0;
}

.calc-spoiler {
  font-size: 0.85rem;
  color: #64748b;
}

.calc-spoiler summary {
  cursor: pointer;
  user-select: none;
}

.calc-breakdown {
  list-style: none;
  margin: 0.4rem 0 0;
  padding: 0.5rem 0.65rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  color: #475569;
  display: grid;
  gap: 0.25rem;
}

.calc-breakdown li {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
}

.calc-date {
  font-variant-numeric: tabular-nums;
}

.calc-amount {
  font-variant-numeric: tabular-nums;
}

.calc-amount.debt {
  color: #b91c1c;
}

.calc-total {
  margin-top: 0.15rem;
  padding-top: 0.35rem;
  border-top: 1px solid #e2e8f0;
  font-weight: 600;
  color: #0f172a;
}

.row {
  display: grid;
  gap: 0.5rem;
  grid-template-columns: minmax(9rem, 11rem) 1fr;
}

.category,
.saving-date,
.row :deep(.date),
.row :deep(.description),
.row :deep(.p-datepicker),
.row :deep(.p-autocomplete),
.row :deep(.p-inputtext) {
  width: 100%;
}
</style>

<script setup lang="ts">
import AutoComplete from "primevue/autocomplete";
import Button from "primevue/button";
import DatePicker from "primevue/datepicker";
import InputText from "primevue/inputtext";
import { computed, reactive, ref, watch } from "vue";
import type { ExpensePayload, FinDay, SavingPayload } from "@/api/fin";
import AmountField from "@/components/fin/AmountField.vue";
import { evalAmountExpression } from "@/utils/calc";
import { formatDayLabel, formatRub } from "@/utils/money";

const PAGE = 5;

const props = defineProps<{
  days: FinDay[];
  categories: string[];
  busy?: boolean;
  error?: string | null;
}>();

const emit = defineEmits<{
  updateExpense: [id: number, payload: ExpensePayload];
  deleteExpense: [id: number];
  updateSaving: [id: number, payload: SavingPayload];
  deleteSaving: [id: number];
}>();

type RecentOp =
  | {
      key: string;
      kind: "expense";
      id: number;
      date: string;
      amount: number;
      category: string;
      description: string;
      optional: boolean;
    }
  | {
      key: string;
      kind: "saving";
      id: number;
      date: string;
      amount: number;
      note: string;
    };

type Editing = { kind: "expense"; id: number } | { kind: "saving"; id: number } | null;

const visibleCount = ref(PAGE);
const editing = ref<Editing>(null);
const awaitingSave = ref(false);
const categorySuggestions = ref<string[]>([]);

const expenseForm = reactive({
  date: null as Date | null,
  amount: null as number | null,
  formula: "",
  category: "",
  description: "",
  optional: false,
});

const savingForm = reactive({
  date: null as Date | null,
  amount: null as number | null,
  formula: "",
  note: "",
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

const operations = computed<RecentOp[]>(() => {
  const ops: RecentOp[] = [];
  for (const day of props.days) {
    for (const e of day.expenses) {
      ops.push({
        key: `e-${e.id}`,
        kind: "expense",
        id: e.id,
        date: e.date,
        amount: e.amount,
        category: e.category,
        description: e.description,
        optional: e.optional,
      });
    }
    for (const s of day.savings) {
      ops.push({
        key: `s-${s.id}`,
        kind: "saving",
        id: s.id,
        date: s.date,
        amount: s.amount,
        note: s.note,
      });
    }
  }
  ops.sort((a, b) => {
    if (a.date !== b.date) return a.date < b.date ? 1 : -1;
    return b.id - a.id;
  });
  return ops;
});

watch(
  () => operations.value.length,
  () => {
    if (visibleCount.value < PAGE) visibleCount.value = PAGE;
  },
);

watch(
  () => props.days,
  () => {
    if (!editing.value) return;
    const stillThere = operations.value.some(
      (op) => op.kind === editing.value?.kind && op.id === editing.value.id,
    );
    if (!stillThere) {
      editing.value = null;
      awaitingSave.value = false;
    }
  },
);

watch(
  () => props.busy,
  (busy, wasBusy) => {
    if (!awaitingSave.value || wasBusy !== true || busy) return;
    awaitingSave.value = false;
    if (!props.error) editing.value = null;
  },
);

const visible = computed(() => operations.value.slice(0, visibleCount.value));
const hasMore = computed(() => visibleCount.value < operations.value.length);

type OpGroup = { date: string; ops: RecentOp[] };

const todayIso = toIso(new Date());

const groups = computed<OpGroup[]>(() => {
  const byDate = new Map<string, RecentOp[]>();
  for (const op of visible.value) {
    const list = byDate.get(op.date);
    if (list) list.push(op);
    else byDate.set(op.date, [op]);
  }
  return [...byDate.entries()].map(([date, ops]) => ({ date, ops }));
});

function loadMore(): void {
  visibleCount.value += PAGE;
}

function searchCategory(event: { query: string }): void {
  const q = event.query.trim().toLowerCase();
  categorySuggestions.value = props.categories.filter((c) => c.toLowerCase().includes(q));
  if (q && !categorySuggestions.value.some((c) => c.toLowerCase() === q)) {
    categorySuggestions.value = [event.query.trim(), ...categorySuggestions.value];
  }
}

function startEdit(op: RecentOp): void {
  if (op.kind === "expense") {
    editing.value = { kind: "expense", id: op.id };
    expenseForm.date = parseIso(op.date);
    expenseForm.amount = op.amount;
    expenseForm.formula = String(op.amount);
    expenseForm.category = op.category;
    expenseForm.description = op.description;
    expenseForm.optional = op.optional;
  } else {
    editing.value = { kind: "saving", id: op.id };
    savingForm.date = parseIso(op.date);
    savingForm.amount = op.amount;
    savingForm.formula = String(op.amount);
    savingForm.note = op.note;
  }
}

function cancelEdit(): void {
  editing.value = null;
  awaitingSave.value = false;
}

function resolveAmount(amount: number | null, formula: string): number | null {
  if (amount != null) return amount;
  if (formula) return evalAmountExpression(formula);
  return null;
}

function submitExpense(): void {
  if (editing.value?.kind !== "expense") return;
  const date = toIso(expenseForm.date);
  const amount = resolveAmount(expenseForm.amount, expenseForm.formula);
  const category = expenseForm.category.trim();
  if (!date || amount == null || amount < 1 || !category) return;
  awaitingSave.value = true;
  emit("updateExpense", editing.value.id, {
    date,
    amount,
    category,
    description: expenseForm.description.trim(),
    optional: expenseForm.optional,
  });
}

function submitSaving(): void {
  if (editing.value?.kind !== "saving") return;
  const date = toIso(savingForm.date);
  const amount = resolveAmount(savingForm.amount, savingForm.formula);
  if (!date || amount == null || amount < 1) return;
  awaitingSave.value = true;
  emit("updateSaving", editing.value.id, {
    date,
    amount,
    note: savingForm.note.trim(),
  });
}

function isEditing(op: RecentOp): boolean {
  return editing.value?.kind === op.kind && editing.value.id === op.id;
}
</script>

<template>
  <section class="ops-card">
    <h2>Последние операции</h2>

    <form
      v-if="editing?.kind === 'expense'"
      class="edit-form"
      @submit.prevent="submitExpense"
    >
      <AmountField
        v-model:amount="expenseForm.amount"
        v-model:formula="expenseForm.formula"
        allow-formula
        placeholder="Сумма, ₽"
      />
      <AutoComplete
        v-model="expenseForm.category"
        :suggestions="categorySuggestions"
        dropdown
        :force-selection="false"
        placeholder="категория"
        @complete="searchCategory"
      />
      <div class="edit-row">
        <DatePicker v-model="expenseForm.date" date-format="yy-mm-dd" show-icon class="date" />
        <InputText
          v-model="expenseForm.description"
          class="description"
          placeholder="описание"
        />
      </div>
      <div class="edit-actions">
        <Button type="submit" label="Сохранить" :loading="busy" />
        <Button type="button" label="Отмена" severity="secondary" text @click="cancelEdit" />
      </div>
    </form>

    <form
      v-else-if="editing?.kind === 'saving'"
      class="edit-form"
      @submit.prevent="submitSaving"
    >
      <AmountField
        v-model:amount="savingForm.amount"
        v-model:formula="savingForm.formula"
        allow-formula
        placeholder="Сумма, ₽"
      />
      <div class="edit-row">
        <DatePicker v-model="savingForm.date" date-format="yy-mm-dd" show-icon class="date" />
        <InputText v-model="savingForm.note" class="description" placeholder="заметка" />
      </div>
      <div class="edit-actions">
        <Button type="submit" label="Сохранить" :loading="busy" />
        <Button type="button" label="Отмена" severity="secondary" text @click="cancelEdit" />
      </div>
    </form>

    <p v-if="!operations.length" class="empty">Пока нет операций.</p>

    <div v-else class="list">
      <section v-for="group in groups" :key="group.date" class="day-group">
        <h3 class="day-label">{{ formatDayLabel(group.date, todayIso) }}</h3>
        <ul class="day-ops">
          <li
            v-for="op in group.ops"
            :key="op.key"
            class="row"
            :class="[op.kind, { active: isEditing(op) }]"
          >
            <template v-if="op.kind === 'expense'">
              <span class="amount">{{ formatRub(op.amount) }}</span>
              <span class="category">{{ op.category }}</span>
              <span v-if="op.description" class="desc">{{ op.description }}</span>
            </template>
            <template v-else>
              <span class="amount saving">{{ formatRub(op.amount) }}</span>
              <span class="kind-label">Сейф</span>
              <span v-if="op.note" class="desc">{{ op.note }}</span>
            </template>

            <div class="actions">
              <Button
                type="button"
                icon="pi pi-pencil"
                text
                rounded
                size="small"
                aria-label="Изменить"
                @click="startEdit(op)"
              />
              <Button
                type="button"
                icon="pi pi-times"
                text
                rounded
                size="small"
                severity="danger"
                aria-label="Удалить"
                :disabled="busy"
                @click="
                  op.kind === 'expense'
                    ? emit('deleteExpense', op.id)
                    : emit('deleteSaving', op.id)
                "
              />
            </div>
          </li>
        </ul>
      </section>
    </div>

    <Button
      v-if="hasMore"
      type="button"
      label="Ещё"
      severity="secondary"
      outlined
      size="small"
      class="more"
      @click="loadMore"
    />
  </section>
</template>

<style scoped>
.ops-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 0.75rem;
  margin-bottom: 25vh;
  max-width: 100%;
  min-width: 0;
  box-sizing: border-box;
  overflow-x: clip;
}

h2 {
  margin: 0 0 0.65rem;
  font-size: 1.05rem;
  font-weight: 600;
}

.edit-form {
  display: grid;
  gap: 0.65rem;
  margin-bottom: 0.85rem;
  padding-bottom: 0.85rem;
  border-bottom: 1px solid #e2e8f0;
}

.edit-row {
  display: grid;
  gap: 0.5rem;
  grid-template-columns: 1fr;
  min-width: 0;
}

@media (min-width: 420px) {
  .edit-row {
    grid-template-columns: minmax(0, 11rem) minmax(0, 1fr);
  }
}

.edit-row :deep(.date),
.edit-row :deep(.description),
.edit-row :deep(.p-datepicker),
.edit-row :deep(.p-inputtext),
.edit-form :deep(.p-autocomplete),
.edit-form :deep(.p-datepicker),
.edit-form :deep(.p-inputtext) {
  width: 100%;
  max-width: 100%;
  min-width: 0;
}

.edit-form :deep(.p-datepicker),
.edit-form :deep(.p-autocomplete) {
  display: flex;
}

.edit-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.list {
  display: grid;
  gap: 0.85rem;
}

.day-group {
  margin: 0;
}

.day-label {
  margin: 0 0 0.25rem;
  padding: 0 0.35rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #64748b;
}

.day-ops {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.15rem;
}

.row {
  display: grid;
  gap: 0.15rem 0.65rem;
  align-items: baseline;
  padding: 0.45rem 0.35rem;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.95rem;
}

.day-ops .row:last-child {
  border-bottom: none;
}

.row.active {
  background: #f8fafc;
  border-radius: 0.4rem;
}

.row.expense {
  grid-template-columns: minmax(0, auto) minmax(0, 1fr) auto;
  grid-template-areas:
    "amount category actions"
    "desc desc actions";
}

.row.saving {
  grid-template-columns: minmax(0, auto) minmax(0, 1fr) auto;
  grid-template-areas:
    "amount kind actions"
    "desc desc actions";
}

.amount {
  grid-area: amount;
  font-weight: 600;
  white-space: nowrap;
}

.amount.saving {
  color: #1d4ed8;
}

.category {
  grid-area: category;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.kind-label {
  grid-area: kind;
  color: #64748b;
  font-size: 0.85rem;
}

.desc {
  grid-area: desc;
  color: #64748b;
  font-size: 0.85rem;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.actions {
  grid-area: actions;
  display: flex;
  justify-content: flex-end;
  align-self: center;
  white-space: nowrap;
}

.empty {
  margin: 0;
  color: #64748b;
}

.more {
  margin-top: 0.65rem;
  width: 100%;
}

@media (min-width: 560px) {
  .row.expense {
    grid-template-columns: 7rem minmax(6rem, 10rem) 1fr auto;
    grid-template-areas: "amount category desc actions";
    align-items: center;
  }

  .row.saving {
    grid-template-columns: 7rem minmax(6rem, 10rem) 1fr auto;
    grid-template-areas: "amount kind desc actions";
    align-items: center;
  }
}
</style>

<script setup lang="ts">
import Message from "primevue/message";
import ProgressSpinner from "primevue/progressspinner";
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";
import { computed, onMounted, ref } from "vue";
import type { Expense, Saving } from "@/api/fin";
import FinBudgetPanel from "@/components/fin/FinBudgetPanel.vue";
import FinExpensePanel from "@/components/fin/FinExpensePanel.vue";
import FinFeed from "@/components/fin/FinFeed.vue";
import FinSavingPanel from "@/components/fin/FinSavingPanel.vue";
import FinStatsPanel from "@/components/fin/FinStatsPanel.vue";
import { useFinStore } from "@/stores/fin";
import { formatRub } from "@/utils/money";

const store = useFinStore();
const confirm = useConfirm();
const toast = useToast();

const editingExpense = ref<Expense | null>(null);
const editingSaving = ref<Saving | null>(null);
const expenseDefaultDate = ref("");
const savingDefaultDate = ref("");
const pickMode = ref(false);
const selectedRemainders = ref<string[]>([]);
const savingPanel = ref<{ setAmount: (value: number) => void } | null>(null);

const state = computed(() => store.state);

onMounted(async () => {
  await store.load();
  if (store.state) {
    expenseDefaultDate.value = store.state.defaults.expense_date;
    savingDefaultDate.value = store.state.defaults.saving_date;
  }
});

async function onStatsChange(from: string, to: string): Promise<void> {
  await store.reloadStats(from, to);
}

async function onBudgetSave(value: number): Promise<void> {
  if (await store.saveBudget(value)) {
    toast.add({ severity: "success", summary: "Бюджет обновлён", life: 2000 });
  }
}

async function onExpenseCreate(payload: Parameters<typeof store.addExpense>[0]): Promise<void> {
  if (await store.addExpense(payload)) {
    toast.add({ severity: "success", summary: "Трата добавлена", life: 2000 });
    expenseDefaultDate.value = store.state?.defaults.expense_date || expenseDefaultDate.value;
  }
}

async function onExpenseBulk(payloads: Parameters<typeof store.addExpensesBulk>[0]): Promise<void> {
  if (await store.addExpensesBulk(payloads)) {
    toast.add({
      severity: "success",
      summary: `Добавлено трат: ${payloads.length}`,
      life: 2000,
    });
    expenseDefaultDate.value = store.state?.defaults.expense_date || expenseDefaultDate.value;
  }
}

async function onExpenseUpdate(
  id: number,
  payload: Parameters<typeof store.saveExpense>[1],
): Promise<void> {
  if (await store.saveExpense(id, payload)) {
    editingExpense.value = null;
    toast.add({ severity: "success", summary: "Трата обновлена", life: 2000 });
  }
}

function onEditExpense(id: number): void {
  editingExpense.value = store.findExpense(id) || null;
  editingSaving.value = null;
}

function onDeleteExpense(id: number): void {
  confirm.require({
    message: "Удалить трату?",
    header: "Подтверждение",
    icon: "pi pi-exclamation-triangle",
    acceptLabel: "Удалить",
    rejectLabel: "Отмена",
    acceptClass: "p-button-danger",
    accept: async () => {
      if (await store.removeExpense(id)) {
        if (editingExpense.value?.id === id) editingExpense.value = null;
        toast.add({ severity: "success", summary: "Трата удалена", life: 2000 });
      }
    },
  });
}

async function onSavingCreate(payload: Parameters<typeof store.addSaving>[0]): Promise<void> {
  if (await store.addSaving(payload)) {
    toast.add({ severity: "success", summary: "Сейв зафиксирован", life: 2000 });
    pickMode.value = false;
    selectedRemainders.value = [];
  }
}

async function onSavingUpdate(
  id: number,
  payload: Parameters<typeof store.saveSaving>[1],
): Promise<void> {
  if (await store.saveSaving(id, payload)) {
    editingSaving.value = null;
    toast.add({ severity: "success", summary: "Сейв обновлён", life: 2000 });
  }
}

function onEditSaving(id: number): void {
  editingSaving.value = store.findSaving(id) || null;
  editingExpense.value = null;
}

function onDeleteSaving(id: number): void {
  confirm.require({
    message: "Удалить сейв?",
    header: "Подтверждение",
    icon: "pi pi-exclamation-triangle",
    acceptLabel: "Удалить",
    rejectLabel: "Отмена",
    acceptClass: "p-button-danger",
    accept: async () => {
      if (await store.removeSaving(id)) {
        if (editingSaving.value?.id === id) editingSaving.value = null;
        toast.add({ severity: "success", summary: "Сейв удалён", life: 2000 });
      }
    },
  });
}

async function onToggleClosed(date: string, closed: boolean): Promise<void> {
  await store.toggleDayClosed(date, closed);
}

function onAddExpenseDate(date: string): void {
  editingExpense.value = null;
  expenseDefaultDate.value = date;
}

function onAddSavingFromRemainder(amount: number, date: string): void {
  editingSaving.value = null;
  pickMode.value = false;
  selectedRemainders.value = [];
  savingDefaultDate.value = date;
  savingPanel.value?.setAmount(amount);
}

function toggleRemainder(date: string): void {
  const set = new Set(selectedRemainders.value);
  if (set.has(date)) set.delete(date);
  else set.add(date);
  selectedRemainders.value = [...set];
}

function confirmPick(): void {
  if (!state.value) return;
  const total = state.value.days
    .filter((d) => selectedRemainders.value.includes(d.date))
    .reduce((sum, d) => sum + d.eod_remainder, 0);
  if (total > 0) savingPanel.value?.setAmount(total);
  pickMode.value = false;
  selectedRemainders.value = [];
}
</script>

<template>
  <section class="fin-page">
    <h1 v-if="state">Сегодня, {{ state.today }}</h1>
    <h1 v-else>Учёт</h1>

    <p v-if="state" class="summary-line">
      Сейвы всего: <strong>{{ formatRub(state.total_saved) }}</strong>
      · авто-остатки:
      <strong>{{ formatRub(state.auto_remainder_total) }}</strong>
    </p>

    <div v-if="store.loading && !state" class="state">
      <ProgressSpinner style="width: 2.5rem; height: 2.5rem" stroke-width="4" />
    </div>

    <Message v-else-if="store.error" severity="error" :closable="false">
      {{ store.error }}
    </Message>

    <template v-else-if="state">
      <FinStatsPanel :stats="state.stats" @change="onStatsChange" />
      <FinBudgetPanel
        :daily-budget="state.settings.daily_budget"
        :busy="store.saving"
        @save="onBudgetSave"
      />
      <FinExpensePanel
        :categories="state.categories"
        :default-date="expenseDefaultDate || state.defaults.expense_date"
        :editing="editingExpense"
        :today-closed="state.today_closed"
        :busy="store.saving"
        @create="onExpenseCreate"
        @create-bulk="onExpenseBulk"
        @update="onExpenseUpdate"
        @cancel="editingExpense = null"
      />
      <FinSavingPanel
        ref="savingPanel"
        :default-date="savingDefaultDate || state.defaults.saving_date"
        :editing="editingSaving"
        :today-closed="state.today_closed"
        :pick-mode="pickMode"
        :busy="store.saving"
        @create="onSavingCreate"
        @update="onSavingUpdate"
        @cancel="editingSaving = null"
        @toggle-pick="pickMode = !pickMode"
        @confirm-pick="confirmPick"
        @cancel-pick="
          pickMode = false;
          selectedRemainders = [];
        "
      />
      <FinFeed
        :days="state.days"
        :today="state.today"
        :pick-mode="pickMode"
        :selected-remainders="selectedRemainders"
        :busy="store.saving"
        @edit-expense="onEditExpense"
        @delete-expense="onDeleteExpense"
        @edit-saving="onEditSaving"
        @delete-saving="onDeleteSaving"
        @toggle-closed="onToggleClosed"
        @add-expense-date="onAddExpenseDate"
        @add-saving-from-remainder="onAddSavingFromRemainder"
        @toggle-remainder="toggleRemainder"
      />
    </template>
  </section>
</template>

<style scoped>
.fin-page h1 {
  margin: 0 0 0.35rem;
  font-size: 1.75rem;
  letter-spacing: -0.03em;
}

.summary-line {
  margin: 0 0 1rem;
  color: #64748b;
}

.state {
  display: flex;
  justify-content: center;
  padding: 2rem 0;
}
</style>

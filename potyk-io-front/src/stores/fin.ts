import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { ApiError } from "@/api/client";
import {
  createExpense,
  createExpensesBulk,
  createSaving,
  deleteExpense,
  deleteSaving,
  type Expense,
  type ExpensePayload,
  type FinState,
  fetchFinState,
  type Saving,
  type SavingPayload,
  setDayClosed,
  updateBudget,
  updateExpense,
  updateSaving,
} from "@/api/fin";

function redirectLogin(): void {
  window.location.href = `/auth/login?next=${encodeURIComponent("/v2/fin")}`;
}

export const useFinStore = defineStore("fin", () => {
  const state = ref<FinState | null>(null);
  const loading = ref(false);
  const saving = ref(false);
  const error = ref<string | null>(null);

  const statsFrom = computed(() => state.value?.stats.from);
  const statsTo = computed(() => state.value?.stats.to);

  async function wrap<T>(fn: () => Promise<T>): Promise<T | null> {
    saving.value = true;
    error.value = null;
    try {
      return await fn();
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        redirectLogin();
        return null;
      }
      error.value = err instanceof Error ? err.message : "Ошибка";
      return null;
    } finally {
      saving.value = false;
    }
  }

  async function load(from?: string, to?: string): Promise<void> {
    loading.value = true;
    error.value = null;
    try {
      state.value = await fetchFinState(from, to);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        redirectLogin();
        return;
      }
      error.value = err instanceof Error ? err.message : "Не удалось загрузить";
    } finally {
      loading.value = false;
    }
  }

  async function applyState(next: FinState | null): Promise<void> {
    if (next) state.value = next;
  }

  async function reloadStats(from: string, to: string): Promise<void> {
    await load(from, to);
  }

  async function addExpense(payload: ExpensePayload): Promise<boolean> {
    const next = await wrap(() => createExpense(payload, statsFrom.value, statsTo.value));
    await applyState(next);
    return Boolean(next);
  }

  async function addExpensesBulk(rows: ExpensePayload[]): Promise<boolean> {
    const next = await wrap(() => createExpensesBulk(rows, statsFrom.value, statsTo.value));
    await applyState(next);
    return Boolean(next);
  }

  async function saveExpense(id: number, payload: ExpensePayload): Promise<boolean> {
    const next = await wrap(() => updateExpense(id, payload, statsFrom.value, statsTo.value));
    await applyState(next);
    return Boolean(next);
  }

  async function removeExpense(id: number): Promise<boolean> {
    const next = await wrap(() => deleteExpense(id, statsFrom.value, statsTo.value));
    await applyState(next);
    return Boolean(next);
  }

  async function addSaving(payload: SavingPayload): Promise<boolean> {
    const next = await wrap(() => createSaving(payload, statsFrom.value, statsTo.value));
    await applyState(next);
    return Boolean(next);
  }

  async function saveSaving(id: number, payload: SavingPayload): Promise<boolean> {
    const next = await wrap(() => updateSaving(id, payload, statsFrom.value, statsTo.value));
    await applyState(next);
    return Boolean(next);
  }

  async function removeSaving(id: number): Promise<boolean> {
    const next = await wrap(() => deleteSaving(id, statsFrom.value, statsTo.value));
    await applyState(next);
    return Boolean(next);
  }

  async function saveBudget(dailyBudget: number): Promise<boolean> {
    const next = await wrap(() => updateBudget(dailyBudget, statsFrom.value, statsTo.value));
    await applyState(next);
    return Boolean(next);
  }

  async function toggleDayClosed(dateStr: string, closed: boolean): Promise<boolean> {
    const next = await wrap(() => setDayClosed(dateStr, closed, statsFrom.value, statsTo.value));
    await applyState(next);
    return Boolean(next);
  }

  function findExpense(id: number): Expense | undefined {
    return state.value?.days.flatMap((d) => d.expenses).find((e) => e.id === id);
  }

  function findSaving(id: number): Saving | undefined {
    return state.value?.days.flatMap((d) => d.savings).find((s) => s.id === id);
  }

  return {
    state,
    loading,
    saving,
    error,
    load,
    reloadStats,
    addExpense,
    addExpensesBulk,
    saveExpense,
    removeExpense,
    addSaving,
    saveSaving,
    removeSaving,
    saveBudget,
    toggleDayClosed,
    findExpense,
    findSaving,
  };
});

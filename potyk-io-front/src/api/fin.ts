import { apiJson } from "@/api/client";

export type Expense = {
  id: number;
  date: string;
  amount: number;
  category: string;
  description: string;
  optional: boolean;
  running_balance: number | null;
};

export type Saving = {
  id: number;
  date: string;
  amount: number;
  note: string;
};

export type FinDay = {
  date: string;
  budget: number;
  carry_in: number;
  start_available: number;
  spent: number;
  end_balance: number;
  eod_remainder: number;
  carry_out: number;
  saved: number;
  closed: boolean;
  expenses: Expense[];
  savings: Saving[];
};

export type StatsCategory = {
  category: string;
  total: number;
  count: number;
  avg: number;
  share: number;
  expenses: Expense[];
};

export type FinState = {
  today: string;
  settings: { daily_budget: number };
  categories: string[];
  defaults: { expense_date: string; saving_date: string };
  today_closed: boolean;
  total_saved: number;
  auto_remainder_total: number;
  stats: {
    from: string;
    to: string;
    total: number;
    saved_total: number;
    expenses_plus_saves: number;
    prev_from: string;
    prev_to: string;
    prev_month_label: string;
    next_from: string | null;
    next_to: string | null;
    next_month_label: string | null;
    categories: StatsCategory[];
  };
  days: FinDay[];
};

export type ExpensePayload = {
  date: string;
  amount: number;
  category: string;
  description: string;
  optional: boolean;
};

export type SavingPayload = {
  date: string;
  amount: number;
  note: string;
};

function withStats(path: string, statsFrom?: string, statsTo?: string): string {
  if (!statsFrom || !statsTo) return path;
  const q = new URLSearchParams({ stats_from: statsFrom, stats_to: statsTo });
  return `${path}?${q}`;
}

export function fetchFinState(statsFrom?: string, statsTo?: string) {
  return apiJson<FinState>(withStats("/v2/api/fin", statsFrom, statsTo));
}

export function createExpense(payload: ExpensePayload, statsFrom?: string, statsTo?: string) {
  return apiJson<FinState>(withStats("/v2/api/fin/expenses", statsFrom, statsTo), {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createExpensesBulk(
  expenses: ExpensePayload[],
  statsFrom?: string,
  statsTo?: string,
) {
  return apiJson<FinState>(withStats("/v2/api/fin/expenses/bulk", statsFrom, statsTo), {
    method: "POST",
    body: JSON.stringify({ expenses }),
  });
}

export function updateExpense(
  id: number,
  payload: ExpensePayload,
  statsFrom?: string,
  statsTo?: string,
) {
  return apiJson<FinState>(withStats(`/v2/api/fin/expenses/${id}`, statsFrom, statsTo), {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteExpense(id: number, statsFrom?: string, statsTo?: string) {
  return apiJson<FinState>(withStats(`/v2/api/fin/expenses/${id}`, statsFrom, statsTo), {
    method: "DELETE",
  });
}

export function createSaving(payload: SavingPayload, statsFrom?: string, statsTo?: string) {
  return apiJson<FinState>(withStats("/v2/api/fin/savings", statsFrom, statsTo), {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateSaving(
  id: number,
  payload: SavingPayload,
  statsFrom?: string,
  statsTo?: string,
) {
  return apiJson<FinState>(withStats(`/v2/api/fin/savings/${id}`, statsFrom, statsTo), {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteSaving(id: number, statsFrom?: string, statsTo?: string) {
  return apiJson<FinState>(withStats(`/v2/api/fin/savings/${id}`, statsFrom, statsTo), {
    method: "DELETE",
  });
}

export function updateBudget(dailyBudget: number, statsFrom?: string, statsTo?: string) {
  return apiJson<FinState>(withStats("/v2/api/fin/settings/budget", statsFrom, statsTo), {
    method: "PUT",
    body: JSON.stringify({ daily_budget: dailyBudget }),
  });
}

export function setDayClosed(
  dateStr: string,
  closed: boolean,
  statsFrom?: string,
  statsTo?: string,
) {
  return apiJson<FinState>(withStats(`/v2/api/fin/days/${dateStr}/close`, statsFrom, statsTo), {
    method: "PUT",
    body: JSON.stringify({ closed }),
  });
}

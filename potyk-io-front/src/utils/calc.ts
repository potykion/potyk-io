/** Безопасно считает выражения вида `123+456-10` (только + - * / и числа). */
export function evalAmountExpression(raw: string): number | null {
  const text = raw.replace(/\s+/g, "").replace(",", ".");
  if (!text) return null;
  if (!/^[\d.+\-*/()]+$/.test(text)) return null;
  try {
    const value = Function(`"use strict"; return (${text});`)();
    if (typeof value !== "number" || !Number.isFinite(value)) return null;
    const rounded = Math.round(value);
    return rounded >= 1 ? rounded : null;
  } catch {
    return null;
  }
}

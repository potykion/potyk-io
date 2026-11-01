(function () {
  const KEYS = ["day", "week", "month", "year", "total"];

  function applyStats(root, data) {
    if (!root || !data) return;
    for (const key of KEYS) {
      if (data[key] == null) continue;
      root.dataset[key] = String(data[key]);
      root.querySelectorAll('[data-k="' + key + '"]').forEach(function (el) {
        el.textContent = String(data[key]);
      });
    }
  }

  async function bump(btn) {
    if (!btn || btn.disabled) return;
    btn.disabled = true;
    try {
      const res = await fetch("/health/meditation", {
        method: "POST",
        headers: { Accept: "application/json" },
        credentials: "same-origin",
      });
      if (!res.ok) throw new Error("bad status");
      const data = await res.json();
      if (!data.ok) throw new Error("not ok");
      document.querySelectorAll(".meditation-stats").forEach(function (root) {
        applyStats(root, data);
      });
      btn.classList.remove("is-pulse");
      void btn.offsetWidth;
      btn.classList.add("is-pulse");
    } catch (e) {
      console.error(e);
    } finally {
      btn.disabled = false;
    }
  }

  document.addEventListener("click", function (ev) {
    const btn = ev.target.closest(".meditation-check");
    if (!btn) return;
    ev.preventDefault();
    ev.stopPropagation();
    bump(btn);
  });
})();

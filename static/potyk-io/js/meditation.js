(function () {
  const KEYS = ["day", "week", "month", "year", "total"];
  const SAVED_MS = 2000;
  const SAVED_TEXT = "Сохранено";

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

  function ensureFeedback(page, afterBtn) {
    let el = page.querySelector(".meditation-feedback");
    if (el) return el;
    el = document.createElement("p");
    el.className = "meditation-feedback";
    el.setAttribute("aria-live", "polite");
    el.hidden = true;
    if (afterBtn && afterBtn.parentNode === page) {
      afterBtn.insertAdjacentElement("afterend", el);
    } else {
      page.appendChild(el);
    }
    return el;
  }

  function showSaved(btn) {
    const widget = btn.closest(".index-v2-widget--meditation");
    const page = btn.closest(".meditation-page");
    const title = widget && widget.querySelector(".index-v2-widget__title");

    if (title) {
      if (!title.dataset.defaultTitle) {
        title.dataset.defaultTitle = title.textContent;
      }
      title.setAttribute("aria-live", "polite");
      title.textContent = SAVED_TEXT;
      title.classList.add("is-saved");
      clearTimeout(title._savedTimer);
      title._savedTimer = setTimeout(function () {
        title.textContent = title.dataset.defaultTitle;
        title.classList.remove("is-saved");
      }, SAVED_MS);
    } else if (page) {
      const feedback = ensureFeedback(page, btn);
      feedback.textContent = SAVED_TEXT;
      feedback.hidden = false;
      feedback.classList.add("is-visible");
      clearTimeout(feedback._hideTimer);
      feedback._hideTimer = setTimeout(function () {
        feedback.classList.remove("is-visible");
        feedback.hidden = true;
        feedback.textContent = "";
      }, SAVED_MS);
    }

    btn.classList.add("is-saved");
    clearTimeout(btn._savedTimer);
    btn._savedTimer = setTimeout(function () {
      btn.classList.remove("is-saved");
    }, SAVED_MS);
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
      showSaved(btn);
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

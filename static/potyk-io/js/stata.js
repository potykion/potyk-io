(function () {
  function initTomSelect(root) {
    if (typeof TomSelect !== "function") return;
    (root || document).querySelectorAll("select[data-tom-select]").forEach(function (el) {
      if (el.tomselect) return;
      new TomSelect(el, {
        create: el.dataset.create === "true",
        createOnBlur: true,
        persist: true,
        maxOptions: 200,
        closeAfterSelect: false,
        plugins: ["remove_button"],
        placeholder: el.dataset.placeholder || "",
        searchField: ["text", "value"],
        sortField: [{ field: "text", direction: "asc" }],
        dropdownParent: "body",
      });
    });
  }

  function syncSelectOptions(stats) {
    if (!Array.isArray(stats)) return;
    document.querySelectorAll("select[data-tom-select]").forEach(function (el) {
      const names = new Set(stats.map(function (s) { return s.name; }));
      if (el.tomselect) {
        const existing = new Set(Object.keys(el.tomselect.options));
        stats.forEach(function (s) {
          if (!existing.has(s.name)) {
            el.tomselect.addOption({ value: s.name, text: s.name });
          }
        });
        el.tomselect.refreshOptions(false);
        return;
      }
      Array.from(el.options).forEach(function (opt) {
        if (!names.has(opt.value)) opt.remove();
      });
      const have = new Set(Array.from(el.options).map(function (o) { return o.value; }));
      stats.forEach(function (s) {
        if (!have.has(s.name)) {
          const opt = document.createElement("option");
          opt.value = s.name;
          opt.textContent = s.name;
          el.appendChild(opt);
        }
      });
    });
  }

  function renderStats(root, stats) {
    if (!root) return;
    if (!stats || !stats.length) {
      root.innerHTML = '<p class="stata-stats__empty muted">Пока нет дел — добавь через форму.</p>';
      return;
    }
    root.innerHTML = stats.map(function (s) {
      return (
        '<section class="stata-stats__item"' +
        ' data-item-id="' + s.id + '"' +
        ' data-name="' + escapeAttr(s.name) + '"' +
        ' data-day="' + s.day + '"' +
        ' data-week="' + s.week + '"' +
        ' data-month="' + s.month + '"' +
        ' data-year="' + s.year + '"' +
        ' data-total="' + s.total + '">' +
        '<h2 class="stata-stats__name">' + escapeHtml(s.name) + "</h2>" +
        '<dl class="stata-stats__grid">' +
        '<div class="stata-stats__row">' +
        cell("День", "day", s.day) +
        cell("Неделя", "week", s.week) +
        cell("Месяц", "month", s.month) +
        "</div>" +
        '<div class="stata-stats__row">' +
        cell("Год", "year", s.year) +
        cell("Всего", "total", s.total) +
        "</div>" +
        "</dl></section>"
      );
    }).join("");
  }

  function cell(label, key, value) {
    return (
      "<div><dt>" + label + '</dt><dd data-k="' + key + '">' + value + "</dd></div>"
    );
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function escapeAttr(str) {
    return escapeHtml(str).replace(/'/g, "&#39;");
  }

  async function submitForm(form) {
    const btn = form.querySelector(".stata-check, [type='submit']");
    const errEl = form.querySelector("[data-stata-error]");
    const select = form.querySelector('select[name="items"]');
    if (!select) return;

    if (errEl) {
      errEl.hidden = true;
      errEl.textContent = "";
    }

    const items = select.tomselect
      ? select.tomselect.getValue()
      : Array.from(select.selectedOptions).map(function (o) { return o.value; });

    if (!items.length) {
      if (errEl) {
        errEl.textContent = "выбери хотя бы одно дело";
        errEl.hidden = false;
      }
      return;
    }

    if (btn) btn.disabled = true;
    try {
      const res = await fetch("/health/stata", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        credentials: "same-origin",
        body: JSON.stringify({ items: items }),
      });
      const data = await res.json().catch(function () { return {}; });
      if (!res.ok || !data.ok) {
        if (errEl) {
          errEl.textContent = data.error || "не вышло отметить";
          errEl.hidden = false;
        }
        return;
      }

      document.querySelectorAll("[data-stata-stats]").forEach(function (root) {
        renderStats(root, data.stats);
      });
      syncSelectOptions(data.stats);

      if (select.tomselect) select.tomselect.clear();
      else Array.from(select.options).forEach(function (o) { o.selected = false; });

      if (btn) {
        btn.classList.remove("is-pulse");
        void btn.offsetWidth;
        btn.classList.add("is-pulse");
      }

      if (window.PotykModal) {
        window.PotykModal.close("health-stata");
      }
    } catch (e) {
      console.error(e);
      if (errEl) {
        errEl.textContent = "не вышло отметить";
        errEl.hidden = false;
      }
    } finally {
      if (btn) btn.disabled = false;
    }
  }

  function onReady() {
    initTomSelect(document);

    document.addEventListener("submit", function (ev) {
      const form = ev.target.closest("[data-stata-form]");
      if (!form) return;
      ev.preventDefault();
      submitForm(form);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", onReady);
  } else {
    onReady();
  }
})();

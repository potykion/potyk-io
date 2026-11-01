(function () {
  function initTomSelect(root) {
    if (typeof TomSelect !== "function") return;
    (root || document).querySelectorAll("select[data-tom-select]").forEach(function (el) {
      if (el.tomselect) return;
      var maxItems = el.dataset.maxItems ? parseInt(el.dataset.maxItems, 10) : (el.multiple ? null : 1);
      if (!Number.isFinite(maxItems) || maxItems < 1) maxItems = el.multiple ? null : 1;
      var single = maxItems === 1;
      new TomSelect(el, {
        create: el.dataset.create === "true",
        createOnBlur: true,
        persist: true,
        maxItems: maxItems,
        maxOptions: 200,
        closeAfterSelect: single,
        plugins: single ? [] : ["remove_button"],
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
      var names = new Set(stats.map(function (s) { return s.name; }));
      if (el.tomselect) {
        var existing = new Set(Object.keys(el.tomselect.options));
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
      var have = new Set(Array.from(el.options).map(function (o) { return o.value; }));
      stats.forEach(function (s) {
        if (!have.has(s.name)) {
          var opt = document.createElement("option");
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
      root.innerHTML = '<p class="stata-stats__empty muted">Пока пусто — добавь через форму.</p>';
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

  function selectedItems(select) {
    var raw = select.tomselect
      ? select.tomselect.getValue()
      : Array.from(select.selectedOptions).map(function (o) { return o.value; });
    if (Array.isArray(raw)) return raw.filter(Boolean);
    return raw ? [raw] : [];
  }

  async function submitForm(form) {
    var btn = form.querySelector("[type='submit']");
    var errEl = form.querySelector("[data-stata-error]");
    var select = form.querySelector('select[name="items"]');
    if (!select) return;

    var endpoint = form.dataset.stataEndpoint || "/health/stata";
    var emptyError = form.dataset.stataEmptyError || "выбери дело";

    if (errEl) {
      errEl.hidden = true;
      errEl.textContent = "";
    }

    var items = selectedItems(select);

    if (!items.length) {
      if (errEl) {
        errEl.textContent = emptyError;
        errEl.hidden = false;
      }
      return;
    }

    if (btn) btn.disabled = true;
    try {
      var res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        credentials: "same-origin",
        body: JSON.stringify({ items: items }),
      });
      var data = await res.json().catch(function () { return {}; });
      if (!res.ok || !data.ok) {
        if (errEl) {
          errEl.textContent = data.error || "не вышло отметить";
          errEl.hidden = false;
        }
        return;
      }

      if (data.reload) {
        window.location.reload();
        return;
      }

      if (Array.isArray(data.stats)) {
        document.querySelectorAll("[data-stata-stats]").forEach(function (root) {
          renderStats(root, data.stats);
        });
        syncSelectOptions(data.stats);
      }

      if (select.tomselect) select.tomselect.clear();
      else Array.from(select.options).forEach(function (o) { o.selected = false; });
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

  async function deleteEntry(btn) {
    var id = btn.getAttribute("data-stata-delete");
    if (!id) return;
    if (!window.confirm("Удалить запись?")) return;

    btn.disabled = true;
    try {
      var res = await fetch("/health/stata/entries/" + encodeURIComponent(id), {
        method: "DELETE",
        headers: { Accept: "application/json" },
        credentials: "same-origin",
      });
      var data = await res.json().catch(function () { return {}; });
      if (!res.ok || !data.ok) {
        window.alert(data.error || "не вышло удалить");
        return;
      }
      window.location.reload();
    } catch (e) {
      console.error(e);
      window.alert("не вышло удалить");
    } finally {
      btn.disabled = false;
    }
  }

  function onReady() {
    initTomSelect(document);

    document.addEventListener("submit", function (ev) {
      var form = ev.target.closest("[data-stata-form]");
      if (!form) return;
      ev.preventDefault();
      submitForm(form);
    });

    document.addEventListener("click", function (ev) {
      var btn = ev.target.closest("[data-stata-delete]");
      if (!btn) return;
      ev.preventDefault();
      deleteEntry(btn);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", onReady);
  } else {
    onReady();
  }
})();

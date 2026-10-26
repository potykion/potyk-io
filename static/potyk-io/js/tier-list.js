(function (global) {
  "use strict";

  var TIERS = ["S", "A", "B", "C", "D"];

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function normalizeTier(t) {
    var v = String(t || "").toUpperCase();
    return TIERS.indexOf(v) >= 0 ? v : null;
  }

  /** Build HTML for a tier-list table (same markup as jinja/_tier_list.html). */
  function render(items, label) {
    var byTier = {};
    TIERS.forEach(function (t) {
      byTier[t] = [];
    });
    (items || []).forEach(function (it) {
      var tier = normalizeTier(it.tier);
      if (!tier) return;
      byTier[tier].push(it);
    });

    var rows = TIERS.map(function (t) {
      var cells = byTier[t]
        .map(function (it) {
          var title = esc(it.title || "");
          var href = esc(it.href || "#");
          if (it.cover) {
            return (
              '<a class="tier-item" href="' +
              href +
              '" title="' +
              title +
              '"><img src="' +
              esc(it.cover) +
              '" alt="' +
              title +
              '" loading="lazy"></a>'
            );
          }
          return (
            '<a class="tier-item" href="' +
            href +
            '" title="' +
            title +
            '"><span class="tier-item-text">' +
            title +
            "</span></a>"
          );
        })
        .join("");
      return (
        '<tr><th class="tier-rank tier-' +
        t.toLowerCase() +
        '" scope="row">' +
        t +
        '</th><td class="tier-items"><div class="tier-flex">' +
        cells +
        "</div></td></tr>"
      );
    }).join("");

    return (
      '<table class="tier-list" aria-label="' +
      esc(label || "Тирлист") +
      '">' +
      rows +
      "</table>"
    );
  }

  /**
   * Mount tier-list into host. Empty items → clear + hide host.
   * Returns whether the list was shown.
   */
  function mount(host, items, label) {
    if (!host) return false;
    var list = (items || []).filter(function (it) {
      return normalizeTier(it.tier);
    });
    if (!list.length) {
      host.hidden = true;
      host.innerHTML = "";
      return false;
    }
    host.innerHTML = render(list, label);
    host.hidden = false;
    return true;
  }

  global.PotykTierList = {
    TIERS: TIERS,
    normalizeTier: normalizeTier,
    render: render,
    mount: mount,
  };
})(typeof window !== "undefined" ? window : this);

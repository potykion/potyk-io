/**
 * Однострочный заголовок контент-карточки: уменьшает font-size, пока h3
 * не влезет в ширину. Включается классом .card-grid--fit-title на сетке.
 */
(function () {
  const MIN_PX = 10;
  const SELECTOR = ".card-grid--fit-title .content-card .note-preview > h3";

  function availableWidth(el) {
    const parent = el.parentElement;
    if (!parent) return 0;
    const cs = getComputedStyle(parent);
    const pad =
      (parseFloat(cs.paddingLeft) || 0) + (parseFloat(cs.paddingRight) || 0);
    return Math.max(0, parent.clientWidth - pad);
  }

  function fitOne(el) {
    const maxW = availableWidth(el);
    if (maxW < 8) return;

    el.style.fontSize = "";
    el.style.whiteSpace = "nowrap";
    el.style.display = "block";
    el.style.width = "100%";
    el.style.maxWidth = "100%";
    el.style.boxSizing = "border-box";

    const base = parseFloat(getComputedStyle(el).fontSize) || 16;
    let lo = MIN_PX;
    let hi = base;
    let best = MIN_PX;

    while (hi - lo > 0.25) {
      const mid = (lo + hi) / 2;
      el.style.fontSize = mid + "px";
      if (el.scrollWidth <= maxW + 0.5) {
        best = mid;
        lo = mid;
      } else {
        hi = mid;
      }
    }
    el.style.fontSize = best + "px";
  }

  function fitAll() {
    document.querySelectorAll(SELECTOR).forEach(fitOne);
  }

  function scheduleFit() {
    requestAnimationFrame(function () {
      requestAnimationFrame(fitAll);
    });
  }

  function watch() {
    scheduleFit();
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(scheduleFit);
    }
    if (typeof ResizeObserver === "undefined") return;
    const ro = new ResizeObserver(scheduleFit);
    document.querySelectorAll(".card-grid--fit-title").forEach(function (grid) {
      ro.observe(grid);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", watch);
  } else {
    watch();
  }
})();

/**
 * Однострочный заголовок и подзаголовок контент-карточки: уменьшает font-size,
 * пока текст не влезет в ширину. Включается классом .card-grid--fit-title на сетке.
 * Подзаголовок (.card-subtitle) дополнительно масштабируется пропорционально
 * подогнанному заголовку, чтобы не выглядеть крупнее сжатого title.
 */
(function () {
  const MIN_PX = 10;
  const PREVIEW_SELECTOR =
    ".card-grid--fit-title .content-card .note-preview";

  function availableWidth(el) {
    const parent = el.parentElement;
    if (!parent) return 0;
    const cs = getComputedStyle(parent);
    const pad =
      (parseFloat(cs.paddingLeft) || 0) + (parseFloat(cs.paddingRight) || 0);
    return Math.max(0, parent.clientWidth - pad);
  }

  function prepareLine(el) {
    el.style.fontSize = "";
    el.style.whiteSpace = "nowrap";
    el.style.display = "block";
    el.style.width = "100%";
    el.style.maxWidth = "100%";
    el.style.boxSizing = "border-box";
  }

  function fitOne(el, maxPx) {
    const maxW = availableWidth(el);
    if (maxW < 8) return 0;

    prepareLine(el);
    const base = parseFloat(getComputedStyle(el).fontSize) || 16;
    let hi = typeof maxPx === "number" ? Math.min(base, maxPx) : base;
    if (hi < MIN_PX) hi = MIN_PX;
    el.style.fontSize = hi + "px";

    let lo = MIN_PX;
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
    return best / base;
  }

  function fitPreview(preview) {
    const h3 = preview.querySelector(":scope > h3");
    const subs = preview.querySelectorAll(":scope > .card-subtitle");
    let titleScale = 1;

    if (h3) {
      titleScale = fitOne(h3) || 1;
    }

    subs.forEach(function (el) {
      prepareLine(el);
      const base = parseFloat(getComputedStyle(el).fontSize) || 14;
      const scaledMax = Math.max(MIN_PX, base * titleScale);
      fitOne(el, scaledMax);
    });
  }

  function fitAll() {
    document.querySelectorAll(PREVIEW_SELECTOR).forEach(fitPreview);
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
    const rouletteResult = document.getElementById("roulette-result");
    if (rouletteResult) ro.observe(rouletteResult);
  }

  window.potykFitContentCardTitles = scheduleFit;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", watch);
  } else {
    watch();
  }
})();

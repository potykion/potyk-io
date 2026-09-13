/**
 * Однострочный заголовок контент-карточки: уменьшает font-size, пока h3
 * не влезет в ширину. Включается классом .card-grid--fit-title на сетке.
 */
(function () {
  const MIN_PX = 11;
  const SELECTOR = ".card-grid--fit-title .content-card .note-preview > h3";

  function fitOne(el) {
    el.style.fontSize = "";
    const base = parseFloat(getComputedStyle(el).fontSize) || 16;
    let size = base;
    el.style.whiteSpace = "nowrap";
    while (el.scrollWidth > el.clientWidth + 0.5 && size > MIN_PX) {
      size -= 0.5;
      el.style.fontSize = size + "px";
    }
  }

  function fitAll(root) {
    const scope = root && root.querySelectorAll ? root : document;
    scope.querySelectorAll(SELECTOR).forEach(fitOne);
  }

  function watch() {
    fitAll(document);
    if (typeof ResizeObserver === "undefined") return;
    const ro = new ResizeObserver(function () {
      fitAll(document);
    });
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

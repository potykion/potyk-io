(function () {
  const root = document.querySelector("main.md-content");
  if (!root) return;

  const NUM = String.raw`\d+(?:[.,]\d+)?`;
  const SCALE_OPTIONS = [
    { divisor: 1, label: "1" },
    { divisor: 2, label: "1/2" },
    { divisor: 4, label: "1/4" },
  ];

  function headingKind(el) {
    if (!el || !/^H[2-4]$/i.test(el.tagName)) return null;
    const text = (el.textContent || "").replace(/:$/, "").trim().toLowerCase();
    if (text.includes("ингредиент")) return "ingredients";
    if (text.includes("приготовлен")) return "steps";
    return null;
  }

  function collectSectionBlocks(heading) {
    const level = Number(heading.tagName[1]);
    const blocks = [];
    let el = heading.nextElementSibling;
    while (el) {
      if (/^H[1-6]$/i.test(el.tagName) && Number(el.tagName[1]) <= level) {
        break;
      }
      if (el.tagName === "TABLE" || el.tagName === "UL") {
        blocks.push(el);
      }
      el = el.nextElementSibling;
    }
    return blocks;
  }

  function parseNum(raw) {
    return parseFloat(String(raw).replace(",", "."));
  }

  function formatNum(value, sample) {
    const useComma = String(sample).includes(",");
    if (!Number.isFinite(value)) return sample;
    const rounded = Math.round(value);
    if (Math.abs(value - rounded) < 1e-9) {
      return String(rounded);
    }
    let out = value.toFixed(2).replace(/\.?0+$/, "");
    if (useComma) out = out.replace(".", ",");
    return out;
  }

  function scaleText(text, divisor) {
    if (!text || divisor === 1) return text;
    const re = new RegExp(
      String.raw`(${NUM})(\s*[–—−-]\s*(${NUM}))?`,
      "g"
    );
    return text.replace(re, (full, a, rangeTail, b) => {
      if (rangeTail && b != null) {
        const sep = rangeTail.replace(new RegExp(NUM + ".*"), "");
        return (
          formatNum(parseNum(a) / divisor, a) +
          sep +
          formatNum(parseNum(b) / divisor, b)
        );
      }
      return formatNum(parseNum(a) / divisor, a);
    });
  }

  function quantityTargets(block) {
    const nodes = [];
    if (block.tagName === "TABLE") {
      block.querySelectorAll("tr").forEach((row, index) => {
        if (index === 0) return;
        const cells = row.querySelectorAll("td");
        if (cells.length >= 2) {
          nodes.push(cells[cells.length - 1]);
        }
      });
      return nodes;
    }
    if (block.tagName === "UL") {
      block.querySelectorAll(":scope > li").forEach((li) => nodes.push(li));
    }
    return nodes;
  }

  function applyScaleToElement(el, divisor) {
    if (!el.dataset.recipeQtyOriginal) {
      el.dataset.recipeQtyOriginal = el.innerHTML;
    }
    el.innerHTML = el.dataset.recipeQtyOriginal;
    if (divisor === 1) return;

    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const texts = [];
    while (walker.nextNode()) texts.push(walker.currentNode);
    texts.forEach((node) => {
      node.nodeValue = scaleText(node.nodeValue, divisor);
    });
  }

  function applyScale(blocks, divisor) {
    blocks.forEach((block) => {
      quantityTargets(block).forEach((el) => applyScaleToElement(el, divisor));
    });
  }

  function initScale() {
    const headings = [...root.querySelectorAll("h2, h3, h4")].filter(
      (h) => headingKind(h) === "ingredients"
    );
    headings.forEach((heading) => {
      const blocks = collectSectionBlocks(heading);
      if (!blocks.length) return;

      const hasQty = blocks.some((block) =>
        quantityTargets(block).some((el) =>
          new RegExp(NUM).test(el.textContent || "")
        )
      );
      if (!hasQty) return;

      const bar = document.createElement("div");
      bar.className = "recipe-scale";
      bar.setAttribute("role", "group");
      bar.setAttribute("aria-label", "Масштаб порции");

      SCALE_OPTIONS.forEach((opt, i) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "recipe-scale-btn";
        btn.textContent = opt.label;
        btn.dataset.divisor = String(opt.divisor);
        if (i === 0) btn.classList.add("is-active");
        btn.addEventListener("click", () => {
          bar.querySelectorAll(".recipe-scale-btn").forEach((b) => {
            b.classList.toggle("is-active", b === btn);
          });
          applyScale(blocks, opt.divisor);
        });
        bar.appendChild(btn);
      });

      heading.insertAdjacentElement("afterend", bar);
    });
  }

  function initSteps() {
    const headings = [...root.querySelectorAll("h2, h3, h4")].filter(
      (h) => headingKind(h) === "steps"
    );
    headings.forEach((heading) => {
      collectSectionBlocks(heading).forEach((block) => {
        if (block.tagName !== "UL") return;
        block.classList.add("recipe-steps");
        block.querySelectorAll(":scope > li").forEach((li) => {
          li.classList.add("recipe-step");
          li.tabIndex = 0;
          li.setAttribute("role", "button");
          li.setAttribute("aria-pressed", "false");
          const toggle = () => {
            const done = li.classList.toggle("is-done");
            li.setAttribute("aria-pressed", done ? "true" : "false");
          };
          li.addEventListener("click", (event) => {
            if (event.target.closest("a")) return;
            toggle();
          });
          li.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              toggle();
            }
          });
        });
      });
    });
  }

  initScale();
  initSteps();
})();

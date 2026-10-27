(function () {
  const root = document.querySelector("main.md-content");
  if (!root) return;

  const NUM = String.raw`\d+(?:[.,]\d+)?`;
  const SCALE_OPTIONS = [
    { factor: 2, label: "2" },
    { factor: 1.5, label: "1.5" },
    { factor: 1, label: "1", isDefault: true },
    { factor: 0.75, label: "3/4" },
    { factor: 2 / 3, label: "2/3" },
    { factor: 0.5, label: "1/2" },
    { factor: 0.25, label: "1/4" },
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

  function scaleText(text, factor) {
    if (!text || factor === 1) return text;
    const re = new RegExp(
      String.raw`(${NUM})(\s*[–—−-]\s*(${NUM}))?`,
      "g"
    );
    return text.replace(re, (full, a, rangeTail, b) => {
      if (rangeTail && b != null) {
        const sep = rangeTail.replace(new RegExp(NUM + ".*"), "");
        return (
          formatNum(parseNum(a) * factor, a) +
          sep +
          formatNum(parseNum(b) * factor, b)
        );
      }
      return formatNum(parseNum(a) * factor, a);
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

  function ingredientRows(block) {
    if (block.tagName === "TABLE") {
      return [...block.querySelectorAll("tr")].slice(1).filter((row) => {
        return row.querySelectorAll("td").length > 0;
      });
    }
    if (block.tagName === "UL") {
      return [...block.querySelectorAll(":scope > li")];
    }
    return [];
  }

  function applyScaleToElement(el, factor) {
    if (!el.dataset.recipeQtyOriginal) {
      el.dataset.recipeQtyOriginal = el.innerHTML;
    }
    el.innerHTML = el.dataset.recipeQtyOriginal;
    if (factor === 1) return;

    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const texts = [];
    while (walker.nextNode()) texts.push(walker.currentNode);
    texts.forEach((node) => {
      node.nodeValue = scaleText(node.nodeValue, factor);
    });
  }

  function applyScale(blocks, factor) {
    blocks.forEach((block) => {
      quantityTargets(block).forEach((el) => applyScaleToElement(el, factor));
    });
  }

  function bindToggle(el) {
    el.tabIndex = 0;
    el.setAttribute("role", "button");
    el.setAttribute("aria-pressed", "false");
    const toggle = () => {
      const done = el.classList.toggle("is-done");
      el.setAttribute("aria-pressed", done ? "true" : "false");
    };
    el.addEventListener("click", (event) => {
      if (event.target.closest("a")) return;
      toggle();
    });
    el.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        toggle();
      }
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

      SCALE_OPTIONS.forEach((opt) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "recipe-scale-btn";
        btn.textContent = opt.label;
        btn.dataset.factor = String(opt.factor);
        if (opt.isDefault) btn.classList.add("is-active");
        btn.addEventListener("click", () => {
          bar.querySelectorAll(".recipe-scale-btn").forEach((b) => {
            b.classList.toggle("is-active", b === btn);
          });
          applyScale(blocks, opt.factor);
        });
        bar.appendChild(btn);
      });

      heading.insertAdjacentElement("afterend", bar);
    });
  }

  function initIngredients() {
    const headings = [...root.querySelectorAll("h2, h3, h4")].filter(
      (h) => headingKind(h) === "ingredients"
    );
    headings.forEach((heading) => {
      collectSectionBlocks(heading).forEach((block) => {
        block.classList.add("recipe-ingredients");
        ingredientRows(block).forEach((row) => {
          row.classList.add("recipe-ingredient");
          bindToggle(row);
        });
      });
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
          bindToggle(li);
        });
      });
    });
  }

  function isTableHeaderRow(cells) {
    const joined = cells.join(" ").toLowerCase();
    return /(?:^|\s)(name|amount|unit|ингредиент|количество|кол-во|ед\.?)(?:\s|$)/.test(
      joined
    );
  }

  function compact(text) {
    return String(text || "").replace(/\s+/g, " ").trim();
  }

  function tableToText(table) {
    const lines = [];
    table.querySelectorAll("tr").forEach((row, index) => {
      const cells = [...row.querySelectorAll("th, td")]
        .map((cell) => compact(cell.textContent))
        .filter(Boolean);
      if (!cells.length) return;
      if (index === 0 && isTableHeaderRow(cells)) return;
      if (cells.length >= 2) {
        lines.push(`• ${cells[0]} — ${cells.slice(1).join(" ")}`);
      } else {
        lines.push(`• ${cells[0]}`);
      }
    });
    return lines.join("\n");
  }

  function listToText(list) {
    return [...list.querySelectorAll(":scope > li")]
      .map((li) => {
        const text = compact(li.innerText);
        return text ? `• ${text}` : "";
      })
      .filter(Boolean)
      .join("\n");
  }

  function blockToText(el) {
    const tag = el.tagName;
    if (/^H[1-6]$/i.test(tag)) return compact(el.textContent);
    if (tag === "TABLE") return tableToText(el);
    if (tag === "UL" || tag === "OL") return listToText(el);
    if (tag === "P" || tag === "PRE" || tag === "BLOCKQUOTE") {
      return compact(el.innerText);
    }
    return "";
  }

  function shouldSkipForCopy(el) {
    if (
      el.classList.contains("recipe-scale") ||
      el.classList.contains("recipe-copy") ||
      el.classList.contains("note-created") ||
      el.classList.contains("md-toc") ||
      el.classList.contains("album-props")
    ) {
      return true;
    }
    if (/^(IMG|PICTURE|VIDEO|SCRIPT|STYLE|HR)$/i.test(el.tagName)) {
      return true;
    }
    if (
      el.tagName === "P" &&
      el.querySelector("img, picture, video") &&
      !compact(el.textContent)
    ) {
      return true;
    }
    return false;
  }

  function recipePlainText() {
    const parts = [];
    [...root.children].forEach((child) => {
      if (shouldSkipForCopy(child)) return;
      const text = blockToText(child);
      if (text) parts.push(text);
    });
    return parts.join("\n\n").replace(/\n{3,}/g, "\n\n").trim();
  }

  async function writeClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.left = "-9999px";
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    ta.remove();
  }

  function initCopy() {
    const h1 = root.querySelector("h1");
    if (!h1) return;

    const looksLikeRecipe = [...root.querySelectorAll("h2, h3, h4")].some(
      (h) => headingKind(h) === "ingredients" || headingKind(h) === "steps"
    );
    if (!looksLikeRecipe) return;

    const wrap = document.createElement("div");
    wrap.className = "recipe-copy";

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "recipe-copy-btn";
    btn.textContent = "Копировать";
    btn.setAttribute("aria-label", "Скопировать рецепт");

    let resetTimer = 0;
    btn.addEventListener("click", async () => {
      const text = recipePlainText();
      if (!text) return;
      try {
        await writeClipboard(text);
        btn.textContent = "Скопировано";
        btn.classList.add("is-done");
        window.clearTimeout(resetTimer);
        resetTimer = window.setTimeout(() => {
          btn.textContent = "Копировать";
          btn.classList.remove("is-done");
        }, 1600);
      } catch (_) {
        btn.textContent = "Не вышло";
        window.clearTimeout(resetTimer);
        resetTimer = window.setTimeout(() => {
          btn.textContent = "Копировать";
        }, 1600);
      }
    });

    wrap.appendChild(btn);

    const after = h1.nextElementSibling;
    if (after && after.classList.contains("note-created")) {
      after.insertAdjacentElement("afterend", wrap);
    } else {
      h1.insertAdjacentElement("afterend", wrap);
    }
  }

  initScale();
  initIngredients();
  initSteps();
  initCopy();
})();

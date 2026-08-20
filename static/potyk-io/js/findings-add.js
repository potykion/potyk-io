(function () {
  const form = document.querySelector("form.findings-add");
  if (!form) return;

  const urlInput = form.querySelector('[name="url"]');
  const titleInput = form.querySelector('[name="title"]');
  const submitBtn = form.querySelector('[type="submit"]');
  if (!urlInput || !titleInput) return;

  function isYoutube(url) {
    try {
      const host = new URL(url).hostname.replace(/^www\./, "").toLowerCase();
      return (
        host === "youtube.com" ||
        host === "youtu.be" ||
        host === "m.youtube.com" ||
        host === "music.youtube.com"
      );
    } catch (_) {
      return false;
    }
  }

  async function fetchOembedTitle(pageUrl) {
    const oembed =
      "https://www.youtube.com/oembed?url=" +
      encodeURIComponent(pageUrl) +
      "&format=json";

    // Прямой запрос из браузера (если CORS пустит).
    try {
      const res = await fetch(oembed);
      if (res.ok) {
        const data = await res.json();
        const title = (data && data.title ? String(data.title) : "").trim();
        if (title) return title;
      }
    } catch (_) {}

    // CORS: youtube oembed через allorigins (сервер YouTube не трогаем).
    try {
      const res = await fetch(
        "https://api.allorigins.win/raw?url=" + encodeURIComponent(oembed)
      );
      if (res.ok) {
        const data = await res.json();
        const title = (data && data.title ? String(data.title) : "").trim();
        if (title) return title;
      }
    } catch (_) {}

    return "";
  }

  form.addEventListener("submit", async function (event) {
    if (form.dataset.oembedDone === "1") {
      form.dataset.oembedDone = "";
      return;
    }

    event.preventDefault();
    const url = (urlInput.value || "").trim();
    if (!url) return;

    const prevLabel = submitBtn ? submitBtn.value : "";
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.value = "…";
    }

    let title = "";
    if (isYoutube(url)) {
      title = await fetchOembedTitle(url);
    }
    titleInput.value = title || url;

    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.value = prevLabel || "Добавить";
    }

    form.dataset.oembedDone = "1";
    if (typeof form.requestSubmit === "function") {
      form.requestSubmit(submitBtn || undefined);
    } else {
      form.submit();
    }
  });
})();

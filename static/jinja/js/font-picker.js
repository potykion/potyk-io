(() => {
  const FONTS = [
    { id: "source", label: "Source Sans 3", family: "Source Sans 3", gf: "Source+Sans+3:ital,wght@0,400;0,500;0,600;0,700;1,400" },
    { id: "onest", label: "Onest", family: "Onest", gf: "Onest:wght@400;500;600;700" },
    { id: "golos", label: "Golos Text", family: "Golos Text", gf: "Golos+Text:wght@400;500;600;700" },
    { id: "plex", label: "IBM Plex Sans", family: "IBM Plex Sans", gf: "IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400" },
    { id: "manrope", label: "Manrope", family: "Manrope", gf: "Manrope:wght@400;500;600;700" },
    { id: "fira", label: "Fira Sans", family: "Fira Sans", gf: "Fira+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400" },
    { id: "ptsans", label: "PT Sans", family: "PT Sans", gf: "PT+Sans:ital,wght@0,400;0,700;1,400" },
    { id: "rubik", label: "Rubik", family: "Rubik", gf: "Rubik:ital,wght@0,400;0,500;0,600;0,700;1,400" },
    { id: "nunito", label: "Nunito Sans", family: "Nunito Sans", gf: "Nunito+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400" },
    { id: "commissioner", label: "Commissioner", family: "Commissioner", gf: "Commissioner:ital,wght@0,400;0,500;0,600;0,700;1,400" },
    { id: "geologica", label: "Geologica", family: "Geologica", gf: "Geologica:wght@400;500;600;700" },
    { id: "wix", label: "Wix Madefor Text", family: "Wix Madefor Text", gf: "Wix+Madefor+Text:ital,wght@0,400;0,500;0,600;0,700;1,400" },
    { id: "mulish", label: "Mulish", family: "Mulish", gf: "Mulish:ital,wght@0,400;0,500;0,600;0,700;1,400" },
    { id: "overpass", label: "Overpass", family: "Overpass", gf: "Overpass:ital,wght@0,400;0,500;0,600;0,700;1,400" },
    { id: "redhat", label: "Red Hat Text", family: "Red Hat Text", gf: "Red+Hat+Text:ital,wght@0,400;0,500;0,600;0,700;1,400" },
    { id: "jost", label: "Jost", family: "Jost", gf: "Jost:ital,wght@0,400;0,500;0,600;0,700;1,400" },
    { id: "exo2", label: "Exo 2", family: "Exo 2", gf: "Exo+2:ital,wght@0,400;0,500;0,600;0,700;1,400" },
    { id: "alegreya", label: "Alegreya Sans", family: "Alegreya Sans", gf: "Alegreya+Sans:ital,wght@0,400;0,500;0,700;1,400" },
    { id: "ubuntu", label: "Ubuntu", family: "Ubuntu", gf: "Ubuntu:ital,wght@0,400;0,500;0,700;1,400" },
    { id: "opensans", label: "Open Sans", family: "Open Sans", gf: "Open+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400" },
    { id: "noto", label: "Noto Sans", family: "Noto Sans", gf: "Noto+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400" },
    { id: "montserrat", label: "Montserrat", family: "Montserrat", gf: "Montserrat:ital,wght@0,400;0,500;0,600;0,700;1,400" },
    { id: "inter", label: "Inter", family: "Inter", gf: "Inter:ital,wght@0,400;0,500;0,600;0,700;1,400" },
    { id: "roboto", label: "Roboto", family: "Roboto", gf: "Roboto:ital,wght@0,400;0,500;0,700;1,400" },
    { id: "outfit", label: "Outfit", family: "Outfit", gf: "Outfit:wght@400;500;600;700" },
    { id: "figtree", label: "Figtree", family: "Figtree", gf: "Figtree:ital,wght@0,400;0,500;0,600;0,700;1,400" },
    { id: "typewriter", label: "Typewriter (old)", family: "Special Elite", gf: "Special+Elite" },
  ];
  const KEY = "potyk-font-pick";
  const loaded = new Set();

  function loadFont(f) {
    if (!f.gf || loaded.has(f.id)) return;
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = `https://fonts.googleapis.com/css2?family=${f.gf}&display=swap`;
    document.head.appendChild(link);
    loaded.add(f.id);
  }

  function apply(f) {
    loadFont(f);
    document.body.style.setProperty(
      "font-family",
      `"${f.family}", system-ui, sans-serif`,
      "important"
    );
  }

  function mount() {
    const saved = localStorage.getItem(KEY);
    const initial = FONTS.find((f) => f.id === saved) || FONTS[0];
    apply(initial);

    const box = document.createElement("div");
    box.id = "font-picker";
    box.innerHTML = `
      <label for="font-picker-select">шрифт</label>
      <select id="font-picker-select"></select>
    `;
    Object.assign(box.style, {
      position: "fixed",
      right: "12px",
      bottom: "12px",
      zIndex: "9999",
      display: "flex",
      alignItems: "center",
      gap: "8px",
      padding: "8px 10px",
      background: "#fff",
      border: "1px solid #ddd",
      borderRadius: "8px",
      boxShadow: "0 4px 16px rgba(0,0,0,.12)",
      fontFamily: "system-ui, sans-serif",
      fontSize: "13px",
    });

    const select = box.querySelector("select");
    for (const f of FONTS) {
      const opt = document.createElement("option");
      opt.value = f.id;
      opt.textContent = f.label;
      if (f.id === initial.id) opt.selected = true;
      select.appendChild(opt);
    }
    Object.assign(select.style, {
      fontFamily: "system-ui, sans-serif",
      fontSize: "13px",
      maxWidth: "14rem",
    });

    select.addEventListener("change", () => {
      const f = FONTS.find((x) => x.id === select.value);
      if (!f) return;
      apply(f);
      localStorage.setItem(KEY, f.id);
    });

    document.body.appendChild(box);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();

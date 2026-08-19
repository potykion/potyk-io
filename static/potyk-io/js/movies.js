(function () {
    "use strict";

    const COLORS = [
        "#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6",
        "#1abc9c", "#e67e22", "#34495e", "#16a085", "#c0392b",
        "#2980b9", "#27ae60", "#d35400", "#8e44ad", "#2c3e50",
    ];

    const dataEl = document.getElementById("movies-by-collection");
    if (!dataEl) return;

    const payload = JSON.parse(dataEl.textContent);
    const moviesByCollection = payload.moviesByCollection || {};
    const defaultCollectionId = payload.watchLaterCollectionId || "watch_later";

    const canvas = document.getElementById("roulette-canvas");
    const spinBtn = document.getElementById("roulette-spin");
    const resultEl = document.getElementById("roulette-result");
    const emptyEl = document.getElementById("roulette-empty");
    const collectionSelect = document.getElementById("roulette-collection-select");

    let rotation = 0;
    let spinning = false;
    let wheelVersion = 0;

    let selectedCollectionId = collectionSelect ? collectionSelect.value : defaultCollectionId;
    if (!selectedCollectionId) selectedCollectionId = defaultCollectionId;

    function getSelectedMovies() {
        return moviesByCollection[selectedCollectionId] || [];
    }

    function movieLabel(movie) {
        let label = movie.title_ru || "";
        if (movie.year) label += " (" + movie.year + ")";
        return label;
    }

    function drawWheel() {
        if (!canvas) return;
        const movies = getSelectedMovies();
        const ctx = canvas.getContext("2d");
        const size = canvas.width;
        const cx = size / 2;
        const cy = size / 2;
        const radius = size / 2 - 4;

        ctx.clearRect(0, 0, size, size);

        if (movies.length === 0) {
            ctx.beginPath();
            ctx.arc(cx, cy, radius, 0, Math.PI * 2);
            ctx.fillStyle = "#ddd";
            ctx.fill();
            ctx.fillStyle = "#888";
            ctx.font = "16px IBM Plex Sans, sans-serif";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText("Пусто", cx, cy);
            return;
        }

        const slice = (Math.PI * 2) / movies.length;

        movies.forEach((movie, i) => {
            const start = i * slice - Math.PI / 2;
            const end = start + slice;

            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.arc(cx, cy, radius, start, end);
            ctx.closePath();
            ctx.fillStyle = COLORS[i % COLORS.length];
            ctx.fill();
            ctx.strokeStyle = "#fff";
            ctx.lineWidth = 2;
            ctx.stroke();

            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(start + slice / 2);
            ctx.textAlign = "right";
            ctx.fillStyle = "#fff";
            ctx.font = "bold 11px IBM Plex Sans, sans-serif";
            const title = movie.title_ru || "";
            const text = title.length > 14 ? title.slice(0, 12) + "…" : title;
            ctx.fillText(text, radius - 10, 4);
            ctx.restore();
        });

        ctx.beginPath();
        ctx.arc(cx, cy, 28, 0, Math.PI * 2);
        ctx.fillStyle = "#fff";
        ctx.fill();
        ctx.strokeStyle = "#222";
        ctx.lineWidth = 3;
        ctx.stroke();
    }

    function updateSpinState() {
        const movies = getSelectedMovies();
        const hasMovies = movies.length > 0;
        if (spinBtn) spinBtn.disabled = !hasMovies || spinning;
        if (emptyEl) emptyEl.hidden = hasMovies;
    }

    function showResult(movie) {
        if (!resultEl) return;
        let html = "";
        if (movie.cover) {
            html += '<img class="roulette-result-cover" src="' + movie.cover + '" alt="">';
        }
        html += "<div><a href=\"" + movie.kinopoisk + "\" target=\"_blank\" rel=\"noopener\">"
            + movieLabel(movie) + "</a></div>";
        if (movie.title_en) {
            html += "<div style=\"opacity:0.7;font-size:0.9em\">" + movie.title_en + "</div>";
        }
        resultEl.innerHTML = html;
        resultEl.hidden = false;
    }

    function invalidateSpin() {
        wheelVersion += 1;
        spinning = false;
        rotation = 0;
        if (canvas) canvas.style.transform = "rotate(0deg)";
        if (resultEl) resultEl.hidden = true;
    }

    function spinWheel() {
        const movies = getSelectedMovies();
        if (movies.length === 0 || spinning) return;

        const version = wheelVersion;
        spinning = true;
        updateSpinState();
        if (resultEl) resultEl.hidden = true;

        const winnerIdx = Math.floor(Math.random() * movies.length);
        const slice = 360 / movies.length;
        const fullSpins = 5 + Math.floor(Math.random() * 3);
        const target = fullSpins * 360 - (winnerIdx + 0.5) * slice;
        rotation += target;

        canvas.style.transform = "rotate(" + rotation + "deg)";

        const onEnd = function () {
            canvas.removeEventListener("transitionend", onEnd);
            if (wheelVersion !== version) return;
            spinning = false;
            updateSpinState();
            showResult(movies[winnerIdx]);
        };
        canvas.addEventListener("transitionend", onEnd);
    }

    if (spinBtn) {
        spinBtn.addEventListener("click", spinWheel);
    }

    if (collectionSelect) {
        collectionSelect.addEventListener("change", function () {
            selectedCollectionId = collectionSelect.value;
            invalidateSpin();
            drawWheel();
            updateSpinState();
        });
    }

    drawWheel();
    updateSpinState();
})();

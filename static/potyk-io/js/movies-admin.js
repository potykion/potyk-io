(function () {
    "use strict";

    const dataEl = document.getElementById("movies-admin-kanban-data");
    const boardEl = document.getElementById("movies-kanban");
    const statusEl = document.getElementById("movies-kanban-status");
    if (!dataEl || !boardEl) return;

    let collections = JSON.parse(dataEl.textContent || "[]");
    let dragged = null;

    function setStatus(text, isError) {
        if (!statusEl) return;
        statusEl.hidden = !text;
        statusEl.textContent = text || "";
        statusEl.style.color = isError ? "#b42318" : "";
    }

    function movieLabel(movie) {
        let text = movie.title_ru || movie.id;
        if (movie.year) text += " (" + movie.year + ")";
        return text;
    }

    function render() {
        boardEl.innerHTML = "";

        collections.forEach(function (collection) {
            const colEl = document.createElement("section");
            colEl.className = "movies-kanban-column";
            colEl.dataset.collectionId = collection.id;

            const headerEl = document.createElement("div");
            headerEl.className = "movies-kanban-header";
            headerEl.innerHTML =
                "<h3>" + escapeHtml(collection.title) + "</h3>" +
                "<div class=\"movies-kanban-meta\">" +
                (collection.watch_later ? "watch_later, " : "") +
                collection.movies.length + " фильмов" +
                "</div>";

            const listEl = document.createElement("ul");
            listEl.className = "movies-kanban-list";

            collection.movies.forEach(function (movie) {
                const cardEl = document.createElement("li");
                cardEl.className = "movies-kanban-card";
                cardEl.draggable = true;
                cardEl.dataset.movieId = movie.id;
                cardEl.dataset.collectionId = collection.id;

                const coverHtml = movie.cover
                    ? "<img class=\"movies-kanban-cover\" src=\"" + escapeAttr(movie.cover) + "\" alt=\"\">"
                    : "<div class=\"movies-kanban-cover\"></div>";

                const enHtml = movie.title_en
                    ? "<div class=\"movies-kanban-subtitle\">" + escapeHtml(movie.title_en) + "</div>"
                    : "";

                const kpHtml = movie.kinopoisk
                    ? "<a class=\"movies-kanban-link\" href=\"" + escapeAttr(movie.kinopoisk) + "\" target=\"_blank\" rel=\"noopener\">КП</a>"
                    : "";

                cardEl.innerHTML =
                    coverHtml +
                    "<div class=\"movies-kanban-card-body\">" +
                    "<button type=\"button\" class=\"movies-kanban-delete\" data-movie-id=\"" + escapeAttr(movie.id) + "\" data-collection-id=\"" + escapeAttr(collection.id) + "\" aria-label=\"Убрать фильм из коллекции\">&times;</button>" +
                    "<div class=\"movies-kanban-title\">" + escapeHtml(movieLabel(movie)) + "</div>" +
                    enHtml +
                    kpHtml +
                    "</div>";

                cardEl.addEventListener("dragstart", onDragStart);
                cardEl.addEventListener("dragend", onDragEnd);
                const deleteBtn = cardEl.querySelector(".movies-kanban-delete");
                if (deleteBtn) {
                    deleteBtn.addEventListener("click", onDeleteClick);
                    deleteBtn.addEventListener("mousedown", stopEvent);
                    deleteBtn.addEventListener("dragstart", stopEvent);
                }
                listEl.appendChild(cardEl);
            });

            colEl.addEventListener("dragover", onDragOver);
            colEl.addEventListener("dragleave", onDragLeave);
            colEl.addEventListener("drop", onDrop);

            colEl.appendChild(headerEl);
            colEl.appendChild(listEl);
            boardEl.appendChild(colEl);
        });
    }

    function onDragStart(event) {
        dragged = {
            movieId: event.currentTarget.dataset.movieId,
            sourceCollectionId: event.currentTarget.dataset.collectionId,
        };
        event.currentTarget.classList.add("is-dragging");
        event.dataTransfer.effectAllowed = "move";
        setStatus("");
    }

    function onDragEnd(event) {
        event.currentTarget.classList.remove("is-dragging");
        clearTargets();
    }

    function onDragOver(event) {
        event.preventDefault();
        event.currentTarget.classList.add("is-drop-target");
        event.dataTransfer.dropEffect = "move";
    }

    function onDragLeave(event) {
        event.currentTarget.classList.remove("is-drop-target");
    }

    async function onDrop(event) {
        event.preventDefault();
        const targetEl = event.currentTarget;
        targetEl.classList.remove("is-drop-target");
        if (!dragged) return;

        const targetCollectionId = targetEl.dataset.collectionId;
        if (!targetCollectionId || targetCollectionId === dragged.sourceCollectionId) return;

        setStatus("Сохраняю перенос...");
        try {
            const response = await fetch("/collections/movies/admin/collection/move-movie", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    sourceCollectionId: dragged.sourceCollectionId,
                    targetCollectionId: targetCollectionId,
                    movieId: dragged.movieId,
                }),
            });
            const result = await response.json();
            if (!response.ok || !result.ok) {
                throw new Error(result.error || "Не удалось перенести фильм");
            }
            moveLocalMovie(dragged.movieId, dragged.sourceCollectionId, targetCollectionId);
            render();
            setStatus("Фильм перенесён");
        } catch (error) {
            setStatus(error.message || "Ошибка переноса", true);
        } finally {
            dragged = null;
        }
    }

    async function onDeleteClick(event) {
        stopEvent(event);
        const movieId = event.currentTarget.dataset.movieId;
        const collectionId = event.currentTarget.dataset.collectionId;
        const movie = findMovie(movieId, collectionId);
        if (!movieId || !collectionId || !movie) return;

        const confirmed = window.confirm("Убрать фильм \"" + movieLabel(movie) + "\" из этой коллекции?");
        if (!confirmed) return;

        setStatus("Убираю фильм из коллекции...");
        try {
            const response = await fetch("/collections/movies/admin/movie/delete", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    movieId: movieId,
                    collectionId: collectionId,
                }),
            });
            const result = await response.json();
            if (!response.ok || !result.ok) {
                throw new Error(result.error || "Не удалось убрать фильм из коллекции");
            }
            removeLocalMovie(movieId, collectionId);
            render();
            setStatus("Фильм убран из коллекции");
        } catch (error) {
            setStatus(error.message || "Ошибка удаления", true);
        }
    }

    function moveLocalMovie(movieId, sourceCollectionId, targetCollectionId) {
        const source = collections.find((c) => c.id === sourceCollectionId);
        const target = collections.find((c) => c.id === targetCollectionId);
        if (!source || !target) return;

        const index = source.movies.findIndex((m) => m.id === movieId);
        if (index === -1) return;

        const movie = source.movies[index];
        source.movies.splice(index, 1);
        if (!target.movies.some((m) => m.id === movieId)) {
            target.movies.push(movie);
        }
    }

    function removeLocalMovie(movieId, collectionId) {
        const collection = collections.find(function (item) {
            return item.id === collectionId;
        });
        if (!collection) return;
        collection.movies = collection.movies.filter(function (movie) {
            return movie.id !== movieId;
        });
    }

    function findMovie(movieId, collectionId) {
        const collection = collections.find(function (item) {
            return item.id === collectionId;
        });
        if (!collection) return null;
        return collection.movies.find(function (item) {
            return item.id === movieId;
        }) || null;
    }

    function clearTargets() {
        boardEl.querySelectorAll(".movies-kanban-column").forEach(function (el) {
            el.classList.remove("is-drop-target");
        });
    }

    function stopEvent(event) {
        event.preventDefault();
        event.stopPropagation();
    }

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/\"/g, "&quot;");
    }

    function escapeAttr(value) {
        return escapeHtml(value);
    }

    render();
})();

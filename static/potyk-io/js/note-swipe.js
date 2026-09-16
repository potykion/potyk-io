(function () {
    "use strict";

    function initNoteSwipe(root) {
        if (!root) return null;

        var content = root.querySelector("[data-note-swipe-content]");
        var actions = root.querySelector("[data-note-swipe-actions]");
        var empty = root.querySelector("[data-note-swipe-empty]");
        var status = root.querySelector("[data-note-swipe-status]");
        var likeBtn = root.querySelector('[data-note-swipe-vote="like"]');
        var dislikeBtn = root.querySelector('[data-note-swipe-vote="dislike"]');

        var shown = [];
        var current = null;
        var busy = false;

        function setBusy(value) {
            busy = value;
            if (likeBtn) likeBtn.disabled = value;
            if (dislikeBtn) dislikeBtn.disabled = value;
        }

        function showEmpty(message) {
            current = null;
            if (content) {
                content.hidden = true;
                content.innerHTML = "";
            }
            if (actions) actions.hidden = true;
            if (empty) {
                empty.hidden = false;
                empty.textContent = message || "Заметок пока нет";
            }
            if (status) status.textContent = "";
        }

        function showNote(note) {
            current = note;
            if (empty) empty.hidden = true;
            if (actions) actions.hidden = false;
            if (content) {
                content.hidden = false;
                var link = document.createElement("a");
                link.className = "note-swipe__open";
                link.href = note.url;
                link.target = "_blank";
                link.rel = "noopener";
                link.textContent = "Открыть страницу";

                var body = document.createElement("div");
                body.className = "note-swipe__body md-content";
                body.innerHTML = note.html || "";

                content.innerHTML = "";
                content.appendChild(link);
                content.appendChild(body);
            }
            if (status) status.textContent = "";
        }

        function loadNext() {
            if (busy) return Promise.resolve();
            setBusy(true);
            if (status) status.textContent = "Загрузка…";

            var qs = shown.length
                ? "?exclude=" + encodeURIComponent(shown.join(","))
                : "";

            return fetch("/activity/notes/random" + qs)
                .then(function (res) {
                    return res.json().then(function (data) {
                        return { ok: res.ok, data: data };
                    });
                })
                .then(function (result) {
                    if (!result.ok || !result.data || !result.data.note) {
                        showEmpty("Заметок пока нет");
                        return;
                    }
                    var note = result.data.note;
                    if (note.id && shown.indexOf(note.id) === -1) {
                        shown.push(note.id);
                    }
                    showNote(note);
                })
                .catch(function () {
                    showEmpty("Не удалось загрузить заметку");
                })
                .finally(function () {
                    setBusy(false);
                });
        }

        function vote(kind) {
            if (busy || !current) return;
            setBusy(true);
            if (status) status.textContent = "Сохраняю…";

            var payload = {
                id: current.id,
                url: current.url,
                title: current.title || "",
                vote: kind,
            };

            fetch("/activity/notes/vote", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            })
                .then(function (res) {
                    return res.json().then(function (data) {
                        return { ok: res.ok, data: data };
                    });
                })
                .then(function (result) {
                    if (!result.ok || !result.data || !result.data.ok) {
                        if (status) status.textContent = "Не удалось сохранить голос";
                        setBusy(false);
                        return;
                    }
                    setBusy(false);
                    return loadNext();
                })
                .catch(function () {
                    if (status) status.textContent = "Не удалось сохранить голос";
                    setBusy(false);
                });
        }

        if (likeBtn) {
            likeBtn.addEventListener("click", function () {
                vote("like");
            });
        }
        if (dislikeBtn) {
            dislikeBtn.addEventListener("click", function () {
                vote("dislike");
            });
        }

        return {
            loadNext: loadNext,
            reset: function () {
                shown = [];
                return loadNext();
            },
        };
    }

    window.initNoteSwipe = initNoteSwipe;
})();

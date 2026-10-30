(function () {
    "use strict";

    function showError(form, message) {
        var err = form.querySelector("[data-anti-post-error]");
        if (!err) return;
        err.textContent = message || "Не вышло запостить";
        err.hidden = false;
    }

    function clearError(form) {
        var err = form.querySelector("[data-anti-post-error]");
        if (!err) return;
        err.textContent = "";
        err.hidden = true;
    }

    function prependFeedPost(post) {
        var feed = document.querySelector(".anti-feed");
        var empty = document.querySelector(".anti-empty");
        if (empty) empty.remove();

        if (!feed) {
            var page = document.querySelector(".anti-page");
            if (!page) return;
            feed = document.createElement("ul");
            feed.className = "anti-feed";
            var tagline = page.querySelector(".anti-tagline");
            if (tagline && tagline.nextSibling) {
                page.insertBefore(feed, tagline.nextSibling);
            } else {
                page.appendChild(feed);
            }
        }

        var li = document.createElement("li");
        li.className = "anti-post";
        li.innerHTML =
            '<time class="anti-post__time" datetime=""></time>' +
            '<div class="anti-post__body"></div>';
        var time = li.querySelector("time");
        var body = li.querySelector(".anti-post__body");
        time.setAttribute("datetime", post.created_at);
        time.textContent = post.created_at_display;
        body.textContent = post.body;
        feed.insertBefore(li, feed.firstChild);
    }

    document.addEventListener("submit", function (e) {
        var form = e.target.closest(".anti-post-form");
        if (!form) return;
        e.preventDefault();
        clearError(form);

        var submit = form.querySelector('[type="submit"]');
        if (submit) submit.disabled = true;

        fetch(form.action, {
            method: "POST",
            body: new FormData(form),
            headers: { Accept: "application/json" },
            credentials: "same-origin",
        })
            .then(function (res) {
                return res.json().then(function (data) {
                    return { ok: res.ok, data: data };
                });
            })
            .then(function (result) {
                if (!result.ok || !result.data.ok) {
                    showError(form, (result.data && result.data.error) || "Не вышло запостить");
                    return;
                }
                form.reset();
                if (window.PotykModal) window.PotykModal.close("anti-post");
                if (result.data.post) prependFeedPost(result.data.post);
            })
            .catch(function () {
                showError(form, "Не вышло запостить");
            })
            .finally(function () {
                if (submit) submit.disabled = false;
            });
    });
})();

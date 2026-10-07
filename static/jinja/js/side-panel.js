(function () {
    "use strict";

    if (window.PotykSidePanel) return;

    var openPanels = [];
    var backdrop = null;

    function ensureBackdrop() {
        if (backdrop) return backdrop;
        backdrop = document.getElementById("side-panel-backdrop");
        if (!backdrop) {
            backdrop = document.createElement("button");
            backdrop.type = "button";
            backdrop.id = "side-panel-backdrop";
            backdrop.className = "side-panel-backdrop";
            backdrop.setAttribute("aria-label", "Закрыть панель");
            document.body.appendChild(backdrop);
        }
        backdrop.addEventListener("click", closeAll);
        return backdrop;
    }

    function getPanel(id) {
        if (!id) return null;
        if (typeof id !== "string") {
            return id.classList && id.classList.contains("side-panel") ? id : null;
        }
        var el = document.getElementById(id);
        return el && el.classList.contains("side-panel") ? el : null;
    }

    function syncToggle(panel, open) {
        if (!panel || !panel.id) return;
        document.querySelectorAll('[data-side-panel-toggle="' + panel.id + '"], [data-side-panel-open="' + panel.id + '"]').forEach(function (btn) {
            btn.setAttribute("aria-expanded", open ? "true" : "false");
        });
    }

    function syncBody() {
        document.body.classList.toggle("side-panel-open", openPanels.length > 0);
    }

    function open(id) {
        var panel = getPanel(id);
        if (!panel) return;
        if (panel.classList.contains("is-open")) return;

        openPanels.slice().forEach(function (other) {
            if (other !== panel) close(other);
        });

        ensureBackdrop();
        panel.classList.add("is-open");
        panel.setAttribute("aria-hidden", "false");
        openPanels.push(panel);
        syncToggle(panel, true);
        syncBody();
        panel.dispatchEvent(new CustomEvent("sidepanel:open", { bubbles: true }));
    }

    function close(id) {
        var panel = getPanel(id);
        if (!panel || !panel.classList.contains("is-open")) return;

        panel.classList.remove("is-open");
        panel.setAttribute("aria-hidden", "true");
        openPanels = openPanels.filter(function (p) { return p !== panel; });
        syncToggle(panel, false);
        syncBody();
        panel.dispatchEvent(new CustomEvent("sidepanel:close", { bubbles: true }));
    }

    function toggle(id) {
        var panel = getPanel(id);
        if (!panel) return;
        if (panel.classList.contains("is-open")) close(panel);
        else open(panel);
    }

    function closeAll() {
        openPanels.slice().forEach(close);
    }

    function isOpen(id) {
        var panel = getPanel(id);
        return !!(panel && panel.classList.contains("is-open"));
    }

    function anyOpen() {
        return openPanels.length > 0;
    }

    document.addEventListener("click", function (e) {
        var toggleBtn = e.target.closest("[data-side-panel-toggle]");
        if (toggleBtn) {
            e.preventDefault();
            toggle(toggleBtn.getAttribute("data-side-panel-toggle"));
            return;
        }

        var openBtn = e.target.closest("[data-side-panel-open]");
        if (openBtn) {
            e.preventDefault();
            open(openBtn.getAttribute("data-side-panel-open"));
        }
    });

    document.addEventListener("keydown", function (e) {
        if (e.key !== "Escape" || !anyOpen()) return;
        close(openPanels[openPanels.length - 1]);
    });

    document.querySelectorAll(".side-panel").forEach(function (panel) {
        if (!panel.hasAttribute("aria-hidden")) {
            panel.setAttribute("aria-hidden", panel.classList.contains("is-open") ? "false" : "true");
        }
    });

    window.PotykSidePanel = {
        open: open,
        close: close,
        toggle: toggle,
        closeAll: closeAll,
        isOpen: isOpen,
        anyOpen: anyOpen,
    };
})();

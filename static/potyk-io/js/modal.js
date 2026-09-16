(function () {
    "use strict";

    var openModals = [];

    function getModal(id) {
        if (!id) return null;
        return document.getElementById(id);
    }

    function openModal(id) {
        var modal = typeof id === "string" ? getModal(id) : id;
        if (!modal || !modal.classList.contains("modal")) return;
        if (!modal.hidden) return;

        modal.hidden = false;
        openModals.push(modal);
        document.body.classList.add("modal-open");
        modal.dispatchEvent(new CustomEvent("modal:open", { bubbles: true }));

        var closeBtn = modal.querySelector(".modal__close");
        if (closeBtn) closeBtn.focus();
    }

    function closeModal(id) {
        var modal = typeof id === "string" ? getModal(id) : id;
        if (!modal || modal.hidden) return;

        modal.hidden = true;
        openModals = openModals.filter(function (m) { return m !== modal; });
        if (openModals.length === 0) {
            document.body.classList.remove("modal-open");
        }
        modal.dispatchEvent(new CustomEvent("modal:close", { bubbles: true }));
    }

    function closeTopModal() {
        if (openModals.length === 0) return;
        closeModal(openModals[openModals.length - 1]);
    }

    document.addEventListener("click", function (e) {
        var openTrigger = e.target.closest("[data-modal-open]");
        if (openTrigger) {
            e.preventDefault();
            openModal(openTrigger.getAttribute("data-modal-open"));
            return;
        }

        var closeTrigger = e.target.closest("[data-modal-close]");
        if (closeTrigger) {
            var modal = closeTrigger.closest(".modal");
            if (modal) closeModal(modal);
        }
    });

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") closeTopModal();
    });

    window.PotykModal = {
        open: openModal,
        close: closeModal,
    };
})();

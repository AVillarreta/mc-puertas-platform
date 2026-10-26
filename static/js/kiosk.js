(function () {
    "use strict";

    document.querySelectorAll("[data-select]").forEach(function (root) {
        var input = root.querySelector("[data-select-input]");
        var button = root.querySelector("[data-select-button]");
        var panel = root.querySelector("[data-select-panel]");
        var value = root.querySelector("[data-select-value]");
        var backdrop = root.querySelector("[data-select-backdrop]");
        var options = Array.prototype.slice.call(root.querySelectorAll("[data-value]"));

        function setOpen(open) {
            root.classList.toggle("is-open", open);
            button.setAttribute("aria-expanded", open ? "true" : "false");
            panel.hidden = !open;
            if (open) {
                var current = root.querySelector(".is-selected") || options[0];
                if (current) current.focus();
            }
        }

        function select(option) {
            options.forEach(function (o) {
                var on = o === option;
                o.classList.toggle("is-selected", on);
                o.setAttribute("aria-selected", on ? "true" : "false");
            });
            input.value = option.getAttribute("data-value");
            value.textContent = option.querySelector(".select__label").textContent;
            root.classList.add("has-value");
            setOpen(false);
            button.focus();
        }

        // Estado inicial (p. ej. al volver con un error de validación)
        var initial = root.querySelector(".is-selected");
        if (initial) {
            value.textContent = initial.querySelector(".select__label").textContent;
            root.classList.add("has-value");
        }

        button.addEventListener("click", function () { setOpen(panel.hidden); });
        if (backdrop) backdrop.addEventListener("click", function () { setOpen(false); });

        options.forEach(function (option) {
            option.addEventListener("click", function () { select(option); });
            option.addEventListener("keydown", function (e) {
                var i = options.indexOf(option);
                if (e.key === "Enter" || e.key === " ") { e.preventDefault(); select(option); }
                else if (e.key === "ArrowDown") { e.preventDefault(); (options[i + 1] || options[0]).focus(); }
                else if (e.key === "ArrowUp") { e.preventDefault(); (options[i - 1] || options[options.length - 1]).focus(); }
                else if (e.key === "Escape") { setOpen(false); button.focus(); }
            });
        });

        document.addEventListener("click", function (e) {
            if (!root.contains(e.target)) setOpen(false);
        });
    });
})();

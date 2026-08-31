document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.querySelector(
        'input[name="q"]'
    );

    if (searchInput) {

        searchInput.addEventListener("keydown", function (event) {

            if (event.key === "Enter") {
                return;
            }

        });

    }


    const quantityButtons =
        document.querySelectorAll("[data-quantity]");

    quantityButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const quantity =
                parseInt(button.dataset.quantity);

            if (quantity < 1) {
                event.preventDefault();
            }

        });

    });

});
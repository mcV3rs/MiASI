document.addEventListener("DOMContentLoaded", function () {
    const inputTypeField = document.getElementById("input_type");
    const selectOptionsField = document.getElementById("select_options");

    if (!inputTypeField || !selectOptionsField) return;

    // Funkcja przełączająca stan pola select_options
    function toggleSelectOptions() {
        if (inputTypeField.value === "select") {
            selectOptionsField.disabled = false;
            selectOptionsField.style.backgroundColor = ""; // Domyślny kolor
        } else {
            selectOptionsField.disabled = true;
            selectOptionsField.style.backgroundColor = "#f0f0f0"; // Szary kolor dla wyłączonego pola
            selectOptionsField.value = ""; // Czyszczenie pola, jeśli nie jest aktywne
        }
    }

    // Nasłuchiwanie zmian w polu input_type
    inputTypeField.addEventListener("change", toggleSelectOptions);

    // Wywołanie funkcji podczas ładowania, aby ustawić początkowy stan
    toggleSelectOptions();
});

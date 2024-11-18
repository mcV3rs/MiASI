document.addEventListener("DOMContentLoaded", function () {
    const inputTypeField = document.getElementById("input_type");
    const selectOptionsField = document.getElementById("select_options");
    const selectValuesField = document.getElementById("select_values");

    if (!inputTypeField || !selectOptionsField || !selectValuesField) return;

    // Funkcja przełączająca stan pola select_options
    function toggleSelectOptions() {
        if (inputTypeField.value === "select") {
            selectOptionsField.disabled = false;
            selectOptionsField.style.backgroundColor = ""; // Domyślny kolor

            selectValuesField.disabled = false;
            selectValuesField.style.backgroundColor = ""; // Domyślny kolor
        } else {
            selectOptionsField.disabled = true;
            selectOptionsField.style.backgroundColor = "#f0f0f0"; // Szary kolor dla wyłączonego pola
            selectOptionsField.value = ""; // Czyszczenie pola, jeśli nie jest aktywne

            selectValuesField.disabled = true;
            selectValuesField.style.backgroundColor = "#f0f0f0"; // Szary kolor dla wyłączonego pola
            selectValuesField.value = ""; // Czyszczenie pola, jeśli nie jest aktywne
        }
    }

    // Nasłuchiwanie zmian w polu input_type
    inputTypeField.addEventListener("change", toggleSelectOptions);

    // Wywołanie funkcji podczas ładowania, aby ustawić początkowy stan
    toggleSelectOptions();
});

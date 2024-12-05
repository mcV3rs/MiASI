document.addEventListener("DOMContentLoaded", function () {
    // Lokalizacja pól formularza
    const selectOptionsField = document.getElementById("select_options");
    const selectValuesField = document.getElementById("select_values");
    const inputTypeField = document.getElementById("input_type");

    if (selectOptionsField && selectValuesField) {
        selectOptionsField.closest(".form-group").classList.add("hidden");
        selectValuesField.closest(".form-group").classList.add("hidden");
    }

    const formGroup = document.createElement("div");
    formGroup.className = "form-group";

    // Etykieta dla pola
    const label = document.createElement("label");
    label.setAttribute("for", "key-value-input");
    label.textContent = "Enter Options";

    // Pole tekstowe do wprowadzania nowych opcji
    const inputField = document.createElement("input");
    inputField.type = "text";
    inputField.id = "key-value-input";
    inputField.className = "form-control";
    inputField.placeholder = "Enter data in format: Key: Value";

    // Kontener na tagi
    const tagContainer = document.createElement("div");
    tagContainer.id = "tag-container";
    tagContainer.className = "tag-container";

    // Dodaj etykietę, pole tekstowe i kontener tagów do formularza
    formGroup.appendChild(label);
    formGroup.appendChild(inputField);
    formGroup.appendChild(tagContainer);

    // Dodaj jako przedostatni element `form-group`
    const formGroups = document.querySelectorAll(".form-group");
    if (formGroups.length > 1) {
        const target = formGroups[formGroups.length - 2];
        target.parentNode.insertBefore(formGroup, target.nextSibling);
    }

    // Zmienna globalna do zarządzania trybem edycji
    let editMode = false;
    let editTag = null;

    // Funkcja do włączania/wyłączania edycji opcji
    function toggleEditing() {
        const isSelectType = inputTypeField && inputTypeField.value === "select";
        inputField.disabled = !isSelectType;
        tagContainer.classList.toggle("hidden", !isSelectType);
    }

    // Nasłuchiwanie zmian w polu #input_type
    if (inputTypeField) {
        inputTypeField.addEventListener("change", toggleEditing);
    }

    // Wywołanie funkcji na starcie, aby dostosować widoczność
    toggleEditing();

    // Funkcja do tworzenia tagów
    function createTag(key, value) {
        const tag = document.createElement("span");
        tag.className = "badge bg-secondary me-2"; // Styl Bootstrap
        tag.textContent = `${key}: ${value}`;

        // Dodaj funkcję edycji po kliknięciu tag
        tag.addEventListener("click", function () {
            if (inputTypeField && inputTypeField.value === "select") {
                enterEditMode(tag, key, value);
            }
        });

        const closeBtn = document.createElement("button");
        closeBtn.className = "btn-close btn-close-white ms-2";
        closeBtn.setAttribute("aria-label", "Close");
        closeBtn.addEventListener("click", function (event) {
            event.stopPropagation(); // Zapobiega wywołaniu edycji podczas usuwania
            tagContainer.removeChild(tag);
            updateHiddenFields();
        });

        tag.appendChild(closeBtn);
        return tag;
    }

    // Funkcja do aktualizacji ukrytych pól
    function updateHiddenFields() {
        const tags = tagContainer.querySelectorAll(".badge");
        const keys = [];
        const values = [];
        tags.forEach(tag => {
            const [key, value] = tag.textContent.replace("×", "").split(":").map(str => str.trim());
            if (key && value) {
                keys.push(key);
                values.push(value);
            }
        });
        selectOptionsField.value = keys.join("; ");
        selectValuesField.value = values.join("; ");
    }

    // Funkcja do inicjalizacji tagów na podstawie istniejących wartości
    function initializeTags() {
        const keys = selectOptionsField.value.split(";").map(str => str.trim());
        const values = selectValuesField.value.split(";").map(str => str.trim());

        if (keys.length !== values.length) {
            console.error("Keys and values do not match in length!");
            return;
        }

        keys.forEach((key, index) => {
            const value = values[index];
            const tag = createTag(key, value);
            tagContainer.appendChild(tag);
        });
    }

    // Funkcja do wejścia w tryb edycji
    function enterEditMode(tag, key, value) {
        editMode = true;
        editTag = tag; // Zapamiętaj tag do edycji
        inputField.value = `${key}: ${value}`; // Wypełnia pole edycji
        inputField.focus(); // Skupia pole wejściowe
    }

    // Obsługa dodawania lub edycji tagów za pomocą klawisza Enter
    inputField.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            const input = inputField.value.trim();

            // Podziel tekst tylko raz i sprawdź oba elementy
            const parts = input.split(":").map(str => str.trim());
            const key = parts[0] || ""; // Zapewnij pustą wartość w razie braku
            const value = parts[1] || ""; // Zapewnij pustą wartość w razie braku

            if (key && value) {
                if (editMode && editTag) {
                    const closeButton = editTag.querySelector(".btn-close");
                    editTag.textContent = `${key}: ${value}`;
                    editTag.appendChild(closeButton);
                    editMode = false;
                    editTag = null;
                    updateHiddenFields();
                } else {
                    const tag = createTag(key, value);
                    tagContainer.appendChild(tag);
                    updateHiddenFields();
                }
                inputField.value = ""; // Czyści pole tekstowe
            } else {
                alert("Invalid format. Please use 'Key: Value' and ensure both key and value are non-empty.");
            }
        }
    });

    // Inicjalizacja tagów z istniejących wartości
    initializeTags();
});

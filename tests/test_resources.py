import pytest
from werkzeug.exceptions import HTTPException
from miasi.ext.restapi.resources import (
    get_system,
    get_request_data,
    validate_data,
    process_data,
    calculate_results,
    evaluate_knowledge, get_equations,
)


def test_get_request_data_no_data(client, setup_system):
    """Test sytuacji, gdy żądanie nie zawiera danych JSON."""
    system_id = setup_system["systems"][0].id
    with client.application.test_request_context(
        f"/api/v1/system/{system_id}/form/submit", data="", content_type="application/json"
    ):
        with pytest.raises(HTTPException) as excinfo:
            get_request_data()
        assert excinfo.value.code == 400
        assert "Error parsing input data" in str(excinfo.value.description)
        assert "Failed to decode JSON object" in str(excinfo.value.description)


def test_get_system_valid(setup_system):
    """Test poprawnego pobrania systemu."""
    system = setup_system["systems"][0]
    result = get_system(system.id)
    assert result.id == system.id
    assert result.name == system.name


def test_get_system_invalid(setup_system):
    """Test pobrania nieistniejącego systemu."""
    with pytest.raises(HTTPException) as excinfo:
        get_system(999)
    assert excinfo.value.code == 404
    assert "System not found" in excinfo.value.description


def test_validate_data_valid():
    """Test poprawnej walidacji danych."""
    validate_data({"field1": "value1"}, ["field1"])  # Brak wyjątku oznacza sukces.


def test_validate_data_missing_fields():
    """Test brakujących pól w walidacji."""
    with pytest.raises(HTTPException) as excinfo:
        validate_data({"field1": "value1"}, ["field1", "field2"])
    assert excinfo.value.code == 400
    assert "Missing required fields: field2" in excinfo.value.description


def test_process_data_valid(setup_system):
    """Test przetwarzania poprawnych danych."""
    data = {"height": "1.75", "weight": "70"}
    required_fields = setup_system["forms"]
    processed = process_data(data, required_fields)
    assert processed == {"height": 1.75, "weight": 70.0}


def test_process_data_invalid(setup_system):
    """Test przetwarzania danych z błędem."""
    required_forms = setup_system["forms"]
    with pytest.raises(HTTPException) as excinfo:
        process_data({"invalid": "data"}, required_forms)  # Nieprawidłowe dane
        print(process_data({"invalid": "data"}, required_forms))
    assert excinfo.value.code == 400
    assert "Error processing data: 400 Bad Request: No valid data provided" in excinfo.value.description


def test_calculate_results_valid(setup_system):
    """Test poprawnych obliczeń."""
    equations = [setup_system["equations"][0]]  # Pobranie równań z setup
    data = {"weight": 70, "height": 1.75}  # Dane testowe
    results = calculate_results(equations, data)
    assert len(results) == 1
    assert results[0]["equation_name"] == "Body Mass Index"
    assert abs(results[0]["result"] - 22.86) < 0.01  # Tolerancja błędu


def test_calculate_results_invalid(setup_system):
    """Test obliczeń z błędami."""
    equations = setup_system["equations"]
    with pytest.raises(HTTPException) as excinfo:
        calculate_results(equations, {"invalid": "data"})
    assert excinfo.value.code == 500
    assert "Error calculating equation Body Mass Index: name 'weight' is not defined" in excinfo.value.description


def test_equations_no_match(setup_system):
    """Test obliczeń bez równań."""
    system = setup_system["systems"][3]  # System bez równań

    with pytest.raises(HTTPException) as excinfo:
        get_equations(system, 0)
    assert excinfo.value.code == 404
    assert "No equations found for this system" in excinfo.value.description

def test_equations_no_match_for_sex(setup_system):
    """Test obliczeń bez równań dla podanej płci."""
    system = setup_system["systems"][1]  # System z równaniami dla płci

    with pytest.raises(HTTPException) as excinfo:
        get_equations(system, 3)
    assert excinfo.value.code == 404
    assert "No equations match the provided sex" in excinfo.value.description


def test_evaluate_knowledge_valid(setup_system):
    """Test poprawnej oceny bazy wiedzy."""
    system = setup_system["systems"][0]
    processed_data = {"BMI": 17.0}
    advice = evaluate_knowledge(system, processed_data)
    assert advice == "Twoja waga jest zbyt niska. Rozważ konsultację z dietetykiem."


def test_evaluate_knowledge_no_match(setup_system):
    """Test braku dopasowania w bazie wiedzy."""
    system = setup_system["systems"][0]
    processed_data = {"BMI": -1}

    advice = evaluate_knowledge(system, processed_data)
    assert advice is None


def test_evaluate_knowledge_no_entries(setup_system):
    """Test braku wpisów w bazie wiedzy."""
    system = setup_system["systems"][3]  # System bez wiedzy
    processed_data = {"BMI": 17.0}

    advice = evaluate_knowledge(system, processed_data)
    assert advice is None


def test_evaluate_knowledge_many_advice_system(setup_system):
    """Test systemu z wieloma poradami."""
    system = setup_system["systems"][4]  # System z wieloma poradami
    processed_data = {"weight": 0, "height": 0}

    advice = evaluate_knowledge(system, processed_data)
    assert len(advice) == 2
    assert advice[0] == "Rada 1"
    assert advice[1] == "Rada 2"


def test_evaluate_knowledge_many_advice_system_no_entries(setup_system):
    """Test braku wpisów w bazie wiedzy."""
    system = setup_system["systems"][4]  # System z wieloma poradami
    processed_data = {"weight": 100, "height": 2}

    advice = evaluate_knowledge(system, processed_data)
    assert advice is None
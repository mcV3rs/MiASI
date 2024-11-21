from flask import abort, jsonify, request
from flask_restful import Resource

from miasi.models import System, Equation, Knowledge


def get_system(system_id):
    """
    Pobranie systemu z bazy danych.
    :param system_id: ID systemu
    """
    return System.query.filter_by(id=system_id).first() or abort(404, "System not found")


def get_request_data():
    """
    Pobranie danych z żądania.
    """
    try:
        data = request.get_json()
        if not data:
            raise ValueError("No data provided")
        return data
    except Exception as e:
        abort(400, f"Error parsing input data: {str(e)}")


def get_required_fields(system):
    """
    Pobranie wymaganych pól formularza powiązanych z systemem.
    :param system: System
    """
    try:
        required_forms = [sf.form for sf in system.system_forms]
        return required_forms, [form.name for form in required_forms]
    except Exception as e:
        abort(500, f"Error retrieving required fields: {str(e)}")


def validate_data(data, required_fields):
    """
    Walidacja danych żądania.
    :param data: Dane wejściowe
    :param required_fields: Wymagane pola
    """
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        abort(400, f"Missing required fields: {', '.join(missing_fields)}")


def process_data(data, required_forms):
    """
    Przetwarzanie danych wejściowych na podstawie wymagań formularza.
    :param data: Dane wejściowe
    :param required_forms: Wymagane formularze
    """
    processed_data = {}
    try:
        for form in required_forms:
            field_name = form.name
            if field_name in data:
                field_value = data[field_name]
                if form.input_type == 'number':
                    processed_data[field_name] = float(field_value)
                elif form.input_type == 'sex':
                    processed_data[field_name] = int(field_value)
                elif form.input_type == 'select':
                    processed_data[field_name] = float(field_value.strip())
                else:
                    processed_data[field_name] = field_value.strip()
        return processed_data
    except Exception as e:
        abort(400, f"Error processing data: {str(e)}")


def get_equations(system, user_sex):
    """
    Pobranie równań powiązanych z systemem, uwzględniając płeć.
    :param system: System
    :param user_sex: Płeć użytkownika
    """
    equations = Equation.query.filter_by(id_system=system.id).all()
    if not equations:
        abort(404, "No equations found for this system")

    filtered_equations = [eq for eq in equations if eq.sex == "None" or eq.sex == user_sex]
    if not filtered_equations:
        abort(404, "No equations match the provided sex")
    return filtered_equations


def calculate_results(filtered_equations, processed_data):
    """
    Obliczanie wyników na podstawie równań.
    :param filtered_equations: Przefiltrowane równania
    :param processed_data: Przetworzone dane
    """
    results = []
    for equation in filtered_equations:
        try:
            result = eval(equation.formula, {}, processed_data)

            if not equation.is_internal:
                results.append({
                    "equation_name": equation.name_human_readable,
                    "result": round(result, 2)
                })

            processed_data[equation.name] = round(result, 2)
        except Exception as e:
            abort(500, f"Error calculating equation {equation.name_human_readable}: {str(e)}")
    return results


def evaluate_knowledge(system, processed_data):
    """
    Ocena wiedzy na podstawie wyników i warunków.
    :param system: System
    :param processed_data: Przetworzone dane
    """
    knowledge_entries = Knowledge.query.filter_by(id_system=system.id).all()
    if not knowledge_entries:
        return None

    # Sprawdzanie, czy system jest typu wielu porad
    if system.system_type:  # Zakładam, że 'system_type' jest typu Boolean
        # Zwróć wszystkie porady, które spełniają warunki
        matching_advices = []
        for entry in knowledge_entries:
            try:
                # Sprawdź, czy wszystkie warunki są spełnione
                met_conditions = sum(
                    eval(condition, {}, processed_data)
                    for condition in entry.condition.split(" and ")
                )
            except Exception as e:
                abort(500, f"Error evaluating knowledge condition for {entry.condition}: {str(e)}")

            if met_conditions > 0:  # Jeśli przynajmniej jeden warunek jest spełniony
                matching_advices.append(entry.advice)

        # Jeśli znaleziono pasujące porady, zwróć je wszystkie
        if matching_advices:
            return matching_advices
        else:
            return None

    # Jeśli system nie jest typu wielu porad, wybierz najlepszą poradę
    best_advice = None
    max_conditions_met = 0
    for entry in knowledge_entries:
        try:
            met_conditions = sum(
                eval(condition, {}, processed_data)
                for condition in entry.condition.split(" and ")
            )
        except Exception as e:
            abort(500, f"Error evaluating knowledge condition for {entry.condition}: {str(e)}")

        if met_conditions > max_conditions_met:
            max_conditions_met = met_conditions
            best_advice = entry.advice

    return best_advice


class FormsSubmissionResource(Resource):
    """Obsługuje przesyłanie formularzy i obliczanie wyników."""
    def get(self, system_id):
        """
        Pobranie formularzy powiązanych z systemem.
        :param system_id: ID systemu
        """
        system = System.query.filter_by(id=system_id).first() or abort(404, "System not found")
        forms = system.forms or abort(204, "No forms found for this system")
        return jsonify({"forms": [form.to_dict() for form in forms]})

    def post(self, system_id):
        """
        Przesłanie formularza i obliczenie wyników.
        :param system_id: ID system
        """
        system = get_system(system_id)
        data = get_request_data()
        required_forms, required_fields = get_required_fields(system)
        validate_data(data, required_fields)

        processed_data = process_data(data, required_forms)
        user_sex = processed_data.get("sex", None)

        filtered_equations = get_equations(system, user_sex)
        results = calculate_results(filtered_equations, processed_data)

        best_advice = evaluate_knowledge(system, processed_data)

        if best_advice:
            return {
                "message": "Equations calculated successfully with advice",
                "results": results,
                "advice": best_advice
            }, 201

        return {
            "message": "Equations calculated successfully, but no advice available",
            "results": results
        }, 201

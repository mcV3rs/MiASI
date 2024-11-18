from flask import abort, jsonify, request
from flask_restful import Resource
from miasi.models import System, Equation, Knowledge

class FormsSubmissionResource(Resource):
    def get(self, system_id):
        system = System.query.filter_by(id=system_id).first() or abort(404, "System not found")
        forms = system.forms or abort(204, "No forms found for this system")
        return jsonify({"forms": [form.to_dict() for form in forms]})

    def post(self, system_id):
        # Pobranie systemu
        system = System.query.filter_by(id=system_id).first() or abort(404, "System not found")

        # Pobranie danych z żądania
        try:
            data = request.get_json()
            if not data:
                return {"message": "No data provided"}, 400
        except Exception as e:
            return {"message": f"Error parsing input data: {str(e)}"}, 400

        # Pobranie wymaganych pól
        try:
            required_forms = [sf.form for sf in system.system_forms]
            required_fields = [form.name for form in required_forms]
        except Exception as e:
            return {"message": f"Error retrieving required fields: {str(e)}"}, 500

        # Walidacja danych
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return {"message": f"Missing required fields: {', '.join(missing_fields)}"}, 400

        # Przetwarzanie danych
        processed_data = {}
        try:
            for form in required_forms:
                field_name = form.name
                if field_name in data:
                    field_value = data[field_name]
                    if form.input_type == 'number':
                        # Rzutowanie do typu float dla pól typu "number"
                        processed_data[field_name] = float(field_value)
                    else:
                        # Zachowaj wartość bez zmian dla innych typów
                        processed_data[field_name] = field_value
        except Exception as e:
            return {"message": f"Error processing data: {str(e)}"}, 400

        # Sprawdzamy, ile równań jest powiązanych z systemem
        equations = Equation.query.filter_by(id_system=system.id).all()
        if not equations:
            return {"message": "No equations found for this system"}, 404

        # Sprawdzamy, czy użytkownik podał płeć w formularzu
        user_sex = int(processed_data.get("sex", None))

        # Filtrujemy równania zależne od płci
        filtered_equations = []
        for equation in equations:
            if equation.sex == "None" or equation.sex == user_sex:
                filtered_equations.append(equation)

        # Zwrócenie równań pasujących do płci
        if not filtered_equations:
            return {"message": "No equations match the provided sex"}, 404

        # Przygotowanie zmiennych do obliczeń
        results = []
        for equation in filtered_equations:
            variables = processed_data

            # Obliczanie równania
            try:
                result = eval(equation.formula, {}, variables)
                results.append({
                    "equation_name": equation.name_human_readable,
                    "result": round(result, 2)
                })
            except Exception as e:
                return {"message": f"Error calculating equation {equation.name_human_readable}: {str(e)}"}, 500

        # Pobranie wpisów wiedzy z tabeli Knowledge dla aktualnego systemu
        knowledge_entries = Knowledge.query.filter_by(id_system=system.id).all()

        # Jeśli brak wpisów w tabeli Knowledge, zwróć wyniki obliczeń
        if not knowledge_entries:
            return {"message": "Equations calculated successfully", "results": results}, 201

        # Jeśli istnieją wpisy w Knowledge, porównaj obliczone wartości z warunkami
        advice = []
        for result in results:
            for entry in knowledge_entries:
                try:
                    if eval(entry.condition, {}, {"value": result["result"]}):
                        advice.append({
                            "equation_name": result["equation_name"],
                            "advice": entry.advice
                        })
                except Exception as e:
                    return {
                        "message": f"Error evaluating knowledge condition for {result['equation_name']}: {str(e)}"}, 500

        # Zwracanie wyników wraz z radami, jeśli takie istnieją
        if advice:
            return {"message": "Equations calculated successfully with advice", "results": results,
                    "advice": advice}, 201
        else:
            return {"message": "Equations calculated successfully, but no advice available",
                    "results": results}, 201

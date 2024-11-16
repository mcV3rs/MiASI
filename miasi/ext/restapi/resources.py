from flask import abort, jsonify, request
from flask_restful import Resource
from miasi.models import System, Form, Equation, EquationFields, Knowledge

class FormsSubmissionResource(Resource):
    def get(self, system_id):
        system = System.query.filter_by(id=system_id).first() or abort(404, "System not found")
        forms = system.forms or abort(204, "No forms found for this system")
        return jsonify({"forms": [form.to_dict() for form in forms]})

    def post(self, system_id):
        system = System.query.filter_by(id=system_id).first() or abort(404, "System not found")
        data = request.get_json()

        # Fetch the relevant equations for the system
        equations = Equation.query.filter_by(id_system=system.id).all()
        if not equations:
            return {"message": "No equations found for this system"}, 404

        for equation in equations:
            # Fetch the fields for the equation
            fields = EquationFields.query.filter_by(id_equation=equation.id).all()
            if not fields:
                continue

            # Prepare the variables for the equation
            variables = {}
            for field in fields:
                form_field = Form.query.filter_by(id=field.id_form).first()
                if form_field and form_field.name in data:
                    # Convert the data to the appropriate type
                    if form_field.input_type == 'number':
                        variables[field.variable_name] = float(data[form_field.name])
                    elif form_field.input_type == 'date':
                        variables[field.variable_name] = data[form_field.name]  # Assuming date is in a proper format
                    elif form_field.input_type == 'email':
                        variables[field.variable_name] = data[form_field.name]
                    elif form_field.input_type == 'textarea':
                        variables[field.variable_name] = data[form_field.name]
                    else:  # Default to text
                        variables[field.variable_name] = data[form_field.name]

            # Calculate the value using the equation formula
            try:
                result = eval(equation.formula, {}, variables)
            except Exception as e:
                return {"message": f"Error calculating equation {equation.name_human_readable}: {str(e)}"}, 500

            # Fetch the relevant knowledge entries for the equation
            knowledge_entries = Knowledge.query.filter_by(id_system=system.id).all()
            for entry in knowledge_entries:
                try:
                    if eval(entry.condition, {}, {"value": result}):
                        advice = entry.advice
                except Exception as e:
                    return {
                        "message": f"Error evaluating knowledge condition for {equation.name_human_readable}: {str(e)}"}, 500

        return {"message": "Form submitted successfully", "result": result, "advice": advice}, 201
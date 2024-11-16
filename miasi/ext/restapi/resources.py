from flask import abort, jsonify, request
from flask_restful import Resource
from miasi.models import Systems, Forms, Equations, EquationFields, Knowledge

class FormsSubmissionResource(Resource):
    def get(self, system_id):
        system = Systems.query.filter_by(id=system_id).first() or abort(404, "System not found")
        forms = system.forms or abort(204, "No forms found for this system")
        return jsonify({"forms": [form.to_dict() for form in forms]})

    def post(self, system_id):
        system = Systems.query.filter_by(id=system_id).first() or abort(404, "System not found")
        data = request.get_json()

        # Fetch the relevant equations for the system
        equations = Equations.query.filter_by(id_systems=system.id).all()
        if not equations:
            return {"message": "No equations found for this system"}, 404

        results = {}
        advice_list = []
        for equation in equations:
            # Fetch the fields for the equation
            fields = EquationFields.query.filter_by(id_equations=equation.id).all()
            if not fields:
                continue

            # Prepare the variables for the equation
            variables = {}
            for field in fields:
                form_field = Forms.query.filter_by(id=field.id_forms).first()
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
            knowledge_entries = Knowledge.query.filter_by(id_equations=equation.id).all()
            for entry in knowledge_entries:
                try:
                    if eval(entry.condition, {}, {"value": result}):
                        advice = entry.advice
                except Exception as e:
                    return {
                        "message": f"Error evaluating knowledge condition for {equation.name_human_readable}: {str(e)}"}, 500

        return {"message": "Form submitted successfully", "result": result, "advice": advice}, 201

"""TODO: PRAWDOPODOBNIE DO USUNIĘCIA, użyte z szablonu jako przykład"""
# class ProductResource(Resource):
#     def get(self):
#         products = Product.query.all() or abort(204)
#         return jsonify(
#             {"products": [product.to_dict() for product in products]}
#         )
#
#     def post(self):
#         """
#         Creates a new product.
#
#         Only admin user authenticated using basic auth can post
#         Basic takes base64 encripted username:password.
#
#         # curl -XPOST localhost:5000/api/v1/product/ \
#         #  -H "Authorization: Basic Y2h1Y2s6bm9ycmlz" \
#         #  -H "Content-Type: application/json"
#         """
#         return NotImplementedError(
#             "Someone please complete this example and send a PR :)"
#         )
#
#
# class ProductItemResource(Resource):
#     def get(self, product_id):
#         product = Product.query.filter_by(id=product_id).first() or abort(404)
#         return jsonify(product.to_dict())

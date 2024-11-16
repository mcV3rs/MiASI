from flask import abort, render_template
from flask_simplelogin import login_required

from miasi.ext.database import db
from miasi.models import System, Product


def index():
    systems = System.query.all()

    return render_template("index.html", systems=systems)

def system(system_id):
    # Pobranie z bazy danych systemu o podanym identyfikatorze
    system = System.query.filter_by(id=system_id).first() or abort(404, "Brak systemu")

    # Pobranie z bazy danych formularzy przypisanych do systemu
    forms = system.forms

    print(f"System: {system.name}")
    print(f"Forms: {[form.name_human_readable for form in forms]}")

    return render_template("system.html", system=system, forms=forms)



def product(product_id):
    product = Product.query.filter_by(id=product_id).first() or abort(
        404, "Brak produktu"
    )
    return render_template("product.html", product=product)


@login_required
def secret():
    return "This can be seen only if user is logged in"


@login_required(username="admin")
def only_admin():
    return "Only admin user can see this text"

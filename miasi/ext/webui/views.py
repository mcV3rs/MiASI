from flask import abort, render_template

from miasi.models import System


def index():
    """Strona główna aplikacji"""
    systems = System.query.all()

    return render_template("index.html", systems=systems)


def system(system_id):
    """
    Strona systemu
    :param system_id: identyfikator systemu
    """
    # Pobranie z bazy danych systemu o podanym identyfikatorze
    system = System.query.filter_by(id=system_id).first() or abort(404, "Brak systemu")

    # Pobranie z bazy danych formularzy przypisanych do systemu
    forms = [sf.form for sf in system.system_forms]

    # Sprawdzenie, czy którykolwiek z pól formularza jest typu select
    for form in forms:
        if form.input_type == "select":
            form.select_options = form.select_options.split(",")
            form.select_values = form.select_values.split(',')

            form.combined = dict()
            for i, option in enumerate(form.select_options):
                form.combined[option] = form.select_values[i]

    return render_template("system.html", system=system, forms=forms)

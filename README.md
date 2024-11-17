# miasi Flask Application

Awesome miasi created by mcV3rs

## Installation

From source:

```bash
git clone https://github.com/mcV3rs/MiASI miasi
cd miasi
make install
```

From pypi:

```bash
pip install miasi
```

## Executing

This application has a CLI interface that extends the Flask CLI.

Just run:

```bash
$ miasi
```

or

```bash
$ python -m miasi
```

To see the help message and usage instructions.

## First run

```bash
miasi create-db # Create the database
miasi populate-db # Populate the database with some data
miasi reset-db # Reset the database - drop all tables, create them again, populate with data, add default user
miasi add-user -u admin -p 1234 # Add a user with username 'admin' and password '1234'

miasi run # Run the application
```

## Go to:

- Website: http://localhost:5000
- Admin: http://localhost:5000/admin/
  - login: admin, hasło: 1234 (_przy wykorzystywaniu domyślnie zapisanego użytkownika_)
- API POST:
  - http://localhost:5000/api/v1/system/<system_id>/form/submit


> **Note**: You can also use `flask run` to run the application.

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
miasi create-db   # run once
miasi populate-db  # run once (optional)
miasi add-user -u admin -p 1234  # ads a user
miasi run
```

Go to:

- Website: http://localhost:5000
- Admin: http://localhost:5000/admin/
  - user: admin, senha: 1234
- API GET:
  - http://localhost:5000/api/v1/product/
  - http://localhost:5000/api/v1/product/1
  - http://localhost:5000/api/v1/product/2
  - http://localhost:5000/api/v1/product/3


> **Note**: You can also use `flask run` to run the application.

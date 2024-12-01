# Użycie lekkiego obrazu Python na bazie Alpine
FROM python:3.12-alpine

# Zainstaluj make i inne wymagane narzędzia
RUN apk add --no-cache make gcc g++

# Skopiowanie plików aplikacji do katalogu /app w obrazie
COPY . /app

# Ustawienie katalogu roboczego
WORKDIR /app

# Stworzenie wirtualnego środowiska Pythona
RUN make virtualenv

# Aktywacja wirtualnego środowiska Pythona
RUN source .venv/bin/activate

# Instalacja aplikacji i jej zależności
RUN make install

# Wystawienie portu, na którym działa aplikacja
EXPOSE 5000

# Stworzenie bazy danych
RUN ["sh", "-c", "source .venv/bin/activate && flask create-db"]

# Wypełnienie bazy danych przykładowymi danymi
RUN ["sh", "-c", "source .venv/bin/activate && flask populate-db"]
RUN ["sh", "-c", "source .venv/bin/activate && flask add-user -u admin -p admin"]

# Ustawienie domyślnej komendy startowej
CMD ["sh", "-c", "source .venv/bin/activate && flask run --host=0.0.0.0 --port=5000"]

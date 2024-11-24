# Użycie lekkiego obrazu Python na bazie Alpine
FROM python:3.12-alpine

# Skopiowanie plików aplikacji do katalogu /app w obrazie
COPY . /app

# Ustawienie katalogu roboczego
WORKDIR /app

# Instalacja aplikacji i jej zależności
RUN pip install --no-cache-dir .

# Wystawienie portu, na którym działa aplikacja
EXPOSE 5000

# Ustawienie domyślnej komendy startowej
CMD ["sh", "-c", "miasi create-db && miasi populate-db && miasi add-user -u admin -p admin && miasi run"]

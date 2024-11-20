# MiASI

Aplikacja webowa demonstrująca działanie systemu eksperckiego opartego na regułach, sformułowanych w Bazie Wiedzy. System udziela porad na temat zdrowego trybu życia. Porady są generowane na podstawie odpowiedzi na pytania zadawane użytkownikowi.

## Zaimplementowane funkcjonalności
- System ekspercki oparty na regułach
- Baza Wiedzy w formie reguł
- System informatyczny pozwalający na zarządzanie Bazą Danych z poziomu przeglądarki

## Instalacja

Ze źródła:
```bash
git clone https://github.com/mcV3rs/MiASI miasi
cd miasi
make install
```

Z wykorzystaniem menadżera pakietów `pip`:
```bash
pip install miasi
```

## Uruchomienie

Aplikacja posiada zestaw poleceń dostępnych z poziomu konsoli. Wystarczy uruchomić:
```bash
$ miasi
```

lub

```bash
$ python -m miasi
```

aby uzyskać listę dostępnych poleceń.

## Pierwsze kroki

```bash
miasi create-db # Stwórz bazę danych
miasi populate-db # Zapełnij bazę danych przykładowymi rekordami
miasi reset-db # Reset bazy danych
miasi add-user -u admin -p 1234 # Dodaj użytkownika `admin` z hasłem `1234`

miasi run # Uruchom aplikację
```

> **Uwaga**: Wszystkie komendy można wywołać z wykorzystaniem polecenia `flask`

## Dostępne adresy

- Strona klienta: http://localhost:5000
- Panel administratora: http://localhost:5000/admin/
  - login: admin, hasło: 1234 (_przy wykorzystywaniu domyślnie zapisanego użytkownika_)
- API POST:
  - http://localhost:5000/api/v1/system/<system_id>/form/submit
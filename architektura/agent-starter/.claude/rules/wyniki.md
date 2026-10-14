---
paths:
  - "wyniki/**/*.md"
---

# Reguły dla plików wynikowych

Ten plik ładuje się tylko wtedy, gdy agent pracuje z plikiem w `wyniki/`.

- Nazwa pliku: `RRRR-MM-DD-krotki-temat.md`, małe litery, łączniki, bez polskich znaków.
- Pierwsza linia pod tytułem: data wygenerowania, tryb, zakres.
- Każde twierdzenie o świecie ma źródło z datą. Każde twierdzenie o systemie ma polecenie
  i jego wynik.
- Na końcu sekcja "Nie sprawdzono" albo "Nie ustalono".
- Bez sekretów i bez danych osobowych spoza zakresu zadania.
- Istniejącego pliku wynikowego nie nadpisuj: dopisz sekcję "Aktualizacja RRRR-MM-DD".

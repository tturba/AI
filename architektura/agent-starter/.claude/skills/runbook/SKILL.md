---
name: runbook
description: Zamienia wykonaną pracę albo luźne notatki w runbook, czyli procedurę krok po kroku, którą inny administrator wykona o trzeciej w nocy bez dopytywania. Użyj po rozwiązaniu awarii, po wdrożeniu usługi, gdy użytkownik mówi "zapisz to jako procedurę", "zrób z tego instrukcję", "udokumentuj", oraz gdy ta sama czynność została wykonana drugi raz.
argument-hint: "[temat procedury]"
---

# Runbook

Runbook opisuje sprawdzoną drogę, a nie wszystko, co wiadomo o usłudze.

## Kroki
1. Zbierz źródła: historia poleceń z sesji (`.agent/dziennik-polecen.jsonl`), zapis zmiany
   z `wyniki/admin/`, notatki użytkownika. Nie odtwarzaj kroków z pamięci.
2. Wypełnij szablon [assets/szablon-runbooka.md](assets/szablon-runbooka.md).
3. Każdy krok ma trzy części: polecenie do wklejenia, oczekiwany wynik, co zrobić, gdy
   wynik jest inny. Krok bez oczekiwanego wyniku nie jest krokiem.
4. Wartości zmienne zapisuj jako `<NAZWA>` i wymień je w sekcji "Zmienne".
5. Sekrety zastąp wskazaniem miejsca: "hasło w menedżerze haseł, wpis X".
6. Oznacz kroki, których nie wykonano w tej sesji: `> NIESPRAWDZONE: ...`.
7. Zapisz w katalogu dokumentacji wskazanym przez użytkownika albo w `wyniki/admin/runbooki/`.

## Zasady
- Jedna procedura, jeden cel. Warianty dla innych systemów to osobne runbooki.
- Polecenia niszczące poprzedź krokiem sprawdzającym, że jesteś na właściwym hoście.
- Na końcu zawsze: jak sprawdzić, że działa, i jak wycofać.
- Data ostatniego sprawdzenia i wersja systemu są częścią runbooka. Bez nich czytelnik
  nie wie, czy procedura jeszcze obowiązuje.

## Gotowe, gdy
- osoba spoza zespołu wykona procedurę bez zadawania pytań,
- każdy krok ma oczekiwany wynik, a kroki niesprawdzone są oznaczone.

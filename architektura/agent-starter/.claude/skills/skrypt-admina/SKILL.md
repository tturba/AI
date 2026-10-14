---
name: skrypt-admina
description: Pisze i poprawia skrypty administracyjne w Bashu i Pythonie tak, żeby dało się je bezpiecznie uruchomić z crona albo ręcznie na produkcji - tryb próbny, obsługa błędów, kody wyjścia, blokada równoległego uruchomienia, log, brak sekretów w kodzie. Użyj, gdy użytkownik prosi "napisz skrypt do", "zautomatyzuj", "zrób z tego crona", przy skryptach do backupu, rotacji, czyszczenia, raportów, zakładania kont, oraz przy przeglądzie cudzego skryptu przed uruchomieniem.
argument-hint: "[co ma robić skrypt]"
---

# Skrypt administracyjny

Skrypt, który raz zadziałał u autora, to jeszcze nie narzędzie. Narzędzie można uruchomić
drugi raz, przerwać w połowie i oddać komuś innemu.

## Kroki
1. Ustal przed pisaniem: wejście, wyjście, na jakim systemie i z jakimi uprawnieniami ma
   działać, co się stanie przy drugim uruchomieniu, co przy przerwaniu w połowie.
2. Zacznij od szablonu: [assets/szablon.sh](assets/szablon.sh) albo [assets/szablon.py](assets/szablon.py).
   Bash do sklejania poleceń, Python, gdy pojawia się parsowanie danych, JSON, API albo
   więcej niż około stu linii.
3. Sprawdź flagi używanych poleceń w `--help` na docelowym systemie (GNU i BSD się różnią).
4. Kontrola statyczna:
   ```bash
   bash -n skrypt.sh && shellcheck skrypt.sh
   python3 -m py_compile skrypt.py
   ```
5. Uruchom w trybie próbnym i pokaż wynik. Potem jedno prawdziwe uruchomienie na danych
   testowych, potem drugie, żeby sprawdzić powtarzalność.
6. Dopisz w nagłówku: co robi, przykład użycia, wymagania, kody wyjścia.

## Wymagania dla każdego skryptu
- Domyślnie tryb próbny albo wyraźna flaga `--wykonaj` dla operacji niszczących.
- Bash: `set -euo pipefail`, zmienne w cudzysłowach, `"$@"` zamiast `$*`, `mktemp` na pliki
  tymczasowe, `trap` sprzątający, brak parsowania `ls`.
- Ścieżki bezwzględne i jawny `PATH`, bo cron ma inne środowisko niż powłoka.
- Sprawdzenie warunków na starcie: wymagane polecenia, uprawnienia, istnienie katalogów,
  wolne miejsce. Błąd ma mówić, czego brakuje.
- Blokada drugiej instancji (`flock`) dla zadań okresowych.
- Usuwanie tylko w obrębie sprawdzonego katalogu. Zmienna ze ścieżką nie może być pusta:
  `rm -rf "${KATALOG:?}/"`.
- Sekrety ze zmiennych środowiska albo pliku z prawami 600. Nigdy w argumentach
  (widać je w `ps`) i nigdy w kodzie.
- Log z czasem na stderr albo do pliku, wynik na stdout. Kod wyjścia 0 tylko przy sukcesie.
- Dane z zewnątrz (nazwy plików, pola z CSV, odpowiedź API) nie trafiają do `eval`,
  `bash -c` ani do sklejanego polecenia.

## Zasady
- Nie uruchamiaj nowego skryptu na produkcji w ramach tego skilla. To osobna decyzja
  użytkownika (skill `bezpieczna-zmiana`).
- Skrypt od osoby trzeciej albo wygenerowany przez model czytasz w całości przed pierwszym
  uruchomieniem. `curl | bash` nie jest instalacją, tylko zaufaniem na ślepo.

## Gotowe, gdy
- kontrola statyczna przechodzi bez ostrzeżeń albo ostrzeżenia są uzasadnione,
- pokazano wynik trybu próbnego i dwóch kolejnych uruchomień.

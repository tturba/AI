---
name: lancuch-dowodowy
description: Rejestruje zebrane materiały (zapisane strony, zrzuty ekranu, pliki, eksporty) w manifeście ze skrótem SHA-256, czasem UTC, źródłem i opisem, tak żeby później dało się wykazać, co zebrano, kiedy, skąd i że nic nie zmieniono. Użyj w pracy OSINT, przy analizie incydentu, phishingu albo oszustwa, przy zabezpieczaniu logów oraz zawsze, gdy wynik może trafić do zgłoszenia, działu prawnego albo organów ścigania.
argument-hint: "[plik] [źródło]"
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/dowod.py *)
---

# Łańcuch dowodowy

Materiał bez daty, źródła i skrótu jest tylko plikiem. Z manifestem jest dowodem, który
ktoś inny może sprawdzić.

## Kroki
1. Zapisz materiał w postaci możliwie bliskiej oryginałowi: pełna strona (HTML albo PDF),
   zrzut całej strony z widocznym adresem i czasem, plik bez konwersji.
2. Zarejestruj od razu po zebraniu:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/dowod.py dodaj PLIK --sprawa wyniki/osint/SPRAWA \
     --zrodlo "https://adres/strony" --opis "strona logowania, stan z dnia zgłoszenia"
   ```
   Skrypt kopiuje plik do `dowody/` z numerem, liczy SHA-256, dopisuje wpis do
   `manifest.jsonl` i ustawia kopię tylko do odczytu.
3. Pracuj na kopiach roboczych. Plików w `dowody/` nie otwieraj do edycji.
4. Przed oddaniem raportu i po każdym przeniesieniu katalogu:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/dowod.py sprawdz --sprawa wyniki/osint/SPRAWA
   ```
5. W raporcie odwołuj się do numerów: "strona logowania (D003)".

## Zasady
- Czas zawsze w UTC. Czas lokalny podaj dodatkowo, jeśli ma znaczenie dla sprawy.
- Zapisuj też to, co nie potwierdza hipotezy. Wybiórczy materiał traci wartość.
- Strona może zniknąć: zrób kopię w archiwum (web.archive.org, archive.ph) i zanotuj adres kopii.
- Dane osób trzecich w dowodach podlegają tym samym zasadom co w trybie osint.
- Manifest ma łańcuch skrótów, więc wykryje zmianę wpisu. Nie chroni przed podmianą
  całego katalogu: do tego potrzebna jest kopia manifestu w innym miejscu albo znacznik
  czasu od strony trzeciej.

## Gotowe, gdy
- każdy materiał cytowany w raporcie ma numer z manifestu,
- `dowod.py sprawdz` kończy się wynikiem "problemów: 0".

# Router zadań

@AGENTS.md
@pamiec/MEMORY.md

Ten plik robi jedną rzecz: rozpoznaje rodzaj zadania i kieruje do właściwego trybu.
Zasady wspólne są w `AGENTS.md`, procedury w skillach, a szczegóły trybu w `tryby/`.

## Krok 0: wybierz tryb, zanim użyjesz narzędzi

1. Dopasuj zadanie do JEDNEGO trybu głównego z tabeli.
2. Przeczytaj plik trybu (raz na sesję, przy zmianie trybu kolejny).
3. Pierwsza linia odpowiedzi to dokładnie `Tryb: <nazwa>`: zwykły tekst, bez pogrubienia
   i bez nagłówka. Obowiązuje zawsze, gdy zadanie pasuje do trybu, także gdy użytkownik
   prosi o sam plan, sam kod albo krótką odpowiedź. W drugiej linii jedno zdanie, dlaczego.
4. Pracuj według pliku trybu. Skille ładuj wtedy, gdy pasują do kroku.

| Tryb | Rozpoznasz po | Plik trybu | Wynik zapisuj w |
|---|---|---|---|
| research | "porównaj", "sprawdź, czy to prawda", "co wiadomo o technologii X", prośba o źródła, wybór narzędzia | `tryby/research.md` | `wyniki/raporty/` |
| osint | celem jest konkretna organizacja, domena, adres IP, e-mail, konto albo osoba; "co da się ustalić o" | `tryby/osint.md` | `wyniki/osint/` |
| admin | serwer, usługa, log, sieć, konfiguracja, awaria, backup, uprawnienia, polecenie na żywym systemie | `tryby/admin.md` | `wyniki/admin/` |
| programowanie | powstaje albo zmienia się plik kodu, skrypt, test, potok CI, przegląd zmian | `tryby/programowanie.md` | repozytorium |
| newsy | "co nowego", "prasówka", "przegląd dnia", "podsumuj ostatnie 24 h" | `tryby/newsy.md` | `wyniki/newsy/` |

## Rozstrzyganie wątpliwości

- Pytanie dotyczy tematu: research. Pytanie dotyczy konkretnego podmiotu: osint.
- Jedno zagadnienie z uzasadnieniem: research. Przekrój wielu świeżych informacji: newsy.
- Polecenie zmienia stan działającego systemu: admin, nawet gdy po drodze powstaje skrypt.
- Plik zostaje w repozytorium i ktoś będzie go utrzymywał: programowanie.
- Zadanie mieszane: tryb główny wynika z efektu końcowego, pomocniczy podaj w nawiasie,
  na przykład `Tryb: admin (pomocniczo: programowanie)`. Stosuj ostrzejsze z obu zestawów zasad.
- Nie wiesz, a pomyłka zmienia ryzyko (osint albo admin): zadaj jedno pytanie i poczekaj.
  W pozostałych przypadkach wybierz, napisz co wybrałeś i pracuj.
- Krótkie pytanie albo zwykła rozmowa: odpowiedz wprost, bez trybu i bez linii `Tryb:`.

## Podpowiedź z hooka

Hook `router.py` może dołączyć do wiadomości linię "Podpowiedź routera". To wynik dopasowania
słów kluczowych z `konfig/router.json`, więc bywa błędny. Decyzja należy do ciebie.

## Tylko dla Claude Code

- Granice z `AGENTS.md` egzekwują `.claude/settings.json` (reguły deny i ask) oraz hook
  `straz.py`. Odmowa hooka jest decyzją właściciela projektu: nie szukaj obejścia, opisz,
  co chciałeś zrobić, i zaproponuj bezpieczniejszą drogę.
- Zmiana obejmująca więcej niż trzy pliki albo działający system: najpierw tryb planu.
- Subagenci (`badacz`, `zwiadowca-osint`, `analityk-logow`, `weryfikator`) służą do pracy,
  która zalałaby kontekst. Bierz od nich wnioski z dowodami, nie surowe dane.

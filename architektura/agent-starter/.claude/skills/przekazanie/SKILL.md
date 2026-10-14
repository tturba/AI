---
name: przekazanie
description: Zapisuje stan długiej pracy do pliku .agent/stan.md, żeby dało się ją podjąć w nowej sesji, po kompakcji kontekstu, następnego dnia albo przez inną osobę i innego agenta. Użyj, gdy zadanie trwa dłużej niż jedną sesję, przed przerwą, gdy kontekst się zapełnia, gdy użytkownik mówi "kończymy na dziś", "zapisz, gdzie jesteśmy", "wróćmy do wczorajszej pracy", oraz na początku sesji, w której taki plik już istnieje.
argument-hint: "[zapisz | wznów]"
---

# Przekazanie pracy

Rozmowa znika, plik zostaje. Stan zapisuj tak, jakby czytał go ktoś, kto nie widział
ani jednej wiadomości z tej sesji.

## Zapis
Utwórz albo zaktualizuj `.agent/stan.md`:
```markdown
# Stan pracy: <temat>
Aktualizacja: RRRR-MM-DD GG:MM. Tryb: <tryb z routera>.

## Cel
<jedno zdanie i kryterium ukończenia>

## Zrobione
- <co> (dowód: <plik, polecenie, wynik>)

## W toku
- <co dokładnie i na czym stanęło>

## Następny krok
<jedno konkretne działanie, od którego zacząć>

## Decyzje
- <decyzja>: <dlaczego>, odrzucono <alternatywa>, bo <powód>

## Ustalenia, których nie widać w plikach
- <fakt o środowisku, pułapka, wynik eksperymentu>

## Otwarte pytania do użytkownika
- <pytanie>

## Pliki
- zmienione: <lista>
- do przeczytania na start: <lista, najwyżej pięć>
```

## Wznowienie
1. Przeczytaj `.agent/stan.md` i pliki z listy "do przeczytania na start".
2. Sprawdź, czy stan zgadza się z rzeczywistością: `git status`, `git log -5 --oneline`,
   daty plików. Plik stanu mógł się zestarzeć.
3. Powiedz użytkownikowi w trzech zdaniach, gdzie jesteśmy, i zaproponuj następny krok.

## Zasady
- Zapisuj wnioski, nie przebieg rozmowy. Bez "najpierw spróbowałem".
- Decyzja bez uzasadnienia zostanie podważona w następnej sesji. Zapisz powód.
- Żadnych sekretów i żadnych danych osobowych w pliku stanu.
- Plik stanu dotyczy jednego zadania i jest tymczasowy. Wiedza trwała o projekcie należy
  do pamięci (skill `zapamietaj`).
- Po zakończeniu zadania plik usuń albo przenieś do `wyniki/`.

## Gotowe, gdy
- nowa sesja po przeczytaniu samego pliku wie, co zrobić jako pierwsze.

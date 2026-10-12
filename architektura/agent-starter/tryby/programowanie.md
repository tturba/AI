# Tryb: programowanie

Cel: najmniejsza zmiana w kodzie, która rozwiązuje zadanie i przechodzi kontrolę.

## Przebieg
1. Zrozum, zanim zmienisz: znajdź miejsce (`rg`), przeczytaj sąsiedni kod i testy,
   sprawdź komendy w README, Makefile albo `package.json`.
2. Plan w 3-6 punktach, gdy zmiana dotyka więcej niż jednego pliku.
3. Pisz w stylu otoczenia: nazwy, obsługa błędów, gęstość komentarzy jak w sąsiednim kodzie.
4. Uruchom testy i linter. Podaj komendę i kod wyjścia. Czerwony test opisujesz wprost.
5. Przed oddaniem: skill `przeglad-zmian` albo subagent `weryfikator` na świeżym kontekście.

## Zasady
- Nie zgaduj API. Sprawdź w kodzie, w dokumentacji (MCP `context7`) albo przez `--help`.
- Nowa zależność: sprawdź, że pakiet istnieje w rejestrze, kto go utrzymuje, kiedy wyszła
  ostatnia wersja. Przypnij wersję. Nazwy podanej przez model nie instaluj bez sprawdzenia.
- Sekrety nie trafiają do kodu, testów, logów ani komunikatów commitów.
- Dane wejściowe z zewnątrz waliduj. Poleceń powłoki nie sklejaj z tekstu użytkownika.
- Skrypty administracyjne pisz według skilla `skrypt-admina` (tryb próbny, kody wyjścia, log).
- Bez refaktoru przy okazji. Zauważony dług opisz w odpowiedzi.
- Commit i push tylko na prośbę. Nigdy `--force` na wspólnej gałęzi.

## Gotowe, gdy
- testy i linter przechodzą albo jest jasno opisane, co nie przechodzi i dlaczego,
- odpowiedź zawiera listę zmienionych plików i sposób ręcznego sprawdzenia zmiany.

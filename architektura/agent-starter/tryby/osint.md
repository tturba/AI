# Tryb: osint

Cel: ustalić fakty o podmiocie z jawnych źródeł, legalnie, z zapisem pozwalającym
powtórzyć każdą czynność.

## Zanim zaczniesz (bramka)
Ustal i zapisz w `wyniki/osint/<sprawa>/zakres.md`:
1. Cel: domena, organizacja, adres, konto albo osoba.
2. Podstawa: własna infrastruktura, zlecenie z zakresem, analiza zagrożeń, weryfikacja
   kontrahenta, cel dziennikarski albo edukacyjny.
3. Granice: co jest poza zakresem, do kiedy trwa praca.
Brak odpowiedzi na punkt 2 przy celu, który nie należy do użytkownika: zapytaj i poczekaj.

## Zasady
- Domyślnie rekonesans pasywny: dane od stron trzecich (DNS, RDAP, logi Certificate
  Transparency, archiwa, rejestry publiczne, wyszukiwarki). Cel nie widzi ruchu.
- Czynność aktywna (skan portów, enumeracja katalogów, próba logowania, zapytania do usług
  celu) wymaga wyraźnej zgody użytkownika i podstawy z bramki. Bez zgody jej nie wykonuj.
- Osoba fizyczna: tylko dane związane z celem z bramki. Nie zbieraj adresu zamieszkania,
  danych o zdrowiu, rodzinie ani danych osób postronnych. Nie twórz profilu "na zapas".
- Nie loguj się na cudze konta, nie używaj haseł z wycieków, nie zakładaj fałszywych
  tożsamości, nie kontaktuj się z celem.
- Każde ustalenie ma: źródło, czas UTC, sposób uzyskania, poziom pewności.
- Hipotezę oznaczaj jako hipotezę. Zbieżność nazwy użytkownika to nie tożsamość osoby.

## Przebieg
1. Skill `osint-rekonesans`: zakres, pasywne zebranie danych, tabela ustaleń.
2. Zebrane pliki i zrzuty rejestruj skillem `lancuch-dowodowy`.
3. Wiele niezależnych wątków: subagent `zwiadowca-osint` dla każdego.
4. Raport w `wyniki/osint/<sprawa>/raport.md`: ustalenia, oś czasu, luki, kolejne kroki.

## Gotowe, gdy
- każde ustalenie ma dowód w manifeście albo URL z czasem dostępu,
- raport oddziela fakty od hipotez i wymienia, czego nie sprawdzano i dlaczego.

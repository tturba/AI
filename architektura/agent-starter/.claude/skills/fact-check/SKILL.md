---
name: fact-check
description: Weryfikuje pojedyncze twierdzenie, cytat, liczbę, zrzut ekranu z informacją albo wiadomość z mediów społecznościowych i wydaje werdykt z dowodami. Użyj, gdy użytkownik pyta "czy to prawda", "skąd ta liczba", "czy ktoś to naprawdę powiedział", "czy ten CVE dotyczy naszej wersji", oraz przed umieszczeniem cudzego twierdzenia w raporcie albo prasówce.
argument-hint: "[twierdzenie]"
---

# Fact-check

## Kroki
1. Zapisz twierdzenie dosłownie. Rozbij je na części, które da się sprawdzić osobno:
   kto, co, kiedy, ile, gdzie.
2. Znajdź źródło pierwotne: dokument, nagranie, komunikat, zbiór danych, commit, wpis w
   bazie podatności. Idź w górę łańcucha cytowań, aż nie będzie do czego odesłać.
3. Sprawdź kontekst: pełne zdanie i akapit, data, jednostki, zakres (kraj, okres, próba),
   wersja produktu. Typowe zniekształcenia: wyrwanie z kontekstu, stara informacja podana
   jako nowa, zmiana jednostki, uogólnienie z jednego przypadku, błędne tłumaczenie.
4. Poszukaj niezależnego potwierdzenia i sprostowań (errata, aktualizacja artykułu, komentarz autora).
5. Wydaj werdykt dla każdej części i dla całości.

## Skala werdyktu
- Potwierdzone: źródło pierwotne mówi to samo.
- W dużej mierze prawdziwe: sedno się zgadza, szczegół jest nieścisły (podaj który).
- Mylące: fakty prawdziwe, wniosek z nich nie wynika albo brakuje kontekstu.
- Fałszywe: źródło pierwotne mówi coś innego.
- Nie do zweryfikowania: brak dostępu do źródła pierwotnego (napisz, czego brakuje).

## Format odpowiedzi
```
Twierdzenie: "<dosłownie>"
Werdykt: <skala>
Dlaczego: <2-3 zdania>
Dowody:
1. <cytat ze źródła> - <URL>, publikacja RRRR-MM-DD, dostęp RRRR-MM-DD
Zastrzeżenia: <czego nie sprawdzono>
```

## Zasady
- Brak dowodu na prawdziwość nie jest dowodem fałszu. Wtedy werdykt to "nie do zweryfikowania".
- Popularność twierdzenia nie jest dowodem. Dziesięć stron powtarzających jedno źródło to jedno źródło.
- Przy podatnościach sprawdzaj wersje w poradniku producenta, nie w nagłówku artykułu.
- Obraz i wideo: szukaj pierwszej publikacji i oryginału w wyższej jakości, zanim ocenisz treść.

## Gotowe, gdy
- werdykt wskazuje źródło pierwotne albo jasno mówi, że nie udało się do niego dotrzeć.

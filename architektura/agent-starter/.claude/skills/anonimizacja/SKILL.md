---
name: anonimizacja
description: Maskuje dane wrażliwe w logach, konfiguracjach i zrzutach przed wysłaniem ich do modelu w chmurze, usługi zewnętrznej, zgłoszenia u dostawcy albo na forum. Zamienia adresy IP, e-maile, hosty własnych domen, tokeny, hasła, klucze, PESEL, IBAN, telefony i wskazane nazwy na spójne znaczniki i pozwala odwrócić zamianę lokalnie. Użyj, gdy użytkownik chce wkleić log albo konfig z produkcji, pyta "czy mogę to wysłać do AI" albo przygotowuje materiał dla osoby trzeciej.
argument-hint: "[plik] [domeny własne]"
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/maskuj.py *)
---

# Anonimizacja przed wysyłką

Zasada: do modelu trafia struktura problemu, nie tożsamość środowiska. Spójne znaczniki
zachowują zależności (ten sam adres to zawsze `[IPV4_001]`), więc diagnoza nadal jest możliwa.

## Kroki
1. Ustal z użytkownikiem domeny własne i nazwy, których wzorce nie złapią: nazwa firmy,
   nazwiska, nazwy projektów, nazwy hostów bez domeny.
2. Zamaskuj plik. Agent nie czyta oryginału, czyta dopiero wynik:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/maskuj.py WEJ -o WEJ.mask \
     --mapa .agent/mapa-maskowania.json --domeny firma.pl,firma.local --slowa "Firma,Kowalski"
   ```
3. Przejrzyj wynik pod kątem tego, co zostało: nazwy użytkowników, ścieżki z nazwiskami,
   nazwy baz i tabel, numery zgłoszeń, treść zapytań SQL, identyfikatory klientów.
   Znalezione wartości dopisz do `--slowa` i uruchom ponownie (mapa zachowa numerację).
4. Pracuj na wersji zamaskowanej. W odpowiedzi używaj znaczników.
5. Odpowiedź dla człowieka można odwrócić lokalnie:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/maskuj.py --odwroc ODP.md -o ODP.jawna.md --mapa .agent/mapa-maskowania.json
   ```

## Czego skrypt nie zamieni
- nazw własnych, których nie podano w `--slowa`, i nazw hostów bez domeny,
- danych w treści swobodnej (opis zgłoszenia, komentarz w konfiguracji),
- adresów pętli zwrotnej i masek sieci (zostają celowo, bo niczego nie identyfikują),
- danych w obrazach i plikach binarnych.

## Zasady
- Mapa jest tak samo wrażliwa jak oryginał. Leży w `.agent/` (poza repozytorium), nie
  czytaj jej do rozmowy i nie wysyłaj.
- Pseudonimizacja nie jest anonimizacją w rozumieniu RODO: z mapą dane da się odtworzyć.
  O tym, czy materiał wolno przekazać, decyduje polityka organizacji, nie ten skill.
- Sekret, który wyciekł do logu, i tak trzeba wymienić. Napisz o tym użytkownikowi.

## Gotowe, gdy
- w wersji `.mask` nie ma wartości z listy ustalonej w kroku 1 (sprawdź `grep -i`),
- użytkownik wie, gdzie leży mapa i że jej nie udostępniamy.

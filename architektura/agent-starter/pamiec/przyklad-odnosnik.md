---
nazwa: przyklad-odnosnik
opis: Wzór wpisu wskazującego zasób zewnętrzny. Dotyczy miejsca, gdzie leży dokumentacja sieci.
typ: odnosnik
data: 2026-01-15
zrodlo: użytkownik
---
Dokumentacja sieci (adresacja, VLAN, schematy) leży w repozytorium `infra-docs`, katalog `siec/`. Aktualny schemat to plik z najnowszą datą w nazwie.

**Dlaczego:** bez tego agent zgaduje adresację albo pyta o nią za każdym razem.
**Jak stosować:** przy zadaniach sieciowych najpierw poproś o dostęp do tego katalogu (`--add-dir`) albo o wklejenie fragmentu.

---
name: diagnoza-hosta
description: Zbiera fakty o serwerze Linux wyłącznie poleceniami do odczytu i układa je w krótką diagnozę - system, obciążenie, pamięć, dyski i i-węzły, usługi w stanie błędu, sieć, porty, błędy z dziennika, ostatnie zmiany pakietów i plików w /etc. Użyj na początku każdej pracy z serwerem, przy zgłoszeniach "wolno działa", "usługa nie wstaje", "brak miejsca", "coś się zmieniło" oraz przed planowaniem zmiany.
argument-hint: "[nazwa usługi]"
allowed-tools: Bash(bash ${CLAUDE_SKILL_DIR}/scripts/zbierz_fakty.sh *)
---

# Diagnoza hosta

Najpierw fakty, potem hipotezy. Skrypt niczego nie zmienia, więc można go uruchomić
bez planu zmiany. Na zdalnym hoście uruchamia go użytkownik albo robi to agent po
wyraźnej zgodzie na połączenie.

## Kroki
1. Zbierz fakty (wynik do pliku, do rozmowy tylko potrzebne sekcje):
   ```bash
   bash ${CLAUDE_SKILL_DIR}/scripts/zbierz_fakty.sh [usługa] > wyniki/admin/fakty-$(date +%F-%H%M).md
   # host zdalny, bez kopiowania skryptu:
   ssh host 'bash -s -- nginx' < ${CLAUDE_SKILL_DIR}/scripts/zbierz_fakty.sh > wyniki/admin/fakty-host.md
   ```
2. Przeczytaj w tej kolejności: usługi w stanie błędu, zapełnione systemy plików,
   błędy z dziennika, ostatnie zmiany. Większość awarii ma przyczynę w jednej z czterech
   rzeczy: brak miejsca, brak pamięci, zmiana konfiguracji albo pakietu, zależność sieciowa.
3. Zadaj pytanie "co się zmieniło": pakiety, pliki w `/etc`, restart, wdrożenie, certyfikat.
4. Pogłęb tylko wskazany obszar. Przydatne polecenia do odczytu:
   ```bash
   systemctl status USŁUGA --no-pager -l ; journalctl -u USŁUGA -b --no-pager | tail -n 60
   du -xh --max-depth=2 /var | sort -h | tail -n 15          # co zajmuje miejsce
   find / -xdev -type f -size +500M 2>/dev/null | head       # duże pliki
   lsof +L1 2>/dev/null | head                                # usunięte, ale wciąż otwarte
   journalctl -k --no-pager | grep -iE 'oom|killed process' | tail
   ss -tulnp ; ip -s link ; resolvectl status 2>/dev/null | head -n 20
   openssl s_client -connect host:443 -servername host </dev/null 2>/dev/null | openssl x509 -noout -dates
   ```
5. Diagnoza w formacie: objaw, dowód (cytat z wyniku), najbardziej prawdopodobna przyczyna,
   czego jeszcze nie wiadomo, proponowany następny krok.

## Zasady
- W tym skillu nie ma poleceń zmieniających stan. Naprawa to osobny krok: skill `bezpieczna-zmiana`.
- Nie zakładaj dystrybucji ani wersji: przeczytaj sekcję "System".
- Wynik zawiera nazwy hostów, adresy i nazwy kont. Przed wysłaniem poza organizację: `anonimizacja`.

## Gotowe, gdy
- diagnoza cytuje konkretne wiersze z zebranych faktów,
- wiadomo, co jest potwierdzone, a co jest hipotezą do sprawdzenia.

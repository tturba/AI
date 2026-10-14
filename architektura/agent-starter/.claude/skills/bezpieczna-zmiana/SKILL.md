---
name: bezpieczna-zmiana
description: Prowadzi zmianę na działającym systemie tak, żeby dało się ją cofnąć - plan, kopia, test składni, próba na sucho, wykonanie, weryfikacja, droga powrotu, zapis. Użyj przed każdą edycją konfiguracji usługi, restartem, aktualizacją pakietów, zmianą zapory, DNS, uprawnień, zadań cron, kontenerów albo maszyn wirtualnych, zwłaszcza na produkcji i zwłaszcza na hoście dostępnym tylko zdalnie.
argument-hint: "[opis zmiany]"
---

# Bezpieczna zmiana

Agent proponuje i przygotowuje. Człowiek zatwierdza każde polecenie zmieniające stan.

## Kroki
1. Wypełnij plan z szablonu [assets/plan-zmiany.md](assets/plan-zmiany.md) i pokaż go
   użytkownikowi. Bez akceptacji planu nie przechodź dalej.
2. Stan przed: zapisz to, co po zmianie będzie porównywane (status usługi, wersja pakietu,
   wynik zapytania testowego, suma kontrolna pliku).
3. Kopia: `cp -a PLIK PLIK.bak-$(date +%Y%m%d-%H%M)`. Dla bazy danych zrzut, dla maszyny
   wirtualnej migawka. Sprawdź, że kopia istnieje i ma niezerowy rozmiar.
4. Test składni narzędziem danej usługi, zanim cokolwiek przeładujesz:
   `nginx -t`, `apachectl configtest`, `sshd -t`, `visudo -c`, `named-checkconf`,
   `haproxy -c -f PLIK`, `postfix check`, `docker compose config -q`,
   `systemd-analyze verify JEDNOSTKA`, `ansible-playbook --syntax-check`, `terraform validate`.
5. Próba na sucho, jeśli narzędzie ją ma: `apt-get -s`, `dnf --assumeno`, `rsync -n`,
   `ansible-playbook --check --diff`, `terraform plan`, `kubectl apply --dry-run=server`.
6. Zabezpieczenie dostępu przy zmianach SSH, zapory, sieci i VPN:
   - druga, otwarta sesja zostaje do końca weryfikacji,
   - automatyczny powrót, na przykład:
     `echo "cp -a /etc/ssh/sshd_config.bak-DATA /etc/ssh/sshd_config && systemctl reload ssh" | at now + 5 minutes`
     Po udanej weryfikacji zadanie usuń (`atq`, `atrm NUMER`).
7. Wykonanie: wybieraj `reload` przed `restart`, jedną zmianę naraz, jedno polecenie naraz.
8. Weryfikacja z zewnątrz usługi, nie tylko `systemctl is-active`: prawdziwe zapytanie,
   logowanie nową sesją, wpis w logu, test z innego hosta.
9. Niepowodzenie: wykonaj drogę powrotu z planu, potwierdź powrót do stanu przed, dopiero
   potem analizuj przyczynę.
10. Zapis w `wyniki/admin/RRRR-MM-DD-temat.md`: stan przed, polecenia, stan po, jak cofnąć.

## Zasady
- Zgoda dotyczy konkretnego polecenia. Kolejne polecenie wymaga kolejnej zgody.
- Nie łącz diagnozy ze zmianą w jednej komendzie i nie łącz kilku zmian operatorem `&&`.
- Nie usuwaj kopii zapasowych w ramach tej samej zmiany.
- Okno serwisowe i powiadomienie użytkowników ustala człowiek. Zapytaj, jeśli plan o tym milczy.

## Gotowe, gdy
- weryfikacja z kroku 8 przeszła i jej wynik jest w zapisie,
- zadanie automatycznego powrotu zostało usunięte,
- wiadomo, gdzie leży kopia i kiedy można ją skasować.

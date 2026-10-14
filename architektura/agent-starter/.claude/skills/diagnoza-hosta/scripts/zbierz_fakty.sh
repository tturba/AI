#!/usr/bin/env bash
# Zbiera fakty o hoście Linux. Wyłącznie polecenia do odczytu, niczego nie zmienia.
# Użycie: zbierz_fakty.sh [usługa]      np. zbierz_fakty.sh nginx
# Działa bez roota; część sekcji pokaże wtedy mniej (zaznaczone w wyniku).
set -u
USLUGA="${1:-}"
LC_ALL=C; export LC_ALL

sekcja() { printf '\n## %s\n' "$1"; }
jest() { command -v "$1" >/dev/null 2>&1; }
uruchom() { "$@" 2>&1 | head -n "${LIMIT:-25}"; }

echo "# Fakty o hoście: $(hostname 2>/dev/null || echo '?')"
echo "Zebrano: $(date -u +%Y-%m-%dT%H:%M:%SZ) UTC, użytkownik: $(id -un) (uid $(id -u))"
[ "$(id -u)" -ne 0 ] && echo "Uwaga: bez uprawnień roota, część danych może być niepełna."

sekcja "System"
( . /etc/os-release 2>/dev/null && echo "OS: ${PRETTY_NAME:-?}" )
echo "Jądro: $(uname -r) ($(uname -m))"
echo "Uptime: $(uptime 2>/dev/null | sed 's/^ *//')"
jest systemd-detect-virt && echo "Wirtualizacja: $(systemd-detect-virt 2>/dev/null)"
[ -f /var/run/reboot-required ] && echo "WYMAGANY RESTART: /var/run/reboot-required istnieje"
jest timedatectl && timedatectl 2>/dev/null | grep -E 'Time zone|synchronized|NTP service'

sekcja "Obciążenie i pamięć"
echo "Procesory: $(nproc 2>/dev/null || echo '?'), load: $(cut -d' ' -f1-3 /proc/loadavg 2>/dev/null)"
jest free && free -h
echo "Procesy z największym użyciem pamięci:"
LIMIT=6 uruchom ps -eo pid,user,%cpu,%mem,rss,comm --sort=-%mem
echo "Procesy z największym użyciem CPU:"
LIMIT=6 uruchom ps -eo pid,user,%cpu,%mem,comm --sort=-%cpu

sekcja "Dyski (wolne miejsce i i-węzły)"
df -hT -x tmpfs -x devtmpfs -x squashfs -x overlay 2>/dev/null
echo "Systemy plików zapełnione powyżej 85% (miejsce albo i-węzły):"
{ df -P -x tmpfs -x devtmpfs -x squashfs 2>/dev/null; df -Pi -x tmpfs -x devtmpfs -x squashfs 2>/dev/null; } \
  | awk 'NR>1 && $5+0>85 {print "  " $6 " " $5}' | sort -u
grep -E '\sro[\s,]' /proc/mounts 2>/dev/null | grep -vE 'squashfs|tmpfs|proc|sysfs|cgroup|/sys/|/snap/' \
  | awk '{print "TYLKO DO ODCZYTU: " $2}'

sekcja "Usługi w stanie błędu"
if jest systemctl; then
  systemctl --failed --no-legend --no-pager 2>/dev/null | head -20
  [ -z "$(systemctl --failed --no-legend --no-pager 2>/dev/null)" ] && echo "brak"
else
  echo "brak systemd"
fi

sekcja "Sieć"
jest ip && ip -brief addr 2>/dev/null | grep -v '^lo '
jest ip && echo "Trasa domyślna: $(ip route show default 2>/dev/null | head -1)"
echo "Resolver: $(grep -E '^nameserver' /etc/resolv.conf 2>/dev/null | awk '{print $2}' | tr '\n' ' ')"
echo "Porty nasłuchujące:"
if jest ss; then LIMIT=30 uruchom ss -tulnH; else echo "brak polecenia ss"; fi

sekcja "Błędy w dzienniku (ostatnia godzina)"
if jest journalctl; then
  journalctl -p err --since "1 hour ago" --no-pager -q 2>/dev/null | tail -n 25
  echo "Liczba wpisów err i wyższych od startu systemu: $(journalctl -p err -b --no-pager -q 2>/dev/null | wc -l)"
else
  echo "brak journalctl, sprawdź /var/log/syslog albo /var/log/messages"
fi
jest dmesg && dmesg --level=err,crit,alert,emerg 2>/dev/null | tail -n 8

sekcja "Logowania i zmiany"
jest last && LIMIT=6 uruchom last -n 6 -a
echo "Zalogowani teraz: $(who 2>/dev/null | wc -l)"
if [ -f /var/log/dpkg.log ]; then
  echo "Ostatnie zmiany pakietów (dpkg):"; grep -E ' (install|upgrade|remove) ' /var/log/dpkg.log 2>/dev/null | tail -n 8
elif jest rpm; then
  echo "Ostatnie zmiany pakietów (rpm):"; rpm -qa --last 2>/dev/null | head -n 8
fi
echo "Pliki w /etc zmienione w ostatnich 24 h:"
find /etc -xdev -type f -mtime -1 2>/dev/null | head -n 15

if [ -n "$USLUGA" ]; then
  sekcja "Usługa: $USLUGA"
  if jest systemctl; then
    systemctl status "$USLUGA" --no-pager -l 2>&1 | head -n 20
    echo "--- ostatnie wpisy dziennika ---"
    journalctl -u "$USLUGA" -n 40 --no-pager -q 2>/dev/null
    echo "--- plik jednostki i nadpisania ---"
    systemctl cat "$USLUGA" --no-pager 2>/dev/null | head -n 40
  fi
fi
exit 0

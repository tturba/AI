#!/usr/bin/env bash
# Co robi:   <jedno zdanie>
# Użycie:    szablon.sh [--wykonaj] [--katalog ŚCIEŻKA] [--dni N]
# Wymaga:    bash 4+, find, flock
# Kody:      0 sukces, 1 błąd działania, 2 błąd użycia, 3 inna instancja działa
set -euo pipefail
IFS=$'\n\t'
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

NAZWA="$(basename "$0")"
WYKONAJ=0
KATALOG="/var/tmp/przyklad"
DNI=14

log()  { printf '%s %s: %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$NAZWA" "$*" >&2; }
blad() { log "BŁĄD: $*"; exit "${2:-1}"; }
uzycie() { sed -n '2,5p' "$0" | sed 's/^# \{0,1\}//'; }

while [ $# -gt 0 ]; do
  case "$1" in
    --wykonaj) WYKONAJ=1 ;;
    --katalog) KATALOG="${2:?brak wartości dla --katalog}"; shift ;;
    --dni)     DNI="${2:?brak wartości dla --dni}"; shift ;;
    -h|--help) uzycie; exit 0 ;;
    *)         uzycie; exit 2 ;;
  esac
  shift
done

# Warunki wstępne: lepiej zatrzymać się tutaj niż w połowie pracy.
for polecenie in find flock; do
  command -v "$polecenie" >/dev/null || blad "brak polecenia: $polecenie"
done
[[ "$DNI" =~ ^[0-9]+$ ]] || blad "--dni musi być liczbą" 2
[ -d "$KATALOG" ] || blad "katalog nie istnieje: $KATALOG"
KATALOG="$(cd "$KATALOG" && pwd -P)"
case "$KATALOG" in /|/etc|/usr|/var|/home|/root) blad "odmowa pracy w katalogu systemowym: $KATALOG" ;; esac

# Jedna instancja naraz.
exec 9>"/tmp/${NAZWA}.lock"
flock -n 9 || { log "inna instancja działa, kończę"; exit 3; }

ROBOCZY="$(mktemp -d)"
trap 'rm -rf "${ROBOCZY:?}"' EXIT

uruchom() {
  if [ "$WYKONAJ" -eq 1 ]; then
    "$@"
  else
    log "PRÓBA (bez zmian): $(printf '%q ' "$@")"
  fi
}

log "start: katalog=$KATALOG dni=$DNI wykonaj=$WYKONAJ"
licznik=0
while IFS= read -r -d '' plik; do
  uruchom rm -f -- "$plik"
  licznik=$((licznik + 1))
done < <(find "$KATALOG" -xdev -type f -mtime +"$DNI" -print0)

log "koniec: plików=$licznik"
[ "$WYKONAJ" -eq 1 ] || log "to była próba, dodaj --wykonaj, żeby wprowadzić zmiany"

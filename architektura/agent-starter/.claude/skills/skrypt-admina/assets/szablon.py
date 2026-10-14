#!/usr/bin/env python3
"""<Jedno zdanie: co robi skrypt>.

Użycie:  szablon.py [--wykonaj] --katalog ŚCIEŻKA [--dni N]
Wymaga:  Python 3.9+, tylko biblioteka standardowa
Kody:    0 sukces, 1 błąd działania, 2 błąd użycia, 3 inna instancja działa
"""
import argparse
import fcntl
import logging
import os
import sys
import time
from pathlib import Path

log = logging.getLogger(Path(__file__).name)
ZAKAZANE = {Path(p) for p in ("/", "/etc", "/usr", "/var", "/home", "/root")}


def argumenty():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--katalog", required=True, type=Path)
    ap.add_argument("--dni", type=int, default=14)
    ap.add_argument("--wykonaj", action="store_true", help="bez tej flagi skrypt tylko pokazuje, co by zrobił")
    ap.add_argument("-v", "--verbose", action="store_true")
    return ap.parse_args()


def jedna_instancja():
    """Trzyma blokadę do końca procesu. Druga instancja kończy się kodem 3."""
    uchwyt = open("/tmp/%s.lock" % Path(__file__).name, "w")
    try:
        fcntl.flock(uchwyt, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        log.info("inna instancja działa, kończę")
        sys.exit(3)
    return uchwyt


def main():
    a = argumenty()
    logging.basicConfig(level=logging.DEBUG if a.verbose else logging.INFO, stream=sys.stderr,
                        format="%(asctime)s %(name)s %(levelname)s: %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z")
    katalog = a.katalog.resolve()
    if not katalog.is_dir():
        log.error("katalog nie istnieje: %s", katalog)
        return 1
    if katalog in ZAKAZANE:
        log.error("odmowa pracy w katalogu systemowym: %s", katalog)
        return 1
    blokada = jedna_instancja()  # noqa: F841 (uchwyt musi żyć do końca)

    # Sekret wyłącznie ze środowiska, nigdy z argumentu ani z kodu:
    # token = os.environ["NAZWA_ZMIENNEJ"]

    prog = time.time() - a.dni * 86400
    licznik = 0
    for plik in katalog.rglob("*"):
        if not plik.is_file() or plik.is_symlink() or plik.stat().st_mtime >= prog:
            continue
        if a.wykonaj:
            plik.unlink()
        else:
            log.info("PRÓBA (bez zmian): usunąłbym %s", plik)
        licznik += 1

    log.info("koniec: plików=%d wykonaj=%s", licznik, a.wykonaj)
    if not a.wykonaj:
        log.info("to była próba, dodaj --wykonaj, żeby wprowadzić zmiany")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception:
        log.exception("nieobsłużony błąd")
        sys.exit(1)

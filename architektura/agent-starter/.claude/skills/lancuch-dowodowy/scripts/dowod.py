#!/usr/bin/env python3
"""Rejestr dowodów: skrót SHA-256, czas UTC i opis każdego zebranego pliku.

Użycie:
  dowod.py dodaj PLIK --sprawa KATALOG --zrodlo URL_LUB_OPIS [--opis TEKST]
  dowod.py sprawdz --sprawa KATALOG

Manifest (manifest.jsonl) jest dopisywany, nigdy przepisywany. Każdy wpis zawiera skrót
poprzedniego wpisu, więc późniejsza zmiana w środku manifestu jest wykrywalna.
"""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import sys


def sha256_pliku(sciezka):
    h = hashlib.sha256()
    with open(sciezka, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def wczytaj(manifest):
    if not os.path.isfile(manifest):
        return []
    with open(manifest, encoding="utf-8") as f:
        return [json.loads(w) for w in f if w.strip()]


def skrot_wpisu(wpis):
    return hashlib.sha256(json.dumps(wpis, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def dodaj(a):
    dowody = os.path.join(a.sprawa, "dowody")
    os.makedirs(dowody, exist_ok=True)
    manifest = os.path.join(a.sprawa, "manifest.jsonl")
    wpisy = wczytaj(manifest)
    nr = len(wpisy) + 1
    nazwa = "D%03d-%s" % (nr, os.path.basename(a.plik))
    cel = os.path.join(dowody, nazwa)
    if os.path.abspath(a.plik) != os.path.abspath(cel):
        shutil.copy2(a.plik, cel)
    wpis = {
        "nr": nr,
        "plik": os.path.join("dowody", nazwa),
        "sha256": sha256_pliku(cel),
        "rozmiar": os.path.getsize(cel),
        "czas_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "zrodlo": a.zrodlo,
        "opis": a.opis or "",
        "poprzedni": skrot_wpisu(wpisy[-1]) if wpisy else "",
    }
    with open(manifest, "a", encoding="utf-8") as f:
        f.write(json.dumps(wpis, ensure_ascii=False, sort_keys=True) + "\n")
    try:
        os.chmod(cel, 0o444)
    except OSError:
        pass
    print("D%03d %s sha256=%s" % (nr, wpis["plik"], wpis["sha256"]))


def sprawdz(a):
    manifest = os.path.join(a.sprawa, "manifest.jsonl")
    wpisy = wczytaj(manifest)
    if not wpisy:
        sys.exit("Brak manifestu albo jest pusty: %s" % manifest)
    bledy = 0
    for i, w in enumerate(wpisy):
        sciezka = os.path.join(a.sprawa, w["plik"])
        if not os.path.isfile(sciezka):
            print("BRAK   D%03d %s" % (w["nr"], w["plik"]))
            bledy += 1
        elif sha256_pliku(sciezka) != w["sha256"]:
            print("ZMIANA D%03d %s (skrót się nie zgadza)" % (w["nr"], w["plik"]))
            bledy += 1
        oczekiwany = skrot_wpisu(wpisy[i - 1]) if i else ""
        if w.get("poprzedni", "") != oczekiwany:
            print("ŁAŃCUCH D%03d: wpis poprzedni został zmieniony albo usunięty" % w["nr"])
            bledy += 1
    print("Sprawdzono %d wpisów, problemów: %d" % (len(wpisy), bledy))
    sys.exit(1 if bledy else 0)


def main():
    ap = argparse.ArgumentParser(description="Rejestr dowodów")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dodaj")
    d.add_argument("plik")
    d.add_argument("--sprawa", required=True)
    d.add_argument("--zrodlo", required=True)
    d.add_argument("--opis")
    s = sub.add_parser("sprawdz")
    s.add_argument("--sprawa", required=True)
    a = ap.parse_args()
    dodaj(a) if a.cmd == "dodaj" else sprawdz(a)


if __name__ == "__main__":
    main()

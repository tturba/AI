#!/usr/bin/env python3
"""Streszczenie dużego logu: szablony wierszy, zakres czasu, adresy, kody, słowa alarmowe.

Użycie: streszcz_log.py PLIK [--top 25] [--filtr WYRAŻENIE] [--przyklady 2]
Czyta strumieniowo, więc działa na plikach wielogigabajtowych. Obsługuje .gz.
Wynik mieści się na ekranie i nadaje się do wklejenia agentowi zamiast surowego logu.
"""
import argparse
import collections
import gzip
import re
import sys

LICZBY = [
    (re.compile(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?"), "<CZAS>"),
    (re.compile(r"\b\d{1,2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2}(?: [+-]\d{4})?"), "<CZAS>"),
    (re.compile(r"\b[A-Z][a-z]{2}\s+\d{1,2} \d{2}:\d{2}:\d{2}\b"), "<CZAS>"),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "<IP>"),
    (re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"), "<UUID>"),
    (re.compile(r"\b0x[0-9a-fA-F]+\b|\b[0-9a-fA-F]{16,}\b"), "<HEX>"),
    (re.compile(r"\d+"), "<N>"),
]
CZAS = [
    re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}"),
    re.compile(r"\d{1,2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2}"),
    re.compile(r"[A-Z][a-z]{2}\s+\d{1,2} \d{2}:\d{2}:\d{2}"),
]
IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
HTTP = re.compile(r'"\s*(?:GET|POST|PUT|DELETE|HEAD|PATCH|OPTIONS)\s+(\S+)[^"]*"\s+(\d{3})\b')
ALARM = re.compile(r"\b(error|fail(?:ed|ure)?|denied|refused|timeout|timed out|panic|fatal|critical|segfault|"
                   r"out of memory|oom|killed|unauthorized|forbidden|invalid user|authentication failure|"
                   r"błąd|odmowa|nieudan\w*)\b", re.IGNORECASE)


def otworz(sciezka):
    if sciezka == "-":
        return sys.stdin
    if sciezka.endswith(".gz"):
        return gzip.open(sciezka, "rt", encoding="utf-8", errors="replace")
    return open(sciezka, encoding="utf-8", errors="replace")


def szablon(linia):
    for wzorzec, znak in LICZBY:
        linia = wzorzec.sub(znak, linia)
    return linia[:220]


def main():
    ap = argparse.ArgumentParser(description="Streszczenie logu")
    ap.add_argument("plik")
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--filtr", help="wyrażenie regularne, analizuj tylko pasujące wiersze")
    ap.add_argument("--przyklady", type=int, default=1)
    a = ap.parse_args()
    filtr = re.compile(a.filtr, re.IGNORECASE) if a.filtr else None

    szablony = collections.Counter()
    przyklady = {}
    adresy, kody, sciezki, alarmy = (collections.Counter() for _ in range(4))
    alarm_ip = collections.Counter()
    pierwszy = ostatni = None
    wierszy = 0
    with otworz(a.plik) as f:
        for linia in f:
            linia = linia.rstrip("\n")
            if not linia or (filtr and not filtr.search(linia)):
                continue
            wierszy += 1
            for wz in CZAS:
                m = wz.search(linia)
                if m:
                    pierwszy = pierwszy or m.group(0)
                    ostatni = m.group(0)
                    break
            s = szablon(linia)
            szablony[s] += 1
            przyklady.setdefault(s, [])
            if len(przyklady[s]) < a.przyklady:
                przyklady[s].append(linia[:300])
            ips = IP.findall(linia)
            adresy.update(ips[:1])
            m = HTTP.search(linia)
            if m:
                kody[m.group(2)] += 1
                sciezki[m.group(1).split("?")[0][:80]] += 1
            m = ALARM.search(linia)
            if m:
                alarmy[m.group(1).lower()] += 1
                alarm_ip.update(ips[:1])

    print("Wierszy: %d | szablonów: %d | zakres: %s -> %s" % (wierszy, len(szablony), pierwszy or "?", ostatni or "?"))

    def sekcja(tytul, licznik, n):
        if licznik:
            print("\n## %s" % tytul)
            for k, v in licznik.most_common(n):
                print("%8d  %s" % (v, k))

    sekcja("Słowa alarmowe", alarmy, 15)
    sekcja("Adresy przy wierszach alarmowych", alarm_ip, 10)
    sekcja("Najczęstsze adresy (pierwszy w wierszu)", adresy, 10)
    sekcja("Kody HTTP", kody, 10)
    sekcja("Najczęstsze ścieżki HTTP", sciezki, 10)
    print("\n## Najczęstsze szablony wierszy")
    for s, v in szablony.most_common(a.top):
        print("%8d  %s" % (v, s))
        for p in przyklady[s]:
            print("          np. %s" % p)
    rzadkie = [s for s, v in szablony.items() if v == 1]
    print("\n## Szablony jednorazowe: %d (często tu jest przyczyna)" % len(rzadkie))
    for s in rzadkie[: a.top]:
        print("          %s" % przyklady[s][0])


if __name__ == "__main__":
    main()

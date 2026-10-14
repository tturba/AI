#!/usr/bin/env python3
"""Pseudonimizacja tekstu przed wysłaniem do modelu albo usługi zewnętrznej.

Użycie:
  maskuj.py WEJ -o WYJ [--mapa mapa.json] [--domeny firma.pl,firma.local] [--slowa Kowalski,ACME]
  maskuj.py --odwroc WEJ -o WYJ --mapa mapa.json

Ta sama wartość dostaje zawsze ten sam znacznik (IP_001, EMAIL_002), więc zależności
w logu pozostają czytelne. Mapa pozwala odwrócić zamianę. Mapa JEST danymi wrażliwymi:
zostaje lokalnie i nie trafia do rozmowy ani do repozytorium.
"""
import argparse
import ipaddress
import json
import re
import sys

WZORCE = [
    ("KLUCZ_PRYWATNY", r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----"),
    ("JWT", r"\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),
    ("KLUCZ_AWS", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ("TOKEN", r"\b(?:ghp|gho|ghs|ghu|github_pat|glpat|xox[baprs]|sk|pk|rk)[-_][A-Za-z0-9_-]{16,}"),
    ("SEKRET", r"(?i)(?<=password=)\S+|(?<=passwd=)\S+|(?<=hasło=)\S+|(?<=haslo=)\S+|(?<=secret=)\S+"
               r"|(?<=token=)[^\s&\"']+|(?<=api_key=)[^\s&\"']+|(?<=apikey=)[^\s&\"']+"
               r"|(?<=Bearer )[A-Za-z0-9._~+/=-]{12,}|(?<=Basic )[A-Za-z0-9+/=]{8,}"),
    ("EMAIL", r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    ("IPV4", r"(?<![\d.])(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)(?![\d.])"),
    ("MAC", r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b"),
    ("IPV6", r"(?<![0-9A-Fa-f:.])[0-9A-Fa-f:]*:[0-9A-Fa-f:]*:[0-9A-Fa-f:]*(?![0-9A-Fa-f:])"),
    ("IBAN", r"\bPL\s?\d{2}(?:\s?\d{4}){6}\b"),
    ("PESEL", r"(?<!\d)\d{11}(?!\d)"),
    ("TELEFON", r"(?<![\d-])(?:\+48[ -]?)?\d{3}[ -]\d{3}[ -]\d{3}(?![\d-])"),
    ("UNC", r"\\\\[A-Za-z0-9._-]+\\[^\s\"']+"),
]


def pesel_poprawny(s):
    wagi = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    return (10 - sum(int(c) * w for c, w in zip(s, wagi)) % 10) % 10 == int(s[10])


def ip_zostaw(s):
    """Prawda, gdy tekst nie jest adresem albo jest adresem bez wartości identyfikującej."""
    try:
        ip = ipaddress.ip_address(s)
    except ValueError:
        return True
    return ip.is_loopback or ip.is_unspecified or s in ("255.255.255.255", "255.255.255.0", "255.255.0.0", "255.0.0.0")


class Maska:
    def __init__(self, mapa=None):
        self.mapa = mapa or {}
        self.liczniki = {}
        for znacznik in self.mapa.values():
            typ, _, nr = znacznik.strip("[]").rpartition("_")
            if nr.isdigit():
                self.liczniki[typ] = max(self.liczniki.get(typ, 0), int(nr))

    def znacznik(self, typ, wartosc):
        klucz = wartosc.lower() if typ in ("EMAIL", "HOST", "MAC") else wartosc
        if klucz not in self.mapa:
            self.liczniki[typ] = self.liczniki.get(typ, 0) + 1
            self.mapa[klucz] = "[%s_%03d]" % (typ, self.liczniki[typ])
        return self.mapa[klucz]

    def zamien(self, tekst, domeny, slowa):
        for typ, wzorzec in WZORCE:
            def f(m, typ=typ):
                w = m.group(0)
                if typ == "PESEL" and not pesel_poprawny(w):
                    return w
                if typ in ("IPV4", "IPV6") and ip_zostaw(w):
                    return w
                return self.znacznik(typ, w)
            tekst = re.sub(wzorzec, f, tekst, flags=re.DOTALL if typ == "KLUCZ_PRYWATNY" else 0)
        for domena in domeny:
            wz = r"(?i)\b(?:[a-z0-9-]+\.)*" + re.escape(domena) + r"\b"
            tekst = re.sub(wz, lambda m: self.znacznik("HOST", m.group(0)), tekst)
        for slowo in slowa:
            tekst = re.sub(r"(?i)\b" + re.escape(slowo) + r"\b", lambda m: self.znacznik("NAZWA", m.group(0).lower()), tekst)
        return tekst


def main():
    ap = argparse.ArgumentParser(description="Pseudonimizacja tekstu")
    ap.add_argument("wej")
    ap.add_argument("-o", "--wyj", required=True)
    ap.add_argument("--mapa", default="mapa-maskowania.json")
    ap.add_argument("--domeny", default="", help="domeny własne, po przecinku")
    ap.add_argument("--slowa", default="", help="nazwy własne do ukrycia, po przecinku")
    ap.add_argument("--odwroc", action="store_true")
    a = ap.parse_args()

    with open(a.wej, encoding="utf-8", errors="replace") as f:
        tekst = f.read()
    try:
        with open(a.mapa, encoding="utf-8") as f:
            mapa = json.load(f)
    except FileNotFoundError:
        mapa = {}

    if a.odwroc:
        for wartosc, znacznik in sorted(mapa.items(), key=lambda kv: -len(kv[1])):
            tekst = tekst.replace(znacznik, wartosc)
        with open(a.wyj, "w", encoding="utf-8") as f:
            f.write(tekst)
        print("Odwrócono %d znaczników -> %s" % (len(mapa), a.wyj))
        return

    maska = Maska(mapa)
    wynik = maska.zamien(tekst, [d.strip() for d in a.domeny.split(",") if d.strip()],
                         [s.strip() for s in a.slowa.split(",") if s.strip()])
    with open(a.wyj, "w", encoding="utf-8") as f:
        f.write(wynik)
    with open(a.mapa, "w", encoding="utf-8") as f:
        json.dump(maska.mapa, f, ensure_ascii=False, indent=1)
    podsumowanie = ", ".join("%s: %d" % kv for kv in sorted(maska.liczniki.items()))
    print("Zamaskowano -> %s" % a.wyj)
    print("Unikalne wartości: %s" % (podsumowanie or "brak"))
    print("Mapa (NIE udostępniaj): %s" % a.mapa, file=sys.stderr)


if __name__ == "__main__":
    main()

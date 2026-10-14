#!/usr/bin/env python3
"""Pasywny rekonesans domeny: tylko źródła stron trzecich, bez połączeń z hostami celu.

Użycie: pasywny_rekon.py DOMENA [--katalog wyniki/osint/SPRAWA] [--bez-ct]

Źródła: publiczny DNS (przez systemowy resolver, polecenie dig), RDAP (rdap.org),
logi Certificate Transparency (crt.sh). Skrypt nie łączy się z hostami celu: nie pobiera
strony, nie skanuje portów, nie odpytuje serwerów nazw celu bezpośrednio. Zapytania DNS
idą przez resolver, więc autorytatywny serwer nazw celu widzi adres resolvera, nie twój.
Każda czynność trafia do dziennika z czasem UTC.
"""
import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request

UA = "pasywny-rekon/1.0 (rekonesans pasywny, kontakt: operator)"
dziennik = []


def teraz():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(czynnosc, zrodlo, wynik):
    dziennik.append({"czas_utc": teraz(), "czynnosc": czynnosc, "zrodlo": zrodlo, "wynik": wynik})


def dig(nazwa, typ):
    if not shutil.which("dig"):
        return None
    try:
        out = subprocess.run(["dig", "+short", "+time=4", "+tries=1", nazwa, typ],
                             capture_output=True, text=True, timeout=12).stdout
    except Exception as e:
        log("dig %s %s" % (nazwa, typ), "resolver systemowy", "błąd: %s" % e)
        return []
    rekordy = [w.strip() for w in out.splitlines() if w.strip() and not w.startswith(";")]
    log("dig %s %s" % (nazwa, typ), "resolver systemowy", "%d rekordów" % len(rekordy))
    return rekordy


def pobierz_json(url, limit=8_000_000, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read(limit).decode("utf-8", errors="replace"))


def rdap(domena):
    url = "https://rdap.org/domain/" + urllib.parse.quote(domena)
    try:
        d = pobierz_json(url)
    except Exception as e:
        log("RDAP", url, "błąd: %s" % e)
        return {}
    wynik = {"status": d.get("status", []), "zdarzenia": {}, "serwery_nazw": [], "rejestrator": ""}
    for z in d.get("events", []):
        wynik["zdarzenia"][z.get("eventAction", "?")] = z.get("eventDate", "")
    wynik["serwery_nazw"] = sorted({n.get("ldhName", "").lower() for n in d.get("nameservers", []) if n.get("ldhName")})
    for e in d.get("entities", []):
        if "registrar" in e.get("roles", []):
            for pole in (e.get("vcardArray") or [None, []])[1]:
                if pole and pole[0] == "fn":
                    wynik["rejestrator"] = pole[3]
    log("RDAP", url, "ok")
    return wynik


def ct(domena):
    url = "https://crt.sh/?q=" + urllib.parse.quote("%." + domena) + "&output=json"
    try:
        d = pobierz_json(url, timeout=60)
    except Exception as e:
        log("Certificate Transparency", url, "błąd: %s (crt.sh bywa przeciążony, ponów później)" % e)
        return None
    nazwy = {}
    for wpis in d:
        for n in str(wpis.get("name_value", "")).lower().split("\n"):
            n = n.strip().lstrip("*.")
            if n == domena or n.endswith("." + domena):
                data = str(wpis.get("not_before", ""))[:10]
                if n not in nazwy or data > nazwy[n]:
                    nazwy[n] = data
    log("Certificate Transparency", url, "%d certyfikatów, %d nazw" % (len(d), len(nazwy)))
    return nazwy


def main():
    ap = argparse.ArgumentParser(description="Pasywny rekonesans domeny")
    ap.add_argument("domena")
    ap.add_argument("--katalog", help="katalog sprawy, tam trafi rekon.md i dziennik")
    ap.add_argument("--bez-ct", action="store_true", help="pomiń crt.sh")
    a = ap.parse_args()
    domena = a.domena.strip().lower().rstrip(".")
    if not re.fullmatch(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", domena):
        sys.exit("To nie wygląda na nazwę domeny: %r" % a.domena)

    w = ["# Rekonesans pasywny: %s" % domena, "", "Wygenerowano: %s (UTC). Źródła stron trzecich, bez połączeń z hostami celu." % teraz(), ""]

    w.append("## DNS")
    if not shutil.which("dig"):
        w.append("Brak polecenia dig (pakiet dnsutils albo bind-utils). Sekcja pominięta.")
    else:
        for typ in ("A", "AAAA", "NS", "MX", "TXT", "CAA", "SOA"):
            r = dig(domena, typ)
            w.append("- %s: %s" % (typ, "; ".join(r) if r else "brak"))
        dmarc = dig("_dmarc." + domena, "TXT")
        w.append("- DMARC: %s" % ("; ".join(dmarc) if dmarc else "brak rekordu"))
        spf = [t for t in (dig(domena, "TXT") or []) if "v=spf1" in t.lower()]
        w.append("- SPF: %s" % ("; ".join(spf) if spf else "brak rekordu"))

    w += ["", "## Rejestracja (RDAP)"]
    r = rdap(domena)
    if r:
        w.append("- Rejestrator: %s" % (r["rejestrator"] or "brak danych"))
        for k, v in sorted(r["zdarzenia"].items()):
            w.append("- %s: %s" % (k, v))
        w.append("- Status: %s" % (", ".join(r["status"]) or "brak danych"))
        w.append("- Serwery nazw: %s" % (", ".join(r["serwery_nazw"]) or "brak danych"))
    else:
        w.append("Brak odpowiedzi RDAP (część rejestrów krajowych nie udostępnia RDAP, użyj whois).")

    if not a.bez_ct:
        w += ["", "## Nazwy z logów Certificate Transparency"]
        nazwy = ct(domena)
        if nazwy is None:
            w.append("crt.sh nie odpowiedział. To nie znaczy, że nazw nie ma.")
        elif not nazwy:
            w.append("Brak wpisów.")
        else:
            w.append("Nazwa | ostatni certyfikat od")
            w.append("---|---")
            for n, data in sorted(nazwy.items(), key=lambda kv: kv[1], reverse=True)[:200]:
                w.append("%s | %s" % (n, data))
            if len(nazwy) > 200:
                w.append("... oraz %d starszych nazw (pełna lista w dzienniku JSON)" % (len(nazwy) - 200))
            w.append("")
            w.append("Uwaga: nazwa w certyfikacie nie oznacza, że host dziś istnieje. To trop do sprawdzenia.")

    w += ["", "## Dziennik czynności"]
    for d in dziennik:
        w.append("- %s | %s | %s | %s" % (d["czas_utc"], d["czynnosc"], d["zrodlo"], d["wynik"]))
    raport = "\n".join(w) + "\n"

    if a.katalog:
        os.makedirs(a.katalog, exist_ok=True)
        with open(os.path.join(a.katalog, "rekon-%s.md" % domena), "w", encoding="utf-8") as f:
            f.write(raport)
        with open(os.path.join(a.katalog, "dziennik-czynnosci.jsonl"), "a", encoding="utf-8") as f:
            for d in dziennik:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
        print("Zapisano: %s" % os.path.join(a.katalog, "rekon-%s.md" % domena), file=sys.stderr)
    print(raport)


if __name__ == "__main__":
    main()

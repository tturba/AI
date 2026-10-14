#!/usr/bin/env python3
"""Skan niezaufanej treści pod kątem prompt injection i ukrytych warstw.

Użycie: skan_tresci.py PLIK [--czysty PLIK_WYJ] [--json]
Kod wyjścia: 0 brak znalezisk, 1 znaleziska ŚREDNIE lub NISKIE, 2 znaleziska WYSOKIE.
Brak znalezisk oznacza "nic oczywistego", a nie "treść bezpieczna".
"""
import argparse
import base64
import json
import re
import sys
import unicodedata

NIEWIDOCZNE = {
    "znaki Unicode Tags (ukryty tekst ASCII)": (0xE0000, 0xE007F),
    "kierunek tekstu (bidi)": (0x202A, 0x202E),
    "izolaty bidi": (0x2066, 0x2069),
    "znaki zerowej szerokości": (0x200B, 0x200F),
    "łącznik słów": (0x2060, 0x2064),
    "selektory wariantów": (0xFE00, 0xFE0F),
    "selektory wariantów (dodatkowe)": (0xE0100, 0xE01EF),
}

WZORCE = [
    ("WYSOKI", "obrazek markdown z danymi w adresie",
     r"!\[[^\]]*\]\(\s*https?://[^)\s]*[?&][^)\s]*=[^)]*\)"),
    ("WYSOKI", "znacznik HTML ładujący zasób z parametrami",
     r"<(img|iframe|script|link)\b[^>]*(src|href)\s*=\s*[\"']?https?://[^\"'>\s]*\?[^\"'>\s]*"),
    ("ŚREDNI", "komentarz HTML", r"<!--.{0,400}?-->"),
    ("ŚREDNI", "treść ukryta stylem",
     r"(display\s*:\s*none|visibility\s*:\s*hidden|font-size\s*:\s*0|opacity\s*:\s*0(\.0+)?\b|color\s*:\s*(#fff(fff)?|white)\b)"),
    ("ŚREDNI", "próba przejęcia instrukcji (EN)",
     r"(ignore|disregard|forget)\s+(all\s+|any\s+|the\s+)?(previous|prior|above|earlier)\s+(instructions|rules|prompts?)"
     r"|you\s+are\s+now\b|new\s+instructions\s*:|system\s+prompt|do\s+not\s+(tell|inform|mention)\b.{0,30}\buser"
     r"|as\s+an?\s+(ai|assistant|agent)\b.{0,40}\b(must|should|have\s+to)"),
    ("ŚREDNI", "próba przejęcia instrukcji (PL)",
     r"(zignoruj|pomiń|zapomnij)\s.{0,30}(instrukcj|polece|zasad|regu)"
     r"|od\s+teraz\s+jesteś|jesteś\s+teraz|nowe\s+instrukcje\s*:|prompt\s+systemow|instrukcj\w*\s+systemow"
     r"|nie\s+(informuj|mów|wspominaj)\w*\s.{0,25}użytkownik"
     r"|(jeśli|jeżeli)\s+jesteś\s+(agentem|asystentem|modelem)|(do|dla)\s+(asystenta|agenta|modelu)\s+ai"),
    ("ŚREDNI", "polecenie użycia narzędzia albo wysyłki",
     r"(run|execute|uruchom|wykonaj)\s+(the\s+)?(following\s+)?(command|polecenie|komend)"
     r"|(send|wyślij|prześlij|upload)\s.{0,40}(to|na|do)\s+https?://"
     r"|(zapisz|dopisz|save|store)\s.{0,30}(pamięci|memory|CLAUDE\.md|AGENTS\.md)"),
    ("NISKI", "fałszywe granice dokumentu",
     r"\[(koniec|end|początek|start)\s+(of\s+)?(logu|danych|dokumentu|data|document|context|input)\]"
     r"|</?(system|assistant|user|instructions?)>"),
]


def niewidoczne(tekst):
    wynik = []
    for nr, linia in enumerate(tekst.splitlines(), 1):
        for nazwa, (a, b) in NIEWIDOCZNE.items():
            ile = sum(1 for z in linia if a <= ord(z) <= b)
            if ile:
                wynik.append({"poziom": "WYSOKI", "typ": nazwa, "linia": nr, "fragment": "%d znaków" % ile})
    ukryty = "".join(chr(ord(z) - 0xE0000) for z in tekst if 0xE0020 <= ord(z) <= 0xE007E)
    if ukryty:
        wynik.append({"poziom": "WYSOKI", "typ": "odczytana ukryta warstwa ASCII", "linia": 0, "fragment": ukryty[:300]})
    return wynik


def base64_podejrzane(tekst):
    wynik = []
    for m in re.finditer(r"[A-Za-z0-9+/]{60,}={0,2}", tekst):
        try:
            surowe = base64.b64decode(m.group(0) + "=" * (-len(m.group(0)) % 4), validate=False)
            zdek = surowe.decode("utf-8")
        except Exception:
            continue
        if sum(c.isprintable() or c.isspace() for c in zdek) / max(len(zdek), 1) > 0.9:
            linia = tekst.count("\n", 0, m.start()) + 1
            wynik.append({"poziom": "ŚREDNI", "typ": "tekst zakodowany base64", "linia": linia, "fragment": zdek[:200]})
    return wynik


def homoglify(tekst):
    wynik = []
    for nr, linia in enumerate(tekst.splitlines(), 1):
        for slowo in re.findall(r"[^\W\d_]{4,}", linia):
            pisma = set()
            for z in slowo:
                nazwa = unicodedata.name(z, "")
                if nazwa.startswith("LATIN"):
                    pisma.add("LATIN")
                elif nazwa.startswith("CYRILLIC"):
                    pisma.add("CYRILLIC")
                elif nazwa.startswith("GREEK"):
                    pisma.add("GREEK")
            if len(pisma) > 1:
                wynik.append({"poziom": "NISKI", "typ": "słowo mieszające alfabety (homoglify)", "linia": nr, "fragment": slowo})
                break
    return wynik


def oczysc(tekst):
    def zostaw(z):
        k = ord(z)
        return not any(a <= k <= b for a, b in NIEWIDOCZNE.values())
    tekst = "".join(z for z in tekst if zostaw(z))
    return re.sub(r"<!--.*?-->", "[usunięto komentarz HTML]", tekst, flags=re.DOTALL)


def main():
    ap = argparse.ArgumentParser(description="Skan niezaufanej treści")
    ap.add_argument("plik")
    ap.add_argument("--czysty", help="zapisz wersję bez znaków niewidocznych i komentarzy HTML")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    with open(a.plik, encoding="utf-8", errors="replace") as f:
        tekst = f.read()

    znaleziska = niewidoczne(tekst)
    for poziom, typ, wzorzec in WZORCE:
        for m in re.finditer(wzorzec, tekst, re.IGNORECASE | re.DOTALL):
            linia = tekst.count("\n", 0, m.start()) + 1
            znaleziska.append({"poziom": poziom, "typ": typ, "linia": linia,
                               "fragment": " ".join(m.group(0).split())[:200]})
    znaleziska += base64_podejrzane(tekst) + homoglify(tekst)
    kolejnosc = {"WYSOKI": 0, "ŚREDNI": 1, "NISKI": 2}
    znaleziska.sort(key=lambda z: (kolejnosc[z["poziom"]], z["linia"]))

    if a.czysty:
        with open(a.czysty, "w", encoding="utf-8") as f:
            f.write(oczysc(tekst))
    if a.json:
        print(json.dumps(znaleziska, ensure_ascii=False, indent=2))
    else:
        if not znaleziska:
            print("Brak oczywistych znalezisk (to nie jest gwarancja bezpieczeństwa).")
        for z in znaleziska[:60]:
            print("%-7s linia %-5s %s: %s" % (z["poziom"], z["linia"] or "-", z["typ"], z["fragment"]))
        if len(znaleziska) > 60:
            print("... oraz %d kolejnych" % (len(znaleziska) - 60))
        if a.czysty:
            print("Wersja oczyszczona: %s" % a.czysty)
    if any(z["poziom"] == "WYSOKI" for z in znaleziska):
        sys.exit(2)
    sys.exit(1 if znaleziska else 0)


if __name__ == "__main__":
    main()

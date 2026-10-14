#!/usr/bin/env python3
"""Hook UserPromptSubmit: podpowiada tryb pracy na podstawie słów kluczowych.

Czyta prompt z JSON na stdin i reguły z konfig/router.json. Gdy jeden tryb wyraźnie
wygrywa, dopisuje do kontekstu jedną linię z podpowiedzią. Niczego nie blokuje.
Decyzję o trybie podejmuje model według CLAUDE.md, hook tylko podsuwa sygnał.
"""
import json
import os
import re
import sys


def main():
    try:
        dane = json.load(sys.stdin)
    except Exception:
        return
    prompt = (dane.get("prompt") or "").strip()
    if len(prompt) < 12 or prompt.startswith(("/", "!", "#")):
        return
    katalog = os.environ.get("CLAUDE_PROJECT_DIR") or dane.get("cwd") or "."
    try:
        with open(os.path.join(katalog, "konfig", "router.json"), encoding="utf-8") as f:
            konfig = json.load(f)
    except Exception:
        return

    tekst = prompt.lower()[:4000]
    wyniki = []
    for tryb, reguly in konfig.get("tryby", {}).items():
        trafienia = []
        for slowo in reguly.get("slowa", []):
            if re.search(r"(?<!\w)" + re.escape(slowo.lower()), tekst):
                trafienia.append(slowo)
        for wzorzec in reguly.get("wzorce", []):
            try:
                if re.search(wzorzec, tekst, re.IGNORECASE):
                    trafienia.append("wzorzec:" + wzorzec[:24])
            except re.error:
                continue
        if trafienia:
            wyniki.append((len(trafienia) * reguly.get("waga", 1.0), tryb, trafienia))
    if not wyniki:
        return
    wyniki.sort(reverse=True)
    najlepszy = wyniki[0]
    if najlepszy[0] < konfig.get("prog", 1.0):
        return
    remis = len(wyniki) > 1 and wyniki[1][0] >= najlepszy[0] * 0.8
    linia = "Podpowiedź routera (dopasowanie słów kluczowych, może być błędne): tryb %s, trafienia: %s." % (
        najlepszy[1], ", ".join(najlepszy[2][:5]))
    if remis:
        linia += " Drugi kandydat: %s. Rozstrzygnij według CLAUDE.md." % wyniki[1][1]
    linia += " Według CLAUDE.md odpowiedź na zadanie w trybie zaczyna się od linii \"Tryb: <nazwa>\"."
    print(json.dumps({
        "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": linia}
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)

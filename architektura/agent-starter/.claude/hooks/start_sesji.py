#!/usr/bin/env python3
"""Hook SessionStart: podaje agentowi kilka faktów o stanie projektu.

Stdout tego zdarzenia trafia do kontekstu. Piszemy fakty, nie polecenia.
"""
import datetime
import json
import os
import sys


def main():
    try:
        dane = json.load(sys.stdin)
    except Exception:
        dane = {}
    katalog = os.environ.get("CLAUDE_PROJECT_DIR") or dane.get("cwd") or "."
    teraz = datetime.datetime.now().astimezone()
    linie = ["Data lokalna: %s (%s)." % (teraz.strftime("%Y-%m-%d %H:%M"), teraz.tzname())]

    stan = os.path.join(katalog, ".agent", "stan.md")
    if os.path.isfile(stan):
        zmiana = datetime.datetime.fromtimestamp(os.path.getmtime(stan)).strftime("%Y-%m-%d %H:%M")
        linie.append("Istnieje plik stanu poprzedniej pracy: .agent/stan.md (zmieniony %s)." % zmiana)

    pamiec = os.path.join(katalog, "pamiec")
    if os.path.isdir(pamiec):
        wpisy = [p for p in os.listdir(pamiec) if p.endswith(".md") and p not in ("MEMORY.md", "README.md")]
        linie.append("Pamięć projektu: %d wpisów w katalogu pamiec/." % len(wpisy))

    dzis = os.path.join(katalog, "wyniki", "newsy", teraz.strftime("%Y-%m-%d") + ".md")
    linie.append("Prasówka z dzisiaj: %s." % ("jest" if os.path.isfile(dzis) else "brak"))
    print("\n".join(linie))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)

#!/usr/bin/env python3
"""Hook PostToolUse (Bash): dopisuje wykonane polecenie do .agent/dziennik-polecen.jsonl.

Dziennik odpowiada na pytanie "co agent uruchomił i kiedy". Leży lokalnie, jest w .gitignore.
Wartości wyglądające na sekrety są zamazywane przed zapisem.
"""
import datetime
import json
import os
import re
import sys

MASKA = re.compile(
    r"((?:pass(?:word|wd)?|haslo|hasło|token|secret|api[_-]?key|authorization|bearer)\s*[=: ]\s*)(\S+)",
    re.IGNORECASE,
)


def main():
    dane = json.load(sys.stdin)
    if dane.get("tool_name") != "Bash":
        return
    polecenie = (dane.get("tool_input") or {}).get("command", "")
    katalog = os.environ.get("CLAUDE_PROJECT_DIR") or dane.get("cwd") or "."
    cel = os.path.join(katalog, ".agent")
    os.makedirs(cel, exist_ok=True)
    wpis = {
        "czas_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sesja": dane.get("session_id", "")[:8],
        "katalog": dane.get("cwd", ""),
        "polecenie": MASKA.sub(r"\1***", polecenie)[:2000],
    }
    with open(os.path.join(cel, "dziennik-polecen.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(wpis, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)

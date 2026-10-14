#!/usr/bin/env python3
"""Hook PreToolUse: strażnik sekretów, poleceń niszczących i wyjścia danych.

Wejście: JSON na stdin (pola tool_name i tool_input).
Wyjście: JSON z hookSpecificOutput.permissionDecision równym "deny" albo "ask".
Brak wyjścia oznacza: decyduje zwykły mechanizm uprawnień.

To jest siatka bezpieczeństwa oparta na wzorcach tekstu, a nie granica bezpieczeństwa.
Polecenie da się zapisać tak, żeby wzorzec go nie złapał. Twardą granicę daje sandbox,
osobne konto bez uprawnień i brak sekretów na maszynie agenta.
"""
import json
import re
import sys

# Ścieżki, których agent nie czyta i nie zmienia.
SEKRETY = re.compile(
    r"(^|[\s/\"'=])\.env(\.[\w.-]+)?($|[\s\"'])"
    r"|(^|[\s/\"'=])sekrety/"
    r"|\.ssh/|\.aws/|\.gnupg/|\.kube/config|\.docker/config\.json"
    r"|id_(rsa|ed25519|ecdsa)\b|\.(key|pfx|p12|kdbx)($|[\s\"'])|(priv|private)[\w.-]*\.pem|-key\.pem"
    r"|\.netrc|\.npmrc|\.pypirc|\.git-credentials|(bash|zsh)_history|/etc/shadow",
    re.IGNORECASE,
)

# Polecenia, których skutków nie da się cofnąć: odmowa.
ODMOWA = [
    (r"\brm\s+(-[a-zA-Z]*\s+)*-[a-zA-Z]*[rR][a-zA-Z]*\s+(-[a-zA-Z]*\s+)*(/|~|\$HOME|/\*|~/\*)(\s|$)",
     "rekurencyjne usuwanie katalogu głównego albo domowego"),
    (r"\bmkfs(\.\w+)?\b|\bwipefs\b|\bshred\b.*\s/dev/", "niszczenie systemu plików"),
    (r"\bdd\b.*\bof=/dev/(sd|nvme|vd|hd|mapper)", "zapis dd na urządzenie blokowe"),
    (r":\(\)\s*\{\s*:\|:&\s*\};:", "fork bomb"),
    (r"\bchmod\s+(-[a-zA-Z]+\s+)*777\s+/(\s|$)|\bchown\s+-R\b.*\s/(\s|$)", "uprawnienia na całym systemie"),
    (r"\b(curl|wget)\b[^|;&]*\|\s*(sudo\s+)?(ba|z|da)?sh\b", "uruchamianie skryptu prosto z sieci"),
    (r">\s*/dev/(sd|nvme|vd|hd)", "nadpisanie urządzenia blokowego"),
]

# Polecenia ryzykowne: decyzję podejmuje człowiek.
PYTANIE = [
    (r"\b(curl|wget|http|httpie)\b.*(\s-d\b|\s--data|\s-F\b|\s--form|\s-T\b|\s--upload-file|\s--post-(data|file)|\s-X\s*(POST|PUT|PATCH|DELETE))",
     "wysłanie danych na zewnątrz"),
    (r"\b(nc|ncat|netcat|socat)\b|\bscp\b|\brsync\b.*\s[\w.-]+@?[\w.-]*:", "przesłanie danych na inny host"),
    (r"\bgit\s+push\b.*(--force|-f\b)|\bgit\s+reset\s+--hard\b|\bgit\s+clean\s+-[a-zA-Z]*f", "nieodwracalna operacja git"),
    (r"\b(shutdown|reboot|poweroff|halt)\b|\binit\s+[06]\b", "wyłączenie albo restart hosta"),
    (r"\bsystemctl\s+(stop|restart|disable|mask|kill)\b|\bservice\s+\S+\s+(stop|restart)\b", "zatrzymanie albo restart usługi"),
    (r"\b(iptables|ip6tables|nft)\b.*(-F\b|--flush|\bflush\b)|\bufw\s+(disable|reset)\b|\bfirewall-cmd\b.*--(remove|panic)",
     "zmiana zapory, ryzyko odcięcia dostępu"),
    (r"\b(userdel|deluser|groupdel)\b|\bpasswd\b|\bvisudo\b|\busermod\b", "zmiana kont i uprawnień"),
    (r"\b(apt|apt-get|dnf|yum|zypper|pacman)\b.*\b(remove|purge|autoremove|erase|-R)\b", "usuwanie pakietów"),
    (r"\bdocker\s+(system|volume|image|container)\s+prune\b|\bdocker\s+(rm|rmi)\b.*-f|\bdocker\s+compose\s+down\b.*(-v|--volumes)",
     "usuwanie zasobów Dockera"),
    (r"\bkubectl\s+(delete|drain|cordon)\b|\bhelm\s+(uninstall|delete)\b", "usuwanie zasobów w klastrze"),
    (r"\bterraform\s+(destroy|apply)\b|\bansible-playbook\b(?!.*--check)", "zmiana infrastruktury bez trybu próbnego"),
    (r"\b(DROP|TRUNCATE)\s+(DATABASE|TABLE|SCHEMA)\b|\bDELETE\s+FROM\s+\w+\s*;", "niszczące polecenie SQL"),
    (r"\bcrontab\s+-r\b|\bqm\s+destroy\b|\bpct\s+destroy\b|\bzfs\s+destroy\b|\blvremove\b|\bvgremove\b", "usunięcie zasobu"),
    (r"\b(nmap|masscan|nikto|sqlmap|hydra|gobuster|ffuf|nuclei|wpscan)\b", "aktywny skan albo test, wymaga zakresu i zgody"),
]


def odpowiedz(decyzja, powod):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decyzja,
            "permissionDecisionReason": "straz.py: " + powod,
        }
    }, ensure_ascii=False))
    sys.exit(0)


def main():
    try:
        dane = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    narzedzie = dane.get("tool_name", "")
    wej = dane.get("tool_input") or {}
    polecenie = wej.get("command", "") if narzedzie == "Bash" else ""
    cele = " ".join(str(wej.get(k, "")) for k in ("file_path", "path", "pattern", "glob", "url", "notebook_path"))
    tekst = polecenie or cele

    if SEKRETY.search(tekst):
        odpowiedz("deny", "dostęp do sekretów jest zablokowany. Poproś użytkownika o nazwę zmiennej "
                          "albo o fragment bez wartości.")

    if narzedzie in ("Edit", "Write") and re.search(r"(^|/)\.claude/(settings.*\.json|hooks/)|(^|/)\.mcp\.json$", cele):
        odpowiedz("ask", "zmiana konfiguracji agenta (uprawnienia, hooki, MCP). Sprawdź dokładnie, co się zmienia.")

    if polecenie:
        for wzorzec, opis in ODMOWA:
            if re.search(wzorzec, polecenie, re.IGNORECASE):
                odpowiedz("deny", opis + ". Tego polecenia agent nie uruchamia. Jeśli jest potrzebne, "
                                         "użytkownik wykona je sam.")
        for wzorzec, opis in PYTANIE:
            if re.search(wzorzec, polecenie, re.IGNORECASE):
                odpowiedz("ask", opis)
    sys.exit(0)


if __name__ == "__main__":
    main()

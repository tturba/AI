---
paths:
  - "**/*.sh"
  - "**/*.bash"
  - "**/*.py"
  - "**/*.ps1"
---

# Reguły dla skryptów

Ten plik ładuje się tylko wtedy, gdy agent pracuje z plikiem skryptu.

- Bash zaczyna się od `set -euo pipefail`. Zmienne zawsze w cudzysłowach.
- Operacja niszcząca wymaga flagi `--wykonaj` albo ma tryb próbny jako domyślny.
- `rm -rf` tylko na ścieżce sprawdzonej wcześniej i z zabezpieczeniem `"${ZMIENNA:?}"`.
- Żadnych sekretów w kodzie ani w argumentach. Zmienna środowiska albo plik z prawami 600.
- PowerShell: `Set-StrictMode -Version Latest`, `$ErrorActionPreference = 'Stop'`,
  `[CmdletBinding(SupportsShouldProcess)]` i `-WhatIf` dla operacji zmieniających stan.
- Po każdej edycji: `bash -n` i `shellcheck` albo `python3 -m py_compile`. Wynik podaj w odpowiedzi.
- Pełna procedura: skill `skrypt-admina`.

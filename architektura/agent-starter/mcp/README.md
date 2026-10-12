# MCP w tej paczce

MCP (Model Context Protocol) podłącza do agenta zewnętrzne narzędzia: przeglądarkę,
dokumentację, API. Każdy serwer to dodatkowy kod uruchamiany z twoimi uprawnieniami
i dodatkowe opisy narzędzi w kontekście modelu, dlatego paczka włącza tylko jeden.

## Co jest w paczce
| Plik | Rola |
|---|---|
| `../.mcp.json` | serwery projektu: `context7` (włączony) i `playwright` (zdefiniowany, niewłączony) |
| `mcp.rozszerzony.przyklad.json` | pełniejszy zestaw do skopiowania wybranych wpisów |
| `katalog-mcp.json` | opis każdego serwera: po co, w którym trybie, jakie sekrety, jakie ryzyko |

Które serwery z `.mcp.json` wolno uruchomić, mówi `enabledMcpjsonServers`
w `.claude/settings.json`. Paczka ustawia `enableAllProjectMcpServers` na `false`,
żeby dopisanie serwera do `.mcp.json` nie włączało go po cichu.

## Jak włączyć serwer
1. Przeczytaj jego wpis w `katalog-mcp.json`, zwłaszcza pole `ryzyko`.
2. Sprawdź aktualną wersję i porównaj z przypiętą:
   ```bash
   npm view @playwright/mcp version
   curl -s https://pypi.org/pypi/mcp-server-fetch/json | python3 -c 'import sys,json;print(json.load(sys.stdin)["info"]["version"])'
   ```
3. Skopiuj wpis do `.mcp.json` i dopisz nazwę do `enabledMcpjsonServers` w swoim
   `.claude/settings.local.json`.
4. Sekrety podaj przez zmienne środowiska powłoki, z której startuje agent
   (`export GITHUB_PAT=...`). W plikach JSON zostaje tylko `${NAZWA_ZMIENNEJ}`.
5. Uruchom agenta i sprawdź stan poleceniem `/mcp`. Z powłoki: `claude mcp list`.

Dodanie serwera poleceniem zamiast edycji pliku:
```bash
claude mcp add --scope project --transport stdio time -- uvx mcp-server-time==2026.10.10 --local-timezone Europe/Warsaw
claude mcp add --scope project --transport http github https://api.githubcopilot.com/mcp/ --header "Authorization: Bearer ${GITHUB_PAT}"
```
Uwaga: drugie polecenie zapisze w `.mcp.json` wartość tokenu rozwiniętą przez powłokę.
Po dodaniu zamień ją ręcznie na `${GITHUB_PAT}` albo użyj zakresu `--scope local`.

## Uprawnienia do narzędzi MCP
Reguły w `.claude/settings.json` działają na nazwach `mcp__<serwer>__<narzędzie>`:
```json
"allow": ["mcp__context7__*"],
"ask":   ["mcp__playwright__*"],
"deny":  ["mcp__github__merge_pull_request"]
```
Nazwy narzędzi danego serwera zobaczysz po jego uruchomieniu w `/mcp`.

## Zanim zainstalujesz cudzy serwer
- Kto go wydaje i czy to ten sam podmiot, który prowadzi usługę? Nazwy pakietów bywają
  podrabiane (literówka, inny zakres w npm).
- Co robi przy starcie: `npm view PAKIET@WERSJA scripts dependencies`, kod w repozytorium.
- Jakie narzędzia wystawia i co jest w ich opisach. Opis narzędzia trafia do kontekstu
  modelu, więc może zawierać ukryte instrukcje. Przepuść opisy przez skill `niezaufana-tresc`.
- Czy wynik narzędzia pochodzi od osób trzecich (zgłoszenia, strony, maile)? Jeśli tak,
  to jest kanał prompt injection.
- Czy potrzebuje sieci i sekretów jednocześnie? Jeśli tak, uruchom go z osobnym,
  wąskim tokenem.
- Po aktualizacji wersji przeczytaj listę zmian. Serwer zaufany wczoraj może dziś
  wystawiać inne narzędzia.

## Limity, o których warto wiedzieć
- `MAX_MCP_OUTPUT_TOKENS` ogranicza wielkość wyniku narzędzia MCP (w paczce 15000,
  domyślnie 25000). Duży wynik to szybko zapełniony kontekst.
- `MCP_TIMEOUT` (milisekundy) to czas na start serwera. Pierwsze `npx -y` pobiera pakiet,
  więc bywa wolne: `MCP_TIMEOUT=30000 claude`.
- Claude Code ładuje definicje narzędzi MCP na żądanie (tool search), więc sam zapis
  w `.mcp.json` nie kosztuje wiele kontekstu. Kosztują wyniki wywołań.

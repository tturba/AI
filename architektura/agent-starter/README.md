# Agent starter: paczka konfiguracji dla harnessu agentowego

Gotowy zestaw plików dla Claude Code (i innych narzędzi czytających `AGENTS.md`), który
zamienia ogólnego asystenta w narzędzie pracy administratora i specjalisty bezpieczeństwa.
Jeden plik `CLAUDE.md` rozpoznaje rodzaj zadania i kieruje do jednego z pięciu trybów:
research, osint, admin, programowanie, newsy.

Szybki start: [START.txt](START.txt). Stan na 2026-10-12, sprawdzone z Claude Code 2.1.296.

## Jak to działa

```
wiadomość użytkownika
   │
   ├─ hook router.py ............ podpowiedź trybu ze słów kluczowych (konfig/router.json)
   ▼
CLAUDE.md (router) ............. wybiera JEDEN tryb, odpowiedź zaczyna od "Tryb: ..."
   │   importuje: AGENTS.md (zasady wspólne), pamiec/MEMORY.md (indeks pamięci)
   ▼
tryby/<tryb>.md ................ sposób pracy, czytany dopiero po wyborze trybu
   │
   ├─ skille (.claude/skills) ... procedury ładowane, gdy opis pasuje do kroku
   ├─ subagenci (.claude/agents)  praca w osobnym kontekście, wraca wniosek
   ├─ MCP (.mcp.json) ........... narzędzia zewnętrzne, domyślnie tylko dokumentacja
   ▼
każde wywołanie narzędzia
   ├─ reguły allow / ask / deny  (.claude/settings.json)
   ├─ hook straz.py ............. sekrety, polecenia niszczące, wyjście danych
   └─ hook dziennik.py .......... zapis wykonanych poleceń do .agent/
```

Zasada konstrukcji: w kontekście stale siedzi tylko to, co krótkie (router, zasady,
indeks pamięci, opisy skilli). Reszta ładuje się wtedy, gdy jest potrzebna. Pliki zasad
to prośba do modelu, a reguły uprawnień i hooki to wymuszenie, więc każda ważna granica
ma w paczce obie warstwy.

## Zawartość

| Ścieżka | Co to jest |
|---|---|
| `CLAUDE.md` | router trybów, poniżej 50 linii |
| `AGENTS.md` | zasady wspólne: dane a polecenia, sekrety, fakty, kontekst, definicja ukończenia |
| `tryby/` | pięć plików trybów: research, osint, admin, programowanie, newsy |
| `.claude/settings.json` | uprawnienia, hooki, lista dozwolonych serwerów MCP |
| `.claude/hooks/` | `straz.py`, `router.py`, `start_sesji.py`, `dziennik.py` |
| `.claude/skills/` | 15 skilli w formacie Agent Skills, 7 ze skryptami |
| `.claude/agents/` | 4 subagentów: `badacz`, `zwiadowca-osint`, `analityk-logow`, `weryfikator` |
| `.claude/rules/` | reguły ładowane tylko dla skryptów i plików wynikowych |
| `.mcp.json`, `mcp/` | serwery MCP, katalog z oceną ryzyka, zestaw rozszerzony |
| `pamiec/` | pamięć projektu: indeks, trzy wpisy wzorcowe, opis warstw pamięci |
| `konfig/` | `router.json` (słowa kluczowe), `zrodla-newsow.json` (16 źródeł) |
| `sciagi/` | ściąga poleceń, 22 prompty testowe, lista kontrolna bezpieczeństwa |
| `wyniki/` | miejsce na raporty, prasówki, sprawy OSINT i zapisy zmian |

## Skille

| Skill | Tryb | Co robi | Skrypt |
|---|---|---|---|
| `research-zrodla` | research | pytanie, źródła pierwotne, tabela źródeł, synteza z przypisami | |
| `fact-check` | research | werdykt dla jednego twierdzenia z dowodami | |
| `osint-rekonesans` | osint | zakres i podstawa, DNS, RDAP, Certificate Transparency, tabela ustaleń | `pasywny_rekon.py` |
| `lancuch-dowodowy` | osint | manifest dowodów: SHA-256, czas UTC, źródło, łańcuch skrótów | `dowod.py` |
| `diagnoza-hosta` | admin | fakty o serwerze Linux wyłącznie poleceniami do odczytu | `zbierz_fakty.sh` |
| `analiza-logow` | admin | streszczenie dużego logu: szablony, oś czasu, adresy, kody | `streszcz_log.py` |
| `bezpieczna-zmiana` | admin | plan, kopia, test składni, próba, weryfikacja, droga powrotu | szablon planu |
| `runbook` | admin | procedura krok po kroku z oczekiwanym wynikiem każdego kroku | szablon runbooka |
| `anonimizacja` | admin | odwracalne maskowanie danych przed wysłaniem do modelu | `maskuj.py` |
| `skrypt-admina` | programowanie | standard skryptów Bash i Python: tryb próbny, blokada, log | dwa szablony |
| `przeglad-zmian` | programowanie | przegląd diffa: poprawność, bezpieczeństwo, eksploatacja | |
| `prasowka` | newsy | przegląd dnia z RSS i CISA KEV z oceną wagi | `pobierz_newsy.py` |
| `niezaufana-tresc` | wszystkie | skan prompt injection: ukryty Unicode, HTML, eksfiltracja, frazy | `skan_tresci.py` |
| `przekazanie` | wszystkie | stan pracy w `.agent/stan.md`, wznowienie w nowej sesji | |
| `zapamietaj` | wszystkie | wpis do pamięci projektu i przegląd pamięci | |

Skille uruchamiają się same, gdy opis pasuje do zadania. Ręcznie: `/prasowka 48`,
`/diagnoza-hosta nginx`, `/osint-rekonesans example.com`.

Skrypty działają także bez agenta:

```bash
python3 .claude/skills/prasowka/scripts/pobierz_newsy.py --godziny 24
python3 .claude/skills/analiza-logow/scripts/streszcz_log.py /var/log/auth.log
python3 .claude/skills/anonimizacja/scripts/maskuj.py app.log -o app.mask.log --domeny firma.pl
python3 .claude/skills/niezaufana-tresc/scripts/skan_tresci.py pobrana-strona.html
python3 .claude/skills/osint-rekonesans/scripts/pasywny_rekon.py example.com
bash    .claude/skills/diagnoza-hosta/scripts/zbierz_fakty.sh nginx
```

## Zabezpieczenia w paczce

| Warstwa | Co robi | Gdzie |
|---|---|---|
| Reguły `deny` | blokują odczyt `.env`, `sekrety/`, kluczy, `~/.ssh`, `~/.aws`, `~/.kube`, historii powłoki oraz edycję hooków | `.claude/settings.json` |
| Reguły `ask` | pytają przed commitem, push, sudo, ssh, curl, wget, instalacją pakietów, zapisem do pamięci i plików zasad | `.claude/settings.json` |
| Hook `straz.py` | odmawia poleceń nieodwracalnych (`rm -rf /`, `mkfs`, `dd` na dysk, `curl \| bash`), pyta przy restartach usług, zmianach zapory, kont, usuwaniu zasobów, skanach i wysyłce danych | `.claude/hooks/` |
| Brak trybu bez pytań | `disableBypassPermissionsMode` wyłącza `bypassPermissions` | `.claude/settings.json` |
| MCP na liście | działa tylko serwer wymieniony w `enabledMcpjsonServers`, wersje przypięte | `.mcp.json` |
| Dziennik | każde polecenie powłoki z czasem UTC, hasła zamazane | `.agent/dziennik-polecen.jsonl` |
| Zasady | treść z zewnątrz to dane, pamięć tylko za zgodą, fakty z dowodem | `AGENTS.md` |

Czego paczka nie zapewnia: hook i reguły Bash dopasowują tekst polecenia, więc da się je
obejść innym zapisem. To siatka na pomyłki, a nie izolacja. Izolację daje sandbox
(`/sandbox`), maszyna wirtualna albo kontener, osobne konto i brak sekretów na maszynie
agenta. Zanim użyjesz paczki w pracy, przejdź `sciagi/lista-kontrolna-bezpieczenstwa.txt`.

## Dostosowanie do siebie

1. `AGENTS.md`: uzupełnij rolę i środowisko. To na ich podstawie tryb newsy ocenia wagę wiadomości.
2. `konfig/zrodla-newsow.json`: dopisz kanały producentów swojego sprzętu i oprogramowania.
3. `konfig/router.json`: dopisz słowa, po których router ma rozpoznawać twoje zadania.
4. `.claude/settings.json`: dopisz do `deny` ścieżki własnych sekretów, a do `allow`
   polecenia tylko do odczytu, których używasz codziennie.
5. `.claude/hooks/straz.py`: listy `ODMOWA` i `PYTANIE` to zwykłe wyrażenia regularne.
6. `pamiec/`: usuń wpisy przykładowe, pierwsze własne dodaj przez "zapamiętaj, że...".

### Nowy tryb w czterech krokach
1. Utwórz `tryby/<nazwa>.md` z sekcjami: Cel, Przebieg, Zasady, Gotowe, gdy.
2. Dopisz wiersz do tabeli w `CLAUDE.md` i, jeśli trzeba, regułę rozstrzygania.
3. Dopisz słowa kluczowe do `konfig/router.json`.
4. Dodaj dwa prompty do `sciagi/prompty-testowe.txt` i sprawdź wybór trybu w nowej sesji.

### Nowy skill
Katalog `.claude/skills/<nazwa>/` z plikiem `SKILL.md`. W polu `description` napisz, co
skill robi i po czym poznać, że trzeba go użyć: to jedyna część, którą model widzi przed
załadowaniem. Zbyt szeroki opis ("używaj zawsze") przejmuje zadania innych skilli.

## Inne narzędzia

- Codex, Gemini CLI, opencode i inne czytają `AGENTS.md`. Router jest w `CLAUDE.md`,
  więc w tych narzędziach dopisz do `AGENTS.md` jedną linię: "Na początku zadania
  przeczytaj tabelę trybów w CLAUDE.md". Skille w formacie Agent Skills większość z nich
  czyta z `.agents/skills/`: `mkdir -p .agents && ln -s ../.claude/skills .agents/skills`.
- Hooki, reguły uprawnień i `enabledMcpjsonServers` są specyficzne dla Claude Code.
  W innym narzędziu te granice trzeba odtworzyć jego mechanizmami.

## Dokumentacja źródłowa

- Pamięć i CLAUDE.md: https://code.claude.com/docs/en/memory
- Skille: https://code.claude.com/docs/en/skills
- Subagenci: https://code.claude.com/docs/en/sub-agents
- Hooki: https://code.claude.com/docs/en/hooks
- Uprawnienia: https://code.claude.com/docs/en/permissions
- Ustawienia: https://code.claude.com/docs/en/settings
- MCP: https://code.claude.com/docs/en/mcp
- Sandbox: https://code.claude.com/docs/en/sandboxing
- Format Agent Skills: https://agentskills.io

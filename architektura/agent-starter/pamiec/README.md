# Pamięć: co gdzie leży i kiedy się ładuje

Agent zaczyna każdą sesję z pustym kontekstem. To, co "pamięta", pochodzi z plików
wczytanych na starcie. Im więcej wczytasz, tym mniej miejsca na zadanie i tym słabiej
model trzyma się zasad, więc warstwy poniżej mają różne przeznaczenie.

| Warstwa | Plik | Kto pisze | Kiedy się ładuje | Na co |
|---|---|---|---|---|
| Zasady projektu | `CLAUDE.md`, `AGENTS.md` | człowiek | zawsze | reguły i router, do 200 linii na plik |
| Zasady osobiste | `CLAUDE.local.md`, `~/.claude/CLAUDE.md` | człowiek | zawsze | prywatne preferencje, poza repozytorium |
| Reguły ścieżkowe | `.claude/rules/*.md` z polem `paths` | człowiek | gdy agent dotyka pasującego pliku | zasady dla typu plików |
| Tryby | `tryby/*.md` | człowiek | gdy router wybierze tryb | sposób pracy w danym rodzaju zadania |
| Skille | `.claude/skills/*/SKILL.md` | człowiek | opis zawsze, treść na żądanie | procedury krok po kroku |
| Pamięć projektu | `pamiec/MEMORY.md` i wpisy | agent za zgodą człowieka | indeks zawsze, wpisy na żądanie | fakty i preferencje wspólne dla zespołu |
| Auto memory | `~/.claude/projects/<projekt>/memory/` | agent | pierwsze 200 linii albo 25 KB indeksu | notatki agenta na tej maszynie |
| Stan zadania | `.agent/stan.md` | agent | gdy sesja go przeczyta | gdzie przerwano bieżącą pracę |

## Pamięć projektu a auto memory
Claude Code ma wbudowaną pamięć automatyczną (auto memory): sam zapisuje notatki
w katalogu domowym, osobno dla każdego repozytorium, i nie przenosi ich między maszynami.
Katalog `pamiec/` z tej paczki to coś innego: leży w repozytorium, przechodzi przegląd
jak kod, działa w każdym narzędziu czytającym `AGENTS.md` i jest wspólny dla zespołu.

Praktyczny podział: fakty o środowisku i ustalenia zespołu do `pamiec/`, osobiste
przyzwyczajenia do auto memory albo `CLAUDE.local.md`.

Polecenie `/memory` w Claude Code pokazuje wszystkie wczytane pliki pamięci i pozwala
włączyć albo wyłączyć auto memory. Wyłączenie dla jednego projektu: `"autoMemoryEnabled": false`
w `.claude/settings.json`.

## Higiena
- Pamięć jest powierzchnią ataku. Treść z zewnątrz, która raz trafi do pamięci, wraca
  w każdej kolejnej sesji jako "zaufana". Dlatego zapis do `pamiec/` wymaga zgody
  (reguła `ask` w ustawieniach), a skill `zapamietaj` odrzuca fakty pochodzące z danych.
- Przeglądaj pamięć jak kod: `git diff pamiec/` przed commitem.
- Wpis bez powodu i daty jest nie do oceny po pół roku. Szablon wymusza oba pola.
- Usuń trzy pliki `przyklad-*.md` i ich linie z indeksu, gdy zaczniesz dodawać własne wpisy.

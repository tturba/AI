# Runbook: <co ta procedura robi>

| Pole | Wartość |
|---|---|
| Dotyczy | <usługa, hosty, środowisko> |
| Kiedy użyć | <objaw albo zdarzenie, które uruchamia procedurę> |
| Czas wykonania | <minuty> |
| Wymagane uprawnienia | <konto, grupa, dostęp> |
| Ostatnio sprawdzono | <RRRR-MM-DD, kto, wersja systemu i usługi> |
| Właściciel | <zespół albo osoba> |

## Zanim zaczniesz
- [ ] Jesteś na właściwym hoście: `hostname -f` zwraca `<HOST>`.
- [ ] <warunek wstępny, na przykład kopia z ostatnich 24 h istnieje>
- [ ] <kogo poinformować>

## Zmienne
| Nazwa | Znaczenie | Przykład |
|---|---|---|
| `<HOST>` | | |

## Kroki

### 1. <nazwa kroku>
```bash
<polecenie>
```
Oczekiwany wynik: <co ma się pojawić>
Jeśli inaczej: <co zrobić, do kogo eskalować>

### 2. <nazwa kroku>
```bash
<polecenie>
```
Oczekiwany wynik: <...>
Jeśli inaczej: <...>

## Sprawdzenie, że działa
```bash
<polecenie testowe z perspektywy użytkownika usługi>
```

## Wycofanie
1. <polecenie>
2. <jak potwierdzić powrót>

## Eskalacja
- <kto, jak się skontaktować, po jakim czasie>

## Historia zmian runbooka
- <RRRR-MM-DD>: <co zmieniono i dlaczego>

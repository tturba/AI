# Jawne źródła do rekonesansu pasywnego

Stan na 2026-10. Serwisy zmieniają warunki i limity: przed pracą na większą skalę
przeczytaj regulamin i sprawdź, czy potrzebny jest klucz API.

## Domena i DNS
| Co | Gdzie | Uwagi |
|---|---|---|
| Rejestracja domeny | `https://rdap.org/domain/DOMENA`, polecenie `whois` | dla .pl dane osób fizycznych są ukryte |
| Rekordy DNS | `dig DOMENA TYP +short` | zapytanie idzie przez resolver |
| Certyfikaty i nazwy hostów | `https://crt.sh/?q=%25.DOMENA&output=json` | bywa przeciążony, ponawiaj |
| Historia DNS | SecurityTrails, DNSDumpster | konto albo limit zapytań |
| Polityka pocztowa | rekordy TXT: SPF, `_dmarc`, `selector._domainkey` | selektor DKIM trzeba znać |

## Adresy IP i sieci
| Co | Gdzie |
|---|---|
| Właściciel adresu, zakres, kontakt abuse | `https://rdap.org/ip/ADRES` |
| ASN, prefiksy, sąsiedzi BGP | bgp.he.net, RIPEstat (`https://stat.ripe.net`) |
| Usługi widoczne z internetu | Shodan, Censys (wynik cudzego skanu, nadal źródło pasywne) |
| Reputacja adresu | AbuseIPDB, GreyNoise |

## Strony i treści
| Co | Gdzie |
|---|---|
| Wcześniejsze wersje strony | `https://web.archive.org/web/*/DOMENA/*` |
| Analiza podejrzanego adresu | urlscan.io, VirusTotal |
| Domeny z ostrzeżeń | lista ostrzeżeń CERT Polska: `https://cert.pl/lista-ostrzezen/` |
| Technologie strony | nagłówki i źródło strony z archiwum, BuiltWith |

## Organizacje w Polsce
| Co | Gdzie |
|---|---|
| Spółki, zarząd, sprawozdania | wyszukiwarka KRS Ministerstwa Sprawiedliwości |
| Działalności jednoosobowe | CEIDG |
| Status VAT i rachunki | wykaz podatników VAT (biała lista) |
| Zamówienia publiczne | Biuletyn Zamówień Publicznych, platforma e-Zamówienia |
| Znaki towarowe | Urząd Patentowy RP, EUIPO |
| Ostrzeżenia finansowe | lista ostrzeżeń publicznych KNF |

## Operatory wyszukiwania
```
site:example.com filetype:pdf            dokumenty w domenie
site:example.com -www                    hosty inne niż www
site:example.com inurl:login             strony logowania
"example.com" -site:example.com          wzmianki poza domeną
intitle:"index of" site:example.com      otwarte katalogi
site:github.com "example.com"            wzmianki w repozytoriach
```

## Czego nie robimy w trybie pasywnym
Skan portów, słownikowe wyliczanie subdomen i katalogów, zapytania do API celu, próby
logowania, kontakt z pracownikami, zakładanie kont pod fałszywą tożsamością.

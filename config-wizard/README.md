# SailingPD Config Wizard

Een browser-gebaseerde configuratiewizard voor [SailingPD](https://github.com/xanderburchartz/sailingpd) — het sailing performance dashboard dat live laat zien hoe goed je vaart en waar snelheidswinst zit. Draait op Windows, Linux of een Raspberry Pi.

![Welkomscherm](docs/screenshot-welcome.png)

---

## Wat doet het?

De Config Wizard leidt u stapsgewijs door alle instellingen van SailingPD. U hoeft geen `.ini`-bestanden handmatig te bewerken. De wizard legt bij elke stap uit waarom een instelling nodig is en schrijft aan het einde de juiste configuratiebestanden weg.

**11 stappen:**

| # | Stap | Inhoud |
|---|------|--------|
| 1 | Welkom | Uitleg over SailingPD en de wizard |
| 2 | Activiteit | Wat wil je doen: live zeilen, uitproberen zonder instrumenten, naspelen of analyse |
| 3 | Bootgegevens | Bootnaam, windmeterhoogte, Leeway K-factor, bootfoto |
| 4 | NMEA Verbinding | Netwerk (UDP/TCP) of serieel; kalibratie-instellingen |
| 5 | Snelheidspolar | Polar uploaden of aanmaken |
| 6 | Correcties | Kompasdeviatie, STW-correctie, hiel polar (optioneel) |
| 7 | NMEA Uitvoer | Welke NMEA-berichten en logbestanden SailingPD genereert |
| 8 | WiFi & Webserver | UDP broadcast en ingebouwde webserver |
| 9 | Trim Advies | Trim-adviezen en drempelwaarden |
| 10 | Weergave | Headless modus, lettertype en vensterdimensies |
| 11 | Opslaan & Starten | Samenvatting, configuratie opslaan, SailingPD starten |

| | |
|--|--|
| ![Activiteit](docs/screenshot-activity.png) | ![NMEA Verbinding](docs/screenshot-nmea-input.png) |
| ![Trim Advies](docs/screenshot-trimadvice.png) | ![Opslaan](docs/screenshot-save.png) |

---

## Vereisten

- **Windows 10/11, 64-bit Linux, of Raspberry Pi** met SailingPD geïnstalleerd
- **Windows:** géén Python nodig als u `SailingPD-ConfigWizard.exe` gebruikt — dubbelklikken volstaat. Wilt u vanaf de broncode werken (`start.bat`), dan wél **Python 3.9+** (van [python.org](https://www.python.org/downloads/), met *"Add Python to PATH"* aangevinkt)
- **Linux / Raspberry Pi:** **Python 3.9+**, meestal al aanwezig
- Geen internetverbinding nodig na de eerste installatie

---

## Installatie

1. Zet de map `config-wizard/` in uw SailingPD-installatiemap:

```
sailingpd-vX.X.X/
├── config-wizard/      ← hier
├── boatspecifics/
├── systemfiles/
├── sailingPD
└── ...
```

2. Maak het startscript uitvoerbaar:

```bash
chmod +x config-wizard/start.sh
```

---

## Starten

**Windows** — dubbelklik op **`SailingPD instellen.exe`**: die heeft geen Python nodig, vindt uw SailingPD-map zelf en opent de browser. Werkt u vanaf de broncode, dubbelklik dan op **`start.bat`**. De eerste keer maakt het script automatisch een Python-omgeving aan, installeert Flask + Pillow en opent de browser. Verschijnt er "Python is niet gevonden"? Installeer Python 3.9+ (zie *Vereisten*).

**Linux / Raspberry Pi:**

```bash
cd sailingpd-vX.X.X/config-wizard
./start.sh
```

De eerste keer wordt automatisch een Python virtual environment aangemaakt en worden de benodigde packages (Flask, Pillow) geïnstalleerd.

Open daarna in de browser op dezelfde computer:

```
http://localhost:5001
```

Of vanaf een ander apparaat op hetzelfde netwerk:

```
http://[ip-adres]:5001
```

> **Tip:** het IP-adres vind je op **Windows** met `ipconfig` (Opdrachtprompt) en op **Linux/Raspberry Pi** met `hostname -I` (terminal).

---

## Configuratiebestanden

De wizard schrijft naar drie bestanden in de SailingPD-installatiemap:

| Bestand | Inhoud |
|---------|--------|
| `boatspecifics/boatspecifics.ini` | Bootgegevens, NMEA-verbinding, trim-instellingen |
| `systemfiles/processlist.ini` | Opstartgedrag, weergave, drempelwaarden |
| `systemfiles/sendoverwifi.ini` | WiFi, UDP en webserver-instellingen |
| `systemfiles/headless.txt` | Aanwezig = headless modus aan |

CSV-bestanden (polars, deviatie, etc.) worden direct opgeslagen wanneer u ze aanmaakt of uploadt in de betreffende stap.

---

## SailingPD starten vanuit de wizard

Op de laatste stap kunt u SailingPD direct starten via de groene knop **▶ SailingPD starten**. De wizard blijft bereikbaar — SailingPD draait als een losstaand achtergrondproces.

---

## Technische details

| | |
|-|-|
| Backend | Python / Flask (Multi-threaded) |
| Frontend | Vanilla JavaScript, Standalone Offline CSS |
| Poort | 5001 (instelbaar via `PORT` omgevingsvariabele) |
| Dependencies | `flask>=3.0.0`, `Pillow>=10.0.0` |
| Offline geschiktheid | 100% lokaal (geen externe CDN of internetverbinding vereist) |

---

## Versies

> De changelog volgt de **release-tags** op GitHub: **`v0.1.0` → `v1.0.0` → `v1.1.0`**. (De wizard had eerder een eigen `v0.1.x`-telling; die is hier samengevoegd in de kit-releases.)

| Versie | Datum | Wijzigingen |
|--------|-------|-------------|
| **v1.1.0** | 2026-08-19 | **Windows zonder Python + configureerbaar dashboard.**<br>- **Startbaar zonder Python**: de wizard is nu ook een losse `.exe` (PyInstaller) — dubbelklikken volstaat; hij vindt de SailingPD-map zelf en opent de browser.<br>- **Configureerbaar prestatiepaneel** als standaarddashboard: alle SPD-velden, vier stijlen (SPD-Default, Modern, Raymarine, B&G), drie kleurmodes (dag / zwart-wit / nacht-rood) en drie sjablonen (Beginner / Gevorderd / Expert); per tegel kies je veld, meter/getal/balk en grootte. Trimadvies als coachingtegel + doel-vs-werkelijk-paren in elke stijl.<br>- **Legacy-dashboard** (`legacy.html`) voor oude toestellen (bijv. iPad 2 / Safari 9).<br>- **Menu-redesign** met thumbnails + SPD-logo als standaard startpagina; **Signal K** als eenvoudige route; **basismodus** verbergt de geavanceerde webserver-opties.<br>- **Windows-bugfixes**: opslaan (`#btn-save` gekoppeld aan `saveAndStart()`); ontbrekende `systemfiles/startupfiles.ini` (headless *"Deadly Error"*); `UnicodeEncodeError` op codepagina cp1252; replay als aparte schakelaar (SPD kent alleen `activity = NMEA` + `[Mode] replay = Y`, schermmodus vereist); startscripts herstellen na een afgebroken pip-install.<br>- `install.bat`/`install.sh` vervallen — de wizard installeert het menu nu zelf (exe-first). Zie ook `TESTRAPPORT.md` / `BACKLOG.md`. |
| **v1.0.0** | 2026-08-10 | **Eerste "Starter Kit"-release**: wizard + dashboard-menu samengebracht in één repo, platform-agnostisch (Windows / Linux / Raspberry Pi), installatie via `install.bat` / `install.sh`.<br>- **100% offline CSS**: externe Tailwind-CDN vervangen door lokaal gegenereerde Tailwind (CLI-build v3.4.17).<br>- **Performance**: Flask multi-threading (`threaded=True`) + kortere NMEA-test-socket-timeout.<br>- **Beveiliging**: path-traversal-opschoning op alle CSV-endpoints. |
| **v0.1.0** | 2026-05-21 | Eerste release — volledige wizard (11 stappen). |

---

## Licentie

Dit project is een add-on voor SailingPD en wordt verspreid onder dezelfde voorwaarden als SailingPD zelf.

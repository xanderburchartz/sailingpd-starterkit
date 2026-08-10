# SailingPD Starter Kit

**Maak [SailingPD](https://www.capolavoro.nl/manual-sailingpd) toegankelijk voor iedereen** — zonder `.ini`-bestanden te bewerken.

Deze starter kit bundelt twee dingen die het opstarten met SailingPD een stuk eenvoudiger maken:

1. **Config-wizard** — een browser-wizard die je stap voor stap door alle instellingen leidt, met uitleg in gewone taal, een woordenlijst, een "Test verbinding & detecteer sensoren"-knop, en een basismodus die alleen de essentiële stappen toont. Werkt op **Windows, Linux en Raspberry Pi**.
2. **Web-menu** — een overzichtspagina op poort 9090 waarmee je met één klik door alle SailingPD-dashboardpagina's bladert, elk met een **thumbnail** en korte toelichting.

![Web-menu](docs/menu-screenshot.png)

> Onafhankelijke add-on. SailingPD zelf is gemaakt door Thomas ten Kortenaar (capolavoro.nl); deze kit is daar geen officieel onderdeel van maar werkt er bovenop.

---

## Wat heb je nodig?

- **SailingPD** geïnstalleerd (download bij [capolavoro.nl](https://www.capolavoro.nl/manual-sailingpd)) — Windows 10/11, 64-bit Linux, of Raspberry Pi.
- **Python 3.9+** (op Windows: [python.org](https://www.python.org/downloads/), vink *"Add Python to PATH"* aan; op Linux/Raspberry Pi meestal al aanwezig).
- Geen internet nodig na installatie.

---

## Installeren

1. Download deze starter kit (groene **Code**-knop → *Download ZIP*, of `git clone`).
2. Pak de map **`sailingpd-starterkit`** uit **in je SailingPD-installatiemap**, naast `sailingPD` en `web_root/`:

   ```
   sailingpd-vX.X.X/
   ├── sailingPD            (of sailingPD.exe op Windows)
   ├── web_root/
   ├── boatspecifics/
   └── sailingpd-starterkit/   ← hier
   ```

3. Draai de installer:
   - **Windows** — dubbelklik `sailingpd-starterkit\install.bat`
   - **Linux / Raspberry Pi** — `./sailingpd-starterkit/install.sh`

De installer plaatst de wizard in je SailingPD-map en zet het web-menu als startpagina (de originele webpagina blijft bereikbaar op `/dials.html`).

---

## Gebruiken

1. **Start de wizard**
   - Windows: dubbelklik `config-wizard\start.bat`
   - Linux/Pi: `./config-wizard/start.sh`

   Open daarna **http://localhost:5001** in je browser. De eerste keer maakt het script automatisch een Python-omgeving aan.

2. **Doorloop de wizard** (activiteit, boot, NMEA-verbinding, polar…) en klik aan het eind op **SailingPD starten**.

3. **Open het dashboard-menu** op **http://localhost:9090/** en kies je favoriete weergave.

---

## Wat zit er in?

| Map | Inhoud |
|-----|--------|
| `config-wizard/` | De configuratie-wizard (Flask). Bewerkt de echte SailingPD-configbestanden. |
| `web-menu/` | De menu-startpagina + thumbnails, die in `web_root/` worden geplaatst. |
| `install.sh` / `install.bat` | Installers voor Linux/Pi en Windows. |

De thumbnails in het menu zijn momentopnamen. Wijzigen de dashboardpagina's of wil je ze verversen met je eigen data? Maak nieuwe met een headless browser (bijv. `chromium --headless=new --screenshot=... http://localhost:9090/SPDfull.html`) en verklein ze naar ~480px breed in `web_root/thumbs/`.

---

## Terugdraaien

- Web-menu terug naar de originele pagina: kopieer in `web_root/` het bestand `index.html.orig-spa` terug over `index.html`.
- Wizard verwijderen: verwijder de map `config-wizard/`.

---

## Licentie & dank

Deze kit is een onafhankelijke add-on voor SailingPD en wordt gedeeld onder dezelfde voorwaarden als SailingPD zelf. Met dank aan Thomas ten Kortenaar voor SailingPD.

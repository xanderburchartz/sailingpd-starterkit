# SailingPD Starter Kit

**Maak [SailingPD](https://www.capolavoro.nl/manual-sailingpd) toegankelijk voor iedereen** — zonder `.ini`-bestanden te bewerken.

Deze starter kit bundelt twee dingen die het opstarten met SailingPD een stuk eenvoudiger maken:

1. **Config-wizard** — een browser-wizard die je stap voor stap door alle instellingen leidt, met uitleg in gewone taal, een woordenlijst, een "Test verbinding & detecteer sensoren"-knop, en een basismodus die alleen de essentiële stappen toont. Werkt op **Windows, Linux en Raspberry Pi**.
2. **Web-menu** — een overzichtspagina op poort 9090 waarmee je met één klik door alle SailingPD-dashboardpagina's bladert, elk met een **thumbnail** en korte toelichting. De wizard kan dit menu met één klik als startpagina zetten.

![Web-menu](docs/menu-screenshot.png)

![De config-wizard in de eenvoudige (basis)modus](docs/wizard-screenshot.png)

> Onafhankelijke add-on. SailingPD zelf is gemaakt door Thomas ten Kortenaar (capolavoro.nl); deze kit is daar geen officieel onderdeel van maar werkt er bovenop.

---

## Wat heb je nodig?

- **SailingPD** geïnstalleerd (download bij [capolavoro.nl](https://www.capolavoro.nl/manual-sailingpd)) — Windows 10/11, 64-bit Linux, of Raspberry Pi.
- **Windows:** niets extra's. De wizard is een los programma (`SailingPD instellen.exe`) — geen Python nodig.
- **Linux / Raspberry Pi:** Python 3.9+ (meestal al aanwezig).
- Geen internet nodig na installatie.

---

## Zo begin je

### Windows

1. Kopieer **`SailingPD instellen.exe`** in je SailingPD-map, naast `sailingPD.exe` en `web_root/`:

   ```
   SailingPD/
   ├── sailingPD.exe
   ├── web_root/
   ├── boatspecifics/
   └── SailingPD instellen.exe   ← hier
   ```

2. **Dubbelklik `SailingPD instellen.exe`.** De wizard opent vanzelf in je browser op **http://localhost:5001** — geen Python, geen installatie.
3. Doorloop de wizard. In de stap **WiFi & Webserver** zet je met één klik het **dashboard-menu** als startpagina. Klik aan het eind op **SailingPD starten**.
4. Open het dashboard op **http://localhost:9090/**.

### Linux / Raspberry Pi

1. Pak de map **`sailingpd-starterkit`** uit in (of naast) je SailingPD-installatiemap.
2. Start de wizard:

   ```bash
   ./sailingpd-starterkit/config-wizard/start.sh
   ```

   Open daarna **http://localhost:5001**. De eerste keer maakt het script automatisch een Python-omgeving aan.
3. Doorloop de wizard (het dashboard-menu installeer je met de knop in de stap **WiFi & Webserver**) en klik aan het eind op **SailingPD starten**.
4. Open het dashboard op **http://localhost:9090/**.

---

## Wat zit er in?

| Onderdeel | Inhoud |
|-----------|--------|
| `SailingPD instellen.exe` | De wizard als los Windows-programma (bevat het web-menu). Alleen in de release-download. |
| `config-wizard/` | De broncode van de wizard (Flask) voor Linux/Pi en ontwikkelaars. |
| `web-menu/` | De menu-startpagina + thumbnails, die de wizard in `web_root/` plaatst. |

De thumbnails in het menu zijn momentopnamen. Wijzigen de dashboardpagina's of wil je ze verversen met je eigen data? Maak nieuwe met een headless browser (bijv. `chromium --headless=new --screenshot=... http://localhost:9090/SPDfull.html`) en verklein ze naar ~480px breed in `web_root/thumbs/`.

---

## Terugdraaien

- **Dashboard-menu** terug naar de originele pagina: kopieer in `web_root/` het bestand `index.html.orig-spa` terug over `index.html` (de originele pagina blijft ook bereikbaar op `/dials.html`).
- **Wizard** verwijderen: verwijder `SailingPD instellen.exe` (Windows) of de map `sailingpd-starterkit` (Linux/Pi). De wizard verandert niets aan SailingPD zelf, alleen aan je configuratiebestanden.

---

## Licentie & dank

Deze kit is een onafhankelijke add-on voor SailingPD en wordt gedeeld onder dezelfde voorwaarden als SailingPD zelf. Met dank aan Thomas ten Kortenaar voor SailingPD.

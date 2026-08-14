# Testrapport — SailingPD dashboardpaneel (`web-menu/panel.html`)

Datum: 2026-08-14. Gestructureerde teststronde: **plan → review → parallel uitvoeren → rapport → fixes hertesten**.

## Aanpak
- Eén agent schreef een testplan (105 cases, coverage-matrix over alle features + alle deze sessie gefixte bugs); een tweede agent reviewde het kritisch (verdict NEEDS-WORK met concrete correcties + twee code-observaties).
- Testomgeving: een **headless jsdom-harness** die het échte `panel.html` laadt, met een WebSocket-shim (zodat óók de **live-modus** getest wordt — daar zat de klacht) en localStorage-seeding.
- Zes test-agents voerden het plan parallel uit als draaiende Node-tests tegen de harness. Totaal **161 asserties**.

## Resultaat: 161/161 PASS (na fixes)

| Groep | Onderwerp | Resultaat |
|---|---|---|
| G1 | Skin-dropdown, dag/nacht-icoon, header-indeling, persistentie | 13/13 |
| G2 | Bewerk-modus, tegel-CRUD, grootte, veldkeuze (88 velden), delete-all | 29/29 |
| G3 | Type/smaak-schakelaars + **sheet-churn (meter→balk/getal)** | 29/29 |
| G4 | Waarde-bugs, robuustheid, **XSS** | 18/18 |
| G5 | 4 skins × tegeltypes, nachtpaletten, CSS-vars, live/demo/staleness | 57/57 |
| G6 | Drag-reorder, resize-grip, integratie | 15/15 |

## Bevestigd gefixt (regressietests slagen)
De eerder deze sessie gefixte bugs zijn nu met een expliciete regressietest bewezen opgelost:
- **Meter → balk/getal in live-modus** (de klacht): een vastgehouden knop-node overleeft meerdere WS-datapushes (ook een frame midden in de klik) en de conversie lukt betrouwbaar. Bewezen niet-vacuüm (de renders veranderen echt tegelwaarden).
- Crash bij hoek-f2 zonder waarde; `Performance-filter` niet meer als perf-%; tekst-subvelden tonen tekst; hoekveld zonder waarde → `--` (niet 0); perf-stilstand → naald op 0; SPD wind/koers = dial + sub-tabel + eerlijke header; f2/f3/f4 op "— geen —"; meter-smaak overschrijft veld niet; resize meet celmaat + selecteert tegel; `pointercancel`-opruiming; delete-all blijft leeg; XSS in tekst-hoofdveld; staleness-terugval; CSS-vars gewist; 88 velden compleet.

## Nieuw gevonden bugs — gefixt en hertest in deze ronde
1. **XSS via tekst-subvelden op B&G/Raymarine-meters (kritiek).** `roseBG`, `wind` en `crs` renderden `f2/f3/f4`-tekst (bv. Trim-advice) ongeëscaped in de SVG → een string als `<i>x</i>` werd een live DOM-element. De eerdere XSS-fix dekte alleen `TPL.text` en de SPD-tabel. **Fix:** de tekst-subvelden worden nu geëscaped (`_esc` in `spd_templates.js`). Hertest: 3 cases (bg-roos, ray-wind, ray-koers) nu PASS — geen injectie meer.
2. **Koers toonde `360` i.p.v. `000` in de B&G-koershoek.** De centrale badge was al gefixt, maar de hoek-uitlezing gebruikte `split(angN)` → `Math.abs(359.7).toFixed(0)='360'`, terwijl het midden `000` toonde. **Fix:** de hoek-uitlezing wrapt nu 0-360 voor whole-degree headings. Hertest: PASS — geen `360` meer in de tegel.

## Visuele teststronde (2026-08-14) — echte rendering (Playwright/Chromium)
Zelfde aanpak: plan (52 cases) → review (verdict NEEDS-WORK, verscherpte de twee door de
gebruiker gemelde defecten) → uitvoeren met een **echte-render-harness** (Chromium, echte layout)
met een overflow/overlap/spill-scanner over alle skins × tegeltypes × groottes.

**Bevestigde visuele bugs — gefixt en her-gescand:**
1. **Tegel-header labels pasten niet → wrapten** (lange sleutels als "Performance-incl-current"
   braken af, lieten de header groeien en klemden de inhoud). De header-`span` had geen
   `nowrap/ellipsis`. **Fix:** één regel met ellipsis + tooltip (`title`). Her-scan: 0 header-wraps.
2. **SPD-default getal/tabel-tegels spilden buiten de kaart** (lang label duwde de `<table>`
   breder dan de tegel, 30-151px eruit). **Fix:** `table-layout:fixed` + vaste kolombreedtes +
   ellipsis op de waarde-cel. Her-scan: 0 spills.

**Vals-positieven (met screenshot weerlegd):** de scanner meldde "overlap" op de B&G/Raymarine-
koersroos (bv. "030 ∩ 026"). Screenshots tonen dat die netjes rendert — het zijn geroteerde
kompasgetallen (andere radius) en een bewust op de voorgrond liggende HDG-badge; hun
as-uitgelijnde bounding-boxes overlappen wel, maar visueel botsen ze niet. Geen fix nodig.

**Bewust gedrag (geen bug):** op een piepkleine 1×1-tegel kan een 24-tekens veldnaam nooit
volledig passen; die kapt nu netjes af met "…" (volledige tekst bij hover), i.p.v. te wrappen/spillen.

Na de visuele fixes bleef de headless-suite **161/161** (twee tests bijgewerkt naar de nieuwe,
uniforme balk waarin het smaak-slot aanwezig-maar-verborgen is i.p.v. afwezig).

## Wat ook headless/echte-render niet volledig dekt
Kleur-/contrast-oordeel en het echte sleep-gevoel blijven deels een menselijke check; screenshots
per skin (dag+nacht) zijn beschikbaar in de sessie.

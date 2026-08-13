# Backlog — SailingPD Starter Kit

Losse verbeter-/bugpunten. Afgevinkte items blijven staan met datum voor de historie.

## Features / nog te bouwen

- [ ] **Zwart/wit-kleurmode per skin.** Nu heeft elke skin (Modern/B&G/Raymarine/SPD-default) twee modes: kleur (dag) + rood/zwart (nacht). De derde mode uit het plan — zwart/wit (grijstinten, hoog contrast, geen kleur) — ontbreekt nog. Palet per skin definiëren en een derde toggle-stand toevoegen.
- [ ] **Skins vs losse menu-layouts.** B&G/Raymarine/SPD-default zitten nu als skins binnen één paneel (matcht de Claude Design-handoff). Eerdere schets was 4 losse layouts in het menu. Afstemmen of dit zo blijft.

## Bugs — open (klein/laag)

- [ ] **roseBG `v1` omzeilt de perf-guard.** Alleen zichtbaar als een Performance-veld het hóófdveld van een B&G wind/koers-roos is (geen standaardconfig) — dan toont de digitale hoek de rauwe ~222 bij stilstand. Smal.
- [ ] **Geen sleep-drempel bij reorder.** Een tik die net een paar px doorschuift naar een buurtegel kan al herordenen. Klein UX-punt; drempel (>6px) toevoegen.
- [ ] **Labels = veldsleutels (niet de NL-labels).** `FIELDS()` overschrijft elk label met de sleutel (`l:k`), dus tegels/keuzelijst tonen "Performance-SOG" i.p.v. "Performance (SOG)". Consistent en dicht bij SPD's eigen naamgeving — bewust laten of NL-labels tonen? Afstemmen.

## Gerepareerd

- [x] 2026-08-13 — **Header + meter-conversie**:
  - Skins zijn nu een **dropdown** (SPD-Default, Modern, Raymarine, B&G) i.p.v. 4 knoppen.
  - Header logisch gegroepeerd: skin-dropdown links, Bewerken + dag/nacht rechts.
  - Nacht-knop is nu een **zon/maan-icoon** dat de doel-modus toont en toggelt.
  - **Bestaande meter → getal/balk lukte niet**: de bewerk-balk werd elke 200ms herbouwd voor live-cijfers, waardoor een tik (vooral traag op touchscreen) de knop miste. De balk wordt tijdens die verversing niet meer herbouwd.
- [x] 2026-08-13 — **Teststronde met 4 audit-agents + interactief: 13 bugs gevonden en verholpen** (commit volgt):
  - CRASH: wind-roos met hoek-f2 zonder waarde → `v2Num.toFixed()` bevroor de hele grid. Nu guard.
  - `Performance-filter` werd als perf-% behandeld (geguard/gezoneerd) → nu alleen echte perf-velden (`isPerf()`).
  - Tekstvelden als f2/f3/f4 toonden `--` → tonen nu de tekst.
  - Hoekvelden zonder waarde toonden `0` i.p.v. `--` (`Math.abs(null)===0`) → guard.
  - Perf-stilstand: getal `--` maar naald/boog stond op vol → naald nu op 0.
  - SPD wind/koers-gauge liet f2/f3/f4 vallen + header loog → toont nu dial + sub-tabel, eerlijke header.
  - f2/f3/f4 waren niet op "— geen —" te zetten → optie toegevoegd.
  - Meter-smaak Wind/Koers overschreef het gekozen hoofdveld → behoudt nu een numeriek veld.
  - Resize-grip volgde de cursor niet (hardcoded 110px) → meet nu de celmaat; grip selecteert de tegel.
  - Geen `pointercancel`-cleanup / drag hercheckte edit-modus niet → kon herordenen in kijk-modus. Nu opgeruimd.
  - `tick()` herbouwde elke 200ms de grid/sheet tijdens sleep/edit → gepauzeerd tijdens gesture; open dropdown blijft staan.
  - Koers `360` i.p.v. `000` bij [359.5,360) → modulo na afronden.
  - Alle tegels wissen → defaults kwamen terug bij reload → lege layout blijft nu bewaard.
  - XSS: `TPL.text` escapete server-tekst niet → nu geëscaped.
  - Half-open WS bleef eeuwig "LIVE" bevriezen → staleness-heartbeat valt na 5s terug op demo.
  - Latent: CSS-vars werden niet gewist tussen skins → union van alle sleutels wordt nu toegepast.
- [x] 2026-08-13 — SPD-default skin toont nu de echte SPD-look (Google-gauge dials + ruwe SPD-datatabel), alle 89 velden kiesbaar. (commit `7db945f`)

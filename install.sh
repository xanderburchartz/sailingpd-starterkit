#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  SailingPD Starter Kit — installer  (Linux / Raspberry Pi)
#  Plaats de map 'sailingpd-starterkit' IN je SailingPD-map
#  en draai dit script:   ./sailingpd-starterkit/install.sh
# ─────────────────────────────────────────────────────────────
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
SPD_DIR="$(dirname "$HERE")"          # bovenliggende map = SailingPD-installatiemap

echo "SailingPD-map: $SPD_DIR"
if [ ! -d "$SPD_DIR/web_root" ] || { [ ! -f "$SPD_DIR/sailingPD" ] && [ ! -f "$SPD_DIR/sailingPD.exe" ]; }; then
  echo
  echo "FOUT: dit lijkt niet je SailingPD-installatiemap (geen web_root/ of sailingPD gevonden)."
  echo "Plaats de map 'sailingpd-starterkit' IN je SailingPD-map en draai dit script opnieuw."
  exit 1
fi

# 1) Config-wizard installeren
echo "-> Config-wizard installeren..."
rm -rf "$SPD_DIR/config-wizard"
cp -r "$HERE/config-wizard" "$SPD_DIR/config-wizard"
chmod +x "$SPD_DIR/config-wizard/start.sh" 2>/dev/null || true

# 2) Web-menu installeren (originele startpagina bewaren als dials.html)
echo "-> Web-menu (startpagina) installeren..."
WR="$SPD_DIR/web_root"
if [ ! -f "$WR/index.html.orig-spa" ] && [ -f "$WR/index.html" ]; then
  cp "$WR/index.html" "$WR/index.html.orig-spa"
fi
[ -f "$WR/index.html.orig-spa" ] && cp "$WR/index.html.orig-spa" "$WR/dials.html"
cp "$HERE/web-menu/index.html" "$WR/index.html"
mkdir -p "$WR/thumbs"
cp "$HERE/web-menu/thumbs/"*.jpg "$WR/thumbs/" 2>/dev/null || true

cat <<EOF

Klaar!  Volgende stappen:
  1) Start de wizard:   $SPD_DIR/config-wizard/start.sh
     Open daarna in je browser:  http://localhost:5001
  2) Doorloop de wizard en klik aan het eind op 'SailingPD starten'.
  3) Open het dashboard-menu:    http://localhost:9090/

(De oude standaard-webpagina blijft bereikbaar op http://localhost:9090/dials.html)
EOF

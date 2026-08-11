#!/usr/bin/env bash
# SailingPD Config Wizard — startscript
set -e

cd "$(dirname "$0")"

# ##############################################################################
# [SCRIPT OPTIMIZATION & ANNOTATION]
# Automatische controle op aanwezigheid van 'python3 -m venv'.
# Op verse Debian / Raspberry Pi OS installaties ontbreekt python3-venv soms.
# ##############################################################################

# Omgeving opzetten zodra de venv ontbreekt OF de pakketten er niet in zitten.
# Op die tweede voorwaarde toetsen is nodig: een afgebroken pip-installatie (geen
# internet aan boord) laat een venv achter die er compleet uitziet, waarna een
# volgende start zou stranden op "ModuleNotFoundError: flask".
if [ ! -x ".venv/bin/python" ] || ! .venv/bin/python -c "import flask, PIL" 2>/dev/null; then
  if [ ! -x ".venv/bin/python" ]; then
    echo "Eerste keer: virtuele omgeving aanmaken..."
    if ! python3 -m venv .venv; then
      # Een mislukte aanmaak laat vaak een halve .venv-map achter; opruimen zodat
      # een volgende run opnieuw begint in plaats van te struikelen over pip.
      rm -rf .venv
      echo ""
      echo "FOUT: kon geen virtuele omgeving aanmaken (zie foutmelding hierboven)."
      echo "Ontbreekt python3-venv? Installeer het dan met:"
      echo "  sudo apt update && sudo apt install -y python3-venv"
      echo ""
      exit 1
    fi
  else
    echo "Benodigde pakketten ontbreken — opnieuw installeren..."
  fi

  if ! .venv/bin/python -m pip install --quiet -r requirements.txt; then
    echo ""
    echo "FOUT: kon Flask/Pillow niet installeren (internetverbinding nodig)."
    echo "Maak verbinding met internet en start dit script opnieuw."
    echo ""
    exit 1
  fi
  echo "Klaar."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SailingPD Config Wizard"
echo "  Zorg dat deze map (config-wizard/) in uw SailingPD-installatiemap staat"
echo "  Open: http://localhost:5001"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

.venv/bin/python app.py

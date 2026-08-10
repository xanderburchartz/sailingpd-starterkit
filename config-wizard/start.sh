#!/usr/bin/env bash
# SailingPD Config Wizard — startscript
set -e

cd "$(dirname "$0")"

# Maak een virtuele omgeving als die er nog niet is
if [ ! -d ".venv" ]; then
  echo "Eerste keer: virtuele omgeving aanmaken..."
  python3 -m venv .venv
  .venv/bin/pip install --quiet -r requirements.txt
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

#!/usr/bin/env bash
set -euo pipefail

APP_DIR=/opt/dbwe_escooter
sudo mkdir -p "$APP_DIR"
sudo cp -r ./* "$APP_DIR"/
cd "$APP_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

echo "Bitte .env bearbeiten und danach systemd/Nginx aktivieren."
echo "Beispiel: sudo cp deploy/escooter.service /etc/systemd/system/"
echo "Beispiel: sudo cp deploy/nginx.conf /etc/nginx/sites-available/dbwe_escooter"

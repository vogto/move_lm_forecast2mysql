# 📈 Logomate Forecast 2 MySQL

Dieses Projekt automatisiert den täglichen Import der neuesten Forecast-CSV-Datei von einem SMB-Netzlaufwerk in eine MySQL-Datenbank. Es nutzt eine virtuelle Python-Umgebung und wird täglich über einen Cronjob ausgeführt.

## 📂 Projektstruktur

```bash
/opt/forecast2mysql/
├── forecast.py       # Hauptskript
├── .env              # Umgebungsvariablen für DB und Pfade
├── venv/             # Virtuelle Umgebung
```

## 🧱 Einrichtung

### 1. Virtuelle Umgebung vorbereiten

```bash
cd /opt/forecast2mysql
python3 -m venv venv
source venv/bin/activate
pip install python-dotenv mysql-connector-python requests
```

### 2. CIFS für SMB-Zugriff installieren

```bash
sudo apt update
sudo apt install cifs-utils
```

### 3. SMB-Zugangsdaten sicher speichern

```bash
sudo nano /root/.smbcredentials
```

Inhalt:

```
username=DEIN_USER
password=DEIN_PASS
```

```bash
sudo chmod 600 /root/.smbcredentials
```

### 4. Automount über `/etc/fstab`

```bash
sudo nano /etc/fstab
```

```
//192.168.230.27/LogoMate_Transfer/LogoMate_Export/SAP_HEP_LIVE/Forecast /mnt/forecast_share cifs credentials=/root/.smbcredentials,iocharset=utf8,uid=1000,gid=1000,file_mode=0644,dir_mode=0755,nofail 0 0
```

```bash
sudo mount -a
```

### 5. Umgebungsvariablen konfigurieren

```bash
nano /opt/forecast2mysql/.env
```

Beispiel:

```
MYSQL_HOST=dedi848.your-server.de
MYSQL_PORT=3306
MYSQL_USER=dein_user
MYSQL_PASSWORD=dein_passwort
MYSQL_DATABASE=deine_datenbank
LOCAL_PATH=/mnt/forecast_share
GOOGLE_CHAT_WEBHOOK_URL=https://chat.googleapis.com/v1/spaces/AAA.../messages?key=...&token=...

```

## 💡 forecast.py

Importiert die neueste Datei und aktualisiert die Tabelle `forecast_to_home24`. Fügt jeder Zeile den aktuellen Timestamp hinzu.
Speichere folgendes Skript unter `/opt/forecast2mysql/forecast.py` und stelle sicher, dass es ausführbar ist:

```bash
chmod +x /opt/forecast2mysql/forecast.py
```


## ▶️ Manuell ausführen

```bash
/opt/forecast2mysql/venv/bin/python /opt/forecast2mysql/forecast.py
```

## 🧩 Systemd-Service

Um das Skript regelmäßig oder beim Systemstart auszuführen, kann ein `systemd`-Service eingerichtet werden.

### 1. Service-Datei erstellen

```bash
sudo nano /etc/systemd/system/logomate_forecast2mysql.service
```

#### Inhalt:

```ini
[Unit]
Description=CSV Datei importieren und Daten wegschreiben
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/forecast2mysql/
ExecStart=/opt/forecast2mysql/venv/bin/python /opt/forecast2mysql/forecast.py
EnvironmentFile=/opt/forecast2mysql/.env
StandardOutput=append:/var/log/forecast2mysql.log
StandardError=append:/var/log/forecast2mysql.log

[Install]
WantedBy=multi-user.target

```

---

### 2. Service aktivieren und starten

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable logomate_forecast2mysql.service
sudo systemctl start logomate_forecast2mysql.service
```

---

### 3. Service prüfen

Status anzeigen:

```bash
sudo systemctl status logomate_forecast2mysql.service
```

Logs live ansehen:

```bash
journalctl -u logomate_forecast2mysql.service -f
```

---


## ⏰ Optional: systemd-Timer (statt Cronjob)

Du kannst einen systemd-Timer verwenden, um den Export regelmäßig auszuführen (z. B. täglich um 03:00 Uhr).

### 1. Timer-Datei erstellen

```bash
sudo nano /etc/systemd/system/logomate_forecast2mysql.timer
```

#### Inhalt:

```ini
[Unit]
Description=Timer für Logomate-Forecast-Import alle 2 Stunden

[Timer]
OnCalendar=0/2:00:00
Persistent=true
Unit=logomate_forecast2mysql.service

[Install]
WantedBy=timers.target
```

---

### 2. Timer aktivieren und starten

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now logomate_forecast2mysql.timer

```

---

### 3. Timer prüfen

Liste aktiver Timer anzeigen:

```bash
systemctl list-timers
```

Status eines bestimmten Timers anzeigen:

```bash
systemctl status logomate_forecast2mysql.timer
```
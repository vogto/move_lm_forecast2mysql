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
pip install python-dotenv mysql-connector-python
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
```

## 💡 forecast.py

Importiert die neueste Datei und aktualisiert `forecast_to_home24`. Fügt jeder Zeile den aktuellen Timestamp hinzu.

## ▶️ Manuell ausführen

```bash
/opt/forecast2mysql/venv/bin/python /opt/forecast2mysql/forecast.py
```

## ⏰ Tägliche Ausführung via Cron

```bash
sudo crontab -e
```

```cron
0 6 * * * /opt/forecast2mysql/venv/bin/python /opt/forecast2mysql/forecast.py >> /var/log/forecast_cron.log 2>&1
```

## 🛟 Lizenz

MIT License

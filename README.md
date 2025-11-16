# MGX Account Generator

## Projektbeschreibung
Dieses Projekt erstellt automatisch neue Konten für die Plattform mgx.dev. Ein sichtbarer Chrome-Browser wird geöffnet, Temp-Mail-Adressen werden erzeugt, Verifizierungscodes ausgelesen und Cloudflare-Challenges werden durchlaufen. Die CLI steuert den gesamten Prozess und zeigt anschließend alle generierten Accounts tabellarisch an.

## Voraussetzungen
- Windows 10/11 mit aktivierter PowerShell/CMD
- Python 3.11 oder neuer im `PATH`
- Google Chrome (Standard-Installation) für den Patchright-Lauf
- Netzwerkzugriff auf https://mgx.dev und https://temp-mail.org

## Installationsanleitung
1. Repository entpacken oder klonen.
2. `setup_env.bat` ausführen – erstellt/aktualisiert den Ordner `env` und installiert alle Pakete aus `requirements.txt`.
3. Optional: `start_cli.bat` einmalig testen; das Skript ruft intern automatisch `setup_env.bat` auf, falls etwas fehlt.

## Nutzung
1. `start_cli.bat` starten.
2. Im Menü Option wählen:
   - `1` erstelle einen neuen Account (inkl. E-Mail-Bestätigung, Turnstile usw.).
   - `2` zeige die sortierte Tabelle aus `accounts.txt`.
   - `3` bereinige die Ordner `bilder`/`errors`, falls vorhanden.
   - `4` beenden (zeigt zuletzt noch einmal die Account-Tabelle).
3. Alle Ausgaben erscheinen farblich markiert (Grün = Erfolg, Gelb = Hinweis, Rot = Fehler). Fehler werden mit verständlichen Meldungen ausgegeben.

## FAQ
- **Das Skript meldet, dass `requirements.txt` fehlt.** – Stelle sicher, dass du die Datei nicht entfernt hast. Sie liegt im Projektwurzelverzeichnis und enthält die benötigten Pakete.
- **`setup_env.bat` findet Python nicht.** – Installiere Python 3.11+ und aktiviere beim Setup „Add to PATH“. Danach die Batch-Datei erneut ausführen.
- **Chrome wird nicht gefunden oder startet nicht.** – Installiere Google Chrome (64-bit, Standardpfad). Wenn du einen anderen Pfad verwendest, passe die Funktion `detect_chrome_executable()` in `main2.py` an.

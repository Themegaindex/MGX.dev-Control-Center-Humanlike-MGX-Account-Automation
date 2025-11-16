<div align="center">

# 🚀 MGX Account Generator

### *Automatische Kontoerstellung für mgx.dev mit intelligenter Verifizierung*

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Chrome](https://img.shields.io/badge/Chrome-Required-4285F4?style=for-the-badge&logo=googlechrome&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

</div>

## 📋 Inhaltsverzeichnis

- [🎯 Projektbeschreibung](#-projektbeschreibung)
- [✨ Features](#-features)
- [⚙️ Voraussetzungen](#️-voraussetzungen)
- [📦 Installation](#-installation)
- [🎮 Nutzung](#-nutzung)
- [❓ FAQ](#-faq)
- [🤝 Beitragen](#-beitragen)

---

## 🎯 Projektbeschreibung

Dieses Projekt erstellt **automatisch neue Konten** für die Plattform [mgx.dev](https://mgx.dev). Ein sichtbarer Chrome-Browser wird geöffnet, Temp-Mail-Adressen werden erzeugt, Verifizierungscodes ausgelesen und Cloudflare-Challenges werden durchlaufen. Die CLI steuert den gesamten Prozess und zeigt anschließend alle generierten Accounts tabellarisch an.

> 💡 **Hinweis:** Dieses Tool nutzt modernste Automatisierungstechnologien für einen reibungslosen, menschenähnlichen Workflow.

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔐 Automatische Verifizierung
- ✅ Temp-Mail-Integration
- ✅ Automatisches Auslesen von Codes
- ✅ Cloudflare Turnstile Bypass

</td>
<td width="50%">

### 🎨 Benutzerfreundliche CLI
- 📊 Farbcodierte Ausgaben
- 📈 Tabellarische Übersicht
- 🧹 Automatische Bereinigung

</td>
</tr>
<tr>
<td width="50%">

### 🌐 Browser-Automatisierung
- 🦾 Patchright-gesteuert
- 👁️ Sichtbarer Chrome-Browser
- 🤖 Menschenähnliches Verhalten

</td>
<td width="50%">

### 💾 Datenverwaltung
- 📝 Speicherung in `accounts.txt`
- 📸 Screenshot-Dokumentation
- 🔄 Fehlerprotokollierung

</td>
</tr>
</table>

---

## ⚙️ Voraussetzungen

Bevor du startest, stelle sicher, dass folgende Anforderungen erfüllt sind:

| Komponente | Anforderung | Status |
|------------|-------------|--------|
| 🖥️ **Betriebssystem** | Windows 10/11 mit PowerShell/CMD | ✅ |
| 🐍 **Python** | Version 3.11 oder neuer im `PATH` | ✅ |
| 🌐 **Browser** | Google Chrome (Standard-Installation) | ✅ |
| 🔌 **Netzwerk** | Zugriff auf `mgx.dev` und `temp-mail.org` | ✅ |

---

## 📦 Installation

### Schritt 1️⃣: Repository klonen oder entpacken

```bash
git clone <repository-url>
cd MGX.dev-Control-Center-Humanlike-MGX-Account-Automation
```

### Schritt 2️⃣: Umgebung einrichten

Führe die automatische Setup-Datei aus:

```cmd
setup_env.bat
```

> 🔧 **Was passiert dabei?**
> - Erstellt/aktualisiert den Ordner `env`
> - Installiert alle Pakete aus `requirements.txt`
> - Konfiguriert die Python-Umgebung

### Schritt 3️⃣: (Optional) Erste Testausführung

```cmd
start_cli.bat
```

> ℹ️ Das Skript ruft intern automatisch `setup_env.bat` auf, falls etwas fehlt.

---

## 🎮 Nutzung

### CLI starten

```cmd
start_cli.bat
```

### Menü-Optionen

<details>
<summary>📖 <b>Klicke hier für eine detaillierte Beschreibung der Optionen</b></summary>

<br>

| Option | Beschreibung | Icon |
|--------|--------------|------|
| **1** | 🆕 Neuen Account erstellen (inkl. E-Mail-Bestätigung, Turnstile usw.) | 🚀 |
| **2** | 📊 Sortierte Tabelle aus `accounts.txt` anzeigen | 📋 |
| **3** | 🧹 Ordner `bilder`/`errors` bereinigen | 🗑️ |
| **4** | ❌ Beenden (zeigt zuletzt noch einmal die Account-Tabelle) | 👋 |

</details>

### Farbcodierung der Ausgaben

```
🟢 Grün  = Erfolgreiche Aktionen
🟡 Gelb  = Hinweise und Warnungen
🔴 Rot   = Fehler mit verständlichen Meldungen
```

---

## ❓ FAQ

<details>
<summary><b>❌ Das Skript meldet, dass <code>requirements.txt</code> fehlt</b></summary>

<br>

**Lösung:** Stelle sicher, dass du die Datei nicht entfernt hast. Sie liegt im Projektwurzelverzeichnis und enthält alle benötigten Pakete.

```
MGX.dev-Control-Center-Humanlike-MGX-Account-Automation/
├── requirements.txt  ← Diese Datei muss vorhanden sein
├── setup_env.bat
└── ...
```

</details>

<details>
<summary><b>🐍 <code>setup_env.bat</code> findet Python nicht</b></summary>

<br>

**Lösung:**
1. Installiere Python 3.11+ von [python.org](https://www.python.org/downloads/)
2. Aktiviere beim Setup **"Add to PATH"**
3. Führe `setup_env.bat` erneut aus

**Überprüfen:**
```cmd
python --version
```

</details>

<details>
<summary><b>🌐 Chrome wird nicht gefunden oder startet nicht</b></summary>

<br>

**Lösung:**
- Installiere Google Chrome (64-bit, Standardpfad)
- Wenn du einen anderen Pfad verwendest, passe die Funktion `detect_chrome_executable()` in `main2.py` an

**Standard Chrome-Pfade:**
```
C:\Program Files\Google\Chrome\Application\chrome.exe
C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
```

</details>

---

## 🤝 Beitragen

Beiträge sind willkommen! Fühle dich frei, Issues zu erstellen oder Pull Requests einzureichen.

<div align="center">

### 🌟 Wenn dir dieses Projekt gefällt, gib ihm einen Stern!

---

**Entwickelt mit ❤️ für die MGX-Community**

</div>

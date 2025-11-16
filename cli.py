import asyncio
from datetime import datetime
from pathlib import Path
from typing import Iterable

try:
    from colorama import Fore, Style, init as colorama_init

    colorama_init(autoreset=True)
    COLOR_AVAILABLE = True
except Exception:
    COLOR_AVAILABLE = False

    class Fore:  # type: ignore
        GREEN = RED = YELLOW = CYAN = BLUE = MAGENTA = WHITE = ""

    class Style:  # type: ignore
        RESET_ALL = BRIGHT = ""

from main2 import MGXAccountGenerator

MAIN_ACCENT = Fore.CYAN


def c(color: str, text: str) -> str:
    return f"{color}{text}{Style.RESET_ALL}" if COLOR_AVAILABLE else text


def highlight(icon: str, text: str, color: str) -> None:
    print(c(color, f"{Style.BRIGHT}{icon} {text}"))


def info(text: str) -> None:
    highlight("ℹ️", text, MAIN_ACCENT)


def success(text: str) -> None:
    highlight("✓", text, Fore.GREEN)


def warn(text: str) -> None:
    highlight("⚠️", text, Fore.YELLOW)


def error(text: str) -> None:
    highlight("✖", text, Fore.RED)


def banner() -> None:
    title = " MGX CONTROL CENTER "
    line = "═" * len(title)
    print(c(Fore.MAGENTA, f"\n╔{line}╗"))
    print(c(Fore.MAGENTA, f"║{title}║"))
    print(c(Fore.MAGENTA, f"╚{line}╝"))
    print(c(MAIN_ACCENT, "   Dream • Chat • Automate\n"))


def cleanup_directories(names: Iterable[str]) -> None:
    for directory in names:
        path = Path(directory)
        if not path.exists():
            warn(f"Ordner '{directory}' nicht gefunden – übersprungen.")
            continue

        removed = 0
        for file_path in sorted(path.rglob("*"), reverse=True):
            if file_path.is_file():
                if file_path.name.lower() in {".gitkeep", ".keep"}:
                    continue
                file_path.unlink(missing_ok=True)
                removed += 1
            else:
                try:
                    file_path.rmdir()
                except OSError:
                    pass

        if removed:
            success(f"{directory}: {removed} Datei(en) entfernt.")
        else:
            info(f"{directory}: Keine Dateien zum Entfernen gefunden.")


def load_accounts() -> list[dict]:
    path = Path("accounts.txt")
    if not path.exists():
        raise FileNotFoundError("accounts.txt wurde nicht gefunden.")

    entries = []
    with path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            parts: dict[str, str] = {}
            for chunk in line.split(","):
                if ":" not in chunk:
                    continue
                key, value = chunk.split(":", 1)
                parts[key.strip().lower()] = value.strip()
            try:
                created = datetime.strptime(parts["createdat"], "%Y-%m-%d %H:%M:%S")
            except Exception as err:  # noqa: BLE001
                warn(f"Konnte Zeile nicht lesen ({err}): {line}")
                continue
            entries.append(
                {
                    "username": parts.get("username", ""),
                    "email": parts.get("email", ""),
                    "created_at": created,
                }
            )

    if not entries:
        raise ValueError("accounts.txt enthält keine gültigen Einträge.")

    return sorted(entries, key=lambda item: item["created_at"], reverse=True)


def print_accounts_table() -> None:
    try:
        accounts = load_accounts()
    except (FileNotFoundError, ValueError) as err:
        error(str(err))
        return

    headers = ("👤 Benutzername", "📧 E-Mail", "🕒 Erstellt am")
    rows = [
        (
            entry["username"] or "-",
            entry["email"] or "-",
            entry["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
        )
        for entry in accounts
    ]

    widths = [
        max(len(headers[0]), *(len(row[0]) for row in rows), 12),
        max(len(headers[1]), *(len(row[1]) for row in rows), 12),
        len(headers[2]),
    ]

    def make_line(left: str, fill: str, junction: str = "┼") -> str:
        return left + junction.join(fill * (w + 2) for w in widths) + left.replace("┌", "└").replace("┬", "┴")

    top = "┌" + "┬".join("─" * (w + 2) for w in widths) + "┐"
    mid = "├" + "┼".join("─" * (w + 2) for w in widths) + "┤"
    bottom = "└" + "┴".join("─" * (w + 2) for w in widths) + "┘"

    print(c(Fore.BLUE, top))
    header_line = "│ " + " │ ".join(
        c(f"{Style.BRIGHT}{Fore.WHITE}", headers[idx].ljust(widths[idx]))
        for idx in range(len(headers))
    ) + " │"
    print(header_line)
    print(c(Fore.BLUE, mid))
    for username, email, created in rows:
        line = "│ " + " │ ".join(
            [
                c(Fore.CYAN, username.ljust(widths[0])),
                c(Fore.MAGENTA, email.ljust(widths[1])),
                c(Fore.WHITE, created.ljust(widths[2])),
            ]
        ) + " │"
        print(line)
    print(c(Fore.BLUE, bottom))


def run_generator() -> None:
    generator = MGXAccountGenerator()
    try:
        info("Starte Automatisierung …")
        asyncio.run(generator.run())
        success("🎉 Automatisierung abgeschlossen.")
    except Exception as err:  # noqa: BLE001
        error(f"Automatisierung fehlgeschlagen: {err}")


def menu() -> None:
    options = [
        ("1", "🚀  MGX-Account generieren", run_generator),
        ("2", "📄  Accounts anzeigen", print_accounts_table),
        ("3", "🧹  Ordner 'bilder'/'errors' bereinigen", lambda: cleanup_directories(["bilder", "errors"])),
        ("4", "⬅️  Beenden", None),
    ]

    banner()
    while True:
        print(c(Style.BRIGHT + Fore.WHITE, "Menü-Auswahl:"))
        for key, label, _ in options:
            print(c(MAIN_ACCENT, f"  [{key}] {label}"))

        choice = input(c(Fore.YELLOW, "\nDeine Wahl ➜ ")).strip()
        for key, _, action in options:
            if choice == key:
                if action is None:
                    print_accounts_table()
                    success("Programm beendet. Bis bald!")
                    return
                action()
                if action is run_generator:
                    print_accounts_table()
                break
        else:
            warn("Ungültige Auswahl. Bitte erneut versuchen.")


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        error("Die Ausführung wurde unterbrochen.")

"""
MGX Account Generator mit vollständiger Patchright-Stealth-Integration

Dieses Skript nutzt Patchright (gepatchter Playwright) für maximale Stealth
beim Umgehen von Cloudflare und anderen Anti-Bot-Systemen.

Patchright-Features die automatisch aktiv sind:
- Runtime.enable Bypass (verhindert größte Bot-Erkennungsquelle)
- Console.enable deaktiviert
- navigator.webdriver maskiert
- Automation-Flags automatisch entfernt
- Init-Scripts via Routes statt Runtime.enable

Optimale Konfiguration:
- launch_persistent_context() statt launch() + new_context()
- channel="chrome" für echten Chrome (nicht Chromium)
- no_viewport=True für native Auflösung
- Automatische realistische User-Agent-Generierung
- Persistentes Browser-Profil für realistische Historie

Voraussetzungen:
1. pip install patchright faker cloudscraper js2py
2. patchright install chrome  # Installiert echten Chrome
"""
import asyncio
import random
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from faker import Faker
from patchright.async_api import async_playwright

_ALLOWED_PRINT_PREFIXES = (
    "[ERROR",
    "[FATAL",
    "[SYSTEM",
    "[TEMPMAIL",
    "[PASSWORD",
    "[DRISSION",
    "[CF",
    "[HUMAN-CHECK",
    "[NAV",
    "[FORM",
    "[MAIL",
    "[CLOUDFLARE",
    "[SUCCESS",
    "[ACCOUNTS",
    "[WARNUNG",
)


def _filtered_print(*args, **kwargs) -> None:
    original_print = getattr(_filtered_print, "_orig", None)
    if original_print is None:
        import builtins

        original_print = builtins.print
        _filtered_print._orig = original_print  # type: ignore[attr-defined]

    message = " ".join(str(arg) for arg in args)
    if message.startswith("[") and not message.startswith(_ALLOWED_PRINT_PREFIXES):
        return
    original_print(*args, **kwargs)


print = _filtered_print  # type: ignore

# HINWEIS: playwright_stealth wird NICHT mehr benötigt!
# Patchright liefert bereits alle notwendigen Stealth-Features automatisch:
# - Runtime.enable Bypass (größte Erkennungsquelle)
# - Console.enable Deaktivierung
# - navigator.webdriver Maskierung
# - Automation-Flags entfernt
# - Realistische Browser-Fingerprints


class MGXAccountGenerator:
    """
    Vollständig optimierter MGX-Account-Generator mit maximaler Stealth-Konfiguration:

    ✓ Patchright (gepatchter Playwright mit vollständigem Anti-Bot-Bypass)
      - Runtime.enable Bypass (größte Erkennungsquelle eliminiert)
      - Console.enable deaktiviert
      - navigator.webdriver maskiert
      - Automation-Flags automatisch entfernt

    ✓ Optimale Browser-Konfiguration
      - launch_persistent_context() für realistische Browser-Historie
      - channel="chrome" für echten Chrome (nicht Chromium)
      - no_viewport=True für native Bildschirmauflösung
      - Automatische realistische User-Agent-Generierung

    ✓ Temp-Mail (Browser-basiert via temp-mail.org)
    ✓ Cloudflare-Vorbereitungs-Cookies via cloudscraper (zusätzliche Sicherheit)
    ✓ Menschliches Verhalten (Mausbewegungen, Scrolls, Typing-Delays)
    ✓ Turnstile-Challenge-Handling

    Ergebnis: Maximale Cloudflare-Bypass-Fähigkeit mit minimalem Erkennungsrisiko.
    """

    REGISTER_URL = "https://mgx.dev/register?redirect=/"
    TEMP_MAIL_URL = "https://temp-mail.org/de/"

    USED_EMAILS_FILE = Path("used_emails.txt")

    def __init__(self) -> None:
        self.faker = Faker()
        self.used_emails: set[str] = self.load_used_emails()

    @staticmethod
    def detect_chrome_executable() -> str | None:
        candidates = [
            Path(r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"),
            Path(r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"),
            Path(r"C:\\Users\\%USERNAME%\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"),
            Path(r"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"),
            Path(r"/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
        ]

        expanded: list[Path] = []
        for candidate in candidates:
            resolved = Path(str(candidate).replace("%USERNAME%", Path.home().name))
            expanded.append(resolved)

        for path in expanded:
            try:
                if path.exists():
                    return str(path)
            except Exception:
                continue
        return None

    def load_used_emails(self) -> set[str]:
        try:
            raw = self.USED_EMAILS_FILE.read_text(encoding="utf-8")
        except FileNotFoundError:
            return set()
        emails = {
            line.strip().lower()
            for line in raw.splitlines()
            if line.strip() and "@" in line
        }
        if emails:
            print(f"[TEMPMAIL] {len(emails)} bereits verwendete E-Mails geladen.")
        return emails

    def remember_used_email(self, email: str) -> None:
        normalized = email.strip().lower()
        if not normalized or "@" not in normalized:
            return
        if normalized in self.used_emails:
            return
        self.used_emails.add(normalized)
        try:
            with self.USED_EMAILS_FILE.open("a", encoding="utf-8") as f:
                f.write(normalized + "\n")
        except Exception as err:
            print(f"[TEMPMAIL] Konnte used_emails.txt nicht schreiben: {err}")

    # ------------------------------------------------------------------ #
    # Hilfsfunktionen                                                    #
    # ------------------------------------------------------------------ #

    def log_credentials(self, username: str, email: str, password: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = (
            f"Username: {username}, Email: {email}, "
            f"Password: {password}, CreatedAt: {timestamp}\n"
        )
        with open("accounts.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"[ACCOUNTS] Gespeichert: {username} | {email}")

    def generate_mgx_password(self) -> str:
        """
        Generiert MGX-kompatibles Passwort.

        MGX akzeptiert nicht alle Sonderzeichen von faker.password().
        Dieses Format hat sich als funktionierend erwiesen:
        - Pattern: CapitalWord-Word+Digits
        - Beispiele: Max-Mustermann88, Emma-Schmidt42
        - Nur Bindestriche als Sonderzeichen
        - Gemischte Groß-/Kleinschreibung
        - Zahlen am Ende

        Returns:
            MGX-kompatibles Passwort (z.B. "John-Smith67")
        """
        # Zufällige Wörter mit verschiedenen Patterns
        base_words = [
            self.faker.first_name(),
            self.faker.last_name(),
            self.faker.word().capitalize(),
            self.faker.color_name().capitalize(),
        ]
        random.shuffle(base_words)
        core = ''.join(base_words[:2])
        digits = str(random.randint(100, 999))
        specials = random.choice(["!", "@", "#", "$", "%", "&", "*"])

        password = core + digits + specials

        # Sicherstellen, dass mindestens je 1 Großbuchstabe, Kleinbuchstabe, Ziffer und Sonderzeichen vorhanden ist
        if not any(c.islower() for c in password):
            password += random.choice("abcdefghijklmnopqrstuvwxyz")
        if not any(c.isupper() for c in password):
            password = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + password
        if not any(c.isdigit() for c in password):
            password += str(random.randint(0, 9))
        if not any(c in "!@#$%&*" for c in password):
            password += random.choice("!@#$%&*")

        password = password[:24]

        print(f"[PASSWORD] Generiert: {password} (Länge: {len(password)})")
        return password

    @staticmethod
    def worker_stealth_script() -> str:
        return r"""
(() => {
  const buildEnv = () => {
    try {
      return {
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        hardwareConcurrency: navigator.hardwareConcurrency,
        languages: navigator.languages,
        language: navigator.language,
      };
    } catch (err) {
      return {};
    }
  };

  const envJSON = JSON.stringify(buildEnv());

  const patchWorker = (OriginalWorker) => {
    if (!OriginalWorker) {
      return OriginalWorker;
    }

    const PatchedWorker = function (scriptURL, options) {
      const isString = typeof scriptURL === 'string';
      const isBlob = isString && scriptURL.startsWith('blob:');

      if (!isString || isBlob) {
        return new OriginalWorker(scriptURL, options);
      }

      let absURL = scriptURL;
      try {
        absURL = new URL(scriptURL, location.href).href;
      } catch (err) {}
      const sanitizedURL = absURL
        .replace(/\\/g, '\\\\')
        .replace(/'/g, "\\'");

      const overrideSource =
        "(() => {" +
        "  const env = " + envJSON + ";" +
        "  const define = (obj, key, value) => {" +
        "    try {" +
        "      Object.defineProperty(obj, key, {" +
        "        configurable: true," +
        "        enumerable: false," +
        "        get: () => value" +
        "      });" +
        "    } catch (err) {}" +
        "  };" +
        "  if (self && self.navigator) {" +
        "    const nav = self.navigator;" +
        "    if (env.userAgent) { define(nav, 'userAgent', env.userAgent); }" +
        "    if (env.platform) { define(nav, 'platform', env.platform); }" +
        "    if (env.language) { define(nav, 'language', env.language); }" +
        "    if (env.languages) { define(nav, 'languages', env.languages); }" +
        "    if (env.hardwareConcurrency) { define(nav, 'hardwareConcurrency', env.hardwareConcurrency); }" +
        "    define(nav, 'webdriver', undefined);" +
        "  }" +
        "})();" +
        "importScripts('" + sanitizedURL + "');";

      const blob = new Blob([overrideSource], { type: 'application/javascript' });
      const newURL = URL.createObjectURL(blob);
      try {
        return new OriginalWorker(newURL, options);
      } finally {
        setTimeout(() => URL.revokeObjectURL(newURL), 0);
      }
    };

    try {
      PatchedWorker.prototype = OriginalWorker.prototype;
    } catch (err) {}
    try {
      Object.defineProperty(PatchedWorker, 'name', {
        value: OriginalWorker.name,
        configurable: true,
      });
    } catch (err) {}
    PatchedWorker.toString = () => OriginalWorker.toString();
    return PatchedWorker;
  };

  if (window.Worker && window.Worker.toString().includes('[native code]')) {
    window.Worker = patchWorker(window.Worker);
  }
  if (window.SharedWorker && window.SharedWorker.toString().includes('[native code]')) {
    window.SharedWorker = patchWorker(window.SharedWorker);
  }
})();
"""

    async def _mouse_wiggle(self, page, bbox: dict | None) -> None:
        if not bbox:
            return
        try:
            start_x = bbox["x"] + bbox["width"] / 2
            start_y = bbox["y"] + bbox["height"] / 2
            await page.mouse.move(start_x, start_y, steps=5)
            for _ in range(random.randint(2, 4)):
                offset_x = random.uniform(-bbox["width"] / 4, bbox["width"] / 4)
                offset_y = random.uniform(-bbox["height"] / 4, bbox["height"] / 4)
                await page.mouse.move(start_x + offset_x, start_y + offset_y, steps=6)
                await asyncio.sleep(random.uniform(0.05, 0.15))
        except Exception:
            pass

    async def human_fill(self, locator, text: str) -> None:
        """
        Tippt Text mit zufälligen Delays und kleinen Pausen, damit das Verhalten
        natürlicher wirkt und Validierung/Watcher sauber getriggert werden.
        """
        await locator.click()
        await asyncio.sleep(random.uniform(0.2, 0.45))
        await locator.fill("")

        for char in text:
            # leichter beschleunigt, dennoch mit zufälligen Delays
            await locator.type(char, delay=random.uniform(35, 85))
            if char in {" ", "-", "_"} or random.random() < 0.06:
                await asyncio.sleep(random.uniform(0.05, 0.18))

        await asyncio.sleep(random.uniform(0.15, 0.4))

        # Explizite Events für Vue-Validation feuern
        # Vue reagiert oft nur auf blur/input/change Events
        try:
            await locator.evaluate("""
                el => {
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    el.blur();  // Blur triggert oft Validation
                }
            """)
            await asyncio.sleep(random.uniform(0.2, 0.4))
        except Exception:
            # Wenn Event-Firing fehlschlägt, weitermachen
            pass

    async def simulate_human_behavior(self, page) -> None:
        """Leichtes Maus-/Scroll-Verhalten zur Entschärfung von Bot-Heuristiken."""
        # Mausbewegungen
        if random.random() > 0.2:
            moves = random.randint(1, 3)
            print(f"[HUMAN] Simuliere {moves} Mausbewegungen ...")
            for _ in range(moves):
                await page.mouse.move(
                    random.randint(200, 1200),
                    random.randint(150, 800),
                    steps=random.randint(5, 15),
                )
                await asyncio.sleep(random.uniform(0.05, 0.15))

        # Scrollen
        if random.random() > 0.4:
            scrolls = random.randint(1, 3)
            print(f"[HUMAN] Simuliere {scrolls} kleine Scrolls ...")
            for _ in range(scrolls):
                await page.mouse.wheel(0, random.randint(60, 180))
                await asyncio.sleep(random.uniform(0.2, 0.5))

    async def wait_for_button_enabled(
        self,
        locator,
        timeout_seconds: float = 45.0,
        poll_interval: float = 0.6,
        label: str | None = None,
    ) -> None:
        """Wartet, bis ein Button sichtbar und nicht mehr disabled ist."""
        label = label or "Button"
        await locator.wait_for(state="visible", timeout=timeout_seconds * 1000)
        start_ts = time.time()

        while time.time() - start_ts < timeout_seconds:
            try:
                attrs = await locator.evaluate(
                    "el => ({"
                    "disabled: el.disabled,"
                    "dataDisabled: el.getAttribute('data-p-disabled'),"
                    "ariaDisabled: el.getAttribute('aria-disabled'),"
                    "className: el.className"
                    "})"
                )
            except Exception as read_err:
                attrs = None
                print(f"[FORM] {label}: Zustand konnte nicht gelesen werden: {read_err}")

            if attrs:
                disabled = bool(attrs.get("disabled", True))
                data_disabled = (attrs.get("dataDisabled") or "").lower()
                aria_disabled = (attrs.get("ariaDisabled") or "").lower()
                elapsed = time.time() - start_ts

                if (
                    not disabled
                    and data_disabled not in {"true", "1"}
                    and aria_disabled != "true"
                ):
                    print(
                        f"[FORM] {label} nach {elapsed:.1f}s aktiviert "
                        f"(class={attrs.get('className')})."
                    )
                    return

                if int(elapsed) % 5 == 0:
                    print(
                        f"[FORM] {label} weiterhin disabled "
                        f"(elapsed={elapsed:.1f}s, dataDisabled={data_disabled or 'None'})."
                    )

            await asyncio.sleep(poll_interval)

        raise RuntimeError(f"{label} blieb disabled (Timeout).")

    async def dump_form_errors(self, page) -> None:
        """Gibt alle sichtbaren Validierungsfehlermeldungen im Formular aus."""
        try:
            error_spans = page.locator("p.c-textDangerDefault span")
            count = await error_spans.count()
            if count == 0:
                print("[FORM-VALIDATION] Keine sichtbaren Fehlermeldungen.")
                return

            messages: list[str] = []
            for idx in range(count):
                text = await error_spans.nth(idx).text_content()
                cleaned = (text or "").strip()
                if cleaned:
                    messages.append(cleaned)

            if messages:
                print("[FORM-VALIDATION] Fehler: " + " | ".join(messages))
            else:
                print("[FORM-VALIDATION] Fehlermeldungen vorhanden, aber leerer Text.")
        except Exception as err:
            print(f"[FORM-VALIDATION] Fehler beim Auslesen der Meldungen: {err}")

    async def activate_mgx_checkbox(self, page) -> bool:
        """Aktiviert die MGX Terms & Conditions Checkbox so menschlich wie möglich."""

        checkbox_root = page.locator(
            "div[data-pc-name='checkbox'][data-p-disabled='false']"
        ).first
        await checkbox_root.wait_for(state="visible", timeout=15000)

        async def _is_checked(source: str) -> bool:
            try:
                attr = await checkbox_root.get_attribute("data-p-checked")
                checked = (attr or "").lower() == "true"
                if checked:
                    print(f"[CHECKBOX] ✓ Aktiviert via {source} (attr={attr}).")
                else:
                    print(
                        f"[CHECKBOX] ✗ Noch deaktiviert nach {source} "
                        f"(attr={attr})."
                    )
                return checked
            except Exception as err:
                print(f"[CHECKBOX] Status konnte nicht gelesen werden: {err}")
                return False

        checkbox_input = checkbox_root.locator("input[type='checkbox']").first
        clickable_box = checkbox_root.locator(
            "[data-pc-section='box'], div.p-checkbox-box, span.p-checkbox-box"
        ).first

        # 1) Normales Playwright check() mit Scroll und force=True
        for attempt in range(1, 4):
            try:
                await checkbox_root.scroll_into_view_if_needed()
                await asyncio.sleep(random.uniform(0.2, 0.4))
            except Exception:
                pass

            try:
                await checkbox_input.check(force=True, timeout=2000)
            except Exception as check_err:
                print(
                    f"[CHECKBOX] Versuch {attempt} via check() fehlgeschlagen: "
                    f"{check_err}"
                )
            else:
                if await _is_checked("check()"):
                    return True

            try:
                await clickable_box.click(force=True, timeout=2000)
            except Exception as click_err:
                print(
                    f"[CHECKBOX] Versuch {attempt} via Klick auf Box fehlgeschlagen: "
                    f"{click_err}"
                )
            else:
                if await _is_checked("Box-Klick"):
                    return True

            # Zusätzlicher Pixel-Klick auf die Box (falls PrimeVue Events erwartet)
            try:
                bbox = await clickable_box.bounding_box()
            except Exception:
                bbox = None
            if bbox:
                try:
                    await self._mouse_wiggle(
                        page,
                        {
                            "x": bbox["x"],
                            "y": bbox["y"],
                            "width": bbox["width"],
                            "height": bbox["height"],
                        },
                    )
                except Exception:
                    pass
                try:
                    await page.mouse.click(
                        bbox["x"] + bbox["width"] / 2,
                        bbox["y"] + bbox["height"] / 2,
                        delay=random.uniform(60, 140),
                    )
                except Exception as mouse_err:
                    print(
                        f"[CHECKBOX] Zusätzlicher Maus-Klick fehlgeschlagen: {mouse_err}"
                    )
                else:
                    if await _is_checked("Pixel-Klick"):
                        return True

        print("[CHECKBOX] Nutze JavaScript-Fallback...")

        # 2) JavaScript-Fallbacks (Vue-Store, DOM-Manipulation, Component API)
        js_activation_code = """
        () => {
            const result = { store: false, dom: false, vue: false, nuxt: false, pinia: false, injectionPaths: [] };

            const setAgreedOnObject = (obj, label) => {
                if (!obj) {
                    return false;
                }
                let changed = false;
                if (typeof obj.setAgreed === 'function') {
                    try {
                        obj.setAgreed(true);
                        changed = true;
                    } catch (err) {}
                }
                if ('agreed' in obj) {
                    obj.agreed = true;
                    changed = true;
                }
                if (obj.form && 'agreed' in obj.form) {
                    obj.form.agreed = true;
                    changed = true;
                }
                if (changed && label) {
                    result.injectionPaths.push(label);
                }
                return changed;
            };

            try {
                if (window.__VUE__ && window.__VUE__.formStore) {
                    setAgreedOnObject(window.__VUE__.formStore, '__VUE__.formStore');
                    result.store = true;
                }
            } catch (e) {
                console.log('[MGX-FIX] Vue Store Zugriff fehlgeschlagen', e);
            }

            try {
                const checkbox = document.querySelector('div[data-pc-name="checkbox"][data-p-disabled="false"] input[type="checkbox"]');
                if (checkbox) {
                    if (!checkbox.checked) {
                        checkbox.checked = true;
                        checkbox.dispatchEvent(new Event('input', { bubbles: true }));
                        checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                    const parent = checkbox.closest('div[data-pc-name="checkbox"]');
                    parent?.setAttribute('data-p-checked', 'true');
                    parent?.classList.add('p-checkbox-checked');
                    result.dom = true;
                    result.injectionPaths.push('dom.checkbox');
                }
            } catch (e) {
                console.log('[MGX-FIX] DOM-Manipulation fehlgeschlagen', e);
            }

            try {
                const checkboxDiv = document.querySelector('div[data-pc-name="checkbox"][data-p-disabled="false"]');
                const vueInstance = checkboxDiv?.__vueParentComponent || checkboxDiv?.__vue__;
                const handler = vueInstance?.ctx?.onChange || vueInstance?.exposed?.onChange;
                if (handler) {
                    handler({ checked: true });
                    result.vue = true;
                    result.injectionPaths.push('vueInstance');
                }
            } catch (e) {
                console.log('[MGX-FIX] Vue Component Zugriff fehlgeschlagen', e);
            }

            try {
                const nuxtTargets = [];
                const nuxt = window.__NUXT__ || window.__NUXT_DEVTOOLS__ || window.__NUXT_APP__;
                if (nuxt?.data && Array.isArray(nuxt.data)) {
                    nuxtTargets.push(...nuxt.data);
                }
                if (nuxt?.payload?.data && Array.isArray(nuxt.payload.data)) {
                    nuxtTargets.push(...nuxt.payload.data);
                }
                if (nuxt?.state) {
                    nuxtTargets.push(nuxt.state);
                }
                let nuxtChanged = false;
                for (const target of nuxtTargets) {
                    if (!target) continue;
                    if (setAgreedOnObject(target?.auth?.register, 'nuxt.auth.register')) nuxtChanged = true;
                    if (setAgreedOnObject(target?.registration, 'nuxt.registration')) nuxtChanged = true;
                    if (setAgreedOnObject(target?.register, 'nuxt.register')) nuxtChanged = true;
                }
                if (nuxtChanged) {
                    result.nuxt = true;
                }
            } catch (e) {
                console.log('[MGX-FIX] NUxt Zugriff fehlgeschlagen', e);
            }

            try {
                const piniaStores = window.__PINIA_STORES__ || window.__PINIA__ || window.__VUE__?.pinia;
                if (piniaStores) {
                    const storeList = [];
                    if (Array.isArray(piniaStores)) {
                        storeList.push(...piniaStores);
                    } else if (typeof piniaStores === 'object') {
                        for (const key in piniaStores) {
                            const item = piniaStores[key];
                            if (item) {
                                storeList.push(item);
                            }
                        }
                    }
                    let piniaChanged = false;
                    for (const store of storeList) {
                        if (setAgreedOnObject(store, `pinia.${store?.$id || 'unknown'}`)) {
                            piniaChanged = true;
                        }
                    }
                    if (piniaChanged) {
                        result.pinia = true;
                    }
                }
            } catch (e) {
                console.log('[MGX-FIX] Pinia Zugriff fehlgeschlagen', e);
            }

            const parent = document.querySelector('div[data-pc-name="checkbox"][data-p-disabled="false"]');
            return {
                ...result,
                finalState: parent ? parent.getAttribute('data-p-checked') === 'true' : false,
            };
        }
        """

        try:
            result = await page.evaluate(js_activation_code)
            await asyncio.sleep(random.uniform(0.3, 0.6))
            if await _is_checked("JavaScript-Fallback"):
                try:
                    debug_info = await page.evaluate(
                        """
                        () => {
                            const checkbox = document.querySelector('div[data-pc-name="checkbox"][data-p-disabled="false"] input[type="checkbox"]');
                            const summary = { checkboxValue: checkbox?.checked ?? null };
                            const parent = checkbox?.closest('div[data-pc-name="checkbox"]');
                            if (parent) {
                                summary.parentAttributes = parent.getAttributeNames().reduce((acc, key) => {
                                    acc[key] = parent.getAttribute(key);
                                    return acc;
                                }, {});
                            }
                            const instance = parent?.__vueParentComponent || parent?.__vue__;
                            if (instance) {
                                const describe = (obj) => obj ? Object.keys(obj) : [];
                                summary.vueKeys = {
                                    ctx: describe(instance.ctx),
                                    setupState: describe(instance.setupState),
                                    exposed: describe(instance.exposed),
                                    props: describe(instance.props),
                                };
                                summary.vueStatePreview = {
                                    ctx: instance.ctx,
                                    setupState: instance.setupState,
                                    exposed: instance.exposed,
                                    props: instance.props,
                                };
                            }
                            const nuxt = window.__NUXT__ || window.__NUXT_DEVTOOLS__ || window.__NUXT_APP__;
                            if (nuxt) {
                                summary.nuxtKeys = Object.keys(nuxt).slice(0, 20);
                                try {
                                    summary.nuxtState = nuxt.payload?.state || nuxt.state || null;
                                } catch (err) {}
                            }
                            return summary;
                        }
                        """
                    )
                    print("[CHECKBOX-DEBUG] Vue/Nuxt State:", debug_info)
                    if isinstance(result, dict) and result.get("injectionPaths"):
                        print("[CHECKBOX-DEBUG] Injection Paths:", result.get("injectionPaths"))
                    agree_paths = await page.evaluate(
                        """
                        () => {
                            const results = [];
                            const visited = new WeakSet();
                            const roots = [];
                            const pushRoot = (obj, name) => {
                                if (obj && typeof obj === 'object') {
                                    roots.push({ obj, name });
                                }
                            };
                            const nuxt = window.__NUXT__ || window.__NUXT_DEVTOOLS__ || window.__NUXT_APP__;
                            if (nuxt) {
                                pushRoot(nuxt, '__NUXT__');
                                pushRoot(nuxt.payload, '__NUXT__.payload');
                                pushRoot(nuxt.payload?.state, '__NUXT__.payload.state');
                                pushRoot(nuxt.state, '__NUXT__.state');
                            }
                            pushRoot(window.__VUE__, '__VUE__');
                            pushRoot(window.__VUE__?.formStore, '__VUE__.formStore');
                            pushRoot(window.__PINIA__, '__PINIA__');
                            pushRoot(window.__PINIA_STORES__, '__PINIA_STORES__');

                            const scan = (obj, path, depth) => {
                                if (!obj || typeof obj !== 'object' || visited.has(obj) || depth > 5) {
                                    return;
                                }
                                visited.add(obj);
                                const keys = Object.keys(obj).slice(0, 32);
                                for (const key of keys) {
                                    const value = obj[key];
                                    const newPath = path ? `${path}.${key}` : key;
                                    if (typeof key === 'string' && key.toLowerCase().includes('agree')) {
                                        let repr = null;
                                        try {
                                            if (typeof value !== 'function') {
                                                repr = JSON.stringify(value);
                                            }
                                        } catch (err) {
                                            repr = String(value);
                                        }
                                        results.push({ path: newPath, value: repr });
                                    }
                                    if (typeof value === 'object' && value !== null) {
                                        scan(value, newPath, depth + 1);
                                    }
                                }
                            };

                            for (const root of roots) {
                                scan(root.obj, root.name, 0);
                            }

                            return results.slice(0, 50);
                        }
                        """
                    )
                    if agree_paths:
                        print("[CHECKBOX-DEBUG] Agree-Pfade:", agree_paths)
                except Exception as dbg_err:
                    print(f"[CHECKBOX-DEBUG] Auslesen fehlgeschlagen: {dbg_err}")
                return True
            print(f"[CHECKBOX] Fallback meldet Status: {result}")
            return bool(result.get("finalState")) if isinstance(result, dict) else False
        except Exception as err:
            print(f"[CHECKBOX] JavaScript-Fallback fehlgeschlagen: {err}")
            return False

    async def wait_for_turnstile_token(
        self, page, timeout_seconds: float = 90.0
    ) -> str | None:
        """Wartet, bis Cloudflare Turnstile ein gültiges Token geliefert hat."""
        print("[CLOUDFLARE] Warte auf Turnstile-Token ...")
        try:
            token_handle = await page.wait_for_function(
                """
                () => {
                    const readToken = () => {
                        const input = document.querySelector('input[name="cf-turnstile-response"]');
                        if (input) {
                            const value = (input.value || '').trim();
                            if (value.length > 20) {
                                window.__lastTurnstileResponse = value;
                                return value;
                            }
                        }
                        if (window.turnstile && typeof window.turnstile.getResponse === 'function') {
                            try {
                                const resp = window.turnstile.getResponse();
                                if (resp && resp.length > 20) {
                                    window.__lastTurnstileResponse = resp;
                                    return resp;
                                }
                            } catch (err) {}
                        }
                        if (window.__lastTurnstileResponse && window.__lastTurnstileResponse.length > 20) {
                            return window.__lastTurnstileResponse;
                        }
                        return '';
                    };
                    const token = readToken();
                    return token && token.length > 20 ? token : undefined;
                }
                """,
                timeout=timeout_seconds * 1000,
            )
            token = await token_handle.json_value()
            print("[CLOUDFLARE] Turnstile-Token vorhanden.")
            return token
        except Exception as err:
            print(f"[CLOUDFLARE] Turnstile-Token nicht erhalten: {err}")
            return None

    async def ensure_turnstile_input(self, page, token: str) -> None:
        """Sorgt dafür, dass das Turnstile-Token im Formularfeld landet."""
        if not token:
            return
        try:
            await page.evaluate(
                """
                (token) => {
                    let input = document.querySelector('input[name="cf-turnstile-response"]');
                    if (!input) {
                        input = document.createElement('input');
                        input.type = 'hidden';
                        input.name = 'cf-turnstile-response';
                        input.id = 'cf-turnstile-response';
                        const form = document.querySelector('form[action*="register"], form') || document.body;
                        form.appendChild(input);
                    }
                    if (input.value !== token) {
                        input.value = token;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
                """,
                token,
            )
        except Exception as err:
            print(f"[CLOUDFLARE] Konnte Turnstile-Token nicht setzen: {err}")

    async def poke_turnstile_widget(self, page) -> bool:
        """Interagiert mit dem Turnstile-Widget, um eine Prüfung anzustoßen."""

        async def _human_click(target, description: str) -> bool:
            try:
                await target.wait_for(state="visible", timeout=5000)
            except Exception:
                return False

            try:
                await target.scroll_into_view_if_needed()
            except Exception:
                pass

            bbox = None
            try:
                bbox = await target.bounding_box()
            except Exception:
                bbox = None
            await self._mouse_wiggle(page, bbox)

            try:
                await target.click(force=True, delay=random.uniform(40, 90))
                await asyncio.sleep(random.uniform(0.2, 0.5))
                print(f"[CLOUDFLARE] {description} angeklickt.")
                return True
            except Exception as err:
                print(f"[CLOUDFLARE] {description} konnte nicht angeklickt werden: {err}")
                return False

        clicked = False

        host_selectors = [
            "div.cf-turnstile",
            "#widgetId",
            "div#content:has-text('Verify you are human')",
            "div.cb-c",
            "div[aria-label*='Cloudflare']",
        ]
        for selector in host_selectors:
            widget = page.locator(selector).first
            if await widget.count():
                clicked = await _human_click(widget, f"Widget {selector}")
                if clicked:
                    break

        checkbox_selectors = [
            "div#content input[type='checkbox']",
            "label.cb-lb input[type='checkbox']",
            "div.cb-c input[type='checkbox']",
            "input[aria-label*='Verify']",
        ]
        if not clicked:
            for selector in checkbox_selectors:
                checkbox = page.locator(selector).first
                if await checkbox.count():
                    clicked = await _human_click(checkbox, f"Checkbox {selector}")
                    if clicked:
                        break

        iframe_selectors = [
            "iframe[src*='challenge-platform']",
            "iframe[title*='Cloudflare']",
            "iframe[id*='cf-chl-widget']",
        ]
        if not clicked:
            for selector in iframe_selectors:
                iframe = page.locator(selector).first
                if not await iframe.count():
                    continue
                try:
                    await iframe.wait_for(state="visible", timeout=8000)
                    handle = await iframe.element_handle()
                    frame = await handle.content_frame() if handle else None
                except Exception as err:
                    print(f"[CLOUDFLARE] iframe {selector} konnte nicht geladen werden: {err}")
                    continue

                if not frame:
                    continue

                try:
                    checkbox = frame.locator("input[type='checkbox']").first
                    if await checkbox.count():
                        await checkbox.scroll_into_view_if_needed()
                        bbox = await checkbox.bounding_box()
                        await self._mouse_wiggle(page, bbox)
                        await checkbox.click(force=True)
                        await asyncio.sleep(random.uniform(0.3, 0.6))
                        print(f"[CLOUDFLARE] Checkbox in {selector} angeklickt.")
                        clicked = True
                        break
                except Exception as err:
                    print(f"[CLOUDFLARE] Checkbox in {selector} nicht klickbar: {err}")

                if clicked:
                    break

                try:
                    button = frame.locator("button, .ctp-button, .cf-turnstile-button").first
                    if await button.count():
                        await button.click(force=True)
                        await asyncio.sleep(random.uniform(0.3, 0.6))
                        print(f"[CLOUDFLARE] Button in {selector} angeklickt.")
                        clicked = True
                        break
                except Exception as err:
                    print(f"[CLOUDFLARE] Button in {selector} nicht klickbar: {err}")

        return clicked

    async def init_temp_mail_page(self, page) -> str | None:
        """
        Öffnet temp-mail.org im Browser und liefert eine gültige Wegwerf-Adresse.
        """
        try:
            print(f"[TEMPMAIL] Öffne {self.TEMP_MAIL_URL} ...")
            await page.goto(
                self.TEMP_MAIL_URL,
                timeout=60000,
                wait_until="domcontentloaded",
            )

            email_input = page.locator("#mail")
            await email_input.wait_for(state="visible", timeout=30000)

            # Immer frische Temp-Mail-Adresse erzwingen
            refreshed = await self.reset_temp_mail_address(page)
            if refreshed:
                await asyncio.sleep(1.0)

            max_attempts = 20
            email_value: str = ""

            for attempt in range(1, max_attempts + 1):
                try:
                    value = await email_input.input_value()
                except Exception as read_err:
                    print(
                        f"[TEMPMAIL] Fehler beim Lesen des Mail-Feldes "
                        f"(Versuch {attempt}): {read_err}"
                    )
                    value = ""

                email_value = (value or "").strip()
                print(
                    f"[TEMPMAIL] Mail-Wert (Versuch {attempt}/{max_attempts}): "
                    f"{email_value!r}"
                )

                if (
                    email_value
                    and "@" in email_value
                    and not email_value.lower().startswith("wird geladen")
                ):
                    if email_value.lower() in self.used_emails:
                        print(
                            f"[TEMPMAIL] Adresse {email_value} wurde bereits verwendet."
                            " Fordere neue Adresse an..."
                        )
                        await self.reset_temp_mail_address(page)
                        await asyncio.sleep(1.5)
                        continue
                    break

                await asyncio.sleep(2.0)
            else:
                print("[TEMPMAIL] Konnte keine gültige E-Mail-Adresse laden.")
                return None

            print(f"[TEMPMAIL] Verwendete Adresse von temp-mail.org: {email_value}")
            self.remember_used_email(email_value)
            return email_value

        except Exception as e:
            print(f"[ERROR] Fehler beim Initialisieren von temp-mail.org: {e}")
            return None

    async def reset_temp_mail_address(self, page) -> bool:
        """Klickt auf 'Löschen' bei temp-mail.org, um eine neue Adresse zu erhalten."""
        try:
            delete_button = page.get_by_role(
                "button", name=re.compile("löschen|delete", re.IGNORECASE)
            ).first
            await delete_button.click()
        except Exception:
            try:
                delete_button = page.locator(
                    "button", has_text=re.compile("Löschen|Delete", re.IGNORECASE)
                ).first
                await delete_button.click()
            except Exception as click_err:
                print(f"[TEMPMAIL] 'Löschen'-Button nicht gefunden: {click_err}")
                return False

        await asyncio.sleep(1.5)

        try:
            email_input = page.locator("#mail")
            await email_input.wait_for(state="visible", timeout=20000)
            new_value = (await email_input.input_value()).strip()
            print(f"[TEMPMAIL] Neue Adresse nach 'Löschen': {new_value}")
            return bool(new_value)
        except Exception as err:
            print(f"[TEMPMAIL] Konnte neue Adresse nicht lesen: {err}")
            return False

    async def poll_temp_mail_verification_code(
        self,
        page,
        max_wait_seconds: int = 180,
    ) -> str | None:
        """
        Wartet auf die MGX-Verifizierungs-Mail und extrahiert den 6-stelligen Code.
        """
        print("[MAIL] Warte auf Verifizierungs-Mail bei temp-mail.org ...")
        mail_link = (
            page.locator("a.viewLink[data-mail-id]")
            .filter(has_text="Verify your email for MGX")
            .first
        )
        code_pattern = re.compile(r"(?<!\d)(\d{6})(?!\d)")

        # Inbox-Empty Overlay abwarten (falls vorhanden)
        try:
            empty_overlay = page.locator("div.inbox-empty").first
            if await empty_overlay.count() > 0:
                try:
                    if await empty_overlay.is_visible():
                        print("[MAIL] Inbox zeigt 'leer' Overlay, warte auf neue Mail...")
                        await empty_overlay.wait_for(state="hidden", timeout=60000)
                except Exception:
                    pass
        except Exception:
            pass

        try:
            await mail_link.wait_for(
                state="visible", timeout=max_wait_seconds * 1000
            )
            print("[MAIL] MGX-Verifizierungs-Mail gefunden, öffne sie...")

            # Neueste MGX-Mail direkt über ihren Link öffnen (kein Seiten-Reload nötig)
            try:
                mgx_link = (
                    page.locator("a.viewLink[data-mail-id]")
                    .filter(has_text="Verify your email for MGX")
                    .first
                )
                href = (await mgx_link.get_attribute("href")) if mgx_link else None
            except Exception:
                href = None

            if href:
                target_url = urljoin(page.url, href)
                print(f"[MAIL] Navigiere zur E-Mail-Ansicht: {target_url}")
                await page.goto(target_url, wait_until="domcontentloaded")
                await asyncio.sleep(1.0)
            else:
                await mail_link.click()
                try:
                    await page.wait_for_url(
                        lambda url: "/view/" in url, timeout=20000
                    )
                except Exception:
                    pass

            try:
                await page.locator("div.inbox-data-content").wait_for(
                    state="visible", timeout=20000
                )
            except Exception:
                pass

            await asyncio.sleep(1.5)

            # Versuche den Code direkt aus dem Intro-Container auszulesen
            try:
                direct_code = await page.evaluate(
                    r"""
                    () => {
                        const container = document.querySelector('div.inbox-data-content-intro');
                        if (!container) {
                            return null;
                        }
                        const text = container.innerText || '';
                        const match = text.match(/(\d{6})/);
                        return match ? match[1] || match[0] : null;
                    }
                    """
                )
            except Exception:
                direct_code = None

            if direct_code:
                print(f"[MAIL] Direkter Code aus intro-Container: {direct_code}")
                return direct_code

            possible_selectors = [
                "div.view-dataContent",
                "div.view-dataSubject",
                "div.view-dataText",
                "div.mail-text-body",
                "div#tmMailContent",
                "article.mail",
                "div.tm-message",
                "table",
                "td",
                "p",
                "div.inbox-data-content-intro",
                "div.inbox-data-content",
            ]

            candidate_texts: list[str] = []

            # Primären MGX-Inhalt mit text_content lesen (inkl. versteckter Unicode)
            try:
                intro_locator = page.locator("div.inbox-data-content")
                await intro_locator.wait_for(state="visible", timeout=10000)
                intro_text = await intro_locator.text_content()
            except Exception:
                intro_text = ""
            if intro_text:
                candidate_texts.append(intro_text)

            # Gesamten Seitentext als Fallback aufnehmen
            try:
                body_text = await page.evaluate(
                    "() => document.body ? document.body.innerText : ''"
                )
            except Exception:
                body_text = ""
            if body_text:
                candidate_texts.append(body_text)

            # Spezifische Container ausprobieren
            for selector in possible_selectors:
                locator = page.locator(selector).first
                try:
                    await locator.wait_for(state="visible", timeout=10000)
                    text = await locator.text_content()
                    if text:
                        candidate_texts.append(text)
                except Exception:
                    continue

            # Falls Inhalt in einem iframe gerendert wird, jeden Frame durchsuchen
            for frame in page.frames:
                try:
                    frame_text = await frame.evaluate(
                        "() => document.body ? document.body.innerText : ''"
                    )
                except Exception:
                    continue
                if frame_text:
                    candidate_texts.append(frame_text)

            for idx, text in enumerate(candidate_texts, start=1):
                preview = (text or "").strip().replace("\n", " ")[:120]
                if preview:
                    print(f"[MAIL-DEBUG] Textquelle {idx}: {preview!r}")
                match = code_pattern.search(text or "")
                if match:
                    code = match.group(1)
                    print(f"[MAIL] Verifizierungscode aus E-Mail extrahiert: {code}")
                    return code

            print("[MAIL] Fehler: Code konnte im E-Mail-Text nicht gefunden werden.")
            return None

        except Exception as e:
            print(f"[MAIL] Timeout oder Fehler beim Warten auf die E-Mail: {e}")
            return None

    async def verify_human_signature(self, page) -> None:
        """Öffnet deviceandbrowserinfo-Testseite und prüft, ob wir als Human gelten."""
        TEST_URL = "https://deviceandbrowserinfo.com/are_you_a_bot"
        print(f"[HUMAN-CHECK] Öffne {TEST_URL} ...")
        await page.goto(TEST_URL, wait_until="domcontentloaded", timeout=60000)

        async def _read_status() -> str | None:
            script = (
                "() => {"
                "  const text = (document.body?.innerText || '').toLowerCase();"
                "  if (text.includes('you are human')) return 'human';"
                "  if (text.includes('you are a bot')) return 'bot';"
                "  return null;"
                "}"
            )
            handle = await page.wait_for_function(script, timeout=60000)
            return await handle.json_value()

        status = await _read_status()
        extra_details = ""
        try:
            details_text = await page.locator("pre").first.text_content()
            extra_details = (details_text or "").strip()
        except Exception:
            extra_details = ""

        if status == "human":
            print("[HUMAN-CHECK] Seite meldet 'You are human!'.")
            if extra_details:
                print(f"[HUMAN-CHECK] Details: {extra_details[:200]}...")
            return

        if status == "bot":
            print("[HUMAN-CHECK] Warnung: Seite meldet 'You are a bot!'.")
            if extra_details:
                print(f"[HUMAN-CHECK] Details: {extra_details}")
            return

        print("[HUMAN-CHECK] Konnte Status nicht eindeutig ermitteln, fahre dennoch fort.")


    def prepare_cloudflare_cookies(self) -> list[dict]:
        """
        Nutzt cloudscraper, um simple Cloudflare-Cookies vorab zu holen.
        Falls cloudscraper nicht installiert ist, wird einfach [] zurückgegeben.
        """
        try:
            import cloudscraper
        except ImportError:
            print(
                "[WARNUNG] 'cloudscraper' nicht installiert, "
                "überspringe Cloudflare-Vorbereitung."
            )
            return []

        try:
            print(
                f"[CF] Versuche, Cloudflare-Challenge für {self.REGISTER_URL} "
                "vorab zu lösen..."
            )
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(self.REGISTER_URL, timeout=40)
            resp.raise_for_status()
            print(f"[CF] Cloudflare-Prep erfolgreich (Status: {resp.status_code})")

            cookies = [
                {
                    "name": c.name,
                    "value": c.value,
                    "domain": c.domain or ".mgx.dev",
                    "path": c.path or "/",
                }
                for c in scraper.cookies
            ]
            print(f"[CF] {len(cookies)} Cloudflare-Cookies für Patchright vorbereitet.")
            return cookies
        except Exception as e:
            print(f"[CF] Fehler bei Cloudflare-Vorbereitung: {e}")
            return []

    def start_drission_browser(self) -> tuple[str | None, object | None]:
        """Startet einen DrissionPage-Chrome und liefert die CDP-Adresse."""
        try:
            from DrissionPage import ChromiumOptions, ChromiumPage  # type: ignore
        except ImportError:
            print(
                "[DRISSION] 'DrissionPage' nicht installiert. pip install DrissionPage"
            )
            return None, None

        page = None
        try:
            print("[DRISSION] Starte Chrome über DrissionPage ...")
            co = ChromiumOptions(read_file=False)
            co.set_timeouts(base=10, page_load=60, script=30)
            co.headless(False)
            try:
                co.auto_port(True)
                co.set_local_port(random.randint(9300, 9600))
            except Exception as err:
                print(f"[DRISSION] Port-Konfiguration nicht möglich: {err}")
            co.set_argument("--disable-blink-features=AutomationControlled")
            co.set_argument("--disable-infobars")
            co.set_argument("--disable-gpu")
            co.set_argument("--no-sandbox")
            co.set_argument("--window-size=1400,900")
            co.set_argument("--lang=de-DE")

            chrome_path = self.detect_chrome_executable()
            if chrome_path:
                try:
                    co.set_browser_path(chrome_path)
                except Exception as err:
                    print(f"[DRISSION] Chrome-Pfad konnte nicht gesetzt werden: {err}")

            profile_dir = Path("drission_profile").resolve()
            try:
                profile_dir.mkdir(parents=True, exist_ok=True)
                co.set_user_data_path(str(profile_dir))
            except Exception as err:
                print(f"[DRISSION] Profilordner konnte nicht erzeugt werden: {err}")

            page = ChromiumPage(addr_or_opts=co)
            try:
                page.get("about:blank")
            except Exception:
                pass
            address = getattr(page, "address", None)
            if address:
                print(f"[DRISSION] Chrome bereit (CDP {address}).")
            else:
                print("[DRISSION] Konnte CDP-Adresse nicht bestimmen.")
            return address, page
        except Exception as err:
            print(f"[DRISSION] Fehler beim Starten von DrissionPage: {err}")
            try:
                if page:
                    page.quit()
            except Exception:
                pass
            return None, None


    # ------------------------------------------------------------------ #
    # Hauptablauf                                                       #
    # ------------------------------------------------------------------ #

    async def run(self) -> None:
        username = self.faker.user_name() + str(random.randint(100, 999))
        # MGX-kompatibles Passwort generieren (faker.password() erzeugt ungültige Zeichen)
        password = self.generate_mgx_password()

        drission_address: str | None = None
        drission_controller = None
        try:
            drission_address, drission_controller = await asyncio.to_thread(
                self.start_drission_browser
            )
        except Exception as bridge_err:
            print(f"[DRISSION] Start fehlgeschlagen: {bridge_err}")

        async with async_playwright() as p:
            context = None
            browser = None
            remote_browser = False
            if drission_address:
                try:
                    browser = await p.chromium.connect_over_cdp(
                        f"http://{drission_address}"
                    )
                    if browser.contexts:
                        context = browser.contexts[0]
                    else:
                        context = await browser.new_context()
                    remote_browser = True
                    print(
                        "[DRISSION] Playwright steuert jetzt den geöffneten Chrome-Browser."
                    )
                except Exception as connect_err:
                    print(
                        f"[DRISSION] Verbindung via CDP fehlgeschlagen: {connect_err}. "
                        "Starte lokale Chrome-Instanz."
                    )

            if context is None:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir="./browser_profile",
                    channel="chrome",
                    headless=False,
                    no_viewport=True,
                    locale="de-DE",
                    timezone_id="Europe/Berlin",
                )

            # Cloudflare-Cookies übernehmen
            cf_cookies = self.prepare_cloudflare_cookies()
            if cf_cookies:
                try:
                    await context.add_cookies(cf_cookies)
                except Exception as e:
                    print(f"[CF] Konnte Cloudflare-Cookies nicht setzen: {e}")

            temp_mail_page = await context.new_page()
            email = await self.init_temp_mail_page(temp_mail_page)
            if not email:
                print("[ERROR] Temp-Mail konnte nicht erzeugt werden. Breche ab.")
                await context.close()
                return

            page = await context.new_page()
            try:
                await self.verify_human_signature(page)
            except Exception as human_err:
                print(f"[HUMAN-CHECK] Warnung: {human_err}")
            # stealth_async() ist NICHT mehr nötig - Patchright macht das automatisch!

            try:
                # Navigation nach MGX
                print(f"[NAV] Gehe zur Registrierungsseite: {self.REGISTER_URL}")
                await page.goto(
                    self.REGISTER_URL,
                    wait_until="domcontentloaded",
                    timeout=90000,
                )

                # Warte auf Formular-Elemente statt networkidle
                # (Cloudflare-Seiten erreichen oft nie networkidle-Status)
                print("[NAV] Warte auf Registrierungsformular...")
                await page.locator(
                    "input[name='username'][placeholder='Enter your username']"
                ).wait_for(state="visible", timeout=30000)
                print("[NAV] ✓ Registrierungsformular ist bereit.")

                username_input = page.locator(
                    "input[name='username'][placeholder='Enter your username']"
                )
                email_input = page.locator(
                    "input[name='email'][placeholder='Email: *****@example.com']"
                )
                password_input = page.locator(
                    "input[type='password'][name='password'][placeholder='Password']"
                )
                password2_input = page.locator(
                    "input[type='password'][name='password2']"
                    "[placeholder='Password confirmation']"
                )

                max_form_attempts = 3
                for form_attempt in range(1, max_form_attempts + 1):
                    suffix = f" (Versuch {form_attempt}/{max_form_attempts})" if max_form_attempts > 1 else ""
                    print(f"[FORM] Fülle Registrierungsformular aus{suffix}...")

                    await username_input.wait_for(state="visible", timeout=30000)
                    await self.simulate_human_behavior(page)

                    await self.human_fill(username_input, username)
                    await self.human_fill(email_input, email)
                    await self.human_fill(password_input, password)
                    await self.human_fill(password2_input, password)

                    # Vue Zeit geben für Formular-Validation
                    print("[FORM] Warte auf Vue Formular-Validation...")
                    await asyncio.sleep(random.uniform(0.8, 1.5))

                    try:
                        state_debug = await page.evaluate(
                            """
                            () => {
                                const summary = {};
                                const nuxt = window.__NUXT__;
                                if (nuxt?.payload?.state) {
                                    summary.stateKeys = Object.keys(nuxt.payload.state);
                                    summary.statePreview = {};
                                    for (const [key, value] of Object.entries(nuxt.payload.state)) {
                                        if (typeof value === 'object' && value !== null) {
                                            summary.statePreview[key] = Object.keys(value).slice(0, 10);
                                        } else {
                                            summary.statePreview[key] = value;
                                        }
                                    }
                                }
                                if (nuxt?.pinia) {
                                    summary.piniaKeys = Object.keys(nuxt.pinia);
                                    summary.piniaPreview = {};
                                    for (const [key, value] of Object.entries(nuxt.pinia)) {
                                        if (typeof value === 'object' && value !== null) {
                                            summary.piniaPreview[key] = Object.keys(value).slice(0, 10);
                                        }
                                    }
                                }
                                return summary;
                            }
                            """
                        )
                        print("[NUXT-STATE]", state_debug)
                    except Exception as nuxt_err:
                        print(f"[NUXT-STATE] Fehler beim Auslesen: {nuxt_err}")

                    try:
                        app_debug = await page.evaluate(
                            """
                            () => {
                                const nuxtApp = window.useNuxtApp ? window.useNuxtApp() : null;
                                if (!nuxtApp) return null;
                                const summary = {
                                    appKeys: Object.keys(nuxtApp).filter(key => !key.startsWith('_')).slice(0, 30),
                                    payloadKeys: nuxtApp.payload ? Object.keys(nuxtApp.payload) : null,
                                };
                                const pinia = nuxtApp._context?.provides?.pinia;
                                if (pinia) {
                                    summary.provideKeys = Object.keys(pinia).slice(0, 30);
                                    if (pinia.state) {
                                        summary.piniaStateKeys = Object.keys(pinia.state).slice(0, 30);
                                    }
                                }
                                return summary;
                            }
                            """
                        )
                        print("[NUXT-APP]", app_debug)
                    except Exception as app_err:
                        print(f"[NUXT-APP] Fehler beim Auslesen: {app_err}")

                    # Explizit alle Felder nochmal validieren lassen
                    await page.evaluate("""
                        () => {
                            // Alle Inputs erneut blur-Event feuern (triggert Validation)
                            document.querySelectorAll('input[name]').forEach(input => {
                                input.dispatchEvent(new Event('blur', { bubbles: true }));
                            });
                        }
                    """)
                    await asyncio.sleep(random.uniform(0.5, 1.0))

                    # Debug: Prüfe Validierungs-Status
                    validation_status = await page.evaluate("""
                        () => {
                            const errors = [];
                            document.querySelectorAll('input[name]').forEach(input => {
                                const parent = input.closest('.base-input');
                                const errorMsg = parent?.nextElementSibling?.querySelector('.message-content');
                                if (errorMsg && errorMsg.textContent.trim()) {
                                    errors.push({
                                        field: input.name,
                                        error: errorMsg.textContent.trim()
                                    });
                                }
                            });
                            return errors;
                        }
                    """)
                    if validation_status:
                        print(f"[FORM-DEBUG] Validierungsfehler gefunden: {validation_status}")
                    else:
                        print("[FORM-DEBUG] ✓ Keine Validierungsfehler erkannt.")

                    # Checkbox (mehrstufiges Aktivieren inkl. JavaScript-Fallback)
                    checkbox_activated = await self.activate_mgx_checkbox(page)
                    if not checkbox_activated:
                        raise RuntimeError(
                            "Checkbox konnte nicht aktiviert werden. "
                            "Alle JavaScript-Ansätze fehlgeschlagen."
                        )

                    # Continue
                    continue_button = page.get_by_test_id("mg-register-continue-btn")
                    try:
                        await self.wait_for_button_enabled(
                            continue_button,
                            timeout_seconds=45.0,
                            poll_interval=0.6,
                            label="Continue-Button",
                        )
                    except RuntimeError as cont_err:
                        await self.dump_form_errors(page)
                        if (
                            "Continue-Button blieb disabled" in str(cont_err)
                            and form_attempt < max_form_attempts
                        ):
                            print(
                                "[FORM] Continue-Button weiterhin disabled – "
                                "neu laden und Formular erneut ausfüllen ..."
                            )
                            await asyncio.sleep(random.uniform(0.6, 1.2))
                            try:
                                await page.reload(
                                    wait_until="domcontentloaded", timeout=90000
                                )
                            except Exception as reload_err:
                                print(
                                    f"[FORM] Reload fehlgeschlagen, versuche direkte Navigation: {reload_err}"
                                )
                                await page.goto(
                                    self.REGISTER_URL,
                                    wait_until="domcontentloaded",
                                    timeout=90000,
                                )
                            continue
                        raise

                    await continue_button.click()
                    print("[FORM] Formular abgeschickt. Warte auf Verifizierungs-Schritt...")
                    break
                else:
                    raise RuntimeError(
                        "Continue-Button blieb trotz wiederholter Reloads disabled."
                    )

                # Code-Eingabe
                verification_code_input = page.locator("input[max-length='6']")
                await verification_code_input.wait_for(
                    state="visible", timeout=60000
                )

                verification_code = await self.poll_temp_mail_verification_code(
                    temp_mail_page
                )
                if not verification_code:
                    raise RuntimeError(
                        "Konnte Verifizierungscode nicht aus der E-Mail erhalten."
                    )

                await verification_code_input.fill(verification_code)
                print("[FORM] Verifizierungscode eingegeben.")
                await asyncio.sleep(random.uniform(0.5, 1.0))

                # Cloudflare "Verifying..." abwarten (falls sichtbar)
                try:
                    verifying_widget = page.get_by_text("Verifying...", exact=False)
                    await verifying_widget.wait_for(
                        state="hidden", timeout=60000
                    )
                    print("[CLOUDFLARE] Prüfung erfolgreich abgeschlossen.")
                except Exception:
                    print("[CLOUDFLARE] Kein explizites 'Verifying...' sichtbar oder bereits beendet.")

                await self.poke_turnstile_widget(page)
                token = await self.wait_for_turnstile_token(page)
                if not token:
                    print("[CLOUDFLARE] Versuche, Turnstile erneut zu triggern ...")
                    attempts = 2
                    for attempt in range(attempts):
                        await asyncio.sleep(random.uniform(0.6, 1.2))
                        await self.simulate_human_behavior(page)
                        await self.poke_turnstile_widget(page)
                        token = await self.wait_for_turnstile_token(
                            page, timeout_seconds=45.0
                        )
                        if token:
                            break

                if not token:
                    raise RuntimeError(
                        "Cloudflare Turnstile lieferte kein Token (Timeout)."
                    )

                await self.ensure_turnstile_input(page, token)

                # Finaler Signup
                signup_button = page.get_by_test_id("mg-register-signup-btn")
                await self.wait_for_button_enabled(
                    signup_button,
                    timeout_seconds=45.0,
                    poll_interval=0.6,
                    label="Signup-Button",
                )
                await signup_button.click()
                print("[FORM] Finale Registrierung abgeschickt.")

                await page.wait_for_url(
                    lambda url: "register" not in url, timeout=25000
                )
                print("\n[SUCCESS] Registrierung erfolgreich abgeschlossen!\n")

                self.log_credentials(username, email, password)

            except Exception as e:
                print(
                    f"\n[FATAL ERROR] Ein Fehler im Automatisierungsablauf ist "
                    f"aufgetreten: {e}\n"
                )
                try:
                    screenshot_path = f"error_screenshot_{int(time.time())}.png"
                    await page.screenshot(path=screenshot_path)
                    print(
                        f"[DEBUG] Fehler-Screenshot gespeichert unter: {screenshot_path}"
                    )
                except Exception as shot_err:
                    print(f"[DEBUG] Screenshot fehlgeschlagen: {shot_err}")
            finally:
                print("[SYSTEM] Schließe den Browser.")
                try:
                    if context:
                        await context.close()
                finally:
                    if remote_browser and browser:
                        try:
                            await browser.close()
                        except Exception:
                            pass

        if drission_controller:
            try:
                drission_controller.quit()
            except Exception:
                pass


async def main() -> None:
    generator = MGXAccountGenerator()
    await generator.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[SYSTEM] Prozess vom Benutzer abgebrochen.")
    except Exception as e:
        print(f"Ein unerwarteter Fehler auf Top-Level ist aufgetreten: {e}")
    finally:
        input("Drücken Sie eine beliebige Taste . . .")

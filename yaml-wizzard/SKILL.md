---
name: yaml-wizzard
description: |
  Creates, validates, explains, and debugs Home Assistant automations in YAML.
  Generates valid HA YAML from natural language descriptions, validates structure
  with a Python script, explains existing automations in plain language, and
  debugs broken configs. ALWAYS use when: creating HA automations, debugging
  YAML, explaining automations, or anything involving triggers/conditions/actions
  in a smart home context. Trigger on: "Home Assistant Automation", "HA Automation",
  "HASS Automation", "automations.yaml", "Automation erstellen", "create automation",
  "Licht geht an wenn", "Wenn Bewegung erkannt", "Automation funktioniert nicht",
  "Automation triggert nicht", "debugging automation", "YAML Automation",
  "Was macht diese Automation?", "Erkläre diese Automation", "explain automation",
  "YAML erklären", "explain this YAML", "Wenn X passiert dann soll Y",
  anything that sounds like "when X happens, do Y" in a smart home context.
---

# yaml-wizzard

Erzeugt valides Home Assistant YAML aus natürlicher Sprache, validiert bestehende
Automationen strukturell, erklärt sie in Klartext und debuggt fehlerhafte Configs.

## Workflow Overview

```
1. Anforderungserfassung (Interview)
   -> Entities, Trigger, Conditions, Actions, Mode, Zielort, Kommentar-Level
2. YAML-Generierung
   -> Valides HA-YAML nach aktueller Syntax (2024+)
3. Explain-Mode (bei bestehender YAML)
   -> Klartext-Erklärung, Edge Cases, Kommentar-Angebot
4. Strukturelle Validierung
   -> Python-Script prüft Syntax, Pflichtfelder, veraltete Patterns
5. Ausgabe als .yaml Datei + Erklärung im Chat
6. Debugging und Iteration
   -> Fehler identifizieren, Diff zeigen, korrigierte Version erzeugen
```

---

## Step 1: Anforderungserfassung

### Natürliche Sprache als Input

Der Nutzer beschreibt sein Ziel in natürlicher Sprache. Claude stellt gezielte
Rückfragen mit `ask_user_input` wo möglich, Freitext nur wenn nötig.

### Interview-Fragen

Stelle diese Fragen gebündelt oder stückweise, je nach Komplexität der Anfrage.
Wenn der Nutzer bereits alle Details liefert, überspringe offensichtlich beantwortete
Fragen.

**Entities** (Freitext nötig):
Welche Entities sind beteiligt? (z.B. `light.wohnzimmer`, `sensor.temperatur`,
`binary_sensor.motion`). Wenn der Nutzer unsicher ist, hilf mit typischen
Entity-Patterns für sein Szenario.

**Trigger-Art** via `ask_user_input`:
```
Question (multi_select): "Welche Trigger-Art(en)?"
  - "State Change (Entity ändert Zustand)"
  - "Zeitbasiert (Uhrzeit, Zeitplan)"
  - "Sonnenauf-/untergang"
  - "Numerischer Schwellwert"
  - "MQTT / Webhook / Event"
  - "Geräte-Trigger (Device)"
  - "Template (eigene Bedingung)"
  - "Kalender"
  - "Andere / unsicher"
```

**Conditions** via `ask_user_input`:
```
Question (single_select): "Brauchst du zusätzliche Bedingungen?"
  - "Ja, zeitbasiert (z.B. nur abends)"
  - "Ja, zustandsbasiert (z.B. nur wenn jemand zuhause)"
  - "Ja, mehrere Bedingungen"
  - "Nein, keine Conditions"
  - "Unsicher, hilf mir"
```

**Actions** via `ask_user_input`:
```
Question (multi_select): "Welche Aktionen sollen ausgeführt werden?"
  - "Entity steuern (Licht, Schalter, Klima etc.)"
  - "Benachrichtigung senden"
  - "Verzögerung / Wartezeit"
  - "Verzweigung (wenn X dann Y, sonst Z)"
  - "Wiederholung (repeat)"
  - "Variablen setzen"
  - "Mehrere parallel"
  - "Andere"
```

**Automation Mode** via `ask_user_input`:
```
Question (single_select): "Was soll passieren, wenn die Automation erneut triggert
  während sie noch läuft?"
  - "Ignorieren (single) - Standard"
  - "Neustarten (restart)"
  - "In Warteschlange (queued)"
  - "Parallel ausführen (parallel)"
  - "Weiß nicht - Standard verwenden"
```

**Zielort** via `ask_user_input`:
```
Question (single_select): "Wo soll die Automation hin?"
  - "automations.yaml (mit ID, Standard)"
  - "configuration.yaml (labeled block)"
  - "Eigene Datei (z.B. automations/lichter.yaml)"
  - "Weiß nicht"
```

**Kommentar-Level** via `ask_user_input`:
```
Question (single_select): "Wie ausführlich soll die YAML kommentiert werden?"
  - "Minimal - Nur alias und description"
  - "Normal - Kurze Kommentare pro Block (empfohlen)"
  - "Lernmodus - Ausführliche Erklärungen an fast jeder Zeile"
```

Siehe `references/comment-levels.md` für Beispiele aller drei Level.

---

## Step 2: YAML-Generierung

### Syntax-Regeln (2024+ Standard)

Diese Regeln sind verbindlich. Lies `references/yaml-schema.md` für das
vollständige Schema.

1. **Immer `alias` und `description` setzen**
2. **Trigger-Syntax**: `triggers:` (Plural) mit `- trigger: <type>`
   NICHT das veraltete `platform:`
3. **Conditions-Syntax**: `conditions:` (Plural)
4. **Actions-Syntax**: `actions:` (Plural) mit `- action: <domain>.<service>`
   NICHT das veraltete `service:`
5. **automations.yaml**: Immer `id` generieren (slugified alias oder Timestamp)
6. **target**: Für `entity_id`/`device_id`/`area_id` unter `target:`,
   NICHT `entity_id` direkt unter `data:`
7. **Templates**: Jinja2 in Quotes: `"{{ trigger.entity_id }}"`
8. **for**: Als `HH:MM:SS` String oder Dictionary (`hours:`, `minutes:`, `seconds:`)
9. **Kommentare**: Gemäß gewähltem Kommentar-Level aus Step 1

### Generierungs-Ablauf

1. YAML erzeugen nach den Syntax-Regeln
2. Kommentare gemäß gewähltem Level einfügen
3. Validierung ausführen (Step 4)
4. Bei Fehlern automatisch korrigieren und erneut validieren
5. Als .yaml Datei speichern

### Referenz-Dateien

Lies bei Bedarf die passende Referenz:
- `references/trigger-types.md` für Trigger-Syntax und Parameter
- `references/condition-types.md` für Conditions
- `references/action-patterns.md` für Action-Patterns
- `references/common-pitfalls.md` für bekannte Fallstricke

---

## Step 3: Explain-Mode

Wird aktiviert wenn der Nutzer eine bestehende YAML hochlädt oder fragt
"Was macht diese Automation?" / "Erkläre diese Automation".

### Erklärungsstruktur

1. **Ablauf-Erklärung**: Schritt für Schritt in natürlicher Sprache.
   Kein Fachjargon, so wie man es jemandem erklären würde, der kein YAML kann.
   Beispiel: "Sobald der Bewegungsmelder im Flur eine Bewegung erkennt UND die
   Sonne bereits untergegangen ist, wird das Flurlicht eingeschaltet. Nach 3
   Minuten ohne neue Bewegung geht es wieder aus."

2. **Trigger-Erklärung**: Was genau löst die Automation aus? Wie oft kann sie
   auslösen? Was passiert bei Mehrfach-Triggern (Mode)?

3. **Conditions-Erklärung**: Welche Bedingungen müssen zusätzlich erfüllt sein?
   Was passiert wenn eine Condition false ist?

4. **Actions-Erklärung**: Was wird der Reihe nach ausgeführt? Gibt es
   Verzweigungen (choose/if), Wiederholungen (repeat), Wartezeiten (delay/wait)?

5. **Edge Cases**: Auf mögliche Probleme hinweisen (z.B. "Wenn dein WLAN
   ausfällt und der MQTT-Broker nicht erreichbar ist, wird dieser Trigger nicht
   feuern")

### Nach der Erklärung

Anbieten via `ask_user_input`:
```
Question (single_select): "Was möchtest du als nächstes?"
  - "YAML mit Kommentaren als Datei ausgeben"
  - "Automation ändern/verbessern"
  - "Fehler suchen / debuggen"
  - "Das war's, danke"
```

Wenn Kommentar-Datei gewünscht: Kommentar-Level abfragen (falls noch nicht
bekannt), dann kommentierte Version als .yaml ausgeben.

---

## Step 4: Strukturelle Validierung

Führe das Validierungs-Script auf jede generierte oder hochgeladene YAML aus:

```bash
python /home/claude/yaml-wizzard/scripts/validate_automation.py <pfad_zur_yaml>
```

Falls der Skill-Ordner nicht beschreibbar ist, kopiere das Script nach
`/home/claude/` und führe es von dort aus.

### Was geprüft wird

- YAML-Syntax valide (keine Tabs, korrekte Einrückung)
- Pflichtfelder vorhanden (`triggers`, `actions`)
- Keine veraltete Syntax (`platform:` statt `trigger:`, `service:` statt `action:`)
- Trigger-Typen bekannt
- Condition-Typen bekannt
- Action-Format korrekt (`action: domain.service` mit `target:` und/oder `data:`)
- Mode gültig (`single`/`restart`/`queued`/`parallel`)
- `id` vorhanden wenn für automations.yaml bestimmt
- Bekannte Fallstricke (z.B. `for:` bei state Trigger ohne `to:`)

### Umgang mit Validierungsergebnis

- **Keine Fehler, keine Warnings**: Weiter zu Step 5
- **Nur Warnings**: Im Chat erwähnen, aber Datei ausgeben
- **Errors**: Automatisch korrigieren, erneut validieren, dann erst ausgeben

---

## Step 5: Ausgabe

1. YAML als `.yaml` Datei erstellen und dem Nutzer bereitstellen
2. Kurze Zusammenfassung im Chat:
   - Was die Automation macht (1-2 Sätze)
   - In welchen Situationen sie triggert
   - Worauf man achten sollte
3. Hinweis wo die Datei hin muss:
   - `automations.yaml`: Inhalt ans Ende der Datei anhängen
   - `configuration.yaml`: Als labeled Block einfügen
   - Eigene Datei: Pfad und Include-Anweisung nennen
4. Wenn der Nutzer mehrere Automationen braucht die zusammenspielen:
   Alle in einer Datei mit klarer Trennung (`---` Separator und Kommentare)

---

## Step 6: Debugging und Iteration

### Fehlerbehebung bei hochgeladener YAML

1. YAML parsen (auch wenn fehlerhaft, so weit wie möglich)
2. Validierungs-Script ausführen
3. Fehler identifizieren und erklären
4. Korrigierte Version erzeugen
5. Diff zwischen alter und neuer Version zeigen (relevante Stellen hervorheben)

### "Automation triggert nicht" Checkliste

Wenn der Nutzer sagt die Automation triggert nicht, gehe diese Punkte durch:

1. Entity-ID korrekt geschrieben? (Tippfehler ist häufigste Ursache)
2. State-Werte als Strings? (`to: "on"` nicht `to: on`)
3. `for:` blockiert den Trigger? (State muss die gesamte `for:`-Dauer anliegen)
4. Condition filtert den Trigger? (Condition ist true wenn Automation durchlässt)
5. `mode: single` und Automation läuft bereits?
6. Automation aktiviert? (Nicht disabled in der UI?)
7. Entity liefert überhaupt Events? (Developer Tools > Events prüfen)
8. Template-Syntax korrekt? (Quotes um Jinja2?)
9. Bei Sun-Trigger: Offset als String mit Vorzeichen?
10. YAML-Einrückung korrekt? (Spaces, keine Tabs)

### Iteration

Nach jeder Änderung:
1. Korrigierte YAML validieren
2. Diff zeigen
3. Erklären was geändert wurde und warum
4. Als neue .yaml Datei ausgeben

---

## Multi-Automation-Pakete

Wenn der Nutzer zusammengehörige Automationen braucht (z.B. "Abwesenheitspaket"):

1. Alle Automationen konzeptionell planen
2. Abhängigkeiten identifizieren (z.B. gemeinsame Helper-Entities)
3. Alle in einer Datei generieren, klar getrennt
4. Hinweis auf benötigte Helper (input_boolean, input_number etc.) und wie man
   sie in HA anlegt
5. Installationsanleitung im Chat

---

## Sprache

- Antworte in der Sprache des Nutzers
- YAML-Kommentare in der Sprache des Nutzers
- Technische Begriffe (Trigger, Condition, Action, Entity) bleiben englisch,
  da sie so in Home Assistant heißen

---

## Dependencies

- **Python 3** mit `PyYAML`: Für das Validierungs-Script
- **docx skill** ist NICHT nötig, Ausgabe ist .yaml

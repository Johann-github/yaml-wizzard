# Comment Levels Reference

Beispiele für alle drei Kommentar-Level anhand derselben Automation.
Szenario: Flurlicht bei Bewegung, nur wenn dunkel, 3 Minuten an.

---

## Level: minimal

Nur `alias` und `description`, keine Inline-Kommentare.

```yaml
- id: "flurlicht_bewegung"
  alias: "Flurlicht bei Bewegung"
  description: "Schaltet Flurlicht bei Bewegung ein wenn es dunkel ist, nach 3 Min wieder aus"
  mode: restart
  triggers:
    - trigger: state
      entity_id: binary_sensor.motion_flur
      to: "on"
  conditions:
    - condition: sun
      after: sunset
  actions:
    - action: light.turn_on
      target:
        entity_id: light.flur
      data:
        brightness_pct: 80
    - wait_for_trigger:
        - trigger: state
          entity_id: binary_sensor.motion_flur
          to: "off"
          for: "00:03:00"
      timeout: "00:10:00"
      continue_on_timeout: true
    - action: light.turn_off
      target:
        entity_id: light.flur
```

---

## Level: normal (Default)

Kurze Kommentare über jedem Block, die erklären was er tut.

```yaml
- id: "flurlicht_bewegung"
  alias: "Flurlicht bei Bewegung"
  description: "Schaltet Flurlicht bei Bewegung ein wenn es dunkel ist, nach 3 Min wieder aus"
  # restart: Bei neuer Bewegung wird der Timer zurückgesetzt
  mode: restart

  # Auslöser: Bewegungsmelder im Flur erkennt Bewegung
  triggers:
    - trigger: state
      entity_id: binary_sensor.motion_flur
      to: "on"

  # Nur wenn es dunkel ist (nach Sonnenuntergang)
  conditions:
    - condition: sun
      after: sunset

  actions:
    # Flurlicht auf 80% einschalten
    - action: light.turn_on
      target:
        entity_id: light.flur
      data:
        brightness_pct: 80

    # Warten bis 3 Minuten keine Bewegung mehr erkannt wird
    - wait_for_trigger:
        - trigger: state
          entity_id: binary_sensor.motion_flur
          to: "off"
          for: "00:03:00"
      timeout: "00:10:00"
      continue_on_timeout: true

    # Licht wieder ausschalten
    - action: light.turn_off
      target:
        entity_id: light.flur
```

---

## Level: lernmodus

Ausführliche Kommentare an fast jeder Zeile. Erklärt WARUM etwas so geschrieben
ist, was die Alternativen wären, und was passiert wenn man es weglässt.

```yaml
# Jede Automation in automations.yaml beginnt mit einem Listenstrich (-)
# und braucht eine eindeutige ID, damit Home Assistant sie speichern kann.
- id: "flurlicht_bewegung"

  # alias ist der Name, der in der HA-Oberfläche angezeigt wird.
  # Wähle einen kurzen, beschreibenden Namen.
  alias: "Flurlicht bei Bewegung"

  # description ist optional, aber hilfreich als Gedächtnisstütze.
  # Wird in der UI angezeigt, wenn du die Automation öffnest.
  description: "Schaltet Flurlicht bei Bewegung ein wenn es dunkel ist, nach 3 Min wieder aus"

  # mode bestimmt was passiert, wenn die Automation erneut triggert
  # während sie noch läuft.
  # - single (Standard): Neuer Trigger wird ignoriert -> schlecht hier,
  #   weil dann die Bewegung während des Wartens ignoriert wird
  # - restart: Laufende Instanz wird abgebrochen, neue startet -> perfekt,
  #   weil damit der "Timer" bei neuer Bewegung zurückgesetzt wird
  # - queued: Trigger wird in Warteschlange gestellt -> hier nicht sinnvoll
  # - parallel: Mehrere Instanzen laufen gleichzeitig -> hier gefährlich
  mode: restart

  # triggers: (Plural!) definiert die Auslöser der Automation.
  # Du kannst mehrere Trigger angeben, einer davon reicht zum Auslösen.
  # WICHTIG: Seit 2024 heisst es "trigger:" im Listenelement,
  # NICHT mehr "platform:" (das war die alte Syntax).
  triggers:
    # Dieser Trigger feuert, wenn der Bewegungsmelder von "off" auf "on" wechselt.
    # entity_id muss exakt dem Entity-Namen in deinem HA entsprechen.
    # Du findest ihn unter Einstellungen > Geräte & Dienste > Entities.
    - trigger: state
      entity_id: binary_sensor.motion_flur
      # to: "on" muss in Anführungszeichen stehen!
      # Ohne Quotes interpretiert YAML "on" als boolean true,
      # und dann matcht der Trigger nie.
      to: "on"

  # conditions: (Plural!) sind zusätzliche Bedingungen.
  # ALLE Conditions müssen true sein, damit die Automation durchläuft.
  # Wenn eine Condition false ist, werden die Actions NICHT ausgeführt,
  # obwohl der Trigger gefeuert hat.
  conditions:
    # Prüft ob die Sonne untergegangen ist.
    # Alternative wäre: condition: state mit entity_id: sun.sun, state: "below_horizon"
    # Die sun-Condition hat den Vorteil, dass du ein Offset angeben kannst
    # (z.B. "schon 30 Min vor Sonnenuntergang").
    - condition: sun
      after: sunset
      # Wenn du das Licht schon vor Sonnenuntergang einschalten willst:
      # after_offset: "-00:30:00"

  # actions: (Plural!) definiert was passiert wenn Trigger UND Conditions erfüllt sind.
  # Actions werden der Reihe nach abgearbeitet.
  # WICHTIG: Seit 2024 heisst es "action:" statt "service:" (alte Syntax).
  actions:
    # Schritt 1: Flurlicht einschalten
    # "light.turn_on" ist der Service-Aufruf. Format: <domain>.<service>
    - action: light.turn_on
      # target: definiert WAS gesteuert wird.
      # entity_id gehört unter target:, NICHT unter data:
      # (entity_id direkt unter data: ist veraltete Syntax)
      target:
        entity_id: light.flur
      # data: enthält zusätzliche Parameter für den Service.
      # Welche Parameter verfügbar sind, findest du unter
      # Entwicklerwerkzeuge > Dienste in HA.
      data:
        # brightness_pct: 0-100 (Prozent)
        # Alternativ: brightness: 0-255 (absoluter Wert)
        brightness_pct: 80

    # Schritt 2: Warten bis der Bewegungsmelder 3 Minuten lang "off" meldet.
    # wait_for_trigger wartet auf einen bestimmten Zustandswechsel.
    # Das ist besser als ein einfacher delay, weil:
    # - Bei neuer Bewegung resettet mode: restart die ganze Automation
    # - Der Timer startet erst wenn KEINE Bewegung mehr erkannt wird
    - wait_for_trigger:
        - trigger: state
          entity_id: binary_sensor.motion_flur
          to: "off"
          # for: "00:03:00" bedeutet: Der Sensor muss 3 Minuten lang
          # durchgehend "off" sein. Wenn zwischendurch eine Bewegung kommt,
          # startet der for:-Timer von vorne.
          for: "00:03:00"
      # timeout ist das Sicherheitsnetz: Falls der wait_for_trigger
      # nie erfüllt wird (z.B. Sensor defekt), geht es nach 10 Min trotzdem weiter.
      # Ohne timeout würde die Automation ewig warten!
      timeout: "00:10:00"
      # continue_on_timeout: true bedeutet: Nach dem Timeout geht es
      # mit der nächsten Action weiter (Licht ausschalten).
      # Bei false würde die Automation hier abbrechen und das Licht bliebe an.
      continue_on_timeout: true

    # Schritt 3: Flurlicht ausschalten
    - action: light.turn_off
      target:
        entity_id: light.flur
    # Tipp: Wenn du willst, dass das Licht langsam ausgeht statt abrupt:
    # Nutze light.turn_on mit brightness_pct: 0 und transition: 5 (Sekunden)
```

---

## Richtlinien pro Level

### minimal
- Nur `alias` und `description`
- Kein einziger Inline-Kommentar
- Für erfahrene Nutzer die den Code übersichtlich halten wollen
- YAML soll "sauber" und kompakt sein

### normal
- Ein Kommentar pro logischem Block (nicht pro Zeile)
- Erklärt WAS der Block tut, nicht WIE die Syntax funktioniert
- Für Nutzer die ihre Automationen auch in 6 Monaten noch verstehen wollen
- Guter Kompromiss zwischen Übersicht und Information

### lernmodus
- Kommentare an fast jeder Zeile
- Erklärt WARUM etwas so geschrieben ist
- Nennt Alternativen und was passiert wenn man etwas weglässt
- Für HA-Einsteiger die YAML lernen wollen
- Hinweise auf häufige Fehler direkt im Kontext
- Kommentare sind NICHT redundant zum Code, sondern bieten Mehrwert

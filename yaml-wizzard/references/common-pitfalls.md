# Common Pitfalls Reference

Bekannte Fehlerquellen bei Home Assistant Automationen. Prüfe diese Punkte
bei jeder Validierung und bei jedem Debug-Vorgang.

---

## Veraltete Syntax (seit 2024.x deprecated)

### `platform:` statt `trigger:`

```yaml
# FALSCH (veraltet)
trigger:
  - platform: state
    entity_id: light.wohnzimmer

# RICHTIG
triggers:
  - trigger: state
    entity_id: light.wohnzimmer
```

### `service:` statt `action:`

```yaml
# FALSCH (veraltet)
action:
  - service: light.turn_on
    entity_id: light.wohnzimmer

# RICHTIG
actions:
  - action: light.turn_on
    target:
      entity_id: light.wohnzimmer
```

### Singular statt Plural auf Top-Level

```yaml
# FALSCH (veraltet)
trigger:
  - ...
condition:
  - ...
action:
  - ...

# RICHTIG
triggers:
  - ...
conditions:
  - ...
actions:
  - ...
```

### `entity_id` unter `data:` statt `target:`

```yaml
# FALSCH (veraltet)
- action: light.turn_on
  data:
    entity_id: light.wohnzimmer

# RICHTIG
- action: light.turn_on
  target:
    entity_id: light.wohnzimmer
```

---

## State-Werte sind IMMER Strings

```yaml
# FALSCH: YAML interpretiert "on" als boolean true
triggers:
  - trigger: state
    entity_id: switch.heizung
    to: on

# RICHTIG: Explizit als String
triggers:
  - trigger: state
    entity_id: switch.heizung
    to: "on"
```

Betroffene Werte die YAML falsch interpretiert:
- `on` / `off` -> `true` / `false`
- `yes` / `no` -> `true` / `false`
- `true` / `false` -> boolean
- Zahlen ohne Quotes -> numerisch

Faustregel: State-Werte bei `to:` und `from:` IMMER in Quotes.

---

## `for:` bei State-Trigger ohne `to:`

```yaml
# PROBLEMATISCH: for: ohne to:
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    for: "00:05:00"
```

Ohne `to:` triggert der State-Trigger bei JEDER Änderung. `for:` prüft dann
ob der NEUE Zustand 5 Minuten gehalten wird, egal welcher. Das führt oft
zu unerwartetem Verhalten.

```yaml
# BESSER: Explizites to:
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "off"
    for: "00:05:00"
```

---

## Sun Trigger Offset als String mit Vorzeichen

```yaml
# FALSCH: Kein Vorzeichen, kein String
triggers:
  - trigger: sun
    event: sunset
    offset: 01:00:00

# FALSCH: Negatives Offset ohne Quotes
triggers:
  - trigger: sun
    event: sunset
    offset: -01:00:00    # YAML interpretiert das als negativen Integer

# RICHTIG
triggers:
  - trigger: sun
    event: sunset
    offset: "-01:00:00"
```

---

## Template Quoting in YAML

Jinja2 Templates mit `{{ }}` brauchen Quotes, weil YAML `{` als Flow Mapping
interpretiert.

```yaml
# FALSCH: Ohne Quotes bricht YAML-Parser ab
value_template: {{ states('sensor.power') | float > 5 }}

# RICHTIG: In Quotes
value_template: "{{ states('sensor.power') | float > 5 }}"

# AUCH RICHTIG: Block Scalar (für mehrzeilige Templates)
value_template: >
  {{ states('sensor.power') | float > 5 and
     states('binary_sensor.home') == 'on' }}
```

---

## Race Conditions: Condition vs. Trigger

Ein häufiges Missverständnis: Die Condition wird zum Zeitpunkt der Trigger-
Auswertung geprüft, nicht zum Zeitpunkt der Action-Ausführung.

```yaml
# Szenario: Licht an wenn Bewegung UND dunkel
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "on"
conditions:
  - condition: sun
    after: sunset
actions:
  - action: light.turn_on
    target:
      entity_id: light.flur
```

Wenn die Sonne genau im Moment des Triggers untergeht, kann die Condition
noch `false` sein. Bei zeitkritischen Szenarien: Template-Trigger mit
allen Bedingungen in einem Template verwenden.

---

## `mode: single` blockiert

```yaml
mode: single  # Default!
```

Wenn eine Automation mit `mode: single` getriggert wird während sie noch
läuft (z.B. wegen eines `delay`), wird der neue Trigger IGNORIERT.

**Typisches Problem:** Bewegungsmelder triggert, Licht geht an, 3 Min Delay,
Licht geht aus. Während der 3 Minuten: Neue Bewegung wird ignoriert.

**Lösung:**
```yaml
mode: restart  # Bricht die laufende Instanz ab und startet neu
```

---

## `initial_state` Tippfehler

```yaml
# FALSCH (wird ignoriert, kein Fehler!)
initial_state: true

# FALSCH (häufiger Tippfehler)
inital_state: true
```

`initial_state` ist deprecated. Automationen starten immer im letzten
bekannten Zustand. Wenn eine Automation beim HA-Start immer aktiv sein soll,
ist das heute das Default-Verhalten.

---

## `entity_id: all` ist deprecated

```yaml
# FALSCH (deprecated)
- action: light.turn_off
  target:
    entity_id: all

# RICHTIG: Explizit auflisten oder area_id nutzen
- action: light.turn_off
  target:
    area_id: wohnzimmer
```

---

## YAML Einrückung: Spaces, keine Tabs

YAML erlaubt NUR Spaces zur Einrückung. Ein einziger Tab bricht die gesamte
Datei. Standard: 2 Spaces pro Level.

```yaml
# FALSCH (Tab-Zeichen, unsichtbar aber fatal)
triggers:
	- trigger: state    # <-- Tab!

# RICHTIG (2 Spaces)
triggers:
  - trigger: state
```

---

## Listen-Item unter `conditions:` ohne `condition:`

```yaml
# FALSCH: condition: fehlt
conditions:
  - entity_id: person.max
    state: "home"

# RICHTIG
conditions:
  - condition: state
    entity_id: person.max
    state: "home"
```

---

## `for:` Format-Fehler

```yaml
# FALSCH: Nur Zahl
for: 5

# FALSCH: Falsches Dict-Format
for:
  min: 5

# RICHTIG: String
for: "00:05:00"

# RICHTIG: Dictionary
for:
  minutes: 5

# RICHTIG: Dictionary komplett
for:
  hours: 0
  minutes: 5
  seconds: 0
```

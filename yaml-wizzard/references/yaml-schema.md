# YAML Schema Reference

Vollständiges Schema einer Home Assistant Automation. Basierend auf der
offiziellen Dokumentation (Stand 2024+).

---

## Top-Level Schema

```yaml
# Pflichtfelder
alias: "Menschenlesbarer Name"           # String, required
triggers:                                  # Liste, required (mind. 1 Trigger)
  - trigger: <type>
    # ... trigger-spezifische Parameter
actions:                                   # Liste, required (mind. 1 Action)
  - action: <domain>.<service>
    # ... action-spezifische Parameter

# Optionale Felder
id: "unique_id_string"                    # String, required wenn automations.yaml
description: "Was die Automation macht"    # String, empfohlen
conditions:                                # Liste, optional
  - condition: <type>
    # ... condition-spezifische Parameter
mode: single                               # single|restart|queued|parallel
max: 10                                    # Int, nur bei queued/parallel
max_exceeded: silent                       # silent|warning|error
trace:
  stored_traces: 5                         # Anzahl gespeicherter Traces (default: 5)
variables:                                 # Dict, Automation-Level Variablen
  my_var: "value"
trigger_variables:                         # Dict, vor Trigger-Auswertung verfügbar
  my_trigger_var: "value"
```

---

## Feld-Details

### `id`

Eindeutige ID für die Automation. Required wenn die Automation in
`automations.yaml` steht (weil HA die ID zum Speichern/Identifizieren nutzt).

Format-Empfehlungen:
- Slugified alias: `"licht_flur_bei_bewegung"`
- Timestamp: `"1709234567"`
- UUID-artig: `"a1b2c3d4"`

### `alias`

Menschenlesbarer Name, erscheint in der HA UI.
- Kurz und beschreibend
- Sprache des Nutzers
- Beispiel: `"Flurlicht bei Bewegung"`, `"Guten Morgen Routine"`

### `description`

Längere Beschreibung, sichtbar in der HA UI wenn man die Automation öffnet.
Nicht required, aber empfohlen.

### `mode`

| Mode | Verhalten bei erneutem Trigger während Lauf |
|------|---------------------------------------------|
| `single` | Neuer Trigger wird ignoriert (Default) |
| `restart` | Laufende Instanz wird abgebrochen, neue startet |
| `queued` | Neuer Trigger wird in Warteschlange gestellt |
| `parallel` | Neue Instanz läuft parallel zur bestehenden |

- `max:` gilt nur bei `queued` und `parallel` (default: 10)
- `max_exceeded:` bestimmt was passiert wenn `max` erreicht ist

### `variables`

Automation-Level Variablen, verfügbar in Conditions und Actions.

```yaml
variables:
  light_entity: "light.wohnzimmer"
  default_brightness: 80
```

### `trigger_variables`

Wie `variables`, aber schon vor der Trigger-Auswertung verfügbar.
Nützlich für dynamische Trigger-Parameter.

```yaml
trigger_variables:
  motion_sensor: "binary_sensor.motion_{{ area }}"
```

---

## Format für automations.yaml

In `automations.yaml` ist die Datei eine YAML-Liste. Jede Automation
ist ein Listenelement:

```yaml
- id: "flurlicht_bewegung"
  alias: "Flurlicht bei Bewegung"
  description: "Schaltet Flurlicht bei Bewegung ein wenn es dunkel ist"
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
  mode: restart

- id: "guten_morgen_routine"
  alias: "Guten Morgen Routine"
  # ...
```

**Wichtig:** Jede Automation beginnt mit `- ` (Listenelement).

---

## Format für configuration.yaml

In `configuration.yaml` werden Automationen als labeled blocks definiert:

```yaml
automation flurlicht_bewegung:
  alias: "Flurlicht bei Bewegung"
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
  mode: restart
```

Oder via Include:

```yaml
# configuration.yaml
automation: !include automations.yaml

# Oder mehrere Dateien
automation split: !include_dir_list automations/
```

---

## Format für eigene Dateien (Split Config)

Wenn `!include_dir_list automations/` genutzt wird, enthält jede Datei
im Ordner `automations/` EINE Automation OHNE den Listen-Strich:

```yaml
# automations/flurlicht.yaml
id: "flurlicht_bewegung"
alias: "Flurlicht bei Bewegung"
triggers:
  - trigger: state
    entity_id: binary_sensor.motion_flur
    to: "on"
actions:
  - action: light.turn_on
    target:
      entity_id: light.flur
```

Bei `!include_dir_merge_list` sind die Dateien Listen (mit `-`).

---

## Datentypen-Übersicht

| Feld | Typ | Beispiel |
|------|-----|----------|
| `alias` | String | `"Flurlicht"` |
| `id` | String | `"flurlicht_001"` |
| `description` | String | `"Beschreibung"` |
| `mode` | Enum | `single`, `restart`, `queued`, `parallel` |
| `max` | Integer | `10` |
| `entity_id` | String oder Liste | `"light.a"` oder `["light.a", "light.b"]` |
| `to` / `from` | String | `"on"`, `"off"`, `"home"` |
| `for` | String oder Dict | `"00:05:00"` oder `{minutes: 5}` |
| `above` / `below` | Number | `25`, `18.5` |
| `offset` | String | `"-01:00:00"` |
| `at` | String oder Entity | `"06:30:00"` oder `input_datetime.wakeup` |
| `weekday` | Liste | `[mon, tue, wed]` |
| `value_template` | String (Jinja2) | `"{{ states('x') == 'on' }}"` |

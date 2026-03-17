# Action Patterns Reference

Häufige Action-Patterns für Home Assistant Automationen.
Syntax: Immer unter `actions:` (Plural) mit `- action: <domain>.<service>`.

---

## Einfache Action

Entity steuern mit `target:` für die Ziel-Entity.

```yaml
actions:
  - action: light.turn_on
    target:
      entity_id: light.wohnzimmer
    data:
      brightness_pct: 80
      color_temp_kelvin: 3000
```

**Wichtig:**
- `entity_id` gehört unter `target:`, NICHT unter `data:`
- `target:` kann auch `device_id:` oder `area_id:` enthalten
- Mehrere Entities als Liste: `entity_id: [light.a, light.b]`

### Weitere Beispiele

```yaml
# Schalter ausschalten
- action: switch.turn_off
  target:
    entity_id: switch.kaffeemaschine

# Klima einstellen
- action: climate.set_temperature
  target:
    entity_id: climate.wohnzimmer
  data:
    temperature: 21
    hvac_mode: heat

# Cover/Rolladen steuern
- action: cover.set_cover_position
  target:
    entity_id: cover.schlafzimmer
  data:
    position: 50

# Input Boolean setzen
- action: input_boolean.turn_on
  target:
    entity_id: input_boolean.vacation_mode

# Scene aktivieren
- action: scene.turn_on
  target:
    entity_id: scene.movie_night
```

---

## Delay

Wartezeit zwischen Actions.

```yaml
actions:
  - action: light.turn_on
    target:
      entity_id: light.flur
  - delay:
      minutes: 3
  - action: light.turn_off
    target:
      entity_id: light.flur
```

**Formate:**
```yaml
# Als Dictionary
- delay:
    hours: 0
    minutes: 3
    seconds: 30

# Als String
- delay: "00:03:30"

# Als Template
- delay: "{{ states('input_number.delay_minutes') | int }}"
```

---

## Wait for Trigger

Wartet auf einen bestimmten Trigger bevor es weitergeht.

```yaml
actions:
  - action: light.turn_on
    target:
      entity_id: light.flur
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

**Parameter:**
- `timeout`: Maximale Wartezeit
- `continue_on_timeout`: Wenn true, geht es nach Timeout weiter (default: true)

---

## Wait Template

Wartet bis ein Template true wird.

```yaml
actions:
  - wait_template: "{{ states('sensor.power') | float < 5 }}"
    timeout: "01:00:00"
    continue_on_timeout: false
```

---

## Choose (If/Else-Verzweigung)

Führt unterschiedliche Actions basierend auf Conditions aus.

```yaml
actions:
  - choose:
      - conditions:
          - condition: trigger
            id: "motion_detected"
        sequence:
          - action: light.turn_on
            target:
              entity_id: light.flur
      - conditions:
          - condition: trigger
            id: "scheduled_off"
        sequence:
          - action: light.turn_off
            target:
              entity_id: light.flur
    default:
      - action: notify.notify
        data:
          message: "Unbekannter Trigger"
```

**Struktur:**
- `choose:` Liste von Optionen, jede mit `conditions:` und `sequence:`
- `default:` Wird ausgeführt wenn keine Option matcht (optional)
- Erste passende Option gewinnt (kein fall-through)

---

## If/Then/Else

Einfachere Alternative zu `choose` für binäre Entscheidungen.

```yaml
actions:
  - if:
      - condition: state
        entity_id: binary_sensor.motion
        state: "on"
    then:
      - action: light.turn_on
        target:
          entity_id: light.flur
    else:
      - action: light.turn_off
        target:
          entity_id: light.flur
```

---

## Repeat

Wiederholt eine Sequenz von Actions.

### Count-basiert

```yaml
actions:
  - repeat:
      count: 3
      sequence:
        - action: notify.mobile_app_phone
          data:
            message: "Waschmaschine fertig!"
        - delay:
            minutes: 5
```

### While-basiert

```yaml
actions:
  - repeat:
      while:
        - condition: state
          entity_id: binary_sensor.door
          state: "on"
      sequence:
        - action: notify.notify
          data:
            message: "Tür ist noch offen!"
        - delay:
            minutes: 5
```

### Until-basiert

```yaml
actions:
  - repeat:
      until:
        - condition: state
          entity_id: input_boolean.acknowledged
          state: "on"
      sequence:
        - action: notify.mobile_app_phone
          data:
            message: "Bitte bestätigen!"
        - delay:
            minutes: 10
```

**Wichtig:**
- `while`: Prüft VOR jeder Iteration (kann 0x laufen)
- `until`: Prüft NACH jeder Iteration (läuft mindestens 1x)
- Sicherheitsnetz: Immer ein Timeout/Maximum einbauen

---

## Variables

Variablen setzen und in nachfolgenden Actions nutzen.

```yaml
actions:
  - variables:
      current_brightness: "{{ state_attr('light.wohnzimmer', 'brightness') }}"
      target_brightness: 200
  - action: light.turn_on
    target:
      entity_id: light.wohnzimmer
    data:
      brightness: "{{ target_brightness }}"
```

Variablen sind innerhalb der Action-Sequenz verfügbar.

---

## Parallel

Führt mehrere Action-Sequenzen gleichzeitig aus.

```yaml
actions:
  - parallel:
      - sequence:
          - action: light.turn_on
            target:
              entity_id: light.wohnzimmer
          - delay:
              seconds: 2
          - action: light.turn_on
            target:
              entity_id: light.kueche
      - sequence:
          - action: cover.open_cover
            target:
              entity_id: cover.wohnzimmer
```

Nützlich wenn Actions unabhängig voneinander sind und nicht aufeinander warten
müssen.

---

## Stop

Bricht die Automation ab.

```yaml
actions:
  - if:
      - condition: state
        entity_id: alarm_control_panel.home
        state: "armed_away"
    then:
      - stop: "Alarm ist aktiv, Automation abgebrochen"
```

`stop:` akzeptiert einen optionalen Grund als String.
Mit `error: true` wird der Stop als Fehler geloggt.

---

## Notify mit Templates

```yaml
actions:
  - action: notify.mobile_app_phone
    data:
      title: "Smart Home Alert"
      message: >
        {{ trigger.to_state.attributes.friendly_name }}
        hat den Zustand auf {{ trigger.to_state.state }} geändert.
      data:
        tag: "automation_alert"
        actions:
          - action: "ACKNOWLEDGE"
            title: "OK"
          - action: "SNOOZE"
            title: "Später erinnern"
```

**Notify-Targets:**
- `notify.notify`: Standard (alle Geräte)
- `notify.mobile_app_<phone_name>`: Spezifisches Gerät
- `notify.persistent_notification`: HA UI Benachrichtigung
- `notify.<service>`: Andere (Telegram, Slack, Email etc.)

**Template-Variablen im Trigger-Kontext:**
- `{{ trigger.entity_id }}`: Entity die getriggert hat
- `{{ trigger.to_state.state }}`: Neuer Zustand
- `{{ trigger.from_state.state }}`: Alter Zustand
- `{{ trigger.to_state.attributes.friendly_name }}`: Anzeigename
- `{{ now().strftime('%H:%M') }}`: Aktuelle Uhrzeit

# Condition Types Reference

Alle verfügbaren Condition-Typen für Home Assistant Automationen.
Syntax: Immer unter `conditions:` (Plural).

Conditions sind Gatekeeper: Wenn eine Condition `false` ergibt, wird die
Automation NICHT ausgeführt, obwohl der Trigger gefeuert hat.

---

## state

Prüft ob eine Entity einen bestimmten Zustand hat.

```yaml
conditions:
  - condition: state
    entity_id: person.max
    state: "home"
```

**Parameter:**
- `entity_id` (required): Entity oder Liste
- `state` (required): Erwarteter Zustand (String!) oder Liste von Zuständen
- `attribute`: Attribut statt State prüfen
- `for`: Entity muss mindestens so lange im Zustand sein

---

## numeric_state

Prüft ob ein numerischer Wert in einem Bereich liegt.

```yaml
conditions:
  - condition: numeric_state
    entity_id: sensor.temperature
    above: 18
    below: 25
```

**Parameter:**
- `entity_id` (required): Entity oder Liste
- `above`: Wert muss darüber liegen
- `below`: Wert muss darunter liegen
- `attribute`: Attribut statt State
- `value_template`: Template für den zu prüfenden Wert

---

## sun

Prüft ob die Sonne auf- oder untergegangen ist.

```yaml
conditions:
  - condition: sun
    after: sunset
    after_offset: "-01:00:00"
```

**Parameter:**
- `after`: `sunrise` oder `sunset`
- `before`: `sunrise` oder `sunset`
- `after_offset`: Offset nach dem Event (String mit Vorzeichen)
- `before_offset`: Offset vor dem Event (String mit Vorzeichen)

**Beispiel: "Nur wenn es dunkel ist":**
```yaml
conditions:
  - condition: sun
    after: sunset
  # ODER einfacher:
  - condition: state
    entity_id: sun.sun
    state: "below_horizon"
```

---

## time

Prüft ob die aktuelle Zeit in einem Zeitfenster liegt.

```yaml
conditions:
  - condition: time
    after: "22:00:00"
    before: "06:00:00"
    weekday:
      - mon
      - tue
      - wed
      - thu
      - fri
```

**Parameter:**
- `after`: Startzeit (String `"HH:MM:SS"` oder `input_datetime` Entity)
- `before`: Endzeit
- `weekday`: Liste von Wochentagen (`mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun`)

**Wichtig:**
- `after: "22:00"` + `before: "06:00"` funktioniert korrekt über Mitternacht

---

## zone

Prüft ob eine Person in einer Zone ist.

```yaml
conditions:
  - condition: zone
    entity_id: person.max
    zone: zone.home
```

**Parameter:**
- `entity_id` (required): Person oder Device-Tracker
- `zone` (required): Zone Entity

---

## template

Prüft ein Template auf true/false.

```yaml
conditions:
  - condition: template
    value_template: "{{ states('sensor.power') | float > 50 }}"
```

**Parameter:**
- `value_template` (required): Jinja2 Template

**Wichtig:**
- Template MUSS in Quotes (wegen `{{ }}`)
- Muss `true` oder `false` zurückgeben

---

## trigger

Prüft welcher Trigger die Automation ausgelöst hat (über Trigger-ID).

```yaml
conditions:
  - condition: trigger
    id: "motion_detected"
```

**Parameter:**
- `id` (required): Trigger-ID (String oder Liste)

Nützlich wenn eine Automation mehrere Trigger hat und je nach Trigger
unterschiedlich reagieren soll (in Kombination mit `choose`).

---

## Logische Verknüpfungen

### and

Alle Conditions müssen true sein (default-Verhalten auf Top-Level).

```yaml
conditions:
  - condition: and
    conditions:
      - condition: state
        entity_id: person.max
        state: "home"
      - condition: sun
        after: sunset
```

### or

Mindestens eine Condition muss true sein.

```yaml
conditions:
  - condition: or
    conditions:
      - condition: state
        entity_id: person.max
        state: "home"
      - condition: state
        entity_id: person.lisa
        state: "home"
```

### not

Negiert die enthaltenen Conditions (alle müssen false sein).

```yaml
conditions:
  - condition: not
    conditions:
      - condition: state
        entity_id: alarm_control_panel.home
        state: "armed_away"
```

### Verschachtelung

Logische Operatoren können beliebig verschachtelt werden:

```yaml
conditions:
  - condition: and
    conditions:
      - condition: sun
        after: sunset
      - condition: or
        conditions:
          - condition: state
            entity_id: person.max
            state: "home"
          - condition: state
            entity_id: person.lisa
            state: "home"
```

Bedeutet: "Es ist dunkel UND (Max ODER Lisa sind zuhause)"

---

## Shorthand-Notation

Für einfache Fälle kann man Conditions auch als Template direkt schreiben:

```yaml
conditions:
  - "{{ states('sun.sun') == 'below_horizon' }}"
```

Das ist equivalent zu einer Template-Condition, aber kürzer.
Empfehlung: Für Klarheit die explizite Notation bevorzugen.

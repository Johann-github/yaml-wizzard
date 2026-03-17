# Trigger Types Reference

Alle verfügbaren Trigger-Typen für Home Assistant Automationen (Stand 2024+).
Syntax: Immer unter `triggers:` (Plural) mit `- trigger: <type>`.

---

## state

Triggert wenn eine Entity ihren Zustand ändert.

```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.motion_hallway
    to: "on"
    from: "off"
```

**Parameter:**
- `entity_id` (required): Entity oder Liste von Entities
- `to`: Zielzustand (String!)
- `from`: Ausgangszustand (String!)
- `for`: Mindestdauer im Zielzustand (`"HH:MM:SS"` oder Dict)
- `attribute`: Auf Attribut-Änderung triggern statt State
- `not_to` / `not_from`: Negierte Bedingungen

**Wichtig:**
- Ohne `to` und `from`: Triggert bei JEDER Änderung (auch Attribut-Updates)
- `for:` erfordert `to:`, sonst Warning
- State-Werte sind IMMER Strings: `to: "on"`, nicht `to: on`
- `to: "unavailable"` ist ein gültiger State

---

## numeric_state

Triggert wenn ein numerischer Wert einen Schwellwert über-/unterschreitet.

```yaml
triggers:
  - trigger: numeric_state
    entity_id: sensor.temperature_living_room
    above: 25
    below: 30
```

**Parameter:**
- `entity_id` (required): Entity oder Liste
- `above`: Unterer Schwellwert (triggert wenn Wert darüber geht)
- `below`: Oberer Schwellwert (triggert wenn Wert darunter geht)
- `for`: Mindestdauer über/unter Schwellwert
- `value_template`: Template das den zu prüfenden Wert liefert
- `attribute`: Attribut statt State prüfen

**Wichtig:**
- Mindestens `above` ODER `below` angeben
- Triggert nur beim ÜBERGANG über den Schwellwert, nicht dauerhaft

---

## time

Triggert zu einer festen Uhrzeit.

```yaml
triggers:
  - trigger: time
    at: "06:30:00"
```

**Parameter:**
- `at` (required): Uhrzeit als String `"HH:MM:SS"` oder `input_datetime` Entity

---

## time_pattern

Triggert periodisch nach einem Muster.

```yaml
triggers:
  - trigger: time_pattern
    minutes: "/5"
```

**Parameter:**
- `hours`: Stunde oder Pattern (z.B. `"/2"` = alle 2 Stunden)
- `minutes`: Minute oder Pattern
- `seconds`: Sekunde oder Pattern

---

## sun

Triggert bei Sonnenauf- oder -untergang.

```yaml
triggers:
  - trigger: sun
    event: sunset
    offset: "-01:00:00"
```

**Parameter:**
- `event` (required): `sunrise` oder `sunset`
- `offset`: Zeitverschiebung als String mit Vorzeichen (`"-01:00:00"`, `"+00:30:00"`)

**Wichtig:**
- Offset MUSS ein String sein mit Vorzeichen
- Negatives Offset = VOR dem Event, positives = NACH dem Event

---

## homeassistant

Triggert bei HA System-Events.

```yaml
triggers:
  - trigger: homeassistant
    event: start
```

**Parameter:**
- `event` (required): `start` oder `shutdown`

---

## mqtt

Triggert bei MQTT-Nachrichten.

```yaml
triggers:
  - trigger: mqtt
    topic: "home/doorbell"
    payload: "ring"
```

**Parameter:**
- `topic` (required): MQTT Topic (Wildcards erlaubt: `#`, `+`)
- `payload`: Erwarteter Payload (optional)
- `encoding`: Encoding (default: `utf-8`)
- `qos`: Quality of Service (0, 1, 2)
- `value_template`: Template für Payload-Auswertung

---

## event

Triggert bei HA Events.

```yaml
triggers:
  - trigger: event
    event_type: call_service
    event_data:
      domain: light
      service: turn_on
```

**Parameter:**
- `event_type` (required): Event-Typ
- `event_data`: Dict mit erwarteten Daten (optional)

---

## webhook

Triggert bei eingehenden Webhook-Aufrufen.

```yaml
triggers:
  - trigger: webhook
    webhook_id: my_automation_webhook
    allowed_methods:
      - POST
    local_only: true
```

**Parameter:**
- `webhook_id` (required): Eindeutige ID
- `allowed_methods`: Liste erlaubter HTTP-Methoden
- `local_only`: Nur lokale Aufrufe (default: `true`)

---

## zone

Triggert wenn eine Person eine Zone betritt oder verlässt.

```yaml
triggers:
  - trigger: zone
    entity_id: person.max
    zone: zone.home
    event: enter
```

**Parameter:**
- `entity_id` (required): Person oder Device-Tracker
- `zone` (required): Zone Entity
- `event` (required): `enter` oder `leave`

---

## tag

Triggert wenn ein NFC-Tag gescannt wird.

```yaml
triggers:
  - trigger: tag
    tag_id: "1234-5678-abcd"
```

**Parameter:**
- `tag_id` (required): Tag-ID (aus HA Tag-Verwaltung)
- `device_id`: Optionale Einschränkung auf bestimmtes Gerät

---

## template

Triggert wenn ein Template zu `true` evaluiert.

```yaml
triggers:
  - trigger: template
    value_template: "{{ states('sensor.power') | float > 100 }}"
    for: "00:05:00"
```

**Parameter:**
- `value_template` (required): Jinja2 Template das true/false liefert
- `for`: Mindestdauer die das Template true sein muss

**Wichtig:**
- Template MUSS in Quotes stehen (wegen `{{ }}`)
- Evaluiert bei jeder State-Änderung der referenzierten Entities

---

## calendar

Triggert bei Kalender-Events.

```yaml
triggers:
  - trigger: calendar
    entity_id: calendar.family
    event: start
    offset: "-00:15:00"
```

**Parameter:**
- `entity_id` (required): Kalender-Entity
- `event` (required): `start` oder `end`
- `offset`: Zeitverschiebung (String mit Vorzeichen)

---

## persistent_notification

Triggert wenn eine persistente Benachrichtigung erstellt oder entfernt wird.

```yaml
triggers:
  - trigger: persistent_notification
    notification_id: "my_notification"
    update_type: added
```

**Parameter:**
- `notification_id`: Optionale ID-Filterung
- `update_type`: `added`, `removed`, oder `current`

---

## conversation

Triggert bei Sprachbefehlen via Assist.

```yaml
triggers:
  - trigger: conversation
    command:
      - "Gute Nacht"
      - "Nachtmodus aktivieren"
```

**Parameter:**
- `command` (required): String oder Liste von Strings/Patterns

---

## sentence

Alias für `conversation` Trigger (gleiche Syntax).

---

## device

Triggert bei Geräte-spezifischen Events (abhängig von der Integration).

```yaml
triggers:
  - trigger: device
    device_id: "abc123def456"
    domain: zha
    type: remote_button_short_press
    subtype: button_1
```

**Parameter:**
- `device_id` (required): Geräte-ID aus HA
- `domain` (required): Integration (z.B. `zha`, `mqtt`, `deconz`)
- `type` (required): Event-Typ (integrationsabhängig)
- `subtype`: Sub-Typ (z.B. Button-Nummer)

**Wichtig:**
- Device-Trigger sind integrationsabhängig
- Am einfachsten über die HA UI erstellen und dann die YAML übernehmen

---

## Trigger-ID

Jeder Trigger kann eine optionale `id` bekommen, um in Conditions/Actions
darauf zu referenzieren:

```yaml
triggers:
  - trigger: state
    id: "motion_detected"
    entity_id: binary_sensor.motion
    to: "on"
  - trigger: time
    id: "scheduled_check"
    at: "22:00:00"
```

Nutzbar in Conditions: `- condition: trigger` mit `id: "motion_detected"`
Nutzbar in Actions: `{{ trigger.id }}` in Templates

#!/usr/bin/env python3
"""
validate_automation.py
Strukturelle Validierung von Home Assistant Automationen.

Input: Pfad zur YAML-Datei
Output: JSON mit {valid: bool, errors: [...], warnings: [...], info: [...]}
Exit Code: 0 bei valid, 1 bei Fehlern
"""

import sys
import json
import yaml
from pathlib import Path

# Bekannte Trigger-Typen (2024+ Standard)
KNOWN_TRIGGER_TYPES = {
    "state", "numeric_state", "sun", "time", "time_pattern",
    "homeassistant", "mqtt", "event", "webhook", "zone", "tag",
    "template", "calendar", "persistent_notification", "conversation",
    "sentence", "device"
}

# Bekannte Condition-Typen
KNOWN_CONDITION_TYPES = {
    "state", "numeric_state", "sun", "time", "zone", "template",
    "trigger", "or", "and", "not"
}

# Gültige Automation Modes
VALID_MODES = {"single", "restart", "queued", "parallel"}

# Veraltete Schlüsselwörter auf Top-Level
DEPRECATED_TOP_LEVEL = {
    "trigger": "triggers",
    "condition": "conditions",
    "action": "actions"
}

# Veraltete Syntax innerhalb von Triggern/Actions
DEPRECATED_TRIGGER_KEY = "platform"  # Sollte "trigger" sein
DEPRECATED_ACTION_KEY = "service"    # Sollte "action" sein


def validate_automation(automation: dict, index: int = 0) -> dict:
    """Validiert eine einzelne Automation und gibt Ergebnis zurück."""
    errors = []
    warnings = []
    info = []

    prefix = f"Automation #{index + 1}"
    alias = automation.get("alias", "<kein alias>")
    prefix = f"[{alias}]"

    # --- Pflichtfelder ---
    if "alias" not in automation:
        errors.append(f"{prefix} Pflichtfeld 'alias' fehlt.")
    else:
        info.append(f"{prefix} alias: {automation['alias']}")

    # Prüfe ob veraltete Singular-Keys auf Top-Level stehen
    for old_key, new_key in DEPRECATED_TOP_LEVEL.items():
        if old_key in automation and new_key not in automation:
            errors.append(
                f"{prefix} Veraltete Syntax: '{old_key}:' statt '{new_key}:' "
                f"(Plural seit 2024 Standard)."
            )

    # triggers vorhanden?
    triggers = automation.get("triggers", automation.get("trigger"))
    if not triggers:
        errors.append(f"{prefix} Pflichtfeld 'triggers' fehlt oder ist leer.")
    elif not isinstance(triggers, list):
        errors.append(f"{prefix} 'triggers' muss eine Liste sein.")
    else:
        validate_triggers(triggers, prefix, errors, warnings, info)

    # actions vorhanden?
    actions = automation.get("actions", automation.get("action"))
    if not actions:
        errors.append(f"{prefix} Pflichtfeld 'actions' fehlt oder ist leer.")
    elif not isinstance(actions, list):
        errors.append(f"{prefix} 'actions' muss eine Liste sein.")
    else:
        validate_actions(actions, prefix, errors, warnings, info)

    # conditions prüfen (optional)
    conditions = automation.get("conditions", automation.get("condition"))
    if conditions:
        if not isinstance(conditions, list):
            warnings.append(f"{prefix} 'conditions' sollte eine Liste sein.")
        else:
            validate_conditions(conditions, prefix, errors, warnings, info)

    # mode prüfen
    mode = automation.get("mode")
    if mode and mode not in VALID_MODES:
        errors.append(
            f"{prefix} Ungültiger mode: '{mode}'. "
            f"Erlaubt: {', '.join(VALID_MODES)}"
        )

    # max nur bei queued/parallel
    if "max" in automation and mode not in ("queued", "parallel"):
        warnings.append(
            f"{prefix} 'max' ist nur bei mode: queued oder parallel relevant."
        )

    # id prüfen (Warnung wenn fehlt)
    if "id" not in automation:
        warnings.append(
            f"{prefix} Kein 'id' gesetzt. Wird benötigt für automations.yaml."
        )

    # description empfohlen
    if "description" not in automation:
        info.append(f"{prefix} Kein 'description' gesetzt (empfohlen).")

    is_valid = len(errors) == 0
    return {
        "valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "info": info
    }


def validate_triggers(triggers: list, prefix: str, errors, warnings, info):
    """Validiert die Trigger-Liste."""
    for i, t in enumerate(triggers):
        if not isinstance(t, dict):
            errors.append(f"{prefix} Trigger #{i + 1}: Kein gültiges Dictionary.")
            continue

        t_prefix = f"{prefix} Trigger #{i + 1}"

        # Prüfe auf veraltetes "platform:" statt "trigger:"
        if DEPRECATED_TRIGGER_KEY in t and "trigger" not in t:
            errors.append(
                f"{t_prefix}: Veraltete Syntax 'platform:' statt 'trigger:'."
            )
            trigger_type = t.get(DEPRECATED_TRIGGER_KEY)
        else:
            trigger_type = t.get("trigger")

        if not trigger_type:
            errors.append(f"{t_prefix}: Kein Trigger-Typ angegeben.")
            continue

        if trigger_type not in KNOWN_TRIGGER_TYPES:
            warnings.append(
                f"{t_prefix}: Unbekannter Trigger-Typ '{trigger_type}'. "
                f"Evtl. Custom-Integration?"
            )

        # State-Trigger: for ohne to
        if trigger_type == "state":
            if "for" in t and "to" not in t:
                warnings.append(
                    f"{t_prefix}: 'for:' ohne 'to:' bei state Trigger. "
                    f"Triggert bei jeder Änderung, 'for' prüft dann auf den "
                    f"neuen (beliebigen) Zustand. Ist das gewollt?"
                )

            # State-Werte als Strings prüfen
            for key in ("to", "from"):
                val = t.get(key)
                if val is not None and isinstance(val, bool):
                    errors.append(
                        f"{t_prefix}: '{key}: {val}' ist ein Boolean. "
                        f"State-Werte müssen Strings sein: '{key}: \"{val}\"'."
                    )

        # Sun-Trigger: Offset prüfen
        if trigger_type == "sun":
            offset = t.get("offset")
            if offset is not None and not isinstance(offset, str):
                errors.append(
                    f"{t_prefix}: 'offset' muss ein String mit Vorzeichen sein "
                    f"(z.B. \"-01:00:00\"), ist aber {type(offset).__name__}."
                )
            if "event" not in t:
                errors.append(
                    f"{t_prefix}: Sun-Trigger braucht 'event: sunrise' oder "
                    f"'event: sunset'."
                )

        # numeric_state: above oder below nötig
        if trigger_type == "numeric_state":
            if "above" not in t and "below" not in t:
                errors.append(
                    f"{t_prefix}: numeric_state braucht mindestens "
                    f"'above' oder 'below'."
                )

        # Template: Prüfe ob value_template vorhanden
        if trigger_type == "template":
            if "value_template" not in t:
                errors.append(
                    f"{t_prefix}: Template-Trigger braucht 'value_template'."
                )


def validate_conditions(conditions: list, prefix: str, errors, warnings, info):
    """Validiert die Conditions-Liste."""
    for i, c in enumerate(conditions):
        # Shorthand-Template als String
        if isinstance(c, str):
            if "{{" not in c:
                warnings.append(
                    f"{prefix} Condition #{i + 1}: String-Condition ohne "
                    f"Template-Syntax. Ist das ein Jinja2 Template?"
                )
            continue

        if not isinstance(c, dict):
            errors.append(
                f"{prefix} Condition #{i + 1}: Kein gültiges Dictionary."
            )
            continue

        c_prefix = f"{prefix} Condition #{i + 1}"
        cond_type = c.get("condition")

        if not cond_type:
            errors.append(f"{c_prefix}: Kein 'condition:' Typ angegeben.")
            continue

        if cond_type not in KNOWN_CONDITION_TYPES:
            warnings.append(
                f"{c_prefix}: Unbekannter Condition-Typ '{cond_type}'."
            )

        # Verschachtelte Conditions (and/or/not)
        if cond_type in ("and", "or", "not"):
            sub_conditions = c.get("conditions")
            if not sub_conditions or not isinstance(sub_conditions, list):
                errors.append(
                    f"{c_prefix}: '{cond_type}' braucht eine 'conditions:' Liste."
                )
            else:
                validate_conditions(sub_conditions, c_prefix, errors, warnings, info)


def validate_actions(actions: list, prefix: str, errors, warnings, info):
    """Validiert die Actions-Liste."""
    for i, a in enumerate(actions):
        if not isinstance(a, dict):
            errors.append(f"{prefix} Action #{i + 1}: Kein gültiges Dictionary.")
            continue

        a_prefix = f"{prefix} Action #{i + 1}"

        # Prüfe auf veraltetes "service:" statt "action:"
        if DEPRECATED_ACTION_KEY in a and "action" not in a:
            errors.append(
                f"{a_prefix}: Veraltete Syntax 'service:' statt 'action:'."
            )

        # Spezial-Actions die kein "action:" haben
        special_keys = {
            "delay", "wait_for_trigger", "wait_template", "choose",
            "if", "repeat", "parallel", "variables", "stop", "event"
        }
        has_special = any(k in a for k in special_keys)

        if not has_special:
            action_name = a.get("action", a.get("service"))
            if not action_name:
                warnings.append(
                    f"{a_prefix}: Weder 'action:' noch eine Spezial-Action gefunden."
                )
            elif isinstance(action_name, str) and "." not in action_name:
                warnings.append(
                    f"{a_prefix}: Action '{action_name}' hat kein domain.service Format."
                )

            # entity_id unter data statt target
            data = a.get("data", {})
            if isinstance(data, dict) and "entity_id" in data and "target" not in a:
                warnings.append(
                    f"{a_prefix}: 'entity_id' unter 'data:' ist veraltet. "
                    f"Verschiebe es nach 'target:'."
                )

        # Verschachtelte Validierung bei choose
        if "choose" in a:
            for j, option in enumerate(a["choose"]):
                if isinstance(option, dict):
                    seq = option.get("sequence", [])
                    if seq:
                        validate_actions(seq, f"{a_prefix} choose[{j}]",
                                         errors, warnings, info)
            default = a.get("default", [])
            if default:
                validate_actions(default, f"{a_prefix} default",
                                 errors, warnings, info)

        # Verschachtelte Validierung bei if/then/else
        if "if" in a:
            then = a.get("then", [])
            if then:
                validate_actions(then, f"{a_prefix} then", errors, warnings, info)
            else_actions = a.get("else", [])
            if else_actions:
                validate_actions(else_actions, f"{a_prefix} else",
                                 errors, warnings, info)

        # Verschachtelte Validierung bei repeat
        if "repeat" in a:
            repeat = a["repeat"]
            if isinstance(repeat, dict):
                seq = repeat.get("sequence", [])
                if seq:
                    validate_actions(seq, f"{a_prefix} repeat",
                                     errors, warnings, info)

        # Verschachtelte Validierung bei parallel
        if "parallel" in a:
            for j, branch in enumerate(a["parallel"]):
                if isinstance(branch, dict):
                    seq = branch.get("sequence", [])
                    if seq:
                        validate_actions(seq, f"{a_prefix} parallel[{j}]",
                                         errors, warnings, info)


def validate_file(filepath: str) -> dict:
    """Validiert eine YAML-Datei mit einer oder mehreren Automationen."""
    path = Path(filepath)

    if not path.exists():
        return {
            "valid": False,
            "errors": [f"Datei nicht gefunden: {filepath}"],
            "warnings": [],
            "info": []
        }

    # YAML parsen
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return {
            "valid": False,
            "errors": [f"YAML-Syntax-Fehler: {e}"],
            "warnings": [],
            "info": []
        }

    if content is None:
        return {
            "valid": False,
            "errors": ["YAML-Datei ist leer."],
            "warnings": [],
            "info": []
        }

    # Tab-Check im Raw-Content
    raw_warnings = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if "\t" in line:
                raw_warnings.append(
                    f"Zeile {line_num}: Tab-Zeichen gefunden. "
                    f"YAML erlaubt nur Spaces zur Einrückung."
                )

    # Einzelne Automation oder Liste von Automationen
    if isinstance(content, list):
        all_errors = []
        all_warnings = list(raw_warnings)
        all_info = []

        for i, automation in enumerate(content):
            if not isinstance(automation, dict):
                all_errors.append(
                    f"Element #{i + 1}: Kein gültiges Automation-Dictionary."
                )
                continue
            result = validate_automation(automation, i)
            all_errors.extend(result["errors"])
            all_warnings.extend(result["warnings"])
            all_info.extend(result["info"])

        all_info.insert(0, f"Datei enthält {len(content)} Automation(en).")
        return {
            "valid": len(all_errors) == 0,
            "errors": all_errors,
            "warnings": all_warnings,
            "info": all_info
        }
    elif isinstance(content, dict):
        result = validate_automation(content, 0)
        result["warnings"] = raw_warnings + result["warnings"]
        return result
    else:
        return {
            "valid": False,
            "errors": [f"Unerwarteter YAML-Typ: {type(content).__name__}. "
                       f"Erwartet: Dict (eine Automation) oder Liste (mehrere)."],
            "warnings": [],
            "info": []
        }


def main():
    """Hauptfunktion: Nimmt Dateipfad als Argument."""
    if len(sys.argv) < 2:
        print(json.dumps({
            "valid": False,
            "errors": ["Kein Dateipfad angegeben. Usage: python validate_automation.py <datei.yaml>"],
            "warnings": [],
            "info": []
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

    filepath = sys.argv[1]
    result = validate_file(filepath)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()

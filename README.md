# yaml-wizzard

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024%2B-41BDF5.svg)](https://www.home-assistant.io/)

A Claude Skill for creating, validating, explaining, and debugging Home Assistant automations in YAML.

> **What it does:** You describe what your automation should do in plain language. The skill generates valid Home Assistant YAML, validates it structurally, and outputs it as a `.yaml` file. It can also explain existing automations in plain language and debug broken configs.

## Features

- **Natural Language to YAML**: Describe your automation goal, get valid HA YAML
- **Structural Validation**: Python script catches syntax errors, deprecated patterns, and common pitfalls before you deploy
- **Explain Mode**: Upload any automation YAML and get a plain-language explanation of what it does, including edge cases
- **Debug Mode**: Paste a broken automation, get a corrected version with a diff explanation
- **3 Comment Levels**: minimal (clean), normal (annotated), lernmodus (educational, explains *why*)
- **Multi-Automation Packages**: Creates sets of related automations with helper entity hints
- **2024+ Syntax**: Always uses current HA syntax (`triggers:`/`actions:`/`trigger:`/`action:`)

## Installation

### Option A: Install the `.skill` file

1. Download `yaml-wizzard.skill` from the [latest release](../../releases/latest)
2. In Claude, go to **Settings > Profile > Skills**
3. Upload the `.skill` file

### Option B: Add as Project Skill

1. Clone this repo or download the `yaml-wizzard/` folder
2. In a Claude Project, add the `yaml-wizzard/` folder as a skill

## Usage

Just talk to Claude naturally:

| What you say | What happens |
|---|---|
| "When motion is detected in the hallway and it's dark, turn on the light for 3 minutes" | Generates a complete automation with trigger, condition, actions, and validation |
| "What does this automation do?" + paste YAML | Explains the automation step by step in plain language |
| "My automation doesn't trigger" | Runs through a debug checklist and identifies the issue |
| "Create an absence package with light simulation" | Generates multiple related automations with helper entity setup |

The skill responds in the language you use. Both English and German are fully supported.

## Skill Structure

```
yaml-wizzard/
├── SKILL.md                              # Main skill instructions (315 lines)
├── scripts/
│   └── validate_automation.py            # Structural validation script
├── references/
│   ├── trigger-types.md                  # All 16+ trigger types with syntax
│   ├── condition-types.md                # All condition types incl. and/or/not
│   ├── action-patterns.md                # 12 action patterns (simple to parallel)
│   ├── common-pitfalls.md                # 12 known error sources
│   ├── yaml-schema.md                    # Full top-level automation schema
│   └── comment-levels.md                 # Examples for all 3 comment levels
└── evals/
    └── evals.json                        # 7 test cases
```

## Validation Script

The included `validate_automation.py` checks for:

- YAML syntax validity (no tabs, correct indentation)
- Required fields (`triggers`, `actions`, `alias`)
- Deprecated syntax (`platform:` instead of `trigger:`, `service:` instead of `action:`)
- Known trigger/condition types
- Action format (`action: domain.service` with `target:`)
- Valid automation modes
- Common pitfalls (`for:` without `to:`, booleans instead of strings, sun offset format)

### Standalone usage

```bash
python validate_automation.py my_automation.yaml
```

Returns JSON:
```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "info": ["File contains 1 automation(s)."]
}
```

Exit code 0 = valid, 1 = errors found.

## Comment Levels

| Level | Description | Use case |
|---|---|---|
| **minimal** | Only `alias` and `description`, zero inline comments | Experienced users who want clean YAML |
| **normal** | One comment per logical block explaining *what* it does | Default, good for future reference |
| **lernmodus** | Detailed comments on nearly every line explaining *why* | HA beginners learning YAML |

See [the wiki](../../wiki/Comment-Levels) for full examples.

## Test Results

All 7 test cases pass validation:

| TC | Description | Result |
|---|---|---|
| 1 | Simple (motion light) | valid, 0 errors |
| 2 | Medium (morning routine weekday/weekend) | valid, 0 errors |
| 3 | Complex (washer notification with repeat) | valid, 0 errors |
| 4 | Debug (fix broken YAML) | 5 errors detected, fix valid |
| 5 | Multi-automation (absence package, 3 automations) | valid, 0 errors |
| 6 | Explain mode (plain language explanation) | correct output |
| 7 | Lernmodus (educational comments) | valid, 0 errors |

## Requirements

- **Claude** with skill support (Claude.ai Pro/Team/Enterprise or Claude Code)
- **Python 3** with `PyYAML` (for the validation script)
- **Home Assistant** 2024.x or newer (the skill generates current syntax)

## Known Limitations

- Reference files are static and need manual updates when HA introduces new trigger types
- The validation script checks YAML structure, not whether entity IDs actually exist in your HA instance
- Jinja2 template syntax inside YAML is not validated beyond basic quote checking
- `for:` value format is not validated (only the presence of `to:` alongside `for:` is checked)

## License

This work is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). See [LICENSE](LICENSE) for details.

## Contributing

Issues and PRs welcome. If you find a HA automation pattern that the skill handles poorly, please open an issue with:

1. What you asked for
2. What the skill generated
3. What you expected instead

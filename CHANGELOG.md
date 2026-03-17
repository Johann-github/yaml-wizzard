# Changelog

## [1.0.0] - 2026-03-17

### Added
- Initial release
- SKILL.md with 6-step workflow (Interview, Generate, Explain, Validate, Output, Debug)
- Validation script (`validate_automation.py`) with checks for:
  - Deprecated syntax (platform/service/singular top-level keys)
  - Boolean instead of string state values
  - Missing required fields
  - Invalid modes
  - Common pitfalls (for without to, sun offset format, entity_id under data)
- 6 reference files:
  - `trigger-types.md` (16+ trigger types)
  - `condition-types.md` (all condition types incl. logical operators)
  - `action-patterns.md` (12 patterns from simple to parallel)
  - `common-pitfalls.md` (12 known error sources)
  - `yaml-schema.md` (full automation schema)
  - `comment-levels.md` (examples for minimal/normal/lernmodus)
- 3 comment levels: minimal, normal, lernmodus
- Explain mode for existing automations
- Debug mode with "Automation triggert nicht" checklist
- Multi-automation package support
- 7 test cases (evals.json)
- `.skill` package file for direct installation

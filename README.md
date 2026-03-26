# md2reqif

Convert Markdown requirements documents to [ReqIF](https://www.omg.org/spec/ReqIF/) XML and back. A lightweight bridge between plain-text authoring and systems engineering toolchains (IBM DOORS, PTC Integrity, Polarion, etc.).

## What it does

- Parses structured Markdown with YAML front matter into an internal requirements model
- Generates standards-compliant ReqIF XML with SPEC-OBJECTs, DATATYPES, and SPECIFICATIONS
- Reverses ReqIF back to Markdown for human review and editing
- Validates ReqIF files for XML well-formedness

## Install

```bash
# Recommended — isolated tool install
uv tool install md2reqif

# Or with pip
pip install md2reqif
```

## Quick start

Given `requirements.md`:

```markdown
# Braking System Requirements

## Functional Requirements

### REQ-BRAKE-001: Emergency Braking Response Time
- Status: Draft
- Priority: High
- Type: Functional

The system SHALL apply emergency braking within 100ms of detecting a collision event.
```

Convert to ReqIF:

```bash
md2reqif convert requirements.md -o requirements.reqif
```

Convert back to Markdown:

```bash
md2reqif reverse requirements.reqif -o recovered.md
```

## Markdown format reference

```markdown
---
module: Module Name          # optional: populates ReqIF TITLE
version: 1.0                 # optional
author: Your Name            # optional
date: 2024-01-15             # optional
---

# Document Title

## Section Name

### REQ-PREFIX-NNN: Requirement Title
- Status: Draft|Approved|Rejected|Obsolete
- Priority: Critical|High|Medium|Low
- Type: Functional|Performance|Interface|Constraint|Informational|Safety
- CustomKey: any value

Requirement description using SHALL language. Keep it to one or two sentences.
```

**ID format**: `REQ-` followed by alphanumeric segments separated by hyphens. If no matching ID is found, one is auto-generated from the section name.

## CLI commands

| Command | Description |
|---------|-------------|
| `md2reqif convert INPUT [-o OUTPUT] [--pretty/--no-pretty]` | Convert Markdown to ReqIF XML |
| `md2reqif reverse INPUT [-o OUTPUT]` | Convert ReqIF XML back to Markdown |
| `md2reqif validate INPUT` | Check ReqIF file for XML well-formedness |
| `md2reqif --version` | Print version |

## Agent usage

See [SKILL.md](SKILL.md) for detailed guidance on using this tool in AI agent pipelines, including the full Markdown format specification, metadata key reference, and writing tips for requirements authoring.

## License

MIT

# md2reqif — Agent Usage Guide (SKILL.md)

## Purpose

`md2reqif` bridges the gap between human-readable Markdown requirements documents and the ReqIF (Requirements Interchange Format) XML standard used by systems engineering tools such as IBM DOORS, PTC Integrity, and Polarion. It enables requirements to be authored and reviewed in plain text, then exchanged with tool ecosystems that consume ReqIF.

## Exact Markdown Format

### Document structure

```
[optional YAML front matter between --- delimiters]

# Document Title (h1 — sets doc.title)

## Section Name (h2 — groups requirements)

### REQ-PREFIX-NNN: Requirement Title (h3 — one requirement per heading)
- Status: Draft
- Priority: High
- Type: Functional

Requirement description text using SHALL language. One paragraph per requirement is recommended.
```

### Fully annotated example

```markdown
---
module: Braking System
version: 2.1
author: Safety Team
date: 2024-01-15
---

# Vehicle Safety Requirements

## Functional Requirements

### REQ-BRAKE-001: Emergency Stop Activation
- Status: Approved
- Priority: Critical
- Type: Safety
- Source: ISO-26262-Clause-4.6

The system SHALL activate emergency braking within 150ms of detecting an imminent collision,
as determined by the forward-facing radar sensor array.

### REQ-BRAKE-002: Brake Force Limiting
- Status: Draft
- Priority: High
- Type: Functional

The system SHALL limit brake force to prevent rear-wheel lock under all load conditions.
```

## Metadata Keys

### Standard keys (recognized by tooling)

| Key | Allowed values | Notes |
|-----|---------------|-------|
| Status | Draft, Approved, Rejected, Obsolete | Lifecycle state of the requirement |
| Priority | Critical, High, Medium, Low | Implementation priority |
| Type | Functional, Performance, Interface, Constraint, Informational, Safety, Accessibility | Requirement classification |

### Custom keys

Any additional `- Key: Value` list items under a requirement heading are preserved as string attributes in the ReqIF output. Examples:

- `Source: CR-42` — links to a change request
- `Verification: Test` — verification method
- `Allocated-To: SW-Module-X` — allocation trace

## How IDs Work

Requirements are identified by the heading format `### REQ-PREFIX-NNN: Title`:

- **Explicit IDs**: Use `REQ-` followed by alphanumeric segments separated by hyphens, e.g. `REQ-BRAKE-001`, `REQ-UI-042`, `REQ-SYS-PERF-007`.
- **Auto-generated IDs**: If the heading does not match the `REQ-*` pattern (e.g., a plain h3 heading), an ID is auto-generated from the first four characters of the parent section title plus a zero-padded counter: `FUNC-001`, `PERF-002`.
- IDs are preserved verbatim through round-trips (MD → ReqIF → MD).

## CLI Invocation

### Convert Markdown to ReqIF

```bash
md2reqif convert requirements.md -o output.reqif
```

Options:
- `-o / --output PATH` — write to file instead of stdout
- `--pretty / --no-pretty` — pretty-print XML (default: pretty)

### Convert ReqIF back to Markdown

```bash
md2reqif reverse output.reqif -o recovered.md
```

### Validate ReqIF XML well-formedness

```bash
md2reqif validate output.reqif
```

### Pipe usage

```bash
md2reqif convert requirements.md | xmllint --format -
```

## Writing Tips for AI Agents

1. **Use SHALL language**: Requirements must be normative. Write "The system SHALL..." not "The system should..." or "The system will...".
2. **One requirement per h3**: Each `### REQ-*:` heading is exactly one atomic requirement. Do not group multiple obligations under one ID.
3. **Keep descriptions concise**: One or two sentences per requirement. Supporting rationale belongs in a separate informational requirement (Type: Informational).
4. **Consistent ID prefixes**: Choose a module prefix (e.g., `BRAKE`, `UI`, `PERF`) and use it consistently within a section. Avoid reusing IDs across documents.
5. **Front matter is optional**: Omit it for simple documents; include it when the module name, version, or author is needed in the ReqIF header.
6. **Attributes are optional**: A heading with no bullet list items is a valid requirement with no custom attributes.
7. **Section nesting**: Only h2 sections are recognized as section groupings. h3 and deeper are always treated as requirement headings.

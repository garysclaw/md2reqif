---
module: Safety Requirements
version: 1.0
author: ACME Systems
---

# Braking System Requirements

## Functional Requirements

### REQ-BRAKE-001: Emergency Braking Response Time
- Status: Draft
- Priority: High
- Type: Functional

The system SHALL apply emergency braking within 100ms of detecting a collision event.

### REQ-BRAKE-002: Brake Force Distribution
- Status: Draft
- Priority: Medium
- Type: Functional

The system SHALL distribute braking force between front and rear axles to prevent wheel lock.

## Performance Requirements

### REQ-BRAKE-003: Braking Distance at 100km/h
- Status: Draft
- Priority: High
- Type: Performance

The system SHALL achieve a complete stop from 100 km/h within 40 meters on dry pavement.

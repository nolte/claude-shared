# Widget Config

Status: draft

## Context

Defines how the widget renderer loads and caches its configuration. Readers: implementors.

## Goals

- Render widgets from a declarative configuration file.

## Requirements

- The renderer MUST cache the resolved widget configuration in memory after first load.
- The renderer MUST read the configuration file fresh on every render and MUST NOT cache
  the resolved widget configuration.
- The renderer MUST validate the configuration against the schema before rendering.

## Acceptance Criteria

- [ ] A widget renders from a valid configuration file.
- [ ] An invalid configuration produces a visible validation error before render.
- [ ] The audit log is rotated daily at midnight UTC.

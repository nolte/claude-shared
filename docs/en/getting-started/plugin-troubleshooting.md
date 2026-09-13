---
title: Plugin troubleshooting
audience: [downstream-user]
content_mode: troubleshooting
track: user-docs
last_updated: 2026-09-13
---

# Plugin troubleshooting

Failures a user of the installed plugins meets, each as `symptom` / `cause` /
`workaround` / `resolution`. Problems while developing this repository itself
are in the [developer troubleshooting guide](../guides/troubleshooting.md).

## A `/nolte-shared:` command doesn't appear

- **Symptom**: after installing, typing `/nolte-shared:` offers no commands.
- **Cause**: the running session loaded its plugins before the install.
- **Workaround**: run `/reload-plugins`.
- **Resolution**: if the commands still don't appear, restart Claude Code and
  check `/plugin` lists `nolte-shared` as installed and enabled.

## A companion plugin's command is missing

- **Symptom**: `/nolte-engineering:quality-gate` or another command outside
  `nolte-shared` is unknown.
- **Cause**: the companion plugins install separately; `nolte-shared` doesn't
  pull them in.
- **Workaround**: none; the command lives only in its plugin.
- **Resolution**: install the plugin from the same marketplace, for example
  `/plugin install nolte-engineering@nolte-shared`, then `/reload-plugins`.

## A skill stops because a spec is unavailable

- **Symptom**: a skill reports that the spec it applies can't be found.
- **Cause**: the skill reads its spec from the repository it runs in, and that
  repository has no copy of the spec.
- **Workaround**: give the skill the spec content yourself, as its message
  offers.
- **Resolution**: run the skill in a repository that carries the spec, or copy
  the spec from the installed `nolte-shared` plugin, which ships the whole
  `spec/` tree.

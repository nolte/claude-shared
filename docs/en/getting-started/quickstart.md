---
title: Quickstart
audience: [downstream-user]
content_mode: how-to
track: user-docs
last_updated: 2026-09-13
---

# Quickstart

The shortest path from a fresh Claude Code session to a first result from the
`nolte-shared` plugin. For every install option and the companion plugins, see
[Using nolte-shared](../using.md).

1. Open Claude Code in any git repository you want to check.
2. Add the marketplace and install the plugin:

    ```text
    /plugin marketplace add nolte/claude-shared
    /plugin install nolte-shared@nolte-shared
    ```

3. Load it into the running session:

    ```text
    /reload-plugins
    ```

4. Ask for a read-only structure audit of the repository:

    ```text
    /nolte-shared:project-structure-apply
    ```

    The skill lists which portfolio conventions the repository already meets
    and which files are missing, and changes nothing until you confirm a
    proposed edit.

If a command doesn't appear or a skill stops early, see
[Plugin troubleshooting](plugin-troubleshooting.md).

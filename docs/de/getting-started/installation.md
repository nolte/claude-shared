---
title: Installation
audience: [maintainer, external-contributor]
content_mode: how-to
track: developer-docs
last_updated: 2026-05-19
---

# Installation

`claude-shared` ist als einzelnes Claude-Code-Plugin namens **`nolte-shared`** gepackt. Das Plugin-Manifest liegt unter `.claude-plugin/plugin.json`, die Marketplace-Beschreibung unter `.claude-plugin/marketplace.json`, Skills unter `skills/<name>/`, Agents unter `agents/<name>.md`.

## Voraussetzungen

- [Claude Code](https://docs.claude.com/en/docs/claude-code) installiert
- Lokaler Checkout dieses Repositorys (oder ein Ort, auf den Claude Code Zugriff hat)

## In einem nachgelagerten Projekt laden

Repository als Marketplace hinzufügen und Plugin installieren:

```bash
/plugin marketplace add nolte/claude-shared
/plugin install nolte-shared@nolte-shared
```

Für lokales Testen ohne Marketplace-Flow lädst du das Plugin direkt aus einem lokalen Pfad:

```bash
claude --plugin-dir /path/to/claude-shared
```

Skills aus diesem Plugin sind per Namespace aufrufbar:

```
/nolte-shared:spec
/nolte-shared:skill-management
```

!!! tip "Symlink statt Kopie"
    Wenn du claude-shared in deinem Projekt neben dem eigenen `.claude/`-Ordner verwenden willst, kannst du die Skills per Symlink einbinden:
    ```bash
    ln -s /path/to/claude-shared/skills/<name> .claude/skills/<name>
    ```
    Damit tauchen sie im `/skills`-Dialog auf und überleben `claude --plugin-dir`-Wechsel.

## Am Plugin selbst arbeiten (Dogfooding)

Beim Entwickeln im `claude-shared`-Repository selbst startest du Claude Code mit dem Plugin auf dem Repo-Root — so werden die Skills gefunden, ohne Dateien zu duplizieren:

```bash
claude --plugin-dir .
```

Änderungen während einer Session übernimmst du mit:

```
/reload-plugins
```

## Überprüfen, dass das Plugin geladen wurde

Nach dem Start sollten in `/skills` die Einträge aus diesem Repository erscheinen (z. B. `nolte-shared:spec`, `nolte-shared:skill-management`). Fehlt etwas, prüfe:

1. `.claude-plugin/plugin.json` ist valides JSON
2. Der Ordner enthält `skills/<name>/SKILL.md` mit gültigem Frontmatter
3. Claude Code wurde mit dem korrekten `--plugin-dir` gestartet

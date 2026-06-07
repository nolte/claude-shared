---
title: Installation
audience: [maintainer, external-contributor]
content_mode: how-to
track: developer-docs
last_updated: 2026-05-19
---

# Installation

`claude-shared` ist als einzelnes Claude-Code-Plugin namens **`nolte-shared`** gepackt. Layout:

- Plugin-Manifest: `.claude-plugin/plugin.json`
- Marketplace-Beschreibung: `.claude-plugin/marketplace.json`
- Skills: `skills/<name>/`
- Agents: `agents/<name>.md`

## Voraussetzungen

- [Claude Code](https://docs.claude.com/en/docs/claude-code) installiert
- Lokale Kopie (Klon) dieses Repositorys (oder ein Ort, auf den Claude Code Zugriff hat)

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
    Optional: Skills per Symlink einbinden. Damit liegt `claude-shared` neben deinem eigenen `.claude/`-Ordner:
    ```bash
    ln -s /path/to/claude-shared/skills/<name> .claude/skills/<name>
    ```
    Damit tauchen sie im `/skills`-Dialog auf und überleben `claude --plugin-dir`-Wechsel.

## Am Plugin selbst arbeiten (Dogfooding)

Beim Entwickeln im `claude-shared`-Repository startest du Claude Code direkt auf dem Repo-Root. Claude Code findet die Skills dann automatisch, ohne Datei-Duplikate:

```bash
claude --plugin-dir .
```

Änderungen während einer Session übernimmst du mit:

```
/reload-plugins
```

## Überprüfen, dass das Plugin geladen wurde

Nach dem Start zeigt `/skills` die Einträge aus diesem Repository — z. B. `nolte-shared:spec` und `nolte-shared:skill-management`. Fehlt etwas, prüfe:

1. `.claude-plugin/plugin.json` ist valides JSON
2. Der Ordner enthält `skills/<name>/SKILL.md` mit gültigem Frontmatter
3. Claude Code wurde mit dem korrekten `--plugin-dir` gestartet

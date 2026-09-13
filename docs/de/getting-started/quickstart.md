---
title: Schnellstart
audience: [downstream-user]
content_mode: how-to
track: user-docs
last_updated: 2026-09-13
---

# Schnellstart

Der kürzeste Weg von einer frischen Claude-Code-Session zu einem ersten
Ergebnis mit dem `nolte-shared`-Plugin. Alle Installationsoptionen und die
Begleit-Plugins beschreibt [Plugin nutzen](../using.md).

1. Öffne Claude Code in einem beliebigen Git-Repository, das du prüfen willst.
2. Füge den Marketplace hinzu und installiere das Plugin:

    ```text
    /plugin marketplace add nolte/claude-shared
    /plugin install nolte-shared@nolte-shared
    ```

3. Lade es in die laufende Session:

    ```text
    /reload-plugins
    ```

4. Fordere ein lesendes Struktur-Audit des Repositorys an:

    ```text
    /nolte-shared:project-structure-apply
    ```

    Der Skill zeigt, welche Portfolio-Konventionen das Repository schon
    erfüllt und welche Dateien fehlen, und ändert nichts, bevor du eine
    vorgeschlagene Änderung bestätigst.

Erscheint ein Befehl nicht oder bricht ein Skill früh ab, hilft
[Plugin-Fehlerbehebung](plugin-troubleshooting.md).

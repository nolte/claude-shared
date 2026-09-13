---
title: Release-Auslieferung
audience: [dogfooding-author, ci-operator]
content_mode: reference
track: developer-docs
last_updated: 2026-09-13
---

# Release-Auslieferung

Was dieses Repository ausliefert, welche Stufe jede Artefaktklasse absichert, was ihre
Provenance festhält und wie man sich von einer schlechten Version erholt. Das ist die
projektbezogene Zuordnung, die `spec/project/continuous-delivery/` §D verlangt.

## Artefaktklassen

| Artefaktklasse | Veröffentlicht als | Absichernde Stufe | Garantie | Provenance-Nachweis | Signierte Attestation |
| --- | --- | --- | --- | --- | --- |
| Plugin-Release (alle fünf Plugins im Lockstep) | Git-Tag `vX.Y.Z` samt GitHub-Release, installiert über den Marketplace | `release-publish.yml`: Pre-Publish-Verifikation, Lizenz-Verdikt | policy-cleared; Integrität über den unveränderlichen Tag | Der Commit-SHA des Tags und der `release-publish.yml`-Lauf, der den Draft veröffentlicht hat | Keine: Ein Git-Tag trägt keine Artefakt-Bytes, an die eine Attestation binden könnte, daher hat diese Klasse keinen Verifikationspfad |
| Dokumentationsseite | Der Branch `gh-pages`, ausgeliefert über GitHub Pages | `release-cd-deliver-docs.yml`, nachdem `mkdocs build --strict` im Pflicht-Check `docs` bestanden hat | built-from-source | Der Deploy-Commit auf `gh-pages`, dessen Nachricht den Quell-Commit nennt | Keine: GitHub Pages bietet keinen Verifikationspfad |

Release-Tags lassen sich weder löschen noch verschieben: Das Repository-Ruleset
`release-tags-immutable` blockiert Löschen, Aktualisieren und Nicht-Fast-Forward-Änderungen
an `refs/tags/v*`, sodass eine Versionsreferenz immer auf denselben Commit auflöst.

## Rollback

Die Erholung wählt eine frühere Version; sie baut nie einen alten Commit neu.

- **Plugins:** Ein Consumer pinnt den Marketplace auf den letzten guten Release-Tag und
  installiert die Plugins von dort neu:

    ```bash
    claude plugin marketplace add nolte/claude-shared@v0.1.10
    ```

- **Dokumentationsseite:** die Seite vom letzten guten Tag neu deployen:

    ```bash
    gh workflow run release-cd-deliver-docs.yml --ref v0.1.10
    ```

- Den Grund für den Rückzug in den Notes des nächsten Releases festhalten.

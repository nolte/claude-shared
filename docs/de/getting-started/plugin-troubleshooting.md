---
title: Plugin-Fehlerbehebung
audience: [downstream-user]
content_mode: troubleshooting
track: user-docs
last_updated: 2026-09-13
---

# Plugin-Fehlerbehebung

Fehler, auf die Nutzer der installierten Plugins stoßen, jeweils als
`symptom` / `cause` / `workaround` / `resolution`. Probleme bei der Entwicklung
dieses Repositorys selbst stehen in der
[Entwickler-Fehlerbehebung](../guides/troubleshooting.md).

## Ein `/nolte-shared:`-Befehl erscheint nicht

- **Symptom**: Nach der Installation bietet `/nolte-shared:` keine Befehle an.
- **Cause**: Die laufende Session hat ihre Plugins vor der Installation geladen.
- **Workaround**: `/reload-plugins` ausführen.
- **Resolution**: Erscheinen die Befehle weiterhin nicht, Claude Code neu
  starten und prüfen, dass `/plugin` `nolte-shared` als installiert und
  aktiviert führt.

## Der Befehl eines Begleit-Plugins fehlt

- **Symptom**: `/nolte-engineering:quality-gate` oder ein anderer Befehl
  außerhalb von `nolte-shared` ist unbekannt.
- **Cause**: Die Begleit-Plugins werden getrennt installiert; `nolte-shared`
  zieht sie nicht mit.
- **Workaround**: keiner; der Befehl existiert nur in seinem Plugin.
- **Resolution**: Das Plugin aus demselben Marketplace installieren, zum
  Beispiel `/plugin install nolte-engineering@nolte-shared`, danach
  `/reload-plugins`.

## Ein Skill bricht ab, weil eine Spec nicht verfügbar ist

- **Symptom**: Ein Skill meldet, dass die anzuwendende Spec nicht gefunden wird.
- **Cause**: Der Skill liest seine Spec aus dem Repository, in dem er läuft, und
  dieses Repository hat keine Kopie der Spec.
- **Workaround**: Dem Skill den Spec-Inhalt selbst geben, wie seine Meldung
  anbietet.
- **Resolution**: Den Skill in einem Repository ausführen, das die Spec trägt,
  oder die Spec aus dem installierten `nolte-shared`-Plugin kopieren, das den
  ganzen `spec/`-Baum mitliefert.

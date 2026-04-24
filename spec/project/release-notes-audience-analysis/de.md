# Zielgruppenanalyse für Release Notes

Status: draft

## Kontext
<!-- Warum existiert diese Spec? Welches Problem, welcher Bedarf oder welche Einschränkung treibt sie? -->

Jedes GitHub-Release eines Projekts liefert ein Release-Notes-Dokument aus — heute typischerweise durch `release-drafter` erzeugt und über `release-automation` veröffentlicht. Wer dieses Dokument tatsächlich *liest* und was es dort braucht, unterscheidet sich stark: Wer upgraded, will Breaking-Change-Hinweise und Migrationsschritte; wer das Paket nachpackt, will das Dependency-Delta; ein Security-Team will CVE-Referenzen; ein automatischer Konsument (Renovate, Dependabot, Release-Tracking-Bot) will eine parsbare Kategoriestruktur. Ohne bewusste Ermittlung der Release-Notes-Zielgruppen eines Projekts verkommen die Notes zu "dem, was `release-drafter` zufällig aus den PR-Titeln gruppiert hat" — eine flache Liste, sortiert nach Commit-Typ statt nach Leser-Bedarf. Die `audience-identification`-Spec liefert das generische Verfahren zur Aufzählung der Zielgruppen eines abgesteckten Kontexts; diese Spec wendet dieses Verfahren auf den spezifischen Kontext "Release Notes eines GitHub-Releases eines Projekts" an, damit die inhaltliche Struktur, die Detailtiefe, die sprachliche Ebene und die Call-to-Actions jedes Releases gegen eine bekannte Zielgruppen-Menge statt gegen Autoren-Annahmen erzeugt werden. Die Spec schließt die Lücke zwischen `release-automation` (die regelt, *wie* ein Release publiziert wird) und der `release-drafter`-Konfiguration (die regelt, *was* im Release steht): diese Spec deckt ab, *für wen* der Inhalt zusammengestellt wird.

## Ziele
<!-- Was diese Spec erreichen will. Stichpunkte, ergebnisorientiert. -->
- Das `audience-identification`-Verfahren auf den abgesteckten Kontext "Release Notes eines GitHub-Releases" eines konkreten Projekts anwenden
- Pro Projekt eine belastbare Liste von Release-Notes-Zielgruppen erzeugen, auf die `release-drafter`-Konfiguration, PR-Label-Konventionen und Review-Standards verweisen können
- Jede identifizierte Zielgruppe mit den konkreten Inhaltsdimensionen verbinden, die sie treibt — Kategoriestruktur, Detailtiefe, Sprachebene, CTAs, Maschinenlesbarkeit
- Die Reviewbarkeit von Release-Notes-Inhalten explizit machen: Reviewer sollen sagen können "dieser Entwurf bedient Zielgruppe A und B, aber der CTA für C fehlt" statt über Geschmack zu streiten
- Angenommene oder unbelegte Release-Notes-Zielgruppen sichtbar machen, damit sie validiert oder verworfen werden — statt als stille Default-Annahmen in `release-drafter.yml` weiterzuleben

## Nicht-Ziele
<!-- Was explizit außerhalb des Scopes liegt. Verhindert Scope Creep. -->
- Generische Zielgruppen-Identifikation — `audience-identification` definiert das Verfahren bereits
- Release-Publikations-Mechanik — `release-automation` regelt den Übergang Draft → Published
- Vorgabe eines Changelog-Formats (Conventional Commits, Keep a Changelog, Eigenformat) — Formatwahl bleibt bei den anwendenden Projekten
- Marketing- oder Launch-Kampagnen-Planung rund um ein Release
- Release-Taktung oder Versioning-Policy (ergibt sich aus `branching-model` und `release-drafter`-Konfiguration)
- CVE- oder Security-Advisory-Disclosure-Workflow — wird als konsumierende Zielgruppe referenziert, aber hier nicht spezifiziert
- Vorgabe, wo das Zielgruppen-Artefakt physisch lebt (eigene Datei, README-Abschnitt, ADR, Inline-Kommentare in `release-drafter.yml`) — Umsetzungsentscheidung, offen gelassen analog zu `audience-identification`

## Anforderungen
<!-- RFC-2119-Schlüsselwörter verwenden: MUST, SHOULD, MAY. Eine atomare Anforderung pro Bullet. -->
- **MUSS [MUST]** "Release Notes eines GitHub-Releases dieses Projekts" als schriftlich deklarierten, abgesteckten Kontext beim Anwenden von `audience-identification` führen — die Deklaration steht vor jeder gelisteten Zielgruppe
- **MUSS [MUST]** das `audience-identification`-Verfahren vollständig befolgen — Beziehungskategorien, Pflichtfelder je Zielgruppe, `confirmed` / `assumed`-Kennzeichnung — und keine seiner Anforderungen umformulieren oder überschreiben
- **MUSS [MUST]** die Zielgruppenliste erzeugen, bevor die `release-drafter`-Kategorien, die PR-Label-Taxonomie oder die Release-Review-Konventionen eines Projekts konfiguriert oder wesentlich geändert werden — damit diese Artefakte auf die Liste verweisen statt eine eigene zu erfinden
- **MUSS [MUST]** mindestens die folgenden Kandidaten-Zielgruppen prüfen und pro Kandidat entweder einen konkreten Eintrag oder "nicht zutreffend" mit Begründung aufnehmen:
  - **Upgrader** — bestehende Adopter, die zwischen Versionen dieses Projekts wechseln
  - **Neuadopter** — Parteien, die das Projekt über ein Release-Tag, einen Release-Feed oder einen Package-Registry-Eintrag entdecken
  - **Nachgelagerte Packager / Distributoren** — OS-Packager, HACS, npm-/PyPI-Abhängige, Container-Image-Builder, alle Weiter-Publizierenden
  - **Betreiber / SREs** — Parteien, die das Projekt betreiben und auf operative Auswirkungen, Deprecations, Config-Änderungen, Rollback-Risiken lesen
  - **Integratoren** — API- oder CLI-Konsumenten, die Breaking Changes verfolgen
  - **Security-sensitive Zielgruppen** — CVE-Tracker, Compliance-Reviewer, Security-Teams, die Release Notes als Disclosure-Kanal nutzen
  - **Automatisierte Konsumenten** — Renovate, Dependabot, Release-Tracking-Bots, GitHub-Release-Feed-Reader und alles, was die Notes maschinell parst
  - **Beitragende und Maintainer** — für Attribution und Sichtbarkeit dessen, was gelandet ist
- **MUSS [MUST]** jede gelistete Release-Notes-Zielgruppe mit den Inhaltsdimensionen verknüpfen, die sie treibt — mindestens:
  - welcher `release-drafter`-Abschnitt / welches Kategorie-Label existieren muss, um diese Zielgruppe zu bedienen
  - geforderte Detailtiefe pro Eintrag für diese Zielgruppe (Einzeiler, verlinkter Migrations-Guide, eingebettetes Code-Diff, …)
  - Sprachebene (Endnutzer-Vokabular, Betreiber-Vokabular, Entwickler-Vokabular)
  - Call-to-Action (Upgrade-Befehl, Migrations-Link, Deprecation-Deadline, Verweis auf Security Advisory)
  - Vorgaben zur Maschinenlesbarkeit (stabile Kategorienamen, PR-Referenzen, CVE-IDs, SemVer-Labels)
- **MUSS [MUST]** Breaking-Change- und Security-Disclosure-Zielgruppen als primär klassifizieren, sobald der Scope des Projekts eine der beiden Änderungsklassen erzeugen kann — Release Notes sind der kanonische Disclosure-Kanal für beide, und eine niedrigere Priorisierung riskiert unangekündigte Nutzer-Auswirkungen
- **MUSS [MUST]** jede Zielgruppe gemäß `audience-identification` als `confirmed` oder `assumed` kennzeichnen; eine Release-Notes-Zielgruppe, die ohne Beleg (reale Vertretung, Subscriber-Signal, Nachweis eines automatisierten Konsumenten, referenzierendes Issue) beansprucht wird, bleibt `assumed`
- **SOLLTE [SHOULD]** die `release-drafter`-Kategoriekonfiguration des Projekts an den identifizierten Zielgruppen ausrichten — jede Kategorie existiert, weil mindestens eine Zielgruppe sie braucht; Kategorien ohne zugeordnete Zielgruppe werden entfernt
- **SOLLTE [SHOULD]** die PR-Label-Taxonomie und die Conventional-Commits-Scopes des Projekts so ausrichten, dass `release-drafter` die zielgruppengetriebenen Kategorien ohne manuelle Nachbearbeitung zusammenstellt
- **SOLLTE [SHOULD]** pro Zielgruppe das tatsächlich genutzte Konsumsignal dokumentieren — GitHub-Release-Feed / Atom, E-Mail-Abo, In-Product-Banner, Dependency-Bot-PR-Body, Release-Tracking-Dienst — weil das Signal die akzeptable Länge, Formatierung und Verlinkbarkeit einschränkt
- **SOLLTE [SHOULD]** die Release-Notes-Zielgruppenliste erneut prüfen, sobald das Projekt einen neuen Konsumkanal erhält (öffentliche HACS-Listung, erste Package-Registry-Veröffentlichung, Container-Registry-Push), eine regulierte Datenklasse hinzukommt oder das Projekt die Schwelle von intern zu öffentlich überschreitet
- **KANN [MAY]** eine Release-Notes-Zielgruppe nach Deployment-Größe (Selbst-Hoster vs. Managed), Expertise (Endnutzer vs. Integrator) oder Mandantenzuordnung unterteilen, wenn diese Unterschiede die geforderte Detailtiefe oder Sprachebene verändern
- **KANN [MAY]** pro Zielgruppe einen minimalen "Release-Notes-Vertrag" festhalten — einen Einzeiler, was jedes Release dieses Projekts dieser Zielgruppe liefern muss (z. B. "jedes Release muss einen Upgrade-Befehl für Upgrader verlinken")

## Abnahmekriterien
<!-- Testbare, abhakbare Bedingungen. Reviewer müssen pro Punkt "erfüllt / nicht erfüllt" markieren können. -->
- [ ] Ein durchgearbeitetes Beispiel existiert, das das Verfahren auf ein konkretes Projekt im Portfolio anwendet (z. B. `claude-shared` selbst, mit dokumentierten Release-Notes-Zielgruppen aus Plugin-Konsumenten-Sicht)
- [ ] Das erzeugte Artefakt deklariert "Release Notes von <Projekt>" schriftlich als abgesteckten Kontext, bevor eine Zielgruppe gelistet wird
- [ ] Jede gelistete Zielgruppe ist mit mindestens einer Inhaltsdimension verknüpft (Abschnitt, Detailtiefe, Sprachebene, CTA, Maschinenlesbarkeit)
- [ ] Jeder Zielgruppen-Eintrag ist als `confirmed` oder `assumed` gekennzeichnet
- [ ] Die `release-drafter`-Konfiguration des Projekts lässt sich Kategorie für Kategorie auf mindestens eine gelistete Zielgruppe zurückführen
- [ ] Der §Nicht-Ziele-Abschnitt von `release-automation` (Ausschluss "Release-Notes-Inhaltsgenerierung") verlinkt auf diese Spec, damit die Grenze zwischen Mechanik und Inhalt explizit wird
- [ ] Der `spec-drift-audit`-Skill kann ein Projekt flaggen, dessen `release-drafter`-Kategorien, CHANGELOG-Abschnitte oder Release-Notes-Review-Checkliste nicht mehr zu den dokumentierten Release-Notes-Zielgruppen passen
- [ ] Ein Reviewer eines `release-drafter`-Drafts kann mithilfe der Zielgruppenliste verifizieren, dass die Inhaltsdimensionen jeder primär gerankten Zielgruppe erfüllt sind, bevor `release-publish.yml` dispatched wird
- [ ] Jede Zielgruppe, deren Konsumsignal ein automatisierter Konsument ist, hat eine dokumentierte Stabilitätserwartung für die Felder, die sie parst (Kategorienamen, PR-Referenz-Format, CVE-ID-Format)

## Offene Fragen
<!-- Ungelöste Entscheidungen, bekannte Unbekannte, Punkte, die eine Stakeholder-Antwort brauchen. -->
- Soll das Release-Notes-Zielgruppen-Artefakt in einer dedizierten Datei (z. B. `docs/release-audiences.md`) leben, Abschnitt des allgemeinen Zielgruppen-Artefakts des Projekts sein oder als kommentierte Begründung in `.github/release-drafter.yml` eingebettet werden?
- Braucht jedes Repository im Portfolio seine eigene Release-Notes-Zielgruppenliste, oder können kleine, rein interne Projekte einen Portfolio-Default erben, den `nolte/gh-plumbing` veröffentlicht?
- Sollen security-sensitive Release-Notes-Zielgruppen automatisch einen strikteren Pre-Publish-Review-Pfad erzwingen (z. B. verpflichtendes `security-review`), oder bleibt das an `pull-request-workflow` delegiert?
- Wie werden die Anforderungen automatisierter Konsumenten (maschinenlesbare Kategorien, parsbare CVE-IDs, stabiles PR-Referenz-Format) ermittelt und validiert — über GitHub-API-Audits der Release-Feed-Subscriber, über Inspektion eingehender Dependency-Bot-PRs oder manuell?
- Wie verhält sich diese Spec zu künftigen SLA-, Privacy-Impact- oder Threat-Modeling-Specs, die ebenfalls die Zielgruppenliste des Projekts konsumieren?
- Gilt diese Spec rückwirkend — auditieren Projekte bereits veröffentlichte Release Notes gegen eine neu abgeleitete Zielgruppenliste — oder erst ab dem ersten Release nach Adoption?
- Wenn sich die Zielgruppenliste mitten im Release-Zyklus ändert: Wer gleicht ab — ist es ein Release-blockierender Task oder ein Folge-Issue, das gegen das nächste Release getrackt wird?

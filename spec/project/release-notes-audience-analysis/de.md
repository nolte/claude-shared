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
- Vorgabe einer neuen Standort-Regel für das Zielgruppen-Artefakt: Diese Spec fügt keine hinzu und erbt `audience-identification` §Anforderungen (Artefakt-Standort) — kanonischer Default `AUDIENCES.md` an der Wurzel des Kontexts, mit einem README-Abschnitt "Audiences" oder einer dedizierten `docs/release-audiences.md` als akzeptierten Alternativen (dieselbe Menge, die `release-skill-layer` konsumiert). Das Artefakt nur als Inline-Kommentare in `release-drafter.yml` einzubetten ist ausgeschlossen, weil es für konsumierende Specs nicht deterministisch auffindbar ist

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
- **MUSS [MUST]** die einzige Release-Zeit-Pflicht dieser Spec für eine Security-Disclosure-Zielgruppe auf die Inhaltsabdeckung beschränken: Die Zielgruppe wird primär gerankt, und ihre Inhaltsdimensionen (Advisory-Verweis, CVE-IDs) werden vor dem Dispatch von `release-publish.yml` verifiziert, gemäß §Abnahmekriterien. Der Security-Review auf Code-Ebene bleibt an den diff-bezogenen `security-review`-Skill delegiert, der im PR-Flow aufgerufen wird (der Pfad, über den `pull-request-workflow` security-sensitive Diffs bereits routet); diese Spec fügt kein separates verpflichtendes Pre-Publish-Security-Gate hinzu
- **MUSS [MUST]** jede Zielgruppe gemäß `audience-identification` als `confirmed` oder `assumed` kennzeichnen; eine Release-Notes-Zielgruppe, die ohne Beleg (reale Vertretung, Subscriber-Signal, Nachweis eines automatisierten Konsumenten, referenzierendes Issue) beansprucht wird, bleibt `assumed`
- **SOLLTE [SHOULD]** die `release-drafter`-Kategoriekonfiguration des Projekts an den identifizierten Zielgruppen ausrichten — jede Kategorie existiert, weil mindestens eine Zielgruppe sie braucht; Kategorien ohne zugeordnete Zielgruppe werden entfernt
- **SOLLTE [SHOULD]** die PR-Label-Taxonomie und die Conventional-Commits-Scopes des Projekts so ausrichten, dass `release-drafter` die zielgruppengetriebenen Kategorien ohne manuelle Nachbearbeitung zusammenstellt
- **SOLLTE [SHOULD]** pro Zielgruppe das tatsächlich genutzte Konsumsignal dokumentieren — GitHub-Release-Feed / Atom, E-Mail-Abo, In-Product-Banner, Dependency-Bot-PR-Body, Release-Tracking-Dienst — weil das Signal die akzeptable Länge, Formatierung und Verlinkbarkeit einschränkt. Für automatisierte Konsumenten ist die Ermittlung eine manuelle Aufzählung der bekannten Bot-Menge des Projekts (Renovate, Dependabot, Release-Tracking-Bots) — kein GitHub-API-Subscriber-Audit, das nicht zuverlässig verfügbar ist — und die Validierung kippt den Eintrag `confirmed` / `assumed` über die Inspektion eines eingehenden Dependency-Bot-PR-Bodys oder die Beobachtung, welche Felder der Bot aus einem realen Release geparst hat (gemäß dem durchgearbeiteten Beispiel in §Abnahmekriterien)
- **SOLLTE [SHOULD]** die Release-Notes-Zielgruppenliste erneut prüfen, sobald das Projekt einen neuen Konsumkanal erhält (öffentliche HACS-Listung, erste Package-Registry-Veröffentlichung, Container-Registry-Push), eine regulierte Datenklasse hinzukommt oder das Projekt die Schwelle von intern zu öffentlich überschreitet
- **MUSS [MUST]** die Zielgruppenliste vorwärtsgerichtet anwenden: Sie gilt für Release Notes ab dem ersten nach Adoption veröffentlichten Release, und bereits veröffentlichte Release Notes sind ein unveränderliches Audit-Trail-Artefakt, das nicht gegen eine neu abgeleitete Liste re-auditiert oder umgeschrieben wird — analog zur Immutable-Publish-Haltung von `release-automation`
- **SOLLTE [SHOULD]** eine Änderung der Zielgruppenliste mitten im Release-Zyklus standardmäßig als nicht-blockierend behandeln — als Folge-Aufgabe, die gegen das nächste Release abgeglichen wird — AUSSER wenn sie eine primäre Breaking-Change- oder Security-Disclosure-Zielgruppe hinzufügt oder neu rankt, deren Inhaltsdimension nun unerfüllt ist; dieser Fall blockiert die Veröffentlichung gemäß §Abnahmekriterien (die Inhaltsdimensionen jeder primären Zielgruppe werden vor dem Dispatch von `release-publish.yml` verifiziert). Der Abgleich erfolgt durch erneutes Ausführen des Draft-Notes-Kurations-Skills (`release-notes-curate`), der den Block der bedienten Zielgruppen idempotent aus dem Artefakt neu ableitet
- **KANN [MAY]** bei einem kleinen, rein internen Projekt eine minimale Portfolio-Default-Release-Notes-Zielgruppenliste (Upgrader + Automatisierte Konsumenten + Beitragende), die `nolte/gh-plumbing` veröffentlicht, erben statt eine eigene zu erzeugen, und die Vererbung als Einzeiler-Referenz festhalten; jedes Projekt, das öffentliche GitHub-Releases publiziert, führt seine eigene Liste, weil `audience-identification` kontextbezogen und nicht organisationsweit ist
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
_Derzeit keine._

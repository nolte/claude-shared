# Defektklassen-Guards

Status: draft
Portfolio-Scope: portfolio

## Kontext

`spec/project/test-falsifiability/` behandelt Tests, die nicht fehlschlagen können. Diese Spec behandelt die andere Hälfte desselben Erkenntnisproblems: was ein **geschlossener** Defekt hinterlässt, damit seine Klasse nicht zurückkommen kann.

Die Evidenz ist eine Auswertung von 325 geschlossenen Issues in `nolte/kamerplanter`. Dreiundzwanzig davon benennen einen Vorgänger im eigenen Titel. Issue `#719` ist als dieselbe IDOR wie `#717` betitelt, `#948` als der schreibseitige Zwilling von `#927`, `#1018` als dieselbe Form wie `#997`, `#952` als die Cross-Tenant-Reads, die `#947` überlebt haben. Die Ketten laufen über vier und fünf Glieder. Die mediane Issue-Lebensdauer in diesem Repository liegt unter einem Tag; Durchsatz hat sie also nicht erzeugt. Jeder Fix reparierte die Stellen, die er gefunden hatte, und die nächste Meldung war derselbe Defekt an einer Stelle, auf die niemand geschaut hatte.

Dasselbe Repository besitzt auch die Heilung, undokumentiert. Es betreibt eine Reihe von `scripts/check_*.py`-Guards und Pre-Commit-Hooks, jeder benannt nach dem Issue, dessen Klasse er festzurrt: `boundary-validation` (`#970`), `utc-calendar-day` (`#858`), `tenant-body-field` (`#1000`), `workflow-gate-integrity` (`#1313`). Die Praxis funktioniert und existiert nirgends als Regel, also erbt sie kein anderes Repository, und das Repository, das sie erfunden hat, wendet sie ungleichmäßig an. `nolte/pre-commit-hooks` liefert zwei generische Hooks aus und kennt die Methode nicht.

Jede der folgenden Regeln ist aus einem konkreten Versagen in diesem Korpus verdient, nicht aus einem Prinzip abgeleitet. Diese Spec deklariert den Bezeichnerraum G1–G6, nach dem Vorbild von D1–D10 und T1–Tn in `spec/project/source-code-review/` und `spec/project/test-falsifiability/`.

Leser: wer einen Defekt schließt und dessen Pull Request verfasst, sowie Reviewer, die `source-code-review` D11 auf die Guards anwenden, die ein Fix hinterlässt.

## Ziele

- Ein geschlossener Defekt hinterlässt etwas Mechanisches, das seine Klasse zurückweist, sodass die Klasse geschlossen wird und nicht die Instanz
- Das Hinterlassene ist vom Issue aus auffindbar, und das Issue von ihm aus
- Der Geltungsbereich eines Guards ist lesbar: eine Leserin erkennt ohne Ausführen, was er aufzählt
- Die Regeln sind billig genug, dass ein Einzeiler-Fix keine Zeremonie erwirbt, und ehrlich genug, dass „kein Guard möglich" eine verfügbare Antwort mit Preisschild bleibt

## Nicht-Ziele

- Die Technologie des Guards vorzuschreiben. Ein Unit-Test, eine Lint-Regel, ein Pre-Commit-Hook, eine Compiler-Einstellung oder ein Typ, der den schlechten Zustand unausdrückbar macht, sind alle Guards; welcher passt, entscheidet das Repository
- Testdesign vorzuschreiben. Ein Guard ist oft ein Test, und dann regeln `spec/project/test-falsifiability/` und die Stufen-Specs, wie er geschrieben wird
- Branch Protection zu besitzen. Ob eine Lane erzwungen ist, entscheidet `spec/project/quality-gate/` §"Erzwungene Lane je Stufe"; G2 konsumiert diese Antwort, statt sie zu wiederholen
- Rückwirkende Anwendung. Diese Regeln binden Defekte, die nach Annahme der Spec geschlossen werden; die Historie eines Repositories durchzukehren ist eine separate, optionale Übung

## Anforderungen

### Die Regeln

- **G1—Eine geschlossene Defektklasse hinterlässt einen Guard, oder eine schriftliche Notiz, warum das nicht geht.** Das Schließen eines Defekts **MUSS** entweder einen mechanischen Guard hinterlassen, der die Klasse zurückweist, oder eine Notiz im Issue, die festhält, warum kein mechanischer Guard möglich ist und worauf eine Leserin stattdessen achten sollte. Ein Abschluss, der nur sagt, der Fix sei offensichtlich und komme nicht wieder, ist keine Notiz; das ist die Überzeugung, die jede Kette im Korpus erzeugt hat. Die Notiz ist der ehrliche Ausgang, und sie **MUSS** aufgeschrieben werden, denn eine ungeschriebene ist von „nicht darüber nachgedacht" nicht unterscheidbar.
- **G2—Der Guard läuft in einer erzwungenen Lane.** Ein Guard **MUSS** dort laufen, wo er den Merge blockieren kann, der die Klasse wieder einführen würde. Ein Guard in einer beratenden Lane ist ein Kommentar: Er erzeugt ein Signal, das niemand lesen muss — dasselbe Vertrauensversagen, das `test-falsifiability` §Kontext von der anderen Seite beschreibt. Welche Lanes erzwungen sind, entscheidet `spec/project/quality-gate/` §"Erzwungene Lane je Stufe", und das dortige Verbot, eine guardtragende Stufe auszunehmen, ist die Hälfte dieser Regel, die dort wohnt. Wo ein Guard tatsächlich nicht vor einem Merge laufen kann, weil er eine deployte Umgebung, ein Nachtfenster oder echte Zugangsdaten braucht, **MUSS** er dieselbe schriftliche Notiz tragen, die G1 verlangt, und benennen, was er nicht abdeckt und wann er läuft.
- **G3—Der Guard zählt die Klasse auf; er prüft nicht die Fundstelle.** Ein Guard **MUSS** als Prädikat über die ganze Klasse geschrieben sein und **DARF NICHT** eine Prüfung sein, die an die Stellen gebunden ist, an denen der Defekt zufällig gefunden wurde. Ein aufzählender Guard findet das Mitglied, auf das noch niemand geschaut hat; ein stellengebundener findet konstruktionsbedingt nichts Neues, und eine neue Stelle wird nur von der Person eingetragen, die sich daran erinnert. Das Prädikat **MUSS** im Header oder Docstring des Guards selbst stehen, nicht nur in der Commit-Message oder im Pull Request, der ihn eingeführt hat, denn das ist die Kopie, die eine Leserin vor sich hat, wenn sie entscheidet, ob ein neuer Fall abgedeckt ist.
- **G4—Ausnahmen sind eine Allowlist mit Begründung je Eintrag, und ein veralteter Eintrag lässt den Guard fehlschlagen.** Wo die Klasse legitime Mitglieder hat, die erlaubt sein müssen, **MÜSSEN** diese eine explizite, beim Guard geführte Allowlist sein, jeder Eintrag mit seiner Begründung, und ein Eintrag, der auf nichts mehr passt, **MUSS** den Guard fehlschlagen lassen. Ohne die Veraltungsregel wächst die Allowlist nur: Einträge überleben ihren Grund, und die Abdeckung des Guards schrumpft still in der einen Richtung, auf die niemand schaut. Eine Begründung **MUSS** es überstehen, gegen das gelesen zu werden, was sie entschuldigt. Der Abschlussvermerk zu `#1353` in kamerplanter benennt drei Allowlist-Einträge, deren Begründung die Review nicht überstand und die echte Defekte entschuldigten — schlimmer als keine Allowlist, weil es die Drift als genehmigt festschreibt.
- **G5—Der Guard trägt die Issue-Nummer.** Der Name einer Guard-Datei, eines Guard-Tests oder einer Guard-Regel **MUSS** die Issue-Nummer des Defekts tragen, den er schließt, damit Befund und Regel voneinander auffindbar bleiben. Nicht jeder Guard hat einen eigenen Namen: ein erforderlicher Keyword-only-Parameter, ein verengter Typ oder eine Signatur, die den falschen Aufruf nicht kompilieren lässt, ist ein Guard ohne Platz für eine Nummer. Ein solcher Guard **MUSS** die Issue-Nummer im Docstring oder Kommentar an der Einschränkung selbst tragen, und genau diese Platzierung ist der Punkt: Wer die Signatur gleich wieder aufweiten will, ist die Person, die den Grund braucht.
- **G6—Der Selektor passt zum Geltungsbereich der Eigenschaft.** Der Selektor eines Guards **MUSS** so weit sein wie die Eigenschaft, die er behauptet. Wo die Eigenschaft der zusammengesetzten Anwendung gehört, **DARF** der Selektor **NICHT** ein Dateiname, ein Verzeichnis oder eine andere Liste sein, der eine neue Datei nur durch korrekte Benennung beitritt. Das sind Opt-in-Listen mit genau dem Loch, das der Guard schließen soll, eine Ebene höher. Leite die Menge aus dem ab, was die Eigenschaft trägt: aus dem gemounteten Router statt aus den Modulen, die wie Router aussehen; aus dem aufgelösten Abhängigkeitsgraphen statt aus der Importliste; aus dem gebauten Artefakt statt aus dem Quellverzeichnis.

### Verhältnismäßige Anwendung

Ein Einzeiler-Fix darf keine Zeremonie erwerben. Die Regeln skalieren mit der Klasse, nicht mit dem Diff:

- Ein Defekt, dessen Klasse genau ein Mitglied hat, erfüllt G1 mit der Notiz, die das in einem Satz sagt. Diesen Satz zu schreiben kostet eine Zeile, und er ist die ganze Arbeit
- Wo für die Klasse bereits ein Guard existiert und der Defekt an ihm vorbeigerutscht ist, besteht die Arbeit darin, sein Prädikat oder seinen Selektor zu reparieren (G3, G6), nicht darin, einen zweiten Guard daneben zu stellen. Zwei Guards für eine Klasse driften, und auch diese Form enthält der Korpus
- Wo die Klasse so groß ist, dass der Guard nicht in derselben Änderung entstehen kann, **MUSS** der Guard ein eigenes Issue sein, referenziert vom schließenden, statt eine im Pull-Request-Body festgehaltene Absicht. Eine Absicht in einem gemergten Body geht beim Merge verloren

### Bindung in den Abschlussprozess

- Ein Pull Request, der einen Defekt schließt, **MUSS** festhalten, was seine Klasse hinterlassen hat, und `spec/project/pull-request-workflow/` §"Klassen-Sweep (Conventional-Commits-Typ `fix`)" ist der Ort dafür: das dortige Feld `Guard` ist die G1-Antwort dieser Spec, und das Feld `Predicate` ist das Prädikat aus G3. Beide Specs beschreiben ein Artefakt von zwei Seiten, und die Felder **DÜRFEN NICHT** auseinanderlaufen: wo ein Guard existiert, ist sein eigener Selektor das, was der Sweep zitiert
- `spec/project/issue-orchestration/` macht den ausgefüllten Sweep zur Abschlussbedingung eines orchestrierten Laufs
- `spec/project/source-code-review/` D11 ist der Ort, an dem die Konformität eines bestehenden Guards zu G3, G4 und G6 im Review bewertet wird, unabhängig von einem einzelnen Defekt

## Akzeptanzkriterien

- [ ] Für eine Stichprobe jüngst geschlossener Defekte hinterließ jeder entweder einen Guard oder eine schriftliche Notiz, warum keiner möglich ist; kein Abschluss stützt sich auf ein ungeschriebenes Urteil, die Klasse könne nicht wiederkehren
- [ ] Das Prädikat jedes Guards ist im Header oder Docstring des Guards selbst lesbar und beschreibt eine Klasse statt der Stellen, an denen der Defekt gefunden wurde
- [ ] Jeder Guard läuft in einer Lane, die einen Merge blockieren kann, oder trägt eine Notiz, die benennt, was seine Lane nicht abdeckt und wann er läuft
- [ ] Jeder Allowlist-Eintrag trägt eine Begründung, und das Entfernen eines passenden Subjekts lässt den Guard am nun veralteten Eintrag fehlschlagen — geprüft durch Entfernen, nicht durch Hinsehen
- [ ] Der Name jedes Guards trägt die Issue-Nummer des Defekts, den er schließt, und jeder Guard ohne eigenen Namen, etwa ein erforderlicher Parameter oder ein verengter Typ, trägt sie an der Einschränkung
- [ ] Kein Guard, der eine Eigenschaft der zusammengesetzten Anwendung behauptet, wählt seine Subjekte über Dateinamen oder Verzeichnis aus
- [ ] **Falsifikation.** Von Hand auf die Kette `#927 → #948 → #950 → #952 → #1263` in kamerplanter angewandt, identifizieren diese Regeln, an welchem Glied die Klasse hätte aufgezählt werden müssen und welche Regel verletzt wurde. Ein Regelsatz, der diese Kette als konform bewertet, ist falsch und wird überarbeitet, bevor er landet

## Referenzen

Jede Referenz unten ist ein Issue oder Pull Request in `nolte/kamerplanter`, am 2026-09-12 aus erster Hand gelesen. Sie sind der Korpus, aus dem die Regeln abgeleitet sind, keine externe Autorität. Ein Issue im Schwester-Repository hat genau einen kanonischen Ort, daher ist das Lesen aus erster Hand das, was `spec/claude/research-triangulate/` §Wann Triangulation Pflicht ist von ihm verlangen kann: eine zweite Quelle würde denselben Datensatz erneut lesen, statt eine unabhängig variierende Tatsache zu bestätigen.

- G1, G3: die Kette `#927` (Cross-Tenant-Reads, auf der Repository-Ebene geschlossen) → `#948` (der schreibseitige Zwilling, der die Klasse benennt und das Durchkehren zum Akzeptanzkriterium macht) → `#950` → `#952` → `#1263`. `#1263` hält fest, dass `#948` zwei der vier Routen mit seiner Form reparierte
- G3, G6: `#1353` und sein Abschlussvermerk. Der zuerst beschriebene Sweep schlüsselte auf den Dateinamen `tenant_router.py` und konnte drei Routen in `nutrient_calculations/router.py` und `plant_instances/diary_router.py` nicht sehen; der ausgelieferte Guard berechnet die Menge stattdessen aus dem gemounteten Router
- G4: der Abschlussvermerk zu `#1353`, zu drei Allowlist-Einträgen, deren Begründungen das Lesen gegen die von ihnen entschuldigten Routen nicht überstanden
- G2, G5: die benannten Guards `boundary-validation` (`#970`), `utc-calendar-day` (`#858`), `tenant-body-field` (`#1000`), `workflow-gate-integrity` (`#1313`) sowie `#1404`, wo ein Guard in einer Lane saß, die keinen Merge blockieren konnte

## Offene Fragen

_Derzeit keine._

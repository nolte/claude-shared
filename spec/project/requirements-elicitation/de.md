# Anforderungserfassung per Interview

Status: draft

## Kontext

Wenn ein KI-Agent beauftragt wird, etwas zu bauen, zu ändern oder zu spezifizieren, ist die empfangene Anfrage fast nie eine vollständige, eindeutige Spezifikation. Der Anfragende ist ein Mensch, der unter drei strukturellen Handicaps operiert, die die Requirements-Engineering-Forschung als Normalfall behandelt, nicht als Ausnahme:

- **Er weiß oft nicht, was er will**, bis er einen Kandidaten sieht — das *IKIWISI*-Problem („I'll know it when I see it"). Vieles von dem, was ein Nutzer braucht, ist *stillschweigendes Wissen* (tacit knowledge, Polanyi): real, tragend, aber nie geäußert, weil der Nutzer es nicht bewusst als formulierbaren Fakt besitzt. Boehm nennt dies das IKIWISI-Syndrom und verschreibt nebenläufiges Prototyping statt vollständiger Vorab-Anforderungen [R13].
- **Er drückt sich unvollkommen aus.** Anfragen in natürlicher Sprache sind durchsetzt von Optionalität, Subjektivität, Vagheit, Schwächewörtern, freistehenden Pronomen und stiller Unterspezifikation. Empirische NLP-für-RE-Studien zeigen, dass diese Defekte allgegenwärtig und häufig *unbewusst* sind — jede Partei ist sich ihrer eigenen Lesart sicher, während die Lesarten auseinandergehen [R8].
- **Er wird missverstanden.** Selbst eine wohlgeformte Anfrage kann der Agent fehllesen. Der gefährliche Fall ist der *selbstsichere Fehlgriff*: Der Agent fährt fort, als hätte er verstanden, produziert ein plausibles Artefakt, und die Lücke zeigt sich erst, nachdem teure Arbeit getan ist. Eine Interpretation, die intern akzeptabel, aber falsch ist, wird stillschweigend erfasst: Solange keine Konsistenzprüfung ihr widerspricht, bleibt der Fehlgriff unentdeckt [R14].

Ein Agent, der die Anfrage einfach auf die nächstliegende plausible Lösung mustert, verstärkt alle drei Fehler. Die billige, hebelstarke Intervention ist ein **diszipliniertes Erfassungs-Interview** — ein begrenzter, adaptiver Dialog, der das *Verständnis* des Agenten bis zu einer gemessenen Schwelle hochtreibt, bevor er sich aufs Bauen festlegt — gepaart mit einer **quantifizierten Verständnis-KPI**, die dem Agenten je Anforderungsdimension sagt, wie gut er tatsächlich versteht, sodass er *gezielt* genau dort nachfragt, wo das Verständnis schwach ist, und dort aufhört zu fragen, wo es stark ist.

Diese Spezifikation definiert dieses Interview-Verfahren und diese KPI. Die KPI ist ein **Confidence-Score je Anforderungsdimension** plus eine **Lücken-Matrix** über eine geschlossene Menge von Dimensionen; zusammen steuern (gaten) sie, ob der Agent eine Rückfrage stellt, welche Frage er stellt und wann das Interview abgeschlossen ist. Das Verfahren ist modell- und domänenunabhängig: Es schreibt die *Form* des Interviews und die *Gestalt* der Metrik vor, nicht eine bestimmte ML-Implementierung oder einen bestimmten Prompt. Die realisierende Capability in diesem Plugin ist der `requirements-elicit`-Skill, der das Interview führt, die Lücken-Matrix pflegt, das Gating anwendet und das Artefakt schreibt.

Das Modell ist in etablierter Literatur verankert, nicht erfunden: die empirische Typologie von Erfassungs-Interviewfragen und die offen→spezifisch-Sequenzheuristik [R1]; die gemessene Baseline, dass ein LLM-Interviewer ~74 % Anforderungs-Recall bei menschenvergleichbarer Fehlerrate erreicht (eine einzelne simulierte Studie; Parität, nicht Überlegenheit) und dass leichtgewichtiges One-Question-at-a-time-Prompting schwere prozedurale Skriptung schlägt [R3]; die Auswahl von Klärungsfragen als Bayessches Versuchsdesign, das den erwarteten Informationsgewinn über den *Lösungsraum* maximiert [R4]; die Trennung von *Spezifikationsunsicherheit* (was der Nutzer will) und *Modellunsicherheit* (was der Agent vorhersagt) sowie EVPI-bewertete, kostenbewusste Frageauswahl [R5], [R12]; der verhaltensbasierte Self-Consistency-Proxy für Mehrdeutigkeit — mehrere Interpretationen sampeln, Divergenz als Mehrdeutigkeitssignal werten [R6]; kontrollierte-natürliche-Sprache-Zielstrukturen (EARS, Rimay), die atomare, eindeutige, vollständige Anforderungen erzwingen [R7], [R9]; der recall-favorisierte Mehrdeutigkeitserkennungs-Trade-off mit seiner benannten, trigger-wort-gestützten Defekt-Trigger-Liste [R8], [R10]; das IKIWISI-Syndrom mit nebenläufigem Prototyping als Abhilfe (Boehm [R13]); und Mehrdeutigkeit als *Ressource* verstanden, die stillschweigendes Wissen zu Tage fördert, wobei Missverständnis als Konsistenzprüfung gegen die Wissensbasis des Analysten erkannt wird (Ferrari, Spoletini, Gnesi [R14]).

Leser: Autoren des `requirements-elicit`-Skills und der nachgelagerten Planungs-Gates (roadmap-plan, feature-decompose, issue-orchestrate), die sein Artefakt konsumieren, sowie Reviewer, die beurteilen, ob eine erfasste Anforderung präzise genug ist, um darauf aufzubauen.

## Ziele
- Ein wiederholbares, adaptives Interview-Verfahren definieren, das ein KI-Agent ausführt, um die Anforderungen eines Nutzers so zielgenau wie möglich zu erfassen
- Das Nicht-Wissen, Fehl-Ausdrücken und Missverstanden-Werden des Nutzers als den Normalfall behandeln, gegen den das Verfahren konstruiert ist, nicht als Randfall
- Eine quantifizierte Verständnis-KPI definieren — einen **Confidence-Score je Dimension** plus eine **Lücken-Matrix** über eine geschlossene Menge von Anforderungsdimensionen
- Klärung **Confidence-gesteuert** machen: nur dort nachfragen, wo das Verständnis messbar schwach ist, und die einzelne informativste Frage stellen, wobei Missverständnisrisiko gegen Nutzer-Ermüdung abgewogen wird
- Ein explizites Sättigungs-/Abbruchkriterium definieren, sodass das Interview endet, wenn das Verständnis ausreicht, nicht wenn dem Agenten die naheliegenden Fragen ausgehen
- Den Agenten verpflichten, das Verständnis durch Rückspiegelung (Teach-back) zu validieren, bevor eine Anforderung als verstanden gilt
- Ein strukturiertes, auditierbares Ergebnis erzeugen: die Anforderungsliste, die ausgefüllte Lücken-Matrix mit finalen Confidences und die explizite Liste überlebender Annahmen

## Nicht-Ziele
- Ein vollständiger Requirements-Engineering-Prozess: Priorisierung, Verhandlung zwischen konfligierenden Stakeholdern, Backlog-Pflege, Change-Management und Traceability-zu-Tests über die erfasste Menge hinaus sind außerhalb des Scopes
- Stakeholder-/Audience-Identifikation — das ist `spec/project/audience-identification/`; diese Spec setzt voraus, dass die befragte Partei bereits bekannt ist
- Zerlegung der erfassten Anforderungen in Features, Sprints oder einen Implementierungsplan — das ist `spec/project/feature/` und `spec/project/spec-driven-development/`
- Vorschreiben eines bestimmten Uncertainty-Quantification-Algorithmus, Kalibrierungsmodells oder Prompts. Diese Spec definiert die *Gestalt* des Confidence-Scores und der Lücken-Matrix sowie die *Regeln*, die sie steuern; der Schätzer ist eine Implementierungsentscheidung
- Prototyping-Werkzeuge. Prototypen und Beispiele werden als Erfassungs-*Techniken* benannt, aber ein Prototyping-Werkzeug zu bauen ist außerhalb des Scopes
- Ersatz für menschliche Domänenexpertise. Wenn eine Frage Autorität erfordert, die der Nutzer nicht besitzt, legt das Verfahren die Lücke offen; es erfindet keine Antwort
- Verfassen des nachgelagerten Spezifikationsdokuments selbst (das ist der `spec`-Skill / `spec-driven-development`); Erfassung speist Spezifikation, sie *ist* keine Spezifikation

## Anforderungen

### A. Interview-Struktur und Frageführung

- **MUST** das Interview als adaptiven Dialog führen und **eine Frage (oder eine eng gekoppelte Fragegruppe) pro Zug** stellen statt eines langen Vorab-Fragebogens; leichtgewichtiges One-Question-at-a-time-Tempo erfasst empirisch mehr Anforderungen, nicht weniger, als schwere prozedurale Skriptung [R3]
- **MUST** einer **Trichter-Sequenz** folgen: das Interview mit breiten, offenen Fragen eröffnen und schrittweise zu spezifischen, geschlossenen Fragen verengen, sobald das Verständnis fester wird [R1]
- **MUST** **Probing-Fragen** (Fragen, die als direkte Reaktion auf eine vorherige Antwort gestellt werden) als primäres Instrument zur Vertiefung des Verständnisses einsetzen, gestützt auf die etablierten Probe-Typen: *Elaboration* („sag mehr zu X"), *Interpreting* („du meinst also Y?"), *Reason-seeking* („warum ist das wichtig?") und *Consistency* („vorhin sagtest du A — wie passt das zu B?") [R1]
- **MUST** jede gestellte Frage nach Zielsetzung klassifizieren, damit das Interview ausgewogen bleibt: *Coverage* (eine neue Dimension öffnen), *Deepening* (eine geöffnete Dimension vertiefen) oder *Validation* (eine verstandene Dimension per Teach-back bestätigen)
- **SHOULD** **szenario- und beispielgetriebene Fragen** nutzen — konkrete Fälle, Durchspielen, „zeig mir, wie gut aussieht" — um Anforderungen zu Tage zu fördern, die der Nutzer nicht abstrakt benennen kann (der IKIWISI-Mechanismus)
- **SHOULD** adaptive, kontextspezifische Folgefragen einem starren vorgeschriebenen Skript vorziehen; das Skript definiert Abdeckungspflichten, keine feste Zugreihenfolge [R3]

### B. Umgang mit stillschweigendem Wissen, IKIWISI und Wunsch-vs-Bedarf

- **MUST** seine Arbeits-**Annahmen explizit machen** und zur Bestätigung vorlegen, statt still darauf aufzubauen; eine unbestätigte Annahme wird als `assumed` erfasst, nie als `confirmed`
- **MUST** **konkrete Beispiele, Gegenbeispiele und negative Szenarien** anbieten („wäre es akzeptabel, wenn … ?", „was sollte *niemals* passieren?"), um Grenzen zu erheben, die der Nutzer nicht abstrakt äußern kann
- **MUST** **Edge-Cases, Fehlerzustände und „Was-wäre-wenn"-Bedingungen** prüfen, bevor eine funktionale Dimension als verstanden gilt — das sind die Dimensionen, die Nutzer am verlässlichsten auslassen
- **SHOULD** **Wunsch von Bedarf trennen**, indem es auf das Rationale laddert (Reason-seeking-Probes): eine genannte Lösung auf das zugrunde liegende Ziel zurückführen, sodass der Agent den Bedarf löst statt die erstvorgeschlagene Lösung abzuschreiben
- **SHOULD** die erste Formulierung des Nutzers als zu prüfende Hypothese behandeln, nicht als abzuschreibende Spezifikation

### C. Mehrdeutigkeits- und Missverständnis-Erkennung

- **MUST** jede Nutzeräußerung gegen eine **nicht-erschöpfende Trigger-Wort-Checkliste** benannter Mehrdeutigkeitsklassen prüfen (projektweise erweiterbar und nie als vollständige Klassifikation von Missverständnis behandelt) und jeden Treffer zur Klärung oder zum Teach-back flaggen: *Optionalität* (kann/darf/optional), *Subjektivität* (ähnlich/besser/benutzerfreundlich), *Vagheit* (signifikant/angemessen/schnell), *Schwäche* (könnte/sollte/darf), *syntaktische Implizitheit* (Pronomen, indirekte Referenzen), *Multiplizität* (mehr als ein Hauptverb/Subjekt/Objekt in einer Anforderung) und *Unterspezifikation* (eine referenzierte Größe, Einheit, ein Akteur oder eine Bedingung fehlt) [R8], [R10]
- **MUST** jede verstandene Anforderung in eine **atomare, eindeutige Zielstruktur** normalisieren — eine EARS-artige Schablone („WENN <Trigger>, SOLL das <System> <Reaktion>") oder äquivalente kontrollierte natürliche Sprache — und jede Anforderung, die sich der Normalisierung widersetzt, als noch-nicht-verstanden flaggen [R7], [R9]
- **MUST** das Verständnis per **Teach-back** validieren: die Interpretation des Agenten dem Nutzer in dessen Begriffen zurückspiegeln und eine explizite Bestätigung einholen, bevor die Confidence einer Anforderung die „verstanden"-Schwelle (§D) überschreiten darf. Eine Anforderung, die der Nutzer nicht per Teach-back bestätigt hat, DARF NICHT als `confirmed` berichtet werden
- **SHOULD** **Recall vor Precision** bevorzugen bei der Entscheidung, ob etwas mehrdeutig ist: eine unnötige Klärung ist billig, eine übersehene Mehrdeutigkeit propagiert in das gebaute Artefakt. Im Zweifel flaggen [R8], [R10]
- **SHOULD** *unbewusste* Mehrdeutigkeit erkennen — Fälle, in denen die Äußerung klar liest, aber mehr als eine vertretbare Interpretation zulässt — über den Self-Consistency-Check in §D, nicht nur über oberflächliche Trigger-Wörter [R6], [R8]

### D. Verständnis-KPI: Confidence-Score und Lücken-Matrix

- **MUST** das Verständnis als **Lücken-Matrix** über eine geschlossene Menge von **Anforderungsdimensionen** modellieren, jede entweder als anwendbar oder explizit als „n/a (Grund)" markiert:
  - `functional`: was das System tun muss
  - `non_functional`: Performance, Sicherheit, Usability und andere Qualitätsattribute
  - `constraints`: Technologie-, Budget-, Regulierungs-, Kompatibilitäts- und Plattformgrenzen
  - `domain_objects`: die beteiligten Entitäten, Daten und das Domänenvokabular
  - `actors`: wer/was mit dem System interagiert
  - `acceptance_criteria`: wie „fertig" und „korrekt" beurteilt werden
  - `edge_cases`: Fehlerzustände, Grenzen und Ausnahmebedingungen
  - `scope_boundaries`: was explizit in und außerhalb des Scopes liegt
- **MUST** je anwendbarer Dimension einen **Confidence-Score** `c_d ∈ [0,1]` führen, der ausdrückt, wie gut der Agent diese Dimension zu verstehen glaubt. Dieser Score ist ein *Unsicherheits-Proxy* (ein aus Self-Consistency abgeleitetes Signal), keine kalibrierte Wahrscheinlichkeit; er MUSS als relative Ordnung das Gating steuern und DARF NICHT als wörtliche Korrektheits-Wahrscheinlichkeit berichtet werden [R6]
- **MUST** zwei Unsicherheitsquellen bei der Schätzung von `c_d` trennen und in der Matrix unterscheidbar halten: **Spezifikationsunsicherheit** (der Nutzer hat nicht festgelegt oder ausgesprochen, was er will) versus **Interpretationsunsicherheit** (der Nutzer war vielleicht klar, aber der Agent ist unsicher, ob er ihn korrekt gelesen hat). Beide erfordern unterschiedliche Abhilfen — Spezifikationsunsicherheit braucht eine entscheidungserhebende Frage an den Nutzer; Interpretationsunsicherheit braucht eine Teach-back-Bestätigung [R5], [R12]
- **MUST** `c_d` gegen ein **Verhaltenssignal kalibrieren, nicht gegen Selbstauskunft allein**: der Referenzmechanismus ist *Self-Consistency* — `k ≥ 2` unabhängige Interpretationen (oder Lösungsskizzen) für die Dimension generieren; je stärker sie divergieren, desto niedriger `c_d` und desto stärker das Mehrdeutigkeitssignal. Verbalisierte/selbstberichtete Confidence DARF dies ergänzen, DARF ABER NICHT der alleinige Input sein, da unkalibrierte Selbst-Confidence das Verständnis systematisch überschätzt [R6]
- **MUST** einen **aggregierten Gating-Score** `U` über die anwendbaren erforderlichen Dimensionen definieren. Da ein einzelnes schweres Missverständnis schädlicher ist als breite milde Unsicherheit, MUSS das Gate von der **schwächsten erforderlichen Dimension** bestimmt werden — `U_gate = min_d c_d` über erforderliche Dimensionen — auch wenn zusätzlich ein gewichtetes Mittel zur Transparenz berichtet wird
- **MUST** zwei Schwellenwerte definieren und anwenden, mit dokumentierten, projekt- und risikoanpassbaren Defaults:
  - `τ_low` (Default **0.4**): jede Dimension mit `c_d < τ_low` **MUSS** eine Klärung auslösen, bevor das Interview darüber hinausgehen darf
  - `τ_high` (Default **0.8**): eine Dimension gilt erst dann als „verstanden", wenn `c_d ≥ τ_high` *und* (für `functional`, `acceptance_criteria` und jede nutzerseitige Dimension) eine Teach-back-Bestätigung eingeholt wurde
  - das Band `τ_low ≤ c_d < τ_high` ist die **Ermessenszone**: nur klären, wenn der erwartete Informationsgewinn die Fragekosten rechtfertigt (§E)
- **SHOULD** die Lücken-Matrix dem Nutzer auf Anfrage **sichtbar machen** — eine schlichte „das verstehe ich / das ist noch unklar"-Ansicht — sodass der Mensch eine fehlkalibrierte Zelle direkt korrigieren kann
- **MUST** `c_d` nur durch Evidenz erhöhen (eine Nutzerantwort, eine bestätigte Annahme, ein erfolgreicher Teach-back), nie durch das bloße Vergehen von Interview-Zügen

### E. Auswahl der nächsten (Klärungs-)Frage

- **MUST** entscheiden, **ob** gefragt wird — eine Klärungsfrage nur stellen, wenn die **erwartete Unsicherheitsreduktion** (erwarteter Informationsgewinn, oder Expected Value of Perfect Information, EVPI) die **Kosten** des Fragens übersteigt (die Nutzer-Ermüdungs- und Latenzkosten eines weiteren Zugs). Unter `τ_low` dominiert der Gewinn und eine Frage ist verpflichtend; in der Ermessenszone entscheidet der EVPI/Kosten-Vergleich [R4], [R5]
- **MUST** **welche** Frage zu stellen ist durch Maximierung des Informationsgewinns **über den Raum gangbarer Interpretationen/Lösungen** wählen, nicht bloß über den Raum der Kandidatenfragen — d. h. die Frage bevorzugen, die die Menge unterschiedlicher gangbarer Lesarten der Anforderung am stärksten schrumpft; Auswahl durch Schlussfolgern über den Lösungsraum schlägt empirisch die Auswahl durch Schlussfolgern allein über Fragen [R4]
- **MUST** die Frage zuerst auf die **erforderliche Dimension mit der niedrigsten Confidence** richten (die Dimension, die `U_gate` setzt), sodass jeder Zug die bindende Beschränkung des Gesamtverständnisses anhebt
- **MUST** **redundante Fragen unterdrücken** — Fragen, deren Antwort bereits durch eine bestätigte Zelle impliziert ist — über eine Aspekt-/Abdeckungsprüfung vor dem Fragen [R5]
- **SHOULD** die Klärung so formulieren, dass sie die *spezifische* erkannte Mehrdeutigkeit offenlegt (die divergierenden Interpretationen als Optionen anbieten), statt ein offenes „kannst du das klären?" zu fragen, sodass die Nutzerantwort maximal disambiguiert [R6]
- **SHOULD** Über-Fragen (Nutzer-Ermüdung, Abbruch) gegen Unter-Fragen (selbstsicherer Fehlgriff) explizit abwägen; die EVPI/Kosten-Regel ist das Abwägungsinstrument, und das Frage-Budget pro Interview (§F) ist ihr Sicherungsnetz

### F. Sättigung und Abbruch

- **MUST** das Interview beenden, wenn **alle** folgenden Bedingungen gelten, und den Abschluss melden: jede erforderliche, anwendbare Dimension hat `c_d ≥ τ_high` (mit Teach-back, wo §D es verlangt), **und** keine verbleibende Kandidatenfrage hat positiven Netto-EVPI (Sättigung — weitere Fragen würden die erfasste Menge nicht ändern) [R5]. Es existiert kein forschungsvalidiertes Terminierungskriterium für Erfassungs-Interviews; diese Regel ist eine Engineering-Konstruktion über der Confidence-/EVPI-Maschinerie, kein Literaturergebnis
- **MUST** ein **hartes Frage-Budget** pro Interview als Sicherung gegen nicht-terminierende Dialoge durchsetzen; bei Erreichen MUSS der Agent stoppen und übergeben, wobei jede Zelle unter `τ_high` explizit als Restrisiko geflaggt wird, statt sie still als verstanden zu behandeln
- **MUST** bei jedem Stopp (gesättigt oder budgetbegrenzt) die **überlebenden Annahmen und Zellen unter der Schwelle** als benannte offene Risiken am Output ausweisen
- **SHOULD** Stoppen einer weiteren geringwertigen Frage vorziehen, sobald Sättigung erreicht ist: eine selbstsicher verstandene kleinere Menge schlägt einen ermüdeten Nutzer und eine aufgeblähte Menge

### G. Output-Artefakt

- **MUST** als Liefergegenstand des Interviews ausgeben: (1) die erfasste **Anforderungsliste** in der normalisierten Zielstruktur (§C), (2) die **ausgefüllte Lücken-Matrix** mit finalen Confidences je Dimension und dem aggregierten `U_gate`, und (3) die explizite Liste der **überlebenden Annahmen / offenen Risiken** (§F)
- **MUST** das Artefakt unter `project/requirements/<slug>.md` persistieren, pluralisiert wie `project/features/`, sodass mehrere Anforderungs-Sets (pro Scope, Outcome oder Feature) koexistieren und ein nachgelagerter Konsument genau eines deterministisch referenzieren kann
- **MUST** jede Anforderung als `confirmed` (per Teach-back oder autoritativer Nutzerantwort validiert) oder `assumed` (gefolgert und noch nicht bestätigt) taggen, spiegelbildlich zur Matrix
- **SHOULD** **Traceability** von jeder erfassten Anforderung zurück zu der/den Nutzeräußerung(en) anhängen, die sie erzeugt haben, sodass ein Reviewer auditieren kann, wie eine Interpretation entstand
- **SHOULD** das Artefakt dem nachgelagerten Konsumenten (Feature-Zerlegung, Spec-Autorenschaft) in einer Form übergeben, die diese referenzieren können, statt erneut zu erfassen

### H. Konsumenten-Vertrag

- **MUST** für die nachgelagerten Planungs-Capabilities gelten, die Anforderungen voraussetzen, mindestens `roadmap-plan`, `feature-decompose` und `issue-orchestrate`: vor substanzieller Zerlegung MUSS jede prüfen, ob ein Anforderungs-Artefakt (§G) für die anstehende Arbeit existiert und ob dessen `U_gate` `τ_high` erreicht. Wenn kein Artefakt existiert oder `U_gate` unter `τ_high` liegt, MUSS der Konsument zuerst `requirements-elicit` dispatchen oder einen expliziten Operator-Override protokollieren, statt gegen ungenannte oder schwach verstandene Anforderungen zu zerlegen. Dies spiegelt das vorgelagerte Gate, das `audience-identification` audience-beanspruchenden Artefakten auferlegt.
- **MUST NOT** das Gate als hart-blockierend behandeln, sobald der Operator die überlebenden Lücken explizit akzeptiert; das Gate legt schwaches Verständnis offen, es verbietet das Fortfahren nicht, und der Override wird protokolliert statt stillschweigend angewandt.
- **SHOULD** das Artefakt über seinen Pfad (`project/requirements/<slug>.md`) referenzieren statt erneut zu erfassen, sodass eine Erfassung Roadmap-Planung, Feature-Zerlegung und Issue-Orchestrierung gleichermaßen speist.

## Akzeptanzkriterien
- [ ] Ein durchgearbeitetes Beispiel existiert, das das Verfahren auf eine konkrete Erfassung in diesem Repository anwendet (zum Beispiel das Erfassen der Anforderungen für einen neuen Skill, bevor `skill-management` ihn scaffoldet)
- [ ] Das Interview-Transkript zeigt One-Question-per-Turn-Tempo und einen sichtbaren offen→spezifisch-Trichter
- [ ] Jede erfasste Anforderung ist in der normalisierten EARS/CNL-Zielstruktur gerendert oder als noch-nicht-verstanden geflaggt
- [ ] Der Output enthält eine Lücken-Matrix, die jede Dimension aus §D abdeckt, jede markiert als anwendbar-mit-`c_d` oder „n/a (Grund)"
- [ ] Jede `c_d` ist durch ein benanntes Evidenz-Ereignis begründet (Nutzerantwort / bestätigte Annahme / erfolgreicher Teach-back), und mindestens eine `c_d` wurde aus einem `k ≥ 2`-Self-Consistency-Check abgeleitet statt aus Selbstauskunft
- [ ] Das Transkript zeigt mindestens eine Klärung, die *zurückgehalten* wurde, weil ihr EVPI ihre Kosten nicht überstieg (Zurückhaltung in der Ermessenszone), und mindestens eine, die *erzwungen* wurde, weil eine Dimension unter `τ_low` lag
- [ ] Jede Klärungsfrage richtet sich auf die erforderliche Dimension mit der niedrigsten Confidence im Moment, in dem sie gestellt wird
- [ ] Das Interview endete durch ein explizites, protokolliertes Kriterium — Sättigung (`min_d c_d ≥ τ_high` und keine Frage mit positivem EVPI verbleibt) oder das Frage-Budget-Limit — und nie dadurch, dass dem Agenten schlicht die Ideen ausgingen
- [ ] Bei einem budgetbegrenzten Stopp erscheint jede Zelle unter `τ_high` im Output als benanntes Restrisiko
- [ ] Jede Output-Anforderung ist `confirmed` / `assumed` getaggt, konsistent mit ihrer Matrixzelle
- [ ] Die Schwellenwerte `τ_low`, `τ_high`, das Self-Consistency-`k` und das Frage-Budget sind im Artefakt explizit genannt und projektweise mit protokolliertem Rationale überschreibbar
- [ ] Das erfasste Artefakt wird nach `project/requirements/<slug>.md` geschrieben
- [ ] Mindestens ein nachgelagerter Konsument (`roadmap-plan`, `feature-decompose` oder `issue-orchestrate`) gated auf Vorhandensein und `U_gate` des Artefakts und dispatcht `requirements-elicit`, wenn es fehlt oder unter `τ_high` liegt, wobei ein etwaiger Operator-Override protokolliert wird

## Referenzen
<!-- Zitierte Quellen aus dem Deep-Research-Durchlauf. Die adversariale Verifikation wurde nicht abgeschlossen (Session-Limit-Enthaltung), daher sind die Claims belegt, aber nicht unabhängig trianguliert; Methoden als gut belegte Primärquellen-Berichte behandeln, Schwellenwerte als zu kalibrierende Defaults. -->

- [R1] J. Sampaio do Prado Leite u. a. / York University, *On the Nature of Requirements Elicitation Interview Questions* (RE2021) — Typologie von Interviewfragen (Content, Style, Probing Style, Sequence, Objective); Probing-Fragen als effizientester Typ mit >10 Subtypen; offen→spezifisch-Sequenzheuristik: <https://www.yorku.ca/liaskos/Papers/RE2021/RE2021.pdf>
- [R2] *A study of elicitation techniques and their performance* (Information & Software Technology, 2020) — Vollständigkeit als Anteil der abgedeckten Referenz-Lösungs-Anforderungen; Qualität als Prozentübereinstimmung; Fragen-gestellt / relevante-Fragen / Qualität-pro-Zeit-Effizienzmetriken: <https://www.uv.es/joigpana/Files/Journals/IST_2020Requirements_elicitation.pdf>
- [R3] *LLMREI: Automating Requirements Elicitation Interviews with LLMs* (arXiv 2507.02564) — LLM-Interviewer erreicht ~60,9 % vollständig + 12,8 % teilweise (≈73,7 % Recall) der Ground-Truth-Anforderungen; minimales One-Question-at-a-time-Prompting übertrifft einen Fünf-Schritt-Leitlinien-Prompt: <https://arxiv.org/html/2507.02564v1>
- [R4] *Active Task Disambiguation with LLMs* (arXiv 2502.04485) — Generierung von Klärungsfragen als Bayessches Versuchsdesign, das den erwarteten Informationsgewinn über den Raum gangbarer Lösungen maximiert; Schlussfolgern über den Lösungsraum schlägt Schlussfolgern über Kandidatenfragen: <https://arxiv.org/pdf/2502.04485>
- [R5] *SAGE-Agent: structured uncertainty-guided clarification* (OpenReview dc8ebScygC) — trennt Spezifikationsunsicherheit von Modellunsicherheit; EVPI-bewerteter Fragewert mit aspektbasierter Kostenmodellierung zur Unterdrückung redundanter Fragen; Stoppkriterium aus der Unsicherheits-/EVPI-Formulierung abgeleitet: <https://openreview.net/forum?id=dc8ebScygC>
- [R6] *ClarifyGPT* (ACM TOSEM, 10.1145/3660810) — entscheidet *wann* geklärt wird über einen Code-Konsistenz-Check: n Lösungen sampeln, die Anforderung als mehrdeutig behandeln, gdw. die gesampelten Outputs divergieren (verhaltensbasierter Self-Consistency-Proxy, keine Selbstauskunft); reasoning-basierte Fragegenerierung aus den divergierenden Implementierungen: <https://dl.acm.org/doi/full/10.1145/3660810>
- [R7] *Easy Approach to Requirements Syntax (EARS)* — kontrollierte Anforderungs-Syntax-Schablonen, die natürliche Sprache hin zu atomaren, eindeutigen Anforderungen einschränken: <https://en.wikipedia.org/wiki/Easy_Approach_to_Requirements_Syntax>
- [R8] *On the detection of unacknowledged anaphoric ambiguity / TAPHSIR* (arXiv 2206.10227) — unbewusste Mehrdeutigkeit: unterschiedliche selbstsichere Lesarten desselben Textes; recall-favorisierte Erkennung (TAPHSIR ≈100 % Recall, ~60 % Precision) als bewusste Schwellenwert-Heuristik: <https://arxiv.org/pdf/2206.10227>
- [R9] *Rimay: a controlled natural language for requirements* (arXiv 2305.07097) — CNL mit kontrollierter Grammatik/kontrolliertem Vokabular, die präzise, eindeutige, vollständige, atomare Anforderungen erzwingt; neun erkennbare „Smells" auf vier Qualitätsattribute (Completeness, Clarity, Atomicity, Correctness) abgebildet als prüfbare Lücken-Taxonomie: <https://arxiv.org/pdf/2305.07097>
- [R10] *Comparative evaluation of NLP ambiguity detectors* (NLP4RE, CEUR Vol-3122, Paper 3) — benannte lexikalische/syntaktische Mehrdeutigkeitskategorien mit Trigger-Wortlisten (Optionalität, Subjektivität, Vagheit, Schwäche, syntaktische Implizitheit, Multiplizität, Unterspezifikation); Precision/Recall-Gerüst; der High-Recall/Low-Precision-Trade-off des Pattern-Matchings: <https://ceur-ws.org/Vol-3122/NLP4RE-paper-3.pdf>
- [R11] `spec/project/audience-identification/` — identifiziert die befragte Partei; diese Spec setzt voraus, dass diese Partei bereits bekannt ist
- [R12] *SAGE (uncertainty separation over structured parameters)* (arXiv 2511.08798) — Trennung von Spezifikationsunsicherheit und Modellunsicherheit über strukturierte Tool-Parameter und ihre Wertebereiche statt über Freitext: <https://arxiv.org/abs/2511.08798>
- [R13] B. Boehm, *Spiral Development: Experience, Principles, and Refinements* (CMU/SEI-2000-SR-008) — benennt das IKIWISI-Syndrom (Anforderungen für neue, nutzerinteraktive Systeme sind vorab nicht erkennbar) und verschreibt nebenläufiges Prototyping/Anforderungen/Architektur statt vollständiger Vorab-Spezifikation: <https://www.sei.cmu.edu/documents/5439/2000_003_001_13655.pdf>
- [R14] A. Ferrari, P. Spoletini, S. Gnesi, *Ambiguity and tacit knowledge in requirements elicitation interviews* (Requirements Engineering journal, 2016) — eine 34-Interview-Studie, die Mehrdeutigkeit als *Ressource* zur Förderung stillschweigenden Wissens behandelt und Missverständnis als Konsistenzprüfung gegen die Wissensbasis des Analysten modelliert, bei der eine intern akzeptable, aber falsche Lesart stillschweigend versagt: <https://link.springer.com/article/10.1007/s00766-016-0249-3>

## Offene Fragen

- Die Default-Schwellenwerte (`τ_low = 0.4`, `τ_high = 0.8`, Self-Consistency-`k`, Frage-Budget) sind aus Literaturheuristiken und Engineering-Urteil abgeleitet, nicht aus einer Kalibrierungsstudie über die eigenen Interviews dieses Portfolios. Sie sollten überarbeitet werden, sobald genug echte Erfassungs-Transkripte existieren, um sie empirisch zu kalibrieren.
- Die adversariale Verifikation des ursprünglichen Deep-Research-Durchlaufs (3 Stimmen je Claim, 2 Widerlegungen zum Verwerfen) bestätigte die tragenden Methoden: die Trichter- und Probing-Typologie [R1], Self-Consistency als Mehrdeutigkeitssignal [R6], Informationsgewinn-/EVPI-Frageauswahl [R4], [R5], die Trennung von Spezifikations- und Modellunsicherheit [R5], [R12], IKIWISI [R13] und Mehrdeutigkeit-als-Ressource mit Konsistenzprüfungs-Missverständnis [R14] überlebten alle. Vier Claims wurden verworfen und bewusst aus dieser Spec herausgehalten: die quantitativen Magnitude-Zahlen von SAGE-Agent, eine *geschlossene Vier-Typen*-Mehrdeutigkeits-Taxonomie, die Aussage, unstrukturierte Interviews seien kategorisch am schlechtesten, und implied-scenario-Erschöpfung als Sättigungsregel.
- Keine der gesichteten Quellen liefert einen kalibrierten Schwellenwert für `τ_low`, `τ_high`, das Self-Consistency-`k`, den Output-Divergenz-Anteil oder das EVPI-zu-Kosten-Verhältnis; jeder numerische Wert in §D/§E ist ein Engineering-Default, keine gemessene Konstante.
- Keine der gesichteten Quellen validiert ein Sättigungs-/Terminierungskriterium für Erfassungs-Interviews; die Regel in §F ist über der Confidence-/EVPI-Maschinerie konstruiert, nicht gemessen.
- Ob ein kalibriertes LLM-Confidence-Maß mit dem Self-Consistency-Proxy fusioniert werden und speziell für *Anforderungsverständnis* gut kalibriert bleiben kann, ist in der Literatur ungeklärt; bis dahin bleibt `c_d` ein Proxy (§D).
- Das Lücken-Matrix-Artefakt und seine Pro-Zug-KPI-Mechanik haben in keiner gesichteten Quelle ein ausgearbeitetes Schema; das Schema in §D/§G ist original zu dieser Spec und sollte an echten Erfassungs-Transkripten validiert werden.
- Wie interagiert die Lücken-Matrix mit Mehr-Parteien-Erfassung (mehrere Nutzer mit konfligierenden Anforderungen)? Diese Spec scoped eine einzelne befragte Partei; Konfliktauflösung ist auf eine künftige Spec verschoben.

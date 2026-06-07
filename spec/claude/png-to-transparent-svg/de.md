# PNG zu transparentem SVG

Status: draft

## Kontext

KI-Bildgeneratoren (Gemini, DALL-E, Midjourney und ähnliche — diese Liste ist illustrativ für das Muster, keine erschöpfende oder normative Menge) liefern häufig PNGs aus, in denen das Schachbrettmuster, das eigentlich „transparent" signalisieren soll, tatsächlich in die RGB-Kanäle gemalt ist — mit `alpha=255` überall. Vektorisierer wie vtracer behandeln dieses Muster als legitimen Bildinhalt, sodass das resultierende SVG ein vollflächiges Schachbrett hinter dem Motiv trägt. Bis diese Spec landet, operationalisiert der Agent `agents/png-to-transparent-svg.md` (Erbe früherer Bild-Utility-Arbeit) die Reinigungs-und-Vektorisierungs-Schleife ohne autorisierende Spec — ein `spec-drift-audit`-Befund (D-3 in der Cross-Cutting-Coverage-Matrix). Diese Spec schließt den Drift, indem sie formalisiert, was der Agent tut, was nicht, und wie ein nachgelagerter Konsument seine Ausgabe beurteilt.

## Ziele

- Eine autoritative, versionskontrollierte Definition des Fake-Transparenz-Reinigungs-und-Vektorisierungs-Vertrags bereitstellen, den der existierende Agent bereits implementiert
- Das Verhalten des Agents reviewbar machen: Der `agent-review`-Skill kann den Agent jetzt gegen eine explizite Spec prüfen statt gegen eine implizite Autoren-Absicht
- Die Grenze zwischen diesem Utility und benachbarter Bild-Arbeit (Vektorisierung ohne Reinigungsbedarf, fotografischer Inhalt) dokumentieren, sodass der Agent nicht außerhalb seines sicheren Anwendungsfensters aufgerufen wird
- Die Spec eng halten: ein kleines, dediziertes Utility, kein allgemeines Bild-Verarbeitungs-Framework

## Nicht-Ziele

- Ersatz für vtracer oder einen anderen Vektorisierer; der Reinigungs-Schritt ist die Wertschöpfung, die Vektorisierung ist eine dünne Hülle
- Verarbeitung fotografischer PNGs, in denen der Hintergrund kein flaches Fake-Transparenz-Muster ist (das würde Raster-zu-Vektor-Training erfordern, außer Scope)
- Reinigung von PNGs, die bereits echte Alpha-Transparenz tragen (`alpha < 255` irgendwo) — die gehen direkt an den Vektorisierer ohne diesen Agent
- Definition eines portfolioweiten Bild-Asset-Format-Specs; dies ist ein Utility, kein Content-Pipeline-Framework

## Anforderungen

- **MUSS [MUST]** das Fake-Transparenz-Muster aus dem Alpha-Kanal und dem Eckpixel-Farbprofil jedes Eingabe-PNGs erkennen, bevor irgendein Pixel-Rewrite stattfindet — eine stillschweigende Behandlung eines Real-Alpha-PNGs als Fake-Transparenz würde legitime Transparenz beschädigen
- **MUSS [MUST]** qualifizierende Pixel (die zur erkannten Fake-Transparenz-Farbe passen) auf `alpha=0` umschreiben und ein Zwischen-„cleaned PNG" erzeugen; das cleaned PNG ist die Eingabe für den Vektorisierer, nie das Original
- **MUSS [MUST]** das cleaned PNG mit vtracer mit Parametern vektorisieren, die im Agent-Body dokumentiert sind; Parameteränderungen leben im Agent, nicht in dieser Spec
- **MUSS [MUST]** Erkennungs-Schwellen (RGB-Delta, Eckcluster-Toleranz) als Tuning-Werte behandeln, die im Agent-Body liegen und nicht auf Spec-Ebene konfiguriert werden; Aufrufer steuern über den Pro-Datei-Ausreißer-Bericht, nicht über einen Schwellen-Parameter
- **MUSS [MUST]** eine Datei im Bericht warnen und überspringen — statt eine Schwelle zu raten oder den Batch mit einer Frage zu blockieren —, wenn der Detektor sie weder als Real-Alpha noch als sauberes Fake-Transparenz-Muster klassifizieren kann (gemischte Eckfarben, teilweise Alpha)
- **MUSS [MUST]** jeden vollflächigen Hintergrund-Pfad entfernen, den der Vektorisierer trotzdem emittieren mag, sodass das resultierende SVG keinen Hintergrund-Fill trägt
- **MUSS [MUST]** eine Pro-Datei-Zusammenfassung berichten (Originalgröße, entfernte Pixel, SVG-Größe, Status), damit der Aufrufer Anomalien erkennen kann (zum Beispiel signalisiert ein „0 % Pixel entfernt"-Ausreißer ein Versagen des Detektors, die Datei sollte erneut geprüft werden)
- **DARF NICHT [MUST NOT]** ein PNG modifizieren, das der Detektor als bereits Real-Alpha-tragend klassifiziert; solche Dateien direkt an den Vektorisierer routen ohne Reinigung, oder ablehnen und melden
- **DARF NICHT [MUST NOT]** Netzwerkzugriff erfordern; Bildverarbeitung läuft lokal via Python in `Bash`
- **SOLLTE [SHOULD]** Single-File-, Directory- und Glob-Eingaben einheitlich akzeptieren, sodass Aufrufer nicht um die Pro-Datei-Schleife herum skripten müssen
- **SOLLTE [SHOULD]** das Original-PNG bewahren und das cleaned PNG sowie das SVG als neue Dateien schreiben, sodass die Eingabe niemals überschrieben wird

## Akzeptanzkriterien

- [ ] Eine Invocation gegen ein Sample-PNG mit eingebackener Schachbrett-Transparenz erzeugt ein cleaned Zwischen-PNG (mit `alpha=0` für die gematchten Pixel) plus ein SVG ohne Hintergrund-Fill
- [ ] Eine Invocation gegen ein PNG, das bereits echte Alpha-Transparenz trägt, überspringt entweder den Reinigungs-Schritt (direkt vektorisierend) oder lehnt mit klarer Meldung ab — und schreibt niemals stillschweigend Alpha-Werte um
- [ ] Die Pro-Datei-Zusammenfassung enthält Pixel-Entfernungs-Zählungen, die dem Aufrufer erlauben, Detektor-Ausreißer zu kennzeichnen (zum Beispiel triggert eine Schwelle unter 5 % einen Aufrufer-Review)
- [ ] Eine Invocation gegen ein PNG, das der Detektor nicht klassifizieren kann (gemischte Eckfarben, teilweise Alpha), warnt und überspringt diese Datei im Pro-Datei-Bericht, statt eine Schwelle zu raten oder den Batch mit einer Frage zu blockieren
- [ ] Der Agent unter `agents/png-to-transparent-svg.md` zitiert diese Spec in seiner `description` oder seinem Body, sodass der Link auffindbar ist
- [ ] Die Tools-Liste des Agents ist das Minimum (`Read`, `Bash`, `Glob`) — kein `Write` (Bilddatei-Schreibvorgänge passieren in den über `Bash` aufgerufenen Python-Helfern), kein `Edit`, keine Netzwerk-Tools

## Offene Fragen

_Derzeit keine._

# Claude-Skill-Autorenschaft

Status: draft

## Kontext
Das Repository claude-shared sammelt wiederverwendbare Claude-Code-Skills und -Agents, die von nachgelagerten Projekten genutzt werden. Ein Skill hat zwei Ausprägungen: eine **Quell-Form** in diesem Repository (unter `skills/`) und eine **Laufzeit-Form** in einem konsumierenden Projekt (unter `.claude/skills/` oder `~/.claude/skills/`), aus der Claude Code den Skill tatsächlich lädt. Ohne einheitliche Form driften Skills in Benennung, Trigger-Beschreibungen und interner Struktur auseinander, was Wiederverwendung brüchig und Wartung aufwendiger macht. Diese Spezifikation definiert, wie neue Skills erstellt werden, wo sie in beiden Formen liegen und woran sich bestehende Skills halten müssen.

## Ziele
- Jeder Skill hat dieselbe vorhersehbare Form auf der Festplatte
- Skills sind für Claude über präzise, trigger-orientierte Beschreibungen auffindbar
- Skills sind portabel über jedes Projekt, das claude-shared konsumiert, ohne versteckte Abhängigkeiten
- Autoren haben eine klare Checkliste und ein Template als Startpunkt

## Nicht-Ziele
- Plugin-Paketierung und -Verteilung (separat behandelt)
- Einrichtung nachgelagerter Projekte und `.claude/`-Konfiguration
- Vorgabe konkreter Skill-Inhalte jenseits struktureller Regeln

## Anforderungen

### Struktur
- **MUSS [MUST]** als Ordner mit dem Namen `<name>/` angelegt werden, wobei `<name>` ASCII-Kebab-Case ist
- **MUSS [MUST]** eine `SKILL.md` im Wurzelverzeichnis des Skill-Ordners enthalten
- **MUSS [MUST]** YAML-Frontmatter in `SKILL.md` mit den Feldern `name` und `description` enthalten
- **MUSS [MUST]** `name` exakt auf den Ordnernamen setzen
- **MUSS [MUST]** eine `description` schreiben, die konkrete Nutzer-Trigger benennt statt abstrakter Fähigkeiten, damit Claude zuverlässig über den Aufruf entscheiden kann
- **MUSS [MUST]** Anweisungen innerhalb von `SKILL.md` aus Token-Effizienzgründen auf Englisch halten; der Skill darf Claude weiterhin anweisen, dem Nutzer in dessen Sprache zu antworten
- **MUSS [MUST]** in sich geschlossen sein — unterstützende Artefakte (Templates, Referenzen, Beispiele) liegen innerhalb des Skill-Ordners

### Quell-Ablageort (Repository claude-shared)
- **MUSS [MUST]** im Quellbaum von claude-shared unter `skills/<name>/` liegen, damit er kopiert, symlinkt oder für die Verteilung in ein Plugin gebündelt werden kann

### Laufzeit-Ablageort (konsumierendes Projekt)
- **MUSS [MUST]** von Claude Code aus einem der Standard-Orte ladbar sein:
  - `.claude/skills/<name>/` — projektbezogene Installation
  - `~/.claude/skills/<name>/` — benutzerbezogene Installation
  - der dafür vorgesehene Skills-Pfad eines Plugins, wenn er als Teil eines Plugins ausgeliefert wird
- **DARF NICHT [MUST NOT]** einen bestimmten Installationsort voraussetzen; alle internen Pfade bleiben relativ zum Skill-Ordner und funktionieren an jedem der genannten Orte

### Empfehlungen
- **SOLLTE [SHOULD]** einen Abschnitt „Hard rules" enthalten, der Invarianten auflistet, die niemals gebrochen werden dürfen
- **SOLLTE [SHOULD]** `SKILL.md` etwa unter 150 Zeilen halten; längere Inhalte in referenzierte Dateien auslagern
- **SOLLTE [SHOULD]** unterstützende Dateien in konventionelle Unterordner legen: `templates/`, `references/`, `examples/`
- **KANN [MAY]** Beispiel-Nutzer-Prompts und erwartetes Verhalten in `examples/` enthalten
- **KANN [MAY]** ein kleines Konfigurationsschema enthalten, falls der Skill projektbezogene Konfiguration benötigt

## Akzeptanzkriterien
- [ ] Quellordner existiert unter `skills/<name>/` in claude-shared mit `<name>` in ASCII-Kebab-Case
- [ ] Skill kann in einem konsumierenden Projekt nach `.claude/skills/<name>/` (oder `~/.claude/skills/<name>/`) ausgebracht werden und wird von Claude Code von dort geladen
- [ ] `SKILL.md` parst mit gültigem YAML-Frontmatter, das `name` und `description` enthält
- [ ] `name` im Frontmatter entspricht dem Ordnernamen
- [ ] `description` nennt die konkreten Nutzer-Formulierungen, die den Skill auslösen sollen
- [ ] Skill funktioniert in einem nachgelagerten Projekt, das keinen claude-shared-spezifischen Kontext enthält
- [ ] Keine hartkodierten absoluten Pfade; alle internen Pfade sind relativ zum Skill-Ordner oder zum Projekt, auf dem der Skill operiert
- [ ] Falls der Skill Dateien schreibt, sind Zielorte und Vorbedingungen dokumentiert

## Offene Fragen
- Soll der Ordnername verpflichtend einem etwaigen nutzerseitigen Slash-Command-Namen entsprechen, oder dürfen sie abweichen?
- Brauchen Skills Versions- oder Kompatibilitäts-Metadaten, während sie sich weiterentwickeln?
- Wo verläuft die Grenze zwischen einem Skill und einem Agent? Wann soll eine Fähigkeit das eine sein, wann das andere?
- Gibt es eine maximale Verschachtelungstiefe für unterstützende Unterordner, oder bleibt das lose?

# Claude-Skill-Autorenschaft

Status: draft

## Kontext
Das Repository claude-shared sammelt wiederverwendbare Claude-Code-Skills und -Agents, die von nachgelagerten Projekten genutzt werden. Ein Skill hat zwei Ausprägungen: eine **Quell-Form** in diesem Repository (unter `skills/`) und eine **Laufzeit-Form** in einem konsumierenden Projekt, aus der Claude Code den Skill tatsächlich lädt. Der einzige unterstützte Verteilungsweg für die Laufzeit ist der Claude-Code-Plugin-Mechanismus: Dieses Repository ist selbst ein Claude-Code-Plugin (`.claude-plugin/plugin.json` plus Marketplace-Eintrag), und konsumierende Projekte erhalten Skills, indem sie das Plugin installieren. Ohne einheitliche Form und einen einzigen Verteilungspfad driften Skills in Benennung, Trigger-Beschreibungen und interner Struktur auseinander, und Konsumenten landen bei ad-hoc Kopien oder Symlinks, die mit der Zeit divergieren. Diese Spezifikation definiert, wie neue Skills erstellt werden, wie sie verteilt werden und woran sich bestehende Skills halten müssen.

## Ziele
- Jeder Skill hat dieselbe vorhersehbare Form auf der Festplatte
- Skills sind für Claude über präzise, trigger-orientierte Beschreibungen auffindbar
- Skills sind portabel über jedes Projekt, das claude-shared konsumiert, ohne versteckte Abhängigkeiten
- Autoren haben eine klare Checkliste und ein Template als Startpunkt

## Nicht-Ziele
- Einrichtung nachgelagerter Projekte und `.claude/`-Konfiguration jenseits der Plugin-Installation
- Vorgabe konkreter Skill-Inhalte jenseits struktureller Regeln
- Die konkrete Marketplace- / Plugin-Installations-UX von Claude Code (wird von Claude Code selbst verantwortet, nicht von diesem Repository)

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
- **MUSS [MUST]** im Quellbaum von claude-shared unter `skills/<name>/` liegen
- **MUSS [MUST]** als Bestandteil des `nolte-shared`-Claude-Code-Plugins ausgeliefert werden, das über `.claude-plugin/plugin.json` und `.claude-plugin/marketplace.json` in diesem Repository deklariert ist; kein Skill in diesem Repository existiert außerhalb des Plugin-Scopes

### Verteilung
- **MUSS [MUST]** konsumierende Projekte ausschließlich über den Claude-Code-Plugin-Mechanismus erreichen — das Plugin wird über den Marketplace-Eintrag installiert, und Claude Code findet den Skill aus dem `skills/<name>/`-Pfad des Plugins heraus
- **DARF NICHT [MUST NOT]** durch Kopieren in das `.claude/skills/<name>/`-Verzeichnis eines konsumierenden Projekts, durch Symlink, durch Vendoring oder auf irgendeinem anderen Out-of-Band-Pfad verteilt werden; solche Kopien driften gegenüber der Quelle und untergraben den Sinn eines geteilten Plugins
- **DARF NICHT [MUST NOT]** die Plugin-Version in `.claude-plugin/plugin.json` oder im zugehörigen Marketplace-Eintrag manuell als Teil eines PRs erhöhen, der einen Skill hinzufügt, umbenennt, entfernt oder seinen Vertrag wesentlich ändert; die Version wird vom veröffentlichten GitHub-Release-Tag abgeleitet und ausschließlich durch den Release-Workflow auf dem Default-Branch aktualisiert — siehe `release-automation` §Plugin-Manifest-Abgleich für den Mechanismus
- **DARF [MAY]** in einem konsumierenden Projekt neben projektlokalen Skills unter dessen eigenem `.claude/skills/` koexistieren; solche projektlokalen Skills liegen außerhalb des Scopes dieser Spec und **DÜRFEN NICHT [MUST NOT]** einen Namen wiederverwenden, der bereits im `nolte-shared`-Plugin belegt ist

### Laufzeit-Auffindbarkeit (konsumierendes Projekt)
- **MUSS [MUST]** von Claude Code aus dem Plugin-Skills-Pfad geladen werden, sobald das Plugin installiert ist; der Skill erscheint dem Nutzer als `nolte-shared:<name>`
- **DARF NICHT [MUST NOT]** irgendeinen spezifischen absoluten oder projekt-relativen Laufzeit-Pfad voraussetzen; alle internen Pfade bleiben relativ zum Skill-Ordner und funktionieren überall dort, wo Claude Code das Plugin entpackt oder einbindet

### Empfehlungen
- **SOLLTE [SHOULD]** einen Abschnitt „Hard rules" enthalten, der Invarianten auflistet, die niemals gebrochen werden dürfen
- **SOLLTE [SHOULD]** `SKILL.md` etwa unter 150 Zeilen halten; längere Inhalte in referenzierte Dateien auslagern
- **SOLLTE [SHOULD]** unterstützende Dateien in konventionelle Unterordner legen: `templates/`, `references/`, `examples/`
- **KANN [MAY]** Beispiel-Nutzer-Prompts und erwartetes Verhalten in `examples/` enthalten
- **KANN [MAY]** ein kleines Konfigurationsschema enthalten, falls der Skill projektbezogene Konfiguration benötigt

## Akzeptanzkriterien
- [ ] Quellordner existiert unter `skills/<name>/` in claude-shared mit `<name>` in ASCII-Kebab-Case
- [ ] Repository enthält eine gültige `.claude-plugin/plugin.json` und `.claude-plugin/marketplace.json`, die diesen Skill als Teil des `nolte-shared`-Plugins bereitstellen
- [ ] Skill ist in einem konsumierenden Projekt allein durch Installation des `nolte-shared`-Plugins aus dem Marketplace auffindbar — kein manuelles Kopieren oder Symlinken nach `.claude/skills/` ist nötig oder zulässig
- [ ] Die Plugin-Version in `.claude-plugin/plugin.json` entspricht dem zuletzt veröffentlichten GitHub-Release-Tag (gepflegt durch den Release-Workflow gemäß `release-automation` §Plugin-Manifest-Abgleich, nicht durch Skill-Änderungs-PRs); kein Diff am `version`-Feld erscheint in einem PR, dessen alleiniger Zweck das Hinzufügen, Umbenennen oder Entfernen eines Skills ist
- [ ] `SKILL.md` parst mit gültigem YAML-Frontmatter, das `name` und `description` enthält
- [ ] `name` im Frontmatter entspricht dem Ordnernamen
- [ ] `description` nennt die konkreten Nutzer-Formulierungen, die den Skill auslösen sollen
- [ ] Skill funktioniert in einem nachgelagerten Projekt, das keinen claude-shared-spezifischen Kontext enthält, geladen über das Plugin
- [ ] Keine hartkodierten absoluten Pfade; alle internen Pfade sind relativ zum Skill-Ordner oder zum Projekt, auf dem der Skill operiert
- [ ] Falls der Skill Dateien schreibt, sind Zielorte und Vorbedingungen dokumentiert
- [ ] Das Review eines einzelnen Skills gegen diese Spec folgt `spec/claude/skill-review/`; die Review-Ausgabe entspricht `spec/claude/review-plan/` und liegt unter `.audits/skill-review/<name>.md`

## Offene Fragen
- Soll der Ordnername verpflichtend einem etwaigen nutzerseitigen Slash-Command-Namen entsprechen, oder dürfen sie abweichen?
- Brauchen Skills Versions- oder Kompatibilitäts-Metadaten, während sie sich weiterentwickeln?
- Wo verläuft die Grenze zwischen einem Skill und einem Agent? Wann soll eine Fähigkeit das eine sein, wann das andere?
- Gibt es eine maximale Verschachtelungstiefe für unterstützende Unterordner, oder bleibt das lose?

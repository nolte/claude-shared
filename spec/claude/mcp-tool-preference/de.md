# Optionale Bevorzugung des GitHub-MCP-Servers

Status: draft
Portfolio-Scope: local

## Kontext

Skills und Agents, die aus GitHub lesen, erreichen es heute, indem sie die `gh`-CLI aufrufen und deren Textausgabe parsen. Ein verbundener GitHub-MCP-Server stellt dieselben Operationen als typisierte, paginierte, strukturierte Tools bereit, die günstiger und verlässlicher zu konsumieren sind als abgekratzter CLI-Text — besonders bei leselastiger Erfassung: ein Issue mit seinen Kommentaren und verknüpften Elementen, ein Workflow-Run mit seinen Logs oder Issues und Pull Requests über das gesamte Portfolio hinweg gesammelt.

Diese Spec definiert die **Autoren-Konvention** für die Übernahme dieses Wegs: wie ein Skill oder Agent ausdrückt „bevorzuge den GitHub-MCP-Server, wenn er vorhanden ist, und falle immer auf `gh` zurück". Die Konvention ist strikt optional und strikt additiv. Ein MCP-Server kann in Headless-, Cron- oder CI-Läufen fehlen, daher darf nichts ihn *voraussetzen*, und auf keinem der beiden Wege darf sich das Verhalten ändern.

Sie ist komplementär zu drei bestehenden Regeln und wiederholt keine davon: `spec/claude/skill-management/` und `spec/claude/agent-management/` fixieren bereits, **wie** ein MCP-Tool im Artefakt-Text benannt wird (die voll qualifizierte `ServerName:tool_name`-Syntax) und vermerken, dass das `mcpServers`-Frontmatter-Feld für plugin-distribuierte Agents ignoriert wird; `spec/claude/permission-allowlist/` besitzt das **Allowlisting** der Tool-Aufrufe, damit sie nicht prompten. Diese Spec regelt nur, **ob und wann** ein GitHub-berührendes Artefakt einen MCP-Read gegenüber `gh` bevorzugt.

Leser: Skill- und Agent-Autoren in `claude-shared`, die GitHub-berührende Artefakte pflegen, und die Reviewer, die sie verifizieren.

## Ziele

- Eine Konvention formulieren, die jeder GitHub-berührende Skill oder Agent für den optionalen MCP-bevorzugten Lesepfad referenziert.
- Headless- und CI-Sicherheit garantieren: der `gh`/git-Fallback funktioniert immer, sodass ein fehlender MCP-Server ein Artefakt nie bricht.
- Verhalten erhalten: dieselben Eingaben erzeugen identische Artefakte und Entscheidungen, egal ob der MCP-Pfad oder der `gh`-Pfad läuft.
- MCP-bevorzugte Reads von Writes und Git-Plumbing abgrenzen, die auf `gh`/git bleiben.
- Sauber mit der MCP-Tool-Namensregel (`skill-management`/`agent-management`) und der Allowlisting-Regel (`permission-allowlist`) komponieren, ohne eine davon zu wiederholen.

## Nicht-Ziele

- Den MCP-Server oder irgendein MCP-Tool vorschreiben: die Konvention ist optional, und `gh`/git bleibt autoritativ.
- Den `gh`/git-Fallback in irgendeinem Artefakt entfernen oder schwächen.
- Installation, Authentifizierung oder Konfigurationsfläche des MCP-Servers festlegen: die Bereitstellung ist ein separates Anliegen und eine Consumer-Entscheidung.
- Git-Plumbing (push, rebase, merge) oder bewusste Schreib-Aktionen als MCP-Aufrufe neu schreiben.
- Die Permission-Allowlist-Einträge selbst besitzen (`permission-allowlist`) oder die MCP-Tool-Namenssyntax (`skill-management`, `agent-management`).

## Anforderungen

### Optionalität und Fallback

- Ein Skill oder Agent, der aus GitHub liest, **SOLLTE** ein verfügbares GitHub-MCP-Read-Tool gegenüber dem Parsen der `gh`-CLI-Ausgabe bevorzugen, wenn ein GitHub-MCP-Server verbunden ist.
- Er **MUSS** einen funktionierenden `gh`/git-Fallback behalten und **DARF** den MCP-Server **NICHT** voraussetzen; ohne verbundenen Server **MUSS** das Artefakt allein über `gh`/git abschließen.
- Er **MUSS** anmutig degradieren: Verfügbarkeit erkennen und still zurückfallen. Fehlende MCP-Tools **DÜRFEN** **NICHT** zu einem Prompt-Fehlschlag, einem Fehler oder einem abgebrochenen Lauf führen.
- Der MCP-bevorzugte Pfad **DARF** das Verhalten **NICHT** ändern: dieselben Eingaben **MÜSSEN** auf beiden Wegen identische Artefakte und Entscheidungen erzeugen. Das ist die akzeptanz-testbare Invariante, gegen die ein übernehmendes Artefakt verifiziert wird (einmal mit vorhandenem Server, einmal nur mit `gh` laufen lassen und das Ergebnis diffen).

### Lesen versus Schreiben

- Reads (get, list, search, Run-Logs) sind die MCP-bevorzugte Fläche.
- Writes und Git-Plumbing (`git push`/`rebase`/`merge`, Pull-Request create/merge/label, `gh workflow run`) **MÜSSEN** standardmäßig auf `gh`/git bleiben; die Übernahme eines MCP-Write-Tools ist eine fallweise, separat begründete Entscheidung, niemals der Default dieser Konvention.

### Ausdruck im Artefakt

- Ein übernehmender Skill oder Agent **MUSS** den optionalen Pfad an einer kurzen Stelle in seinem Body benennen (zum Beispiel einer Tooling-Notiz) und **MUSS** diese Spec referenzieren, sodass ein Leser weiß, dass der MCP-Pfad existiert und dass `gh`/git autoritativ bleibt.
- Wenn ein Artefakt ein MCP-Tool in seinem Text referenziert, **MUSS** es die voll qualifizierte `ServerName:tool_name`-Syntax verwenden, die `spec/claude/skill-management/` und `spec/claude/agent-management/` fordern; diese Spec wiederholt jene Regel nicht, hängt aber von ihr ab.
- Ein Agent, der MCP-Tools aufruft, **MUSS** diese Tool-Namen in seinem `tools:`-Frontmatter gewährt bekommen (additiv), und die Gewährung **MUSS** innerhalb der Agent-Description- und Tool-Routing-Budget-Governance bleiben; das `mcpServers`-Frontmatter-Feld wird für plugin-distribuierte Agents ignoriert, daher stellt die Consumer-Projektkonfiguration den Server bereit, nicht der Agent.
- Die MCP-Tool-Namen, die ein Artefakt verwendet, **MÜSSEN** gemäß `spec/claude/permission-allowlist/` allowlisted sein, sodass kein Bestätigungs-Prompt pro Aufruf auftritt.

### Server und Tool-Katalog

- Diese Spec **DARF** keinen bestimmten MCP-Server **vorschreiben**; der Referenz-Server ist GitHubs offizieller `github-mcp-server`, den ein Consumer ersetzen **KANN**.
- Da MCP-Tool-Kataloge über Server-Versionen hinweg variieren, **MUSS** ein übernehmendes Artefakt die exakten Tool-Namen gegen die gepinnte Server-Version verifizieren, statt eine ungepinnte Annahme hart zu kodieren.

## Akzeptanzkriterien

- [ ] Die Konvention ist als optional formuliert: SOLLTE bevorzugen, MUSS zurückfallen, DARF NICHT voraussetzen.
- [ ] Headless-/CI-Sicherheit ist ein MUSS, mit einer expliziten `gh`-only-Abschluss-Garantie.
- [ ] Die Identisch-Output-Invariante ist normativ und als Beides-laufen-lassen-und-diffen-Prüfung formuliert.
- [ ] Die Abgrenzung Lesen-versus-Schreiben/Git-Plumbing ist explizit.
- [ ] Die Ausdrucksregeln sind alle vorhanden: Body-Notiz plus Spec-Referenz, qualifizierte `ServerName:tool_name`-Benennung (per Referenz), additive `tools:`-Gewährung innerhalb des Budgets und Allowlisting (per Referenz).
- [ ] Die Spec ist server-agnostisch mit `github-mcp-server` als Referenz benannt und fordert die Verifikation der Tool-Namen gegen die gepinnte Server-Version.
- [ ] Die Spec wiederholt weder die MCP-Tool-Namensregel noch den Allowlist-Mechanismus; sie referenziert sie.

## Referenzen

- [R1] MCP-Tool-Namenssyntax und die skill-seitigen Autorenregeln: `spec/claude/skill-management/`
- [R2] Agent-Frontmatter, `tools:`-Gewährungen und das ignorierte `mcpServers`-Feld für plugin-distribuierte Agents: `spec/claude/agent-management/`
- [R3] Allowlisting von Shell- und MCP-Tool-Aufrufen, damit sie nicht prompten: `spec/claude/permission-allowlist/`
- [R4] Agent-Description- und Tool-Routing-Budget-Governance, die die `tools:`-Gewährungen respektieren müssen: Roadmap-Item R-9
- [R5] Herkunft und der gestaffelte Adoptionsplan (Work-Packages P1-P9): Issue #378; Pre-Analysis in die Git-Historie überführt

## Offene Fragen

- **Portfolio-Scope**: diese Konvention wird als `local` ausgeliefert. Wenn Downstream-Consumer beginnen, ihre eigenen GitHub-berührenden Skills/Agents gegen MCP zu autoren, ist die Promotion auf `Portfolio-Scope: portfolio` (wie die gepaarte `permission-allowlist` bereits ist) ein bewusster Maintainer-Akt, kein automatischer.
- **Bereitstellungsfläche**: ob der Referenz-Server als repo-root `.mcp.json` ausgeliefert oder per Consumer dokumentiert wird, gehört dem Bereitstellungs-Work-Package (P1/P2 von Issue #378), nicht dieser Konvention.
- **Nicht-GitHub-MCP-Server**: diese Spec ist auf den GitHub-MCP-Server beschränkt; eine allgemeine „MCP für Reads externer Dienste bevorzugen"-Konvention wird vertagt, bis ein zweiter Server die Frage erzwingt.

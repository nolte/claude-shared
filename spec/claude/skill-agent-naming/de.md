# Skill- und Agent-Naming

Status: draft
Portfolio-Scope: portfolio

## Kontext

Bis zu dieser Spec lebte die Namenskonvention für wiederverwendbare Claude-Code-Artefakte verteilt auf zwei Owner-Specs: die Skill-Form in `skill-management` §Frontmatter validation, die Agent-Form in `agent-management` §Structure, mit den Ausnahmelisten ein drittes Mal gespiegelt in `scripts/validate_skills.py`. Das Skills-&-Agents-Audit 2026-07 zeigte, was diese Aufteilung kostet: Reviewer zitieren zwei verschiedene Anker für eine Konvention, die beiden Hälften driften im Wortlaut, und ein Consumer-Plugin (etwa `claude-home-assistant`) hat kein einzelnes Dokument zum Erben. Diese Spec konsolidiert die gesamte Namensform-Konvention in einen **normativen Owner**. Die ehemaligen Host-Abschnitte in `skill-management` und `agent-management` delegieren nur noch hierher und wiederholen nichts; bei jeder Diskrepanz zwischen dieser Spec und einer älteren Wiederholung anderswo **gewinnt diese Spec**.

Scope-Grenze: Diese Spec besitzt die **Form** eines Namens — semantische Gestalt, Morphologie, Ausnahmen und Rename-Policy. Die **Zeichen-Ebene** (1–64 Zeichen, lowercase ASCII-kebab-case, kein führender/abschließender Bindestrich, kein `--`, reservierte Tokens `anthropic`/`claude`, kein XML) bleibt bei `skill-management` §Frontmatter validation und `agent-management` §Structure; der Digest am Ende dieses Dokuments zeigt nur dorthin.

## Ziele

- Ein normatives Zuhause für die komplette Namenskonvention, erbbar von jedem Portfolio-Plugin
- Deterministische Review-Anker: ein Namensform-Finding zitiert genau eine Spec
- Die geschlossenen Listen des Validators und diese Spec ändern sich im Lockstep, nie unabhängig

## Nicht-Ziele

- Zeichen-Ebenen-Validierung von `name` (gehört den oben benannten Frontmatter-Validation-Abschnitten)
- Umbenennung bestehender Artefakte (stehender Naming-Audit-Entscheid: nur Suggestions, keine Renames)
- Naming von Specs, Dateien, Branches oder HA-Domänen-Objekten (`spec/ha/naming-conventions` im HA-Repo regelt Home-Assistant-Entity-/Geräte-Naming — ein anderes Thema)

## Anforderungen

### Upstream-Basis

- Anthropics veröffentlichte Konvention bevorzugt für Skill-Namen die **Gerundium-Form** (`processing-pdfs`); Verb-Substantiv und Nominalphrasen sind akzeptable Alternativen, aber **Mischformen innerhalb eines Repositories sind es nicht** ([R1](#references)). Dieses Portfolio standardisiert bewusst auf die Alternativen unten; die No-Mixing-Hälfte der Upstream-Regel ist der bindende Teil.

### Skill-Namen: `<object-noun>-<action>`

- **MUSS** jeden Skill in Verb-Substantiv-Form benennen, konkret `<object-noun>-<action>`: die führenden Tokens benennen das Objekt, das **nachgestellte** Token die Aktion — als finites Verb (`pull-request-create`, `roadmap-init`, `feature-decompose`, `mission-define`) oder als verb-abgeleitetes Aktions-Nomen (`dependency-audit`, `gemini-image-handoff`, `skill-management`)
- Die Aktion steht **zuletzt**, spiegelbildlich zur Agent-Seite, wo das Rollen-Nomen zuletzt steht
- Das Aktions-Vokabular ist **auf Regel-Ebene offen**: jedes finite Verb oder verb-abgeleitete Aktions-Nomen qualifiziert (`add`, `augment`, `scaffold`, `migrate`, `sync`, `determine`, `release` und weitere). Die `SKILL_ACTION_TOKENS`-Liste des Validators ist ein Oberflächen-Spiegel, der mit den realen Tokens des Portfolios wächst — nie ein semantisches Gate, das ein legitimes Verb verbietet
- **Geschlossene Ausnahmen** (ein Reviewer **DARF** sie **NICHT** flaggen; die Liste ist abschließend): `spec` (nacktes Nomen), `yaml-json-schema` (Nomen-Kompositum), `quality-gate` (nachgestelltes Nomen benennt ein Ding, keine Aktion). Alle drei sind älter als die Konvention; Umbenennung bräche jede Consumer-Aufrufstelle — bei `spec` zusätzlich die `$ref`-/Querverweis-Maschinerie. Jeder *neue* Skill **MUSS** der Konvention folgen

### Agent-Namen: `<subject>-<role-noun>`

- **MUSS** jeden Agent in Objekt-Rolle-Form benennen, `<subject>-<role-noun>`: das nachgestellte Token ist die Rolle, die der Agent über dem führenden Subjekt spielt (`code-security-reviewer`, `feature-consistency-reviewer`, `portfolio-manifest-collector`, `vocab-drift-scanner`, `lektorat-scanner`)
- Das nachgestellte Rollen-Nomen trägt fast immer `-er`/`-or`/`-ist`-Morphologie (`-reviewer`, `-checker`, `-scanner`, `-collector`, `-curator`, `-enforcer`, `-extractor`, `-generator`, `-author`, `-developer`); ein Akteurs-Nomen, das eine Rolle ohne diese Morphologie benennt, ist weiterhin konform — `webview-ui-expert` ist der stehende Fall
- **Geschlossene Ausnahmen** (ein Reviewer **DARF** sie **NICHT** flaggen; die Liste ist abschließend): `png-to-transparent-svg` (Transformations-Phrase ohne Rollen-Token) und `audience-review` (nachgestelltes `review` benennt eine Aktion, keinen Akteur). Umbenennung bräche jede `subagent_type:`-Aufrufstelle; die Bruchkosten überwiegen den Kohärenz-Gewinn. Jeder *neue* Agent **MUSS** der Konvention folgen

### Eine Form pro Artefakt-Typ, pro Plugin

- **MUSS** das Naming über das ganze Plugin konsistent halten — eine Konvention pro Artefakt-Typ; eine Gerundium- oder Freiform in eine der beiden Flächen zu mischen ist selbst das Discoverability-Anti-Pattern, vor dem `plugin-scoping` §Namespace and naming coherence warnt
- Domänen-Plugins, die diesen Korpus erben (etwa `claude-home-assistant`), **DÜRFEN** jedem Artefakt-Namen ein festes Domänen-Präfix (`ha-`) voranstellen; die Form nach dem Präfix folgt unverändert den obigen Regeln (`ha-config-flow-augment`, `ha-blueprint-author`)
- Erbende Plugins auditieren ihre Fläche gegen die **Regeln** dieser Spec, nicht wörtlich gegen die nolte-shared-Validator-Listen, und **MÜSSEN** eigene geschlossene Ausnahmelisten in ihrem Spec-Index-README deklarieren, unter derselben Disziplin (geschlossen, greppable, Reviewer DARF NICHT flaggen). Eine **Familien-Suffix-Ausnahme** (ein bewusstes, uniformes Suffix, das eine Artefakt-Familie benennt, etwa eine `*-solution`-Front-Door-Familie) qualifiziert, wenn sie dort deklariert ist und intern konsistent bleibt

### Rename-Policy

- Die Umbenennung eines bestehenden Artefakts ist ein **Breaking Change** für jede Consumer-Aufrufstelle und **MUSS** als neues Artefakt plus Deprecation-Notiz auf dem alten ausgeliefert werden, nie als stiller Flip (gemäß `skill-vs-agent` §Portfolio-wide consistency)
- Ein künftiger koordinierter Portfolio-Rename (etwa der Flip auf Gerundium-Form) **DARF** mit Deprecation-Periode stattfinden; bis eine solche Änderung shippt, gelten die obigen Formen
- Der stehende Naming-Audit-Entscheid von 2026 gilt: Form-Abweichungen in der Bestandsfläche sind **Beobachtungs-Suggestions**, nie Rename-Aufträge

### Bindung an `scripts/validate_skills.py`

- `scripts/validate_skills.py` operationalisiert diese Spec als **Suggestion-grade** `check_name_form` (eine Form-Abweichung ist ein Discoverability-Smell, kein Plattform-Fehler) mit vier gespiegelten geschlossenen Listen: `SKILL_ACTION_TOKENS`, `SKILL_NAME_FORM_EXCEPTIONS`, `AGENT_ROLE_NOUNS`, `AGENT_NAME_FORM_EXCEPTIONS`
- **MUSS** diese Spec und jene Listen im **selben PR** ändern, wann immer sich eine Seite bewegt; ein Listeneintrag ohne Spec-Gegenstück (oder umgekehrt) ist ein Defekt

### Zeichen-Ebenen-Digest (anderswo besessen)

Nur zur Bequemlichkeit — die normativen Regeln leben in `skill-management` §Frontmatter validation und `agent-management` §Structure: 1–64 Zeichen, lowercase ASCII-Buchstaben/Ziffern/Bindestriche, kein führender/abschließender Bindestrich, kein `--`, kein XML, reservierte Tokens `anthropic`/`claude` in `name` verboten (enge dokumentierte Ausnahme via `## Reserved-token rationale`), generische Namen (`helper`, `utils`, `tools`, `documents`, `data`, `files`) verboten.

## Akzeptanzkriterien

- [ ] `skill-management` und `agent-management` enthalten keine normative Wiederholung der Form-Konvention — nur den Delegations-Verweis auf diese Spec
- [ ] Jede reviewer-seitige Zitierung des Namensform-Checks (`skill-review`, `skills-agents-sweep`, die Authoring-Skills) ankert auf dieser Spec
- [ ] Die vier Validator-Listen matchen die Ausnahme- und Morphologie-Sets dieser Spec exakt
- [ ] `spec/README.md` indiziert diese Spec; en/de bleiben strukturell synchron

## References

- [R1] Skill authoring best practices, Anthropic platform docs: <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
- [R2] `plugin-scoping` §Namespace and naming coherence: `spec/claude/plugin-scoping/`
- [R3] Zeichen-Ebenen-Owner: `spec/claude/skill-management/` §Frontmatter validation · `spec/claude/agent-management/` §Structure
- [R4] `scripts/validate_skills.py` (`check_name_form` und die vier geschlossenen Listen)

## Offene Fragen

_Derzeit keine._

# License-Check — Recherche-Notiz Runde 5: Spec-Followups (2026-06-04)

> Schließt die offenen Fragen OQ-2, OQ-3, OQ-4 der gemergten Spec
> `spec/project/license-check/`. Gezielte Primärquellen-Recherche (kein
> Workflow), Belege unten je Punkt.

## OQ-3 — Patent-Grant/-Retaliation: Apache-2.0 §3 und GPL-3.0 §11

### Apache-2.0 §3 (Grant of Patent License) — verbatim belegt
- Grant: „each Contributor hereby grants to You a perpetual, worldwide,
  non-exclusive, no-charge, royalty-free, irrevocable (except as stated in this
  section) patent license to make, have made, use, offer to sell, sell, import,
  and otherwise transfer the Work, where such license applies only to those
  patent claims licensable by such Contributor that are necessarily infringed by
  their Contribution(s) alone or by combination of their Contribution(s) with the
  Work to which such Contribution(s) was submitted."
- Retaliation-Termination: „If You institute patent litigation against any entity
  (including a cross-claim or counterclaim in a lawsuit) alleging that the Work or
  a Contribution incorporated within the Work constitutes direct or contributory
  patent infringement, then any patent licenses granted to You under this License
  for that Work shall terminate as of the date such litigation is filed."
- Quelle: `apache.org/licenses/LICENSE-2.0`

### GPL-3.0 §11 (Patents) — belegt
- Grant: „Each contributor grants you a non-exclusive, worldwide, royalty-free
  patent license under the contributor's essential patent claims, to make, use,
  sell, offer for sale, import and otherwise run, modify and propagate the
  contents of its contributor version."
- Bedingung statt Retaliation-Termination: Anti-Diskriminierungs-Regel — man darf
  nicht conveyen, wenn man Partei einer Vereinbarung ist, die diskriminierende
  Patentlizenzen an Downstream-Empfänger gewährt (kommerzielle Szenarien nach dem
  28.03.2007). **Wichtig:** GPL-3.0 §11 trägt KEINE klassische
  Patent-Retaliation-*Termination* wie Apache-2.0 §3 / MPL-2.0 §5.2 / EPL-2.0 §7
  — der Mechanismus ist Grant + Anti-Diskriminierung.
- Quelle: `spdx.org/licenses/GPL-3.0-only.html` (gnu.org war zeitweise HTTP 429)

## OQ-4 — NOTICE-/Attribution-Generierung + go-licenses-Grenzen

### Verifizierter automatisierter Generator: ORT-Reporter
- Erzeugt NOTICE in zwei Varianten: `-f PlainTextTemplate` (Lizenztexte +
  Copyrights je Paket) und die Summary-Variante via
  `-O PlainTextTemplate=template.id=NOTICE_SUMMARY`; beide Apache-Freemarker-
  anpassbar. Reporter emittiert zusätzlich CycloneDX- und SPDX-2.2-Dokumente.
- → Verifizierter, stack-übergreifender NOTICE-Default, der an das SBOM-Substrat
  anschließt. Quelle: `oss-review-toolkit.org/ort/docs/tools/reporter`

### go-licenses (Google) — Modi + dokumentierte Grenzen
- `report`: CSV-Liste (Library, Lizenz-URL, Lizenztyp). `save`: bündelt, was zur
  Lizenzerfüllung neben dem Binary/Package redistribuiert werden muss (Lizenz +
  Copyright-Notice, ggf. Quelltext).
- Grenzen (README): warnt bei Nicht-Go-Code („not possible to check the non-Go
  code for further dependencies, which may conceal additional license
  requirements"); kann eine ungültige/falsche URL finden oder die URL gar nicht
  finden. README quantifiziert weder Confidence-Schwelle noch Vendoring-Verhalten.
- → Nicht-Go- oder ungelöste Komponente ist ein `review`-Befund, nie ein Silent-Pass.
- Quelle: `github.com/google/go-licenses`

### Nicht empfohlen: amzn/oss-attribution-builder
- Web-Tool, weitgehend manuell (manuelle Paket-/Lizenz-Eingabe), Repo seit
  2021-05-05 archiviert. → Kein automatisierter Default. Quelle:
  `github.com/amzn/oss-attribution-builder`

## OQ-2 — Output-Rechte/Terms kommerzieller Generatoren (verifizierte Tabelle)

Volatil (ToS ändern sich) — daher als Evidenznotiz, nicht im normativen Spec-Text.

- **GitHub Copilot:** IP-Indemnity (Copilot Copyright Commitment) nur für Business
  und Enterprise, nicht Individual/Free; seit 2026-04-03 ist der
  Duplicate-Detection-Filter KEINE CCC-Voraussetzung mehr (überholt). Läuft über
  „Defense of Third Party Claims". (Runde 4)
- **OpenAI:** weist Output-Eigentum per Assignment zu („you … own the Output. We
  hereby assign … all our right, title, and interest, if any"); „Similarity of
  Content" → nicht exklusiv. (Runde 4)
- **Adobe Firefly:** Kunde besitzt/kontrolliert Output, Adobe beansprucht keine
  IP-Rechte, garantiert aber KEINE Schützbarkeit (jurisdiktionsabhängig);
  IP-Indemnity paid-tier-gated; automatisches C2PA-Content-Credential. (Runde 3)
- **Midjourney:** zahlende Nutzer „own all Assets You create … to the fullest
  extent possible under current law"; Free-Trial-Output nur unter
  CC BY-NC 4.0 (Midjourney behält Eigentum); Firmen >1 Mio USD Umsatz brauchen
  Pro/Mega für kommerzielle Nutzung; jeder Nutzer gewährt Midjourney eine
  „perpetual, worldwide, non-exclusive, sublicensable, no-charge, royalty-free,
  irrevocable copyright license" auf Prompts + Assets (Training, öffentliche
  Anzeige, Derivate, Sublizenz). Indemnification nicht belegt. Quelle:
  `docs.midjourney.com` (ToS; direkter Fetch HTTP 403, Verbatim via Sekundärquelle
  `terms.law/ai-output-rights/midjourney`).

## Konsequenz für die Spec (in diesem PR umgesetzt)
- §Klassifizierung: Patent-Bullet um Apache-2.0 §3 / GPL-3.0 §11 präzisiert
  (GPL-3.0 ohne Retaliation-Termination explizit).
- §Per-Stack-Tooling: NOTICE-Default auf ORT-Reporter gehärtet (von „SHOULD/
  unverifiziert" zu benanntem Default) + go-licenses `save` + dessen Grenzen.
- §KI-Provenienz: MUST-NOT bleibt generisch, verweist auf diese Notiz für die
  per-Generator-Terms (volatil).
- OQ-1: Cross-Ref-Realignment in `tech-stack` + `dependency-audit` umgesetzt.

# License-Check — Recherche-Notiz Runde 3: KI-Provenienz (2026-06-01)

> Fokussierter Lückenschluss zu L3 (KI-Provenienz), die in Runde 2 unbelegt blieb.
> Quelle: deep-research-Workflow `wf_5be7c4e5-0ef` (103 Agenten, 21 Quellen,
> 99 Claims extrahiert → 25 adversarial verifiziert → 23 bestätigt, 2 widerlegt).
> Fünf Such-Angles: USCO-Rechtslage, Compliance-Risiko (akademisch),
> kommerzielle ToS, SBOM-Metadaten-Standards, Asset-/Modellgewicht-Lizenzen.

## Ergebnis in einem Satz

KI-Provenienz ist ein **belegbares, nicht nur theoretisches** Compliance-Risiko:
rein KI-generierter Output ist (US-Recht) nicht copyright-schützbar, Code-LLMs
reproduzieren nachweislich Copyleft-Code ohne Lizenzinfo, und es existieren heute
reife maschinenlesbare Provenienz-Standardfelder (CycloneDX ML-BOM, SPDX 3.0.1 AI Profile).

---

## Verifizierte Befunde

### 3.1 USCO: rein KI-generierter Output NICHT schützbar — `high` (3-0) ⭐
- U.S. Copyright Office, "Copyright and AI, Part 2: Copyrightability" (29.01.2025):
  „Because entirely AI-generated outputs do not contain the human authorship
  required to be a work of authorship."
- Prompting allein genügt nicht: „prompts alone do not provide sufficient human
  control … Prompts essentially function as instructions that convey unprotectible
  ideas." — „Repeatedly revising prompts does not change this analysis."
- Schutz nur „where a human author has determined sufficient expressive elements …
  but not the mere provision of prompts" (kreative Anordnung/Bearbeitung zählt).
- Office sieht **keinen** Gesetzgebungsbedarf — bestehendes Recht „flexible enough".
- ⚠️ CAVEAT: bindet nur **US-Recht** (EU/DE-Autorschaftsschwelle weicht ab, nicht
  recherchiert); betrifft **Copyrightability** (Part 2), NICHT Training/Fair-Use (Part 3).
- Quellen: copyright.gov AI Part 2 PDF, blogs.loc.gov, copyright.gov/newsnet/2025/1060

### 3.2 Code-LLMs reproduzieren OSS-Code quasi-wörtlich — `high` (3-0)
- LiCoEval (arXiv:2408.02487, **ICSE 2025**, 14 Modelle, 4.187 Samples): „even
  top-performing LLMs produce a non-negligible proportion (**0.88 % to 2.01 %**) of
  code strikingly similar to existing open-source implementations."
- „striking similarity"-Standard ist konservativ (Funktionskörper >10 Zeilen,
  zyklomatische Komplexität >3, Textähnlichkeit >0.6 UND ≥1 identischer Kommentar)
  → also **Untergrenze**.
- CODEIPPROMPT (Yu et al., **ICML 2023**, inkl. GPT-4/ChatGPT/Codex/Copilot): die
  meisten Modelle reproduzieren lizenzierten Code „within 50 prompted code generations".
- Mechanismus (arXiv:2302.13681): Trainingsdaten werden „memorized and emitted …
  often in a verbatim manner".
- ⚠️ CAVEAT: Extraktionsraten sind prompt-/angriffsabhängig — Studien belegen die
  **Existenz** des Mechanismus, **nicht eine hohe Häufigkeit** (absolute Rate ≤2 %).

### 3.3 Konkretes Compliance-Risiko: Copyleft-Code ohne Lizenzinfo — `high` (2-1→3-0) ⭐
- LiCoEval: „LLMs can generate license-protected code without providing the necessary
  license information, leading to potential intellectual property violations" und
  „**Most models fail to provide any license information for code snippets under
  copyleft licenses**, with only Claude-3.5-sonnet demonstrating some ability".
- CODEIPPROMPT differenziert die Pflichten: permissiv (MIT/BSD) = Lizenzkopie +
  Attribution; Copyleft (GPL/AGPL) = gesamtes Programm unter gleicher Lizenz.
- ⚠️ WICHTIG: Die Papers verwenden den Term **„license laundering" NICHT** — sie
  sprechen von „compliance risks"/"IP infringement". Die Kausalkette
  (striking-similar Copyleft-Code ohne Lizenzinfo → nicht-attribuierter Copyleft-Code
  im permissiven Projekt) ist belegt; **„laundering" ist zulässige Interpretation,
  kein Paper-Wortlaut** → in der Spec so kennzeichnen.

### 3.4 Selbst permissiv-kuratierte Trainingskorpora enthalten Copyleft — `high` (3-0)
- TU Delft (FORGE 2024, arXiv:2403.15230): „every dataset we examined contained
  license inconsistencies, despite being selected based on their associated
  repository licenses." (SHA-256-Exact-Match, 514 Mio. Dateien gegen ~35 Mio.
  GPL/AGPL-Repos.)
- Copyleft-Overlap: The Stack v1 **6,14 %** (16,1 Mio. Dateien), RedPajama 5,49 %,
  The Pile 22,80 %. „at least 5 %" selbst bei permissiv-gefilterten Sets.
- Korroboriert: „Cracks in the Stack" (arXiv:2501.02628, IEEE, Jan 2025) für Stack v2.
- ⚠️ CAVEAT: misst exakten Datei-Hash-Overlap, **keine festgestellte Rechtsverletzung**
  (exploratory). „use of copyleft code to train LLMs is a legal and ethical dilemma".

### 3.5 Kommerzielle Generatoren regeln Output-Rechte vertraglich (Adobe Firefly belegt) — `high` (3-0)
- Adobe Firefly Legal FAQs (Enterprise, 2024-06-11): „the customer owns and controls
  Firefly outputs … Adobe does not assert any IP rights in the output."
- ABER keine Schützbarkeits-Garantie: „Whether or not a customer owns the copyright …
  depends on the laws of the customer local jurisdiction."
- **IP-Indemnity ist paid-tier-gated**: nur bei gekauftem Entitlement, nur GA-Bild-
  Features. Free-Tier = keine Indemnification; Enterprise = volle (Caps 50K+ USD).
- Adobe setzt automatisch ein maschinenlesbares **C2PA-Content-Credential** (markiert
  Output als Generative-AI; ab Anfang 2026 verpflichtend, kein Opt-out).
- ⚠️ CAVEAT: **GitHub Copilot / OpenAI / Midjourney ToS NICHT verifiziert** in dieser
  Runde (siehe offene Fragen).

### 3.6 CycloneDX ML-BOM = reifes Provenienz-Format — `high` (3-0) ⭐
- OWASP-Flaggschiff, ECMA-424. ML-BOM „Represents datasets, models, and configurations
  … Documents provenance and ethical considerations for datasets."
- Component-Typ `machine-learning-model` (Schema-Enum, eingeführt v1.5 Juni 2023,
  gültig bis v1.7 Okt 2025).
- `modelCard`-Block: modelParameters, datasets, quantitativeAnalysis,
  technicalLimitations, ethicalConsiderations, fairnessAssessments, externalReferences.
- Modell-Lineage via `pedigree.ancestors`; v1.7 ergänzt „Citations and Data Provenance".
- ⚠️ EINSCHRÄNKUNG: `ancestors` modelliert Ableitung **zwischen Komponenten**, ist NICHT
  das Flag „dieser Artefakt wurde von KI erzeugt" — dafür dienen modelCard / Component-Typ.

### 3.7 SPDX 3.0.1 AI Profile = normatives Provenienz-Vokabular — `high` (3-0) ⭐
- SPDX 3.0.1 (Linux Foundation, 2024-12-27). AI Profile „standardized way of
  documenting … AI software packages".
- Konkrete instanziierbare `AIPackage`-Klasse (`SubclassOf: /Software/Package`).
- ~13 Provenienz-Properties: typeOfModel, hyperparameter, limitation,
  safetyRiskAssessment, standardCompliance, autonomyType, domain,
  informationAboutTraining, informationAboutApplication, modelDataPreprocessing,
  modelExplainability, metric, useSensitivePersonalInformation, energyConsumption.
- ⚠️ EINSCHRÄNKUNG (zentral für Spec-Frage 4): Das AI Profile dokumentiert das
  AI-System/-Modell **als Artefakt** (SBOM-Komponente), NICHT primär das Flaggen, dass
  eine **beliebige Datei/ein Asset KI-generiert** wurde (Provenienz-als-Autor). Für reine
  Datei-Provenienz behelfsweise SPDX-Comment/Annotation — **kein dediziertes
  „AI-generated-file"-Flag existiert** (offene Frage).

---

## Abgeleitete Empfehlung (Synthese, `medium`)

Belegt = die Risiken; Empfehlung = die Prozess-Ausgestaltung. Drei Pflichten:

1. **KI-Provenienz als Pflicht-Attribut im Inventar.** Jedes KI-erzeugte Artefakt
   maschinenlesbar markieren (Generator/Modell/Tier). Standardträger existieren heute:
   CycloneDX `machine-learning-model` + `modelCard` + `externalReferences`; SPDX
   `AIPackage`-Properties; für reine Datei-Provenienz hilfsweise SPDX-Comment/Annotation.
2. **Copilot/LLM-Duplikat-Erkennung als Gate.** Begründet durch 0,88–2,01 %
   striking-similarity + fehlende Copyleft-Lizenzinfo: Snippet-Ähnlichkeitsscan gegen
   Copyleft-OSS (analog LiCoEval / GitHub Copilot Duplicate Detection) für KI-erzeugten Code.
3. **Open-weight-Modelllizenzen als erhöhter Review-Tier.** OpenRAIL / Llama Community
   License / Gemma Terms als use-restricted / nicht-OSI-konform behandeln → separater
   manueller Review-Tier, NICHT in die automatische permissive Allowlist.
   (OSI-Status nicht final verifiziert — siehe offene Fragen.)

---

## ⚠️ WIDERLEGTE Claims — NICHT in die Spec
- „Verteilung trainierter Modelle = Weiterverbreitung geschützten Materials" — **0-3 ✗**
  (arxiv 2403.15230 rahmt das als ungelöstes Dilemma, nicht als Befund).
- „Existing code LMs implement no mechanism to ensure license compliance" — **1-2 ✗**
  (zu absolut formuliert; Claude-3.5-sonnet zeigt teilweise Lizenzinfo, s. 3.3).

## Verbleibende offene Fragen
1. **GitHub Copilot / OpenAI / Midjourney ToS** — Output-Rechte + Indemnity (Free vs.
   Paid) nicht verifiziert (nur Adobe Firefly belegt). Teilfrage 3(a) offen.
2. **Open-weight-Lizenz-OSI-Status** — OpenRAIL-M / Llama / Gemma: der belegbare
   Unterschied (use-restricted, kein OSI-Approval) wurde nicht durch verifizierte
   Primärquellen-Claims abgedeckt (gefetcht: opensource.org/ai-definition,
   huggingface.co/blog/open_rail) → gezielt nachsourcen.
3. **Dediziertes „AI-generated-file"-Flag** in SPDX/CycloneDX — existiert nicht;
   Provenienz-als-Autor muss behelfsweise modelliert werden.
4. **Verbindliche Duplikat-Erkennungs-Schwelle/Toolchain** inkl. False-Positive-Rate
   (analog LiCoEval / Copilot Duplicate Detection) für ein CI-Gate.

## Pins / Stichtag (2026-06-01)
- USCO Part 2: 29.01.2025 (Copyrightability; US-Recht).
- SPDX 3.0.1 AI Profile (2024-12-27); CycloneDX ML-BOM v1.5–v1.7.
- C2PA-Content-Credentials bei Adobe ab Anfang 2026 verpflichtend.

# License-Check — Recherche-Notiz Runde 4: ToS, Open-Weight & Patent-Klauseln (2026-06-01)

> Schluss-Runde zu den Rest-Punkten aus Runde 2+3.
> Quelle: deep-research-Workflow `wf_690e16b5-ad1` (106 Agenten, 24 Quellen,
> 83 Claims extrahiert → 25 adversarial verifiziert → 22 bestätigt, 3 widerlegt).
> Fünf Angles: Copilot-ToS, OpenAI/Midjourney-ToS, Open-Weight vs. OSI,
> MPL/EPL Copyleft+Patente, NOTICE-Generatoren+go-licenses.

## Ergebnis in einem Satz

Drei der fünf Punkte sind jetzt primärquellengestützt belegt (Copilot, OpenAI,
Open-Weight-Lizenzen, MPL/EPL). **Drei Teilfragen fielen aus** (Midjourney,
Apache-2.0 §3 / GPL-3.0 §11 Patente, NOTICE-Generatoren/go-licenses) — diese
bleiben für die Spec offen.

---

## Verifizierte Befunde

### 4.1 GitHub Copilot: Indemnity nur Business/Enterprise — Filter NICHT mehr Pflicht — `high` (3-0) ⭐⚠️
- Copilot Copyright/IP-Indemnity gilt **nur für Copilot Business und Enterprise**,
  NICHT für Individual/Free. Product Specific Terms (März 2026): „These terms only
  apply to Copilot Business and Copilot Enterprise … If you purchase GitHub Copilot
  Individual, these terms do not apply to you."
- Läuft über die „Defense of Third Party Claims"-Klausel.
- ⭐ **STICHTAGS-FUND (überschreibt Annahme aus den Vorrunden):** Seit **3. April 2026**
  ist der **Duplicate-Detection-Filter KEINE Voraussetzung mehr** für die CCC-Deckung
  der GitHub Offerings. Microsoft Learn (Update 2026-05-12): „as of April 3, 2026,
  there are no additional required mitigations. Use of the Duplicate Detection filter
  feature is no longer required for CCC coverage. This feature remains available for
  optional use."
- CCC = Klausel der Microsoft Product Terms: „Microsoft's obligation to defend
  customers against certain third-party intellectual property claims relating to
  Output Content."
- ⚠️ Für **Azure OpenAI** (nicht Copilot) bleiben die dokumentierten Required
  Mitigations weiterhin CCC-Voraussetzung — Quelle des Outputs unterscheiden.
- ⚠️ SPEC-HINWEISE: (a) Stichtagsdatum 3.4.2026 explizit verankern + bei Wartung neu
  prüfen; viele Sekundärquellen zitieren noch die überholte „Filter=Pflicht". (b) Das
  kursierende Indemnity-„Zitat" ist Paraphrase — echte „Defense of Third Party Claims"-
  Klausel zitieren.
- Quellen: learn.microsoft.com/.../customer-copyright-commitment, GitHub Copilot Product Specific Terms 2026-03-05 PDF

### 4.2 OpenAI: Output-Eigentum per Assignment, aber nicht exklusiv — `high` (3-0)
- ToS verbatim: „you (a) retain your ownership rights in Input and (b) own the Output.
  We hereby assign to you all our right, title, and interest, **if any**, in and to Output."
- „Similarity of Content"-Klausel schränkt faktisch ein: „Output may not be unique and
  other users may receive similar output." → kein Exklusivitätsanspruch; Assignment
  erstreckt sich NICHT auf Output anderer Nutzer.
- „if any" + „to the extent permitted by applicable law" → reiner KI-Output ggf. nicht
  schutzfähig (verbindet mit USCO-Befund 3.1).
- ⚠️ CAVEAT: openai.com gab HTTP 403; Verbatim über zwei unabhängige Sekundärabrufe
  bestätigt — Primärquelle bleibt openai.com, direkte Verifikation eingeschränkt.
- Quelle: openai.com/policies/row-terms-of-use

### 4.3 Open-Weight-Lizenzen sind NICHT OSI/OSAID-konform — `high` (3-0) ⭐
- **OSAID 1.0** verlangt vier Freiheiten, drei explizit „**for any purpose**" (Use,
  Modify, Share).
- **OpenRAIL/RAIL-M:** verhaltensbasierte Use-Restrictions in kritischen Szenarien;
  Hugging Face räumt die Spannung zu „criteria 6 of the Open Source Definition" selbst ein.
- **Llama Community License (3.1):** kommerzielle **700-Mio-MAU-Schwelle** („greater
  than 700 million monthly active users … you must request a license from Meta") +
  verpflichtende Acceptable Use Policy („incorporated by reference").
- **Gemma (custom Terms of Use):** §3.2 Use Restrictions (bindet an Prohibited Use
  Policy) + §3.1 Downstream-Flow-down (Restrictions müssen an alle Empfänger
  weitergegeben werden).
- Alle drei verstoßen gegen „for any purpose" bzw. OSD §5/§6 → **keine Open Source**.
  OSI bestätigt das für Llama und Gemma explizit.
- ⚠️ VERSIONS-NUANCE: Gilt für custom Gemma ToU (Gemma 1/2/3). **Gemma 4 (2026-03)
  wechselte auf Apache-2.0** ohne diese Restrictions → Spec versionsbezogen formulieren,
  nicht „Gemma" pauschal.
- Quellen: opensource.org/ai/open-source-ai-definition, huggingface.co/blog/open_rail, llama.com/llama3_1/license, ai.google.dev/gemma/terms

### 4.4 MPL-2.0: datei-granulares Copyleft + Patent-Klauseln — `high` (3-0)
- **Datei-granulares (weak) Copyleft:** FAQ Q12: „MPL: The copyleft applies to any
  files containing MPLed code." (Kontrast: LGPL = library-based, GPL = all software).
- `Modifications` (§1.10) per Datei definiert: geänderte Datei mit Covered Software
  ODER neue Datei mit Covered Software. Neue Dateien **ohne** MPL-Code sind keine
  Modifications (§3.3, FAQ Q11) → dürfen im Larger Work andere Lizenz tragen.
- **Offenlegungs-Trigger:** §3.1 (jede Source-Distribution inkl. Modifications unter MPL),
  §3.2 (auch bei Executable-Form: Source verfügbar machen + Informationspflicht).
- **Patent-Grant** §2.1(b); **Patent-Retaliation** §5.2: Patentklage („Contributor
  Version … infringes any patent") lässt §2.1-Patentrechte **aller Contributors**
  für die Covered Software erlöschen.
- Quellen: mozilla.org/MPL/2.0, mozilla.org/MPL/2.0/FAQ

### 4.5 EPL-2.0: werk-/datei-granulares Copyleft + Patent-Klauseln — `high` (3-0)
- Copyleft greift nur auf **Modified Works**; reiner Link-/Bind-/Subclass-Code ist keine
  Contribution: „Modified Works shall not include works that contain only declarations,
  interfaces, types, classes, structures, or files of the Program solely … to link to,
  bind by name, or subclass the Program."
- Brückensatz §1: „Contributions do not include changes or additions to the Program
  that are not Modified Works." → effektiv weak Copyleft.
- **Patent-Grant** §2(b): non-exclusive, weltweit, royalty-free pro Contribution;
  **Hardware ausdrücklich ausgeschlossen** („No hardware per se is licensed hereunder").
- **Patent-Retaliation** §7: Patentklage („the Program itself … infringes such
  Recipient's patent(s)", Kombinationen ausgeschlossen) → §2(b)-Rechte erlöschen
  zum Klagedatum.
- ⚠️ SPEC-HINWEIS: Linking-Ausschluss korrekt der „Modified Works"-Definition zuordnen
  (nicht direkt „Contribution") und den Brückensatz mitführen.
- Quellen: spdx.org/licenses/EPL-2.0.html, eclipse.org/legal/epl-2.0

---

## ⚠️ WIDERLEGTE Claims — NICHT in die Spec
- „Copilot-Indemnity greift nur bei aktiviertem Duplicate-Detection-Filter" — **0-3 ✗**
  (seit 3.4.2026 überholt, s. 4.1).
- „Copilot: Output gehört dem Kunden, GitHub beansprucht kein Eigentum" — **1-2 ✗**
  (so pauschal nicht belegt aus den März-2026-Terms).
- „MPL-Disclosure-Trigger = §1.10" — **1-2 ✗** (korrekt sind §3.1/§3.2, s. 4.4).

## ❌ NICHT belegt — bleiben für die Spec offen
1. **Midjourney ToS (2b):** Bildeigentum, Sonderklausel nicht-zahlende vs. zahlende
   Nutzer, non-exclusive license to Midjourney, Indemnification — kein verifizierter
   Claim (Budget-Drop). Folgerunde nötig, wenn die Spec Midjourney adressieren soll.
2. **Apache-2.0 §3 / GPL-3.0 §11 Patent-Grant + Retaliation:** in dieser Runde kein
   Claim (nur MPL/EPL abgedeckt). Vor Festschreibung der Patent-Matrix prüfen, ob die
   Vorrunden das schon abdecken (Runde 1 erwähnte Apache-2.0-Patenttermination als
   GPLv2-Inkompatibilitätsgrund, aber nicht den §3-Grant selbst).
3. **NOTICE-/Attribution-Generierung + go-licenses-Grenzen (5):** ORT NOTICE-reporter,
   oss-attribution-generator, go-licenses (Vendoring, fehlende LICENSE-Dateien,
   Confidence-Schwelle/FP) — komplett unbelegt (Budget-Drop). Primärquellen gefetcht
   (github.com/google/go-licenses + issue #143, oss-review-toolkit.org/.../reporter,
   zumwald/oss-attribution-generator, amzn/oss-attribution-builder), aber keine
   verifizierten Claims.

## Pins / Stichtag (2026-06-01)
- Copilot CCC: Duplicate-Filter seit **3.4.2026** nicht mehr Pflicht (MS-Learn Update 2026-05-12).
- Gemma: custom ToU für 1/2/3; **Gemma 4 (2026-03) = Apache-2.0**.
- OSAID 1.0 als Maßstab für OSI-Konformität.

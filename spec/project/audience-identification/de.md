# Zielgruppen-Identifikation

Status: draft

## Kontext
<!-- Warum existiert diese Spec? Welches Problem, welcher Bedarf oder welche Einschränkung treibt sie? -->

Software-Module und Projekte werden von mehreren Zielgruppen konsumiert, betrieben, eingeschränkt oder beobachtet — Nutzer, Betreiber, nachgelagerte Integratoren, Maintainer, Security, Compliance, Business-Stakeholder, indirekt betroffene Endnutzer und mehr. Ohne ein diszipliniertes Verfahren, die zutreffenden Zielgruppen für einen *abgesteckten Kontext* (ein konkretes Modul, einen Service, eine Bibliothek oder ein Projekt) zu ermitteln, werden Entscheidungen über Dokumentationstiefe, API-Oberfläche, Release-Taktung, SLAs und Sicherheitslage gegen die privaten Annahmen der Autoren statt gegen die tatsächliche Zielgruppen-Menge getroffen. Diese Spec definiert ein wiederholbares Verfahren, mit dem sich die Zielgruppen eines abgesteckten Kontexts ermitteln und charakterisieren lassen, damit nachgelagerte Artefakte (READMEs, Specs, Threat Models, Release Notes, SLAs) auf eine belastbare Zielgruppenliste verweisen können, statt sie jedes Mal neu zu erfinden.

## Ziele
<!-- Was diese Spec erreichen will. Stichpunkte, ergebnisorientiert. -->
- Ein konsistentes Verfahren zum Aufzählen der Zielgruppen eines abgesteckten Kontexts bereitstellen
- Sicherstellen, dass jede identifizierte Zielgruppe über ihre Beziehung zum Kontext charakterisiert wird (konsumieren, betreiben, erweitern, regeln, …)
- Ein Artefakt erzeugen, auf das andere Specs (`readme-structure`, `pull-request-workflow`, künftige Threat-Modeling-Specs, …) verweisen können
- Zielgruppen-Identifikation wiederholbar und reviewbar machen — nicht das Bauchgefühl einzelner Autoren
- Unbekannte oder angenommene Zielgruppen explizit sichtbar machen, damit sie validiert oder verworfen werden können

## Nicht-Ziele
<!-- Was explizit außerhalb des Scopes liegt. Verhindert Scope Creep. -->
- Definition von Marketing-Personas oder demografischer Segmentierung
- Vorgaben, wie mit identifizierten Zielgruppen kommuniziert wird
- Erzeugen einer dauerhaften, organisationsweiten Master-Zielgruppenliste (diese Spec gilt pro Kontext, nicht pro Organisation)
- Threat Modeling — Zielgruppen fließen dort ein, sind aber nicht mit Angreifern gleichzusetzen
- Festlegen, in welchem Artefakt-Format (README-Abschnitt, eigene Datei, ADR, …) die Zielgruppenliste lebt; das ist eine Umsetzungsentscheidung der anwendenden Specs

## Anforderungen
<!-- RFC-2119-Schlüsselwörter verwenden: MUST, SHOULD, MAY. Eine atomare Anforderung pro Bullet. -->
- **MUSS [MUST]** mit einer schriftlichen Deklaration des abgesteckten Kontexts beginnen: was das Modul oder Projekt *ist*, wo seine Grenzen verlaufen und was explizit außerhalb liegt
- **MUSS [MUST]** Zielgruppen unter folgenden Beziehungskategorien aufzählen und "keine" mit Begründung angeben, wenn eine Kategorie nicht zutrifft:
  - **Direkte Konsumenten** — wer die Schnittstelle des Kontexts aufruft (Menschen, andere Services, nachgelagerte Bibliotheken)
  - **Betreiber** — wer den Kontext in Produktion oder Test ausführt, deployt, überwacht oder hostet
  - **Beitragende / Maintainer** — wer den Code oder dessen Inhalte ändert
  - **Steuernde Parteien** — Legal, Compliance, Security, Architektur-Review, Business-Stakeholder mit Freigabe- oder Vorgabebefugnis
  - **Indirekte Zielgruppen** — Parteien, die vom Kontext betroffen sind, ohne direkt mit ihm zu interagieren (z. B. Endnutzer hinter einem konsumierten Service)
- **MUSS [MUST]** pro gelisteter Zielgruppe erfassen:
  - kurzes Label
  - Beziehungskategorie
  - Interaktionsfläche (API, CLI, Config, Docs, Dashboard, Incident-Kanal, …)
  - was die Zielgruppe vom Kontext erwartet oder benötigt
  - offene Fragen oder Annahmen, wenn Informationen fehlen
- **MUSS [MUST]** jede Zielgruppe als `confirmed` (mit realer Vertretung oder belastbarer Quelle validiert) oder `assumed` (vom Autor angenommen) kennzeichnen
- **MUSS [MUST]** die Zielgruppenliste erzeugen, bevor nachgelagerte Artefakte geschrieben werden, die eine Zielgruppe beanspruchen (README "intended consumers", SLAs, Threat Models, …), damit diese darauf verweisen statt sie neu zu formulieren
- **SOLLTE [SHOULD]** Zielgruppen nach Kritikalität für den Erfolg des Kontexts ordnen (primär / sekundär / peripher)
- **SOLLTE [SHOULD]** das Zielgruppen-Artefakt neben dem beschriebenen Kontext ablegen (Modul-README, projektweite `docs/audiences.md`, ADR, …) statt in einem zentralen Register
- **SOLLTE [SHOULD]** die Zielgruppenliste erneut prüfen, sobald sich der Scope des Kontexts wesentlich ändert — neue öffentliche API, neues Deployment-Target, neue regulierte Datenklasse, neuer Stakeholder
- **KANN [MAY]** jeden Zielgruppen-Eintrag auf die für ihn erzeugten Specs, Docs oder SLAs verlinken, damit Abdeckung sichtbar wird
- **KANN [MAY]** Zielgruppen zusätzlich nach Geografie, Organisationseinheit oder Mandantenzuordnung unterteilen, wenn solche Unterschiede das erwartete Liefergut verändern

## Abnahmekriterien
<!-- Testbare, abhakbare Bedingungen. Reviewer müssen pro Punkt "erfüllt / nicht erfüllt" markieren können. -->
- [ ] Ein durchgearbeitetes Beispiel existiert, das das Verfahren auf ein konkretes Artefakt dieses Repositories anwendet (z. B. das `nolte-shared`-Plugin oder einen seiner Skills)
- [ ] Die `readme-structure`-Spec verweist auf diese Spec an der Stelle, an der sie von "intended consumers" spricht
- [ ] Eine nach dieser Spec erzeugte Zielgruppenliste enthält mindestens eine Zielgruppe pro zutreffender Beziehungskategorie oder dokumentiert "keine" mit Begründung für jede ausgelassene Kategorie
- [ ] Jeder Zielgruppen-Eintrag unterscheidet `confirmed` von `assumed`
- [ ] Der abgesteckte Kontext ist schriftlich deklariert, bevor eine Zielgruppe gelistet wird
- [ ] Der `spec-drift-audit`-Skill kann ein Modul flaggen, dessen dokumentierte Zielgruppen nicht mehr mit der tatsächlichen Interaktionsfläche übereinstimmen

## Offene Fragen
<!-- Ungelöste Entscheidungen, bekannte Unbekannte, Punkte, die eine Stakeholder-Antwort brauchen. -->
- Soll das Zielgruppen-Artefakt auf eine dedizierte Datei (z. B. `AUDIENCES.md`) standardisiert werden oder Abschnitt in bestehenden Artefakten (README, ADR) bleiben?
- Gibt es eine minimale Kontextgröße, unterhalb der dieses Verfahren übertrieben ist (z. B. ein 50-Zeilen-internes Utility)?
- Gilt diese Spec portfolioweit oder nur für Repositories, die sich explizit dazu entscheiden?
- Wie wird eine Zielgruppenliste versioniert — pro Release, pro wesentlicher API-Änderung oder fortlaufend über Git-Historie?
- Ist die Kategorie "Steuernde Parteien" auch für rein interne Single-Team-Module verpflichtend oder dort optional?
- Wie verhält sich diese Spec zu künftigen Threat-Modeling-, Privacy-Impact- oder SLA-Specs, die dieselbe Zielgruppenliste konsumieren werden?

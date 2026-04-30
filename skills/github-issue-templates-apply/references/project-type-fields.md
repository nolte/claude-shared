# Project-Type-Specific Field Bundles

Read this file in step 3 (Derive templates and fields) of the skill's operation.

Each bundle lists the additional Issue Forms components to append to the baseline `bug_report.yml` (and, where relevant, `feature_request.yml`) for one detected project type. Bundles are starting points — the audience artefact may motivate further fields. Never copy a bundle that does not match the detected project type.

All YAML stays English regardless of the repo's documentation language (the GitHub issue UI is English-only in practice).

---

## Claude Code plugin

**Detection.** `.claude-plugin/plugin.json` exists at the repo root; top-level `skills/` and/or `agents/` folder present.

**Append to `bug_report.yml`:**

```yaml
  - type: dropdown
    id: artefact-kind
    attributes:
      label: Affected artefact
      description: Which kind of plugin artefact does this bug touch?
      options:
        - skill
        - agent
        - spec
        - plugin manifest
        - other
    validations:
      required: true
  - type: input
    id: artefact-name
    attributes:
      label: Artefact name
      placeholder: e.g. pull-request-create, github-issue-templates-apply
    validations:
      required: true
  - type: input
    id: plugin-version
    attributes:
      label: Plugin version
      description: Version from `.claude-plugin/plugin.json` or the marketplace entry.
    validations:
      required: true
  - type: input
    id: claude-code-version
    attributes:
      label: Claude Code version
      description: Output of `claude --version` or the IDE-extension version.
    validations:
      required: true
  - type: textarea
    id: transcript
    attributes:
      label: Session transcript
      description: Paste the relevant turns of your Claude Code session, redacted as needed.
      render: shell
    validations:
      required: false
```

**Append to `feature_request.yml`** (all fields stay **optional** — feature requests are deliberately permissive per the spec; never raise these to `required: true` even when the matching bug-report field is required):

```yaml
  - type: dropdown
    id: target-artefact
    attributes:
      label: Target artefact type
      description: What kind of artefact would carry the proposed change? Skip if you're not sure yet.
      options:
        - new skill
        - new agent
        - revision to existing skill or agent
        - new spec
        - revision to existing spec
    validations:
      required: false
```

---

## Python application

**Detection.** `pyproject.toml` declares an application entry point (typically `[project.scripts]`) without library distribution metadata. Dockerfile, docker-compose.yml, or runtime config commonly present.

**Append to `bug_report.yml`:**

```yaml
  - type: input
    id: app-version
    attributes:
      label: Application version
      description: Output of `<app> --version`, or the release tag you installed from.
    validations:
      required: true
  - type: input
    id: python-version
    attributes:
      label: Python version
      description: Output of `python --version`.
    validations:
      required: true
  - type: dropdown
    id: install-method
    attributes:
      label: Install method
      options:
        - pip / pipx
        - Docker / OCI image
        - source checkout
        - distribution package (apt, brew, …)
    validations:
      required: true
  - type: input
    id: os
    attributes:
      label: Operating system
      placeholder: e.g. Ubuntu 24.04, macOS 14.5, Raspberry Pi OS Bookworm
    validations:
      required: true
  - type: textarea
    id: traceback
    attributes:
      label: Traceback or error output
      render: shell
    validations:
      required: false
```

**Hardware-touching variant.** If the application touches cameras, sensors, robotics, or embedded hardware (signals: `gphoto2`, `picamera2`, `pyserial`, `RPi.GPIO`, `smbus`, `pyudev` in dependencies, or user confirmation — for example `kamerplanter`), additionally append:

```yaml
  - type: input
    id: hardware-model
    attributes:
      label: Hardware model
      description: Specific device, sensor, or camera model.
    validations:
      required: true
  - type: input
    id: firmware-version
    attributes:
      label: Firmware version
    validations:
      required: false
  - type: textarea
    id: hardware-context
    attributes:
      label: Hardware context
      description: Connection (USB, I²C, SPI, network), power source, environment notes.
    validations:
      required: false
```

---

## Python library

**Detection.** `pyproject.toml` declares a distributable package (typically `[project]` with `name`, no `[project.scripts]`, build backend such as `hatchling`, `setuptools`, or `poetry-core`).

**Append to `bug_report.yml`:**

```yaml
  - type: input
    id: library-version
    attributes:
      label: Library version
    validations:
      required: true
  - type: input
    id: python-version
    attributes:
      label: Python version
    validations:
      required: true
  - type: textarea
    id: reproducer
    attributes:
      label: Minimal reproducer
      description: The smallest snippet that reproduces the bug.
      render: python
    validations:
      required: true
  - type: textarea
    id: traceback
    attributes:
      label: Traceback
      render: shell
    validations:
      required: false
```

---

## Node / TypeScript library or app

**Detection.** `package.json` exists. Library bias when `main` / `exports` is set; app bias when `bin` / `scripts.start` is set. When both are set, treat as a hybrid and ask the user.

**Append to `bug_report.yml`:**

```yaml
  - type: input
    id: package-version
    attributes:
      label: Package version
      description: Version from `package.json` or `npm ls <package>`.
    validations:
      required: true
  - type: input
    id: node-version
    attributes:
      label: Node.js version
      description: Output of `node --version`.
    validations:
      required: true
  - type: input
    id: package-manager
    attributes:
      label: Package manager and version
      placeholder: e.g. pnpm 9.12.0, npm 10.8.1
    validations:
      required: false
  - type: textarea
    id: reproducer
    attributes:
      label: Minimal reproducer
      description: The smallest snippet (TypeScript or JavaScript) that reproduces the bug.
      render: typescript
    validations:
      required: true
```

For pure apps (browser-side or server-side without a public API surface), drop the reproducer field and replace with:

```yaml
  - type: dropdown
    id: runtime
    attributes:
      label: Runtime
      options:
        - browser
        - Node.js server
        - serverless / edge
        - other
    validations:
      required: true
  - type: input
    id: browser
    attributes:
      label: Browser and version
      description: Only relevant for browser-side bugs.
    validations:
      required: false
```

---

## CLI tool

**Detection.** Declared CLI entry point in `pyproject.toml` (`[project.scripts]`), `package.json` (`bin`), or `Cargo.toml` (`[[bin]]`). The repo's primary deliverable is a command, not a library.

**Append to `bug_report.yml`:**

```yaml
  - type: input
    id: tool-version
    attributes:
      label: Tool version
      description: Output of `<tool> --version`.
    validations:
      required: true
  - type: textarea
    id: command
    attributes:
      label: Command and arguments
      description: The exact command line that triggered the bug. Redact secrets.
      render: shell
    validations:
      required: true
  - type: textarea
    id: output
    attributes:
      label: Output / stderr
      render: shell
    validations:
      required: true
  - type: input
    id: os
    attributes:
      label: Operating system
    validations:
      required: true
```

---

## Documentation-only repository

**Detection.** `mkdocs.yml`, `docusaurus.config.*`, or similar exists; no application source.

**Replace** the baseline `bug_report.yml` with `documentation.yml`:

```yaml
name: Documentation Issue
description: Report a documentation problem (incorrect, missing, unclear, or out of date).
title: "[docs] "
labels: ["documentation", "needs-triage"]
body:
  - type: checkboxes
    id: search
    attributes:
      label: Search
      options:
        - label: I have searched the existing issues for similar reports.
          required: true
  - type: input
    id: page
    attributes:
      label: Page or section
      description: URL or path of the affected page.
    validations:
      required: true
  - type: dropdown
    id: kind
    attributes:
      label: Issue kind
      options:
        - incorrect
        - missing
        - unclear or confusing
        - out of date
        - broken link
    validations:
      required: true
  - type: textarea
    id: details
    attributes:
      label: Details
    validations:
      required: true
  - type: textarea
    id: suggestion
    attributes:
      label: Suggested fix
    validations:
      required: false
```

Keep `feature_request.yml` only when the repository accepts new content suggestions; otherwise route via `config.yml`'s `contact_links`.

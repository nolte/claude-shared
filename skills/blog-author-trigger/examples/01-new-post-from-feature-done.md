# Example: new post from a feature → done transition

`sprint-execute` has just marked feature `F-7` (`add-lektorat-scanner-agent`) `done` and automatically dispatched `blog-author-trigger`.

## 1. Resolve the trigger event

```
project/features/add-lektorat-scanner-agent.md
  id: F-7
  status: done           # confirmed — feature → done fires
  title: Add lektorat-scanner agent
  description: Read-only scanner that walks Markdown artefacts and returns D1–D6 findings.
  roadmap_item: R-8
done-transition commit: 3b7fc1d
repo: nolte/claude-shared
```

## 2. Derived briefing

| Field | Derived value |
| --- | --- |
| topic-as-thesis | "The read-only lektorat-scanner agent walks Markdown artefacts and returns D1–D6 findings." |
| grounded artefact | `nolte/claude-shared@3b7fc1d` |
| primary audience | *unset* — operator selects at intake |
| source list | `https://github.com/nolte/claude-shared/commit/3b7fc1d` |
| slug | `lektorat-scanner-agent` (lifecycle prefix dropped) |
| translationKey | `lektorat-scanner-agent` |
| portfolioProject | `claude-shared` (from the blog consumer's portfolio mapping) |

## 3. Suggestion + choice

Derived slug `lektorat-scanner-agent` is **absent** from `nolte/blog`'s existing-post index → the skill suggests **Choice 1 (new post)**. The operator confirms Choice 1.

## 4. Execute

- The skill pre-stages `project/blog-triggers/add-lektorat-scanner-agent.briefing.md` in `claude-shared`.
- It surfaces the blog-consumer clone path `~/repos/github/blog` and asks the operator to confirm the working-directory switch (no silent cross-repo write).
- The operator opens a new Claude Code session in `~/repos/github/blog` and invokes `blog-author` with the pre-staged briefing as Step-1 input; the standard seven-step `blog-author` workflow runs from there, with the operator selecting the primary audience at intake.

# Example 01 — `design` for a repository with no pipeline beyond the release workflows

## Input prompt

> "Dieses Repo hat nur die Release-Workflows. Entwirf mir eine CI/CD-Pipeline dafür."

## Input state

A Python application repository containing:

- `Taskfile.yml` with `setup`, `lint`, `typecheck`, `test`, `check`
- `uv.lock`, `pyproject.toml`
- `Dockerfile`
- `.github/workflows/` holding only `release-drafter.yml`, `release-publish.yml`, `release-cd-refresh-master.yml`, `automerge.yaml`
- `project/portfolio.yml` declaring the project type

## Expected behaviour

1. Confirms the three governing specs are reachable, then reads the repository rather than assuming a stack.
2. Resolves the artifact classes against `spec/project/release-artifact/`: for a Python application that's a Git tag **and** a container image tag — read from the taxonomy, never re-derived.
3. Proposes the stage set mapped onto `continuous-integration` §A, and names the one stage it omits with a reason (no separate package step beyond the image build).
4. Asks the operator which stages are required versus advisory before proposing the split, instead of deciding alone.
5. Produces the artifact-to-securing-stage matrix per `continuous-delivery` §D, with a guarantee per class:

   | Artifact class | Securing stage | Guarantee |
   |---|---|---|
   | Git tag | release dispatch | built-from-source, policy-cleared |
   | Container image | image build and publish | built-from-source, integrity, provenance |

6. Names the handover boundary: the image reference the deployment side consumes. Stops there rather than proposing cluster changes.
7. Flags that lint/type-check/test must be invoked through the existing Taskfile targets, per the parity rule, rather than inlined.
8. Writes nothing; ends by asking whether to proceed to `scaffold`.

## What would be wrong

- Emitting workflow YAML in this operation. `design` proposes; `scaffold` writes.
- Re-listing the artifact taxonomy instead of reading `release-artifact`.
- Proposing a cluster rollout step — that's past the handover boundary.
- Picking required-versus-advisory without asking.

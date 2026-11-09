#!/usr/bin/env bash
# Serial merge train per spec/project/pull-request-workflow/ §"Serial pull-request flow".
#
# Usage: merge-train.sh <pr> [<pr> ...]
#   Run from the repository's working copy. The PRs are the slot holders in train order:
#   open dependency-bot PRs first, then the run's own head PR. Pass only PRs the run's
#   standing authorisation covers; a PR that is not a verified dependency-bot PR is
#   treated as the run's own.
#
# Emits one line per event on stdout. Exit codes:
#   0  every PR in the queue merged ("train done")
#   1  train stopped: a failed required check, a merge conflict (DIRTY), or a PR closed unmerged
#   2  usage or environment error
#   3  wait cap reached with the head still open (pending, not handled)
#
# Environment (all optional):
#   TRAIN_POLL_SECONDS    poll interval, default 60
#   TRAIN_MAX_MINUTES     wait cap per head PR, default 120
#   TRAIN_BOT_LOGINS      space-separated dependency-bot author logins,
#                         default "app/renovate renovate[bot] renovate"
#   TRAIN_BOT_PREFIX      dependency-bot branch prefix, default "renovate/"
#   TRAIN_CANCEL_BOT      1 (default) cancels runs on dependency-bot branches while a head runs
set -uo pipefail

[ $# -ge 1 ] || { echo "usage: merge-train.sh <pr> [<pr> ...]" >&2; exit 2; }
command -v gh >/dev/null && command -v jq >/dev/null || { echo "gh and jq are required" >&2; exit 2; }
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "run from the repository's working copy" >&2; exit 2; }

poll=${TRAIN_POLL_SECONDS:-60}
max_minutes=${TRAIN_MAX_MINUTES:-120}
bot_logins=" ${TRAIN_BOT_LOGINS:-app/renovate renovate[bot] renovate} "
bot_prefix=${TRAIN_BOT_PREFIX:-renovate/}
cancel_bot=${TRAIN_CANCEL_BOT:-1}
tmpdir=$(mktemp -d) && [ -d "$tmpdir" ] || exit 2
# ${tmpdir:?} aborts the removal instead of running it on an empty path.
trap 'rm -rf -- "${tmpdir:?}"' EXIT

queue=("$@")
declare -A branch isbot ticked lastms

for p in "${queue[@]}"; do
  meta=$(gh pr view "$p" --json headRefName,author,isCrossRepository,baseRefName 2>/dev/null) \
    || { echo "cannot read #$p" >&2; exit 2; }
  [ "$(jq -r .baseRefName <<<"$meta")" = develop ] || { echo "#$p does not target develop" >&2; exit 2; }
  branch[$p]=$(jq -r .headRefName <<<"$meta")
  login=$(jq -r .author.login <<<"$meta")
  # A dependency-bot PR is identified by its author AND a same-repository head branch;
  # a branch name alone (a fork can name a branch renovate/x) never qualifies.
  # A cross-repository PR is neither a verified bot PR nor one of the run's own: refuse it.
  [ "$(jq -r .isCrossRepository <<<"$meta")" = false ] || { echo "#$p is a cross-repository PR; not a train member" >&2; exit 2; }
  if [[ "$bot_logins" == *" $login "* ]]; then isbot[$p]=1; else isbot[$p]=0; fi
done

# Cancel queued and in-progress pull_request runs of waiting train branches and of
# dependency-bot branches. Guards (spec §"Serial pull-request flow", runner-sweep reference):
# only pull_request / pull_request_target events, never develop/main, never the head's
# own branch, never a delivery workflow (path contains release, publish, deploy, or cd-).
cancel_waiting() {
  local head_branch=$1 others=$2 s
  for s in queued in_progress waiting pending; do
    gh api "repos/{owner}/{repo}/actions/runs?status=$s&per_page=100" \
      --jq '.workflow_runs[]
            | select(.event == "pull_request" or .event == "pull_request_target")
            | [.id, .head_branch, .path] | @tsv' 2>/dev/null
  done | while IFS=$'\t' read -r id br path; do
    [ -n "$id" ] || continue
    case "$br" in develop|main|"$head_branch") continue ;; esac
    case "$path" in *release*|*publish*|*deploy*|*cd-*) continue ;; esac
    if grep -qxF -- "$br" <<<"$others" || { [ "$cancel_bot" = 1 ] && [[ "$br" == "$bot_prefix"* ]]; }; then
      gh run cancel "$id" >/dev/null 2>&1 && echo "cancelled run $id ($br)"
    fi
  done
}

for head in "${queue[@]}"; do
  echo "train: head is #$head (${branch[$head]})$([ "${isbot[$head]}" = 1 ] && echo ' [dependency bot]')"
  deadline=$(( $(date +%s) + max_minutes * 60 ))
  while true; do
    if [ "$(date +%s)" -ge "$deadline" ]; then
      echo "#$head PENDING after ${max_minutes}m - wait cap reached"; exit 3
    fi
    j=$(gh pr view "$head" --json state,mergeStateStatus,mergeCommit,headRefOid 2>/dev/null) \
      || { sleep "$poll"; continue; }
    st=$(jq -r .state <<<"$j"); ms=$(jq -r .mergeStateStatus <<<"$j")
    if [ "$ms" != "${lastms[$head]:-}" ]; then echo "#$head state $ms"; lastms[$head]=$ms; fi

    if [ "$st" = MERGED ]; then echo "#$head MERGED $(jq -r '.mergeCommit.oid // ""' <<<"$j" | cut -c1-9)"; break; fi
    if [ "$st" = CLOSED ]; then echo "#$head CLOSED without merge - train stops"; exit 1; fi
    if [ "$ms" = DIRTY ]; then echo "#$head DIRTY (merge conflict with develop) - train stops"; exit 1; fi

    if [ "$ms" = CLEAN ] && [ "${isbot[$head]}" = 1 ]; then
      # Portfolio decision: dependency-bot PRs merge on all-green required checks. Squash only, never --admin.
      gh pr merge "$head" --squash >/dev/null 2>&1 && echo "#$head clean -> squash merge requested"
      sleep "$poll"; continue
    fi

    if [ "$ms" = BEHIND ]; then
      if [ "${isbot[$head]}" = 1 ]; then
        # Never update-branch a bot branch (the bot stops maintaining it); tick its rebase checkbox once per head.
        hsha=$(jq -r .headRefOid <<<"$j")
        if [ "${ticked[$head]:-}" != "$hsha" ]; then
          body=$(gh api "repos/{owner}/{repo}/pulls/$head" --jq .body 2>/dev/null)
          if grep -qF -- '- [ ] <!-- rebase-check -->' <<<"$body"; then
            printf '%s' "$body" | sed 's/- \[ \] <!-- rebase-check -->/- [x] <!-- rebase-check -->/' >"$tmpdir/body-$head.md"
            gh api -X PATCH "repos/{owner}/{repo}/pulls/$head" -F body=@"$tmpdir/body-$head.md" >/dev/null 2>&1 \
              && echo "#$head behind -> bot rebase requested"
          fi
          ticked[$head]=$hsha
        fi
      else
        # Own branch: the platform's rebase update (rebase is the spec-mandated sync method).
        gh pr update-branch "$head" --rebase >/dev/null 2>&1 && echo "#$head behind -> branch rebased onto develop"
      fi
      sleep "$poll"; continue
    fi

    # A cancelled run (bucket "cancel") is not a failure: only a failed required check stops the train.
    fails=$(gh pr checks "$head" --required --json name,bucket \
              --jq '.[] | select(.bucket == "fail") | .name' 2>/dev/null | paste -sd, -)
    if [ -n "$fails" ]; then echo "#$head FAIL $fails - train stops"; exit 1; fi

    others=$(for p in "${queue[@]}"; do [ "$p" != "$head" ] && echo "${branch[$p]}"; done)
    cancel_waiting "${branch[$head]}" "$others"
    sleep "$poll"
  done
  queue=("${queue[@]:1}")
done
echo "train done"

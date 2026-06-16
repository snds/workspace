---
name: github-guardrails
description: >
  Interactive guardrails for GitHub operations — designed for someone new to
  Git and GitHub who doesn't want to accidentally break things for their team.
  Covers the how, when, and why of every common operation (branching, committing,
  pushing, opening PRs, requesting review, merging, tagging releases). Provides
  named, dismissable interrupt checkpoints that pause before risky actions and
  explain what could go wrong. Interrupts can be individually dismissed once
  learned and bulk-reset on demand. Use this skill whenever the user is about
  to perform any Git or GitHub action, or asks how GitHub works. Load alongside
  `centric-ui-workflow` (which has the team-specific rules) — this skill
  provides the educational safety layer underneath those rules.
aliases: [github-guardrails]
spec_version: "2.0"
tier: cross-cutting
domain: engineering
---

# GitHub Guardrails

Safety layer for GitHub operations. Designed for someone who is new to Git
and GitHub and wants to contribute confidently without accidentally breaking
things for the team.

`centric-ui-workflow` has the *what* — the specific rules for this project.
This skill has the *why* — plain-language explanations of what each rule
prevents, plus interactive checkpoints that interrupt before risky actions.

---

## How This Skill Works

### Interrupts

Before certain actions, this skill inserts a **checkpoint** — a pause that
explains what you're about to do, what could go wrong, and what to confirm
before proceeding. Each interrupt has an ID (e.g., `GUARD-001`).

```
┌─────────────────────────────────────────────────────────┐
│  GUARD-001 · Branch before you code                     │
│                                                         │
│  You're about to commit changes directly to `main`.     │
│  This is the shared branch — committing here bypasses   │
│  review and risks overwriting teammates' work.          │
│                                                         │
│  → Create a branch first. (See: how to branch)         │
│                                                         │
│  [Got it, continue]   [Show me how]   [Dismiss forever] │
└─────────────────────────────────────────────────────────┘
```

### Dismissing an interrupt

When you've seen an interrupt and understand it, say:
> **"dismiss GUARD-001"** or **"got it, dismiss this"**

Claude will record the dismissal. The interrupt won't appear again.

### Resetting all interrupts

If you want all guardrails back (useful after onboarding someone else, or if
you want a refresher), say:
> **"reset github guardrails"**

Claude will delete the dismissed state and all interrupts become active again.

### State file

Dismissed state is stored at:
```
~/.claude/projects/-Users-sean-sands-projects-cpes-software/memory/github-guardrails.json
```

Format: `{ "dismissed": ["GUARD-001", "GUARD-004"], "last_reset": "2026-04-15" }`

Claude reads this file at the start of every guarded operation. If the file
doesn't exist, all interrupts are active.

---

## GitHub Mental Model (start here)

Understanding three concepts makes everything else click:

### 1. The repository is shared

When you push code, it goes to a server that your whole team can see and
pull from. There is no "undo" for a push the way there is for a local file
edit — once it's there, others may already have it. That's why the rules
around what and when to push matter.

### 2. `main` is the source of truth

`main` is the branch that represents "what's actually working and deployed."
Think of it as the published version. You never work directly on `main` —
you make a copy (a branch), do your work there, and then merge it back after
review. This means if your work breaks something, it's isolated and easy to
revert without touching what everyone else is doing.

### 3. Pull requests are the gate

A pull request (PR) is a formal "I'd like to merge my branch into `main`"
request. It's where teammates review your changes, catch bugs, and ensure the
work fits the codebase. The PR exists so that no single person can accidentally
ship something broken without another set of eyes.

---

## Guardrail Interrupts

### GUARD-001 · Branch before you code

**Triggers when:** You're about to commit or push while on the `main` branch.

**Why this matters:**
`main` is the shared baseline — it's what gets deployed. If you commit
directly to `main`, you skip review entirely. If something breaks, it breaks
for everyone immediately. There's also no clean way to revert just your
changes if they're mixed with others.

**Before proceeding:**
Create a branch first. Use the naming format from `centric-ui-workflow`:
```
feat/my-feature-name
fix/the-thing-i-am-fixing
```

How to create and switch to a branch:
```bash
git checkout -b feat/my-feature-name
```

This creates the branch and puts you on it. Now all your commits stay there
until you explicitly open a PR to merge them back.

**Safe to dismiss when:** You understand that `main` is off-limits for direct commits.

---

### GUARD-002 · Quality gate before requesting review

**Triggers when:** You're about to mark a PR as ready for review or add reviewers.

**Why this matters:**
Your teammates' review time is valuable. If you submit code that fails linting,
type checks, or tests, the first reviewer comment will just be "please fix the
automated issues" — which means another round-trip before they can even look
at the actual logic. The quality gate catches these things in seconds.

**Before proceeding:**
Run this from `centric-ui/`:
```bash
npm run check:quality && npm run test
```

Both must pass with zero errors. If either fails, fix the issues before
requesting review.

**Safe to dismiss when:** You've internalized "run the gate first" as a reflex.

---

### GUARD-003 · Scope check before opening a PR

**Triggers when:** A branch touches files across more than two unrelated feature
folders, or a diff is over ~400 lines without a clear single purpose.

**Why this matters:**
Large, mixed-scope PRs are painful to review. Reviewers can't tell what the
"one thing" is that changed. If the PR gets reverted (because something
breaks), you lose unrelated good work along with the bad. And merge conflicts
multiply when branches live a long time.

**Before proceeding:**
Ask yourself: "If I had to describe this PR in one sentence, can I?" If not,
consider splitting it. A PR that does one thing — even if it's a big thing —
is always easier to review than one that does several small things.

It's fine to have a large diff if it's all part of one coherent change.
The question is *coherence*, not size.

**Safe to dismiss when:** You're comfortable evaluating PR scope before opening.

---

### GUARD-004 · Force push warning

**Triggers when:** Any `git push --force` or `git push -f` command is about
to run.

**Why this matters:**
Force push rewrites the history on the remote branch. If a teammate has
already pulled your branch (e.g., to review locally), their copy of the
branch now has commits that no longer exist on the server. Their next pull
will fail and they'll have to manually recover. In the worst case, commits
get permanently lost.

**Before proceeding:**
Ask: why do I feel like I need to force push?

- *"I need to fix my last commit"* → Use `git commit --amend` locally,
  but only if the branch hasn't been pulled by anyone else yet.
- *"I rebased onto main"* → Force push is acceptable here, but give
  teammates a heads-up first (e.g., in Slack/chat): "heads up, force
  pushing `feat/my-branch` after rebase."
- *"Something seems broken"* → Stop and ask for help before force pushing.

**Safe to dismiss when:** You understand the specific situations where force
push is acceptable and have communicated with the team about it.

---

### GUARD-005 · Author merges — not the approver

**Triggers when:** A PR was opened by someone else and you're about to click
Merge, or you've just approved a PR and you're about to merge it yourself.

**Why this matters:**
The author of a PR is the one who knows exactly what they tested, what
edge cases they thought about, and whether they're comfortable with the
current state of the branch. Merging someone else's PR takes that decision
away from them. They may have planned one more commit, or be waiting for
something before they're ready to ship.

Per the team convention: **after approving, leave merging to the author**.

**Before proceeding:**
If you're the author: merge when you're ready.
If you're a reviewer: leave a comment or message the author that you've
approved — don't hit Merge for them.

**Safe to dismiss when:** You've internalized "approve ≠ merge."

---

### GUARD-006 · Re-request review after late commits

**Triggers when:** You push new commits to a branch that already has at
least one approval on its PR.

**Why this matters:**
When a reviewer clicks Approve, they're approving the exact snapshot they
read. New commits after that approval mean they haven't seen part of what
will be merged. If those new commits introduce a bug, no one reviewed it.

**Before proceeding:**
After pushing, go to the PR and click **"Re-request review"** next to the
reviewer's name. This marks their previous approval as stale and notifies
them to take another look.

If the new commits are trivial (e.g., a typo fix in a comment), you can
leave a comment saying "minor fix: [what changed]" and let the reviewer
decide if they need to re-review — but don't assume.

**Safe to dismiss when:** Re-requesting review after late commits is automatic for you.

---

### GUARD-007 · Never commit secrets or credentials

**Triggers when:** A staged or about-to-be-committed file matches patterns
like `.env`, `*.key`, `*secret*`, `*credential*`, `*token*`, `*password*`,
or contains strings that look like API keys (long alphanumeric tokens).

**Why this matters:**
This is the most severe risk in this list. Once a secret is committed and
pushed, it is in the git history **permanently** — even if you delete the
file in the next commit, the secret is still visible in the history. Anyone
with access to the repo can find it. The only safe recovery is to immediately
rotate (invalidate and replace) the exposed credential.

**Before proceeding:**
- Never commit `.env` files. They should be in `.gitignore`.
- Use GitHub Actions Variables/Secrets for anything needed in CI.
- If you've already committed a secret by accident: **stop and ask for help**
  before pushing. A local commit can be undone cleanly; a pushed commit
  requires history rewriting and credential rotation.

**Safe to dismiss when:** You have a firm mental reflex to check what you're
staging before every commit.

---

### GUARD-008 · Release tag format

**Triggers when:** You're about to create a `git tag`.

**Why this matters:**
The CI/CD pipeline watches for tags in the exact format `X.Y.Z` (e.g.,
`1.4.2`). Other formats either do nothing or cause unexpected behavior:

| Tag format | What happens |
|------------|-------------|
| `1.4.2` | ✅ Triggers deploy to `ghcr.io/cpes-software/centric-ui` |
| `v1.4.2` | ❌ Not matched — no deploy |
| `1.4.2rc1` | ❌ Explicitly excluded — no deploy (intentional) |
| `latest` | ❌ Not matched — no deploy |

**Before proceeding:**
Confirm the version number with the team before tagging. Semver format:
`MAJOR.MINOR.PATCH` — no `v` prefix, no suffix.

```bash
git tag 1.4.2
git push origin 1.4.2
```

**Safe to dismiss when:** You've successfully run a release and understand the tag format.

---

### GUARD-009 · Open a draft PR early

**Triggers when:** A branch has been active for more than a day with commits
but no corresponding PR exists.

**Why this matters:**
An open draft PR — even on day one — does several things:
- Signals to teammates that this work is in progress (avoids accidental
  duplicate effort)
- Kicks off CI checks on each push (catches integration issues early)
- Makes rebasing easier before the diff grows large

A draft PR isn't asking for review. It's just saying "I'm working on this."

**Before proceeding:**
On GitHub, click "New pull request" → then select "Create draft pull request"
(the dropdown arrow next to the green button). You can convert it to ready
when you are.

**Safe to dismiss when:** Opening draft PRs early is your default habit.

---

### GUARD-010 · Delete the branch after merging

**Triggers when:** A PR has just been merged and the source branch hasn't
been deleted.

**Why this matters:**
After a PR merges into `main`, the branch's work is preserved in `main`
forever. The branch itself becomes a stale pointer. Over time, dozens of
stale branches accumulate and make navigation confusing. GitHub shows a
"Delete branch" button immediately after merge — it's safe and reversible
(GitHub keeps a "restore branch" option for 90 days).

**Before proceeding:**
Click "Delete branch" on the merged PR page. Then on your local machine:
```bash
git checkout main
git pull
git branch -d feat/my-feature-name   # lowercase -d = safe delete
```

`-d` (lowercase) only deletes if the branch is fully merged. It will refuse
if you haven't merged yet, protecting you from accidental deletion.

**Safe to dismiss when:** Deleting branches after merge is automatic for you.

---

## Operation Reference

A quick lookup table for common operations.

### Starting new work

```bash
# 1. Always start from an up-to-date main
git checkout main
git pull

# 2. Create your branch
git checkout -b feat/my-feature-name

# 3. Verify you're on the right branch
git branch   # asterisk (*) shows current branch
```

### Saving and sharing work

```bash
# Stage specific files (preferred over "git add .")
git add app/features/myFeature/MyComponent.tsx

# Check what you're about to commit
git status
git diff --staged

# Commit with the required format: type(scope): summary
git commit -m "feat(views): add filter panel to table widget"

# Push to the remote for the first time
git push -u origin feat/my-feature-name

# Push subsequent commits
git push
```

### Keeping your branch current with main

Do this regularly — the longer you wait, the harder merges become.

```bash
git checkout main
git pull
git checkout feat/my-feature-name
git merge main          # brings main's changes into your branch
```

Or with rebase (cleaner history, but requires more care):
```bash
git rebase main         # replays your commits on top of latest main
```

If there are conflicts, Git will pause and show you the files to resolve.
Open each file, find the `<<<<<<` / `======` / `>>>>>>` markers, and edit
to the correct state. Then:
```bash
git add <resolved-file>
git rebase --continue   # or: git merge --continue
```

### Opening and managing a PR

1. Push your branch: `git push -u origin feat/my-feature-name`
2. GitHub will print a link — click it, or go to the repo → "Pull requests" → "New pull request"
3. Write a description: what you changed, why, and how to verify it works
4. Open as **Draft** first; convert to ready when `npm run check:quality && npm run test` pass
5. Add reviewers under "Reviewers" on the right sidebar
6. After approval: you (the author) click Merge

### Emergency: something went wrong

**"I committed to main by accident"**
```bash
# Undo the last commit, keep your changes staged
git reset --soft HEAD~1
# Now create a branch and re-commit there
git checkout -b fix/what-i-was-doing
git commit -m "fix(scope): what I was fixing"
```
Only works if you haven't pushed yet. If you've pushed: ask for help.

**"I pushed something I shouldn't have"**
Do not try to rewrite history. Alert the team immediately — in chat/Slack —
so they know what's in `main`. For secrets specifically, rotate the credential
first, then handle the git cleanup with the team.

**"My branch has merge conflicts"**
Don't panic. Conflicts are normal and always resolvable:
```bash
git checkout main && git pull
git checkout feat/my-feature-name
git merge main
# Resolve conflict markers in the flagged files
git add <resolved-files>
git commit
```

---

## Safe vs. Risky — At a Glance

| Operation | Safety level | Notes |
|-----------|-------------|-------|
| `git status` | ✅ Safe | Read-only, shows current state |
| `git log` | ✅ Safe | Read-only, shows history |
| `git diff` | ✅ Safe | Read-only, shows changes |
| `git checkout <branch>` | ✅ Safe | Switches branches |
| `git checkout -b <branch>` | ✅ Safe | Creates new branch |
| `git add <file>` | ✅ Safe | Stages file for commit |
| `git commit` | ✅ Safe | Local only until pushed |
| `git push` (first time) | ⚠️ Team-visible | Creates branch on remote |
| `git push` (subsequent) | ⚠️ Team-visible | Updates remote branch |
| `git merge main` (into feature branch) | ⚠️ Careful | Can create conflicts |
| `git pull` | ⚠️ Careful | Can create conflicts |
| `git push --force` | 🔴 Dangerous | Rewrites remote history |
| `git reset --hard` | 🔴 Dangerous | Destroys uncommitted changes |
| `git commit` on `main` | 🔴 Dangerous | Bypasses review |
| Committing `.env` or secrets | 🔴 Dangerous | Permanent exposure risk |
| Creating a release tag | 🔴 Irreversible | Triggers a production deploy |

---

## Interrupt State Management

### Check dismissed state
Claude reads the state file before each guarded operation.
File: `~/.claude/projects/-Users-sean-sands-projects-cpes-software/memory/github-guardrails.json`

### Dismiss an interrupt
Say: `"dismiss GUARD-003"` or `"got it, I understand this one"`
Claude updates the JSON file: adds the ID to the `dismissed` array.

### Reset all interrupts
Say: `"reset github guardrails"` or `"show me all guardrails again"`
Claude sets `dismissed: []` in the JSON file (or deletes it).

### Override for the current action only (without dismissing)
Say: `"proceed anyway"` or `"skip this time"`
Claude continues without recording a dismissal — the interrupt will appear again next time.

### Manual reset (if Claude is unavailable)
Delete or clear the file:
```bash
echo '{"dismissed":[],"last_reset":"'"$(date +%Y-%m-%d)"'"}' \
  > ~/.claude/projects/-Users-sean-sands-projects-cpes-software/memory/github-guardrails.json
```

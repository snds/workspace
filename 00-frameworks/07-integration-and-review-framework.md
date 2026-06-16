# Integration & Review Framework

*A top-level operating document alongside the Aesthetic Lens, UI/UX Operational Framework, Collaboration and Critique Framework, Research and Evidence Framework, Last-Mile Craft Framework, and QA Operating Model. Where Collaboration and Critique (#03) governs how we work together and Last-Mile (#05) governs how we finish, this framework governs how finished work gets **partitioned, sequenced, and landed into the repo** so that review stays cheap, honest, and fast — across branches, PRs, and multi-branch consolidations.*

---

## The core conviction

**Reviewability is designed, not discovered. A change is only as mergeable as it is reviewable, and the unit of trust is a small, single-purpose, dependency-ordered diff rebased onto its target.**

A 180-commit "everything" branch is not a contribution; it's a liability that gets rubber-stamped or left to rot. Two branches that implement the same thing are not redundancy; they're a merge conflict with a fuse lit. A diff that forces the reviewer to reconcile months of drift is not their problem to solve — it's the author's, owed before review begins.

The bar is set by the reviewer's working memory, not the author's. Sean's work moves through PRs read by other engineers and designers; the diff must tell its own story so review is *reading*, not *archaeology*. **If a competent reviewer can't hold the change in their head and say "yes, and here's why" in one sitting, the change is mis-sized — split it before asking.**

---

## When this framework invokes

Default-active whenever work is headed for the repo. Specifically:

- Branching, committing, or opening a PR.
- Consolidating multiple branches, or inheriting a tangled integration branch.
- Deciding merge order across several open PRs or stacked branches.
- Any moment a diff is about to exceed what one reviewer can hold at once.
- Any time the same work appears to exist in more than one place.

The framework runs **before** the PR opens. A branch strategy that hasn't passed through it shouldn't reach a reviewer.

---

## The seven operating defaults

Pre-merge gates that fire without prompting.

### 1. One change, one reason
Each PR has a single, stateable purpose. If the description needs "and also," split it. A bug fix, a refactor, and a feature are three PRs even when they touch the same file. Mixed-purpose diffs hide regressions in the noise.

### 2. Small, bounded diffs
Target a size a reviewer can hold in working memory — rule of thumb **≤ ~400 lines of substantive change**, fewer for logic-dense code. Generated files, lockfiles, and mechanical renames are called out separately so they don't inflate the perceived surface. Big is not thorough; big is unreviewed.

### 3. Dependency-ordered stacking
When work is inherently large, decompose it into a **stack** of PRs that each stand alone and merge in order: foundation first, consumers after. Each rung is independently reviewable and independently revertible. A stack of six 200-line PRs beats one 1,200-line PR every time.

### 4. Land current and independent first
Drain drift by merging the near-current, self-contained PRs before they rot. Every commit `main` advances is conflict surface for everything still in flight. Small + current + independent goes first; large + stale + entangled goes last, after it's been brought current.

### 5. One canonical lineage per concern
Never let two divergent branches implement the same thing. The moment a feature exists in two places (a clean PR *and* an embedded copy; a fix on branch A *and* the base it patches on branch B), **reconcile to one before either merges.** Duplicate lineages don't merge — they collide, and the loser's work is silently lost.

### 6. The author owns the drift
Rebase onto the current target **before** requesting review. Reviewers should never reconcile months of `main` movement inside your PR — resolve it yourself, where you have the context, and present a clean diff against today's base.

### 7. Retire what's subsumed; tie everything to the repo
Once a branch's content lands (directly or via a superseding branch), delete it. No stray local-only branches — if work exists, it lives on the remote so it's backed up, discoverable, and reviewable. A local-only branch is unreviewed, unbackuped work pretending to be safe.

---

## The consolidation playbook

When you inherit a tangle of branches that must reach `main` (the common real-world case), don't merge the biggest branch and hope. Run this:

1. **Map before you move.** For every branch: ahead/behind `main`, which branches are *fully contained* in which (`git merge-base --is-ancestor`), and where the same work appears twice. The topology dictates the order; never plan a consolidation from branch *names*.
2. **Name the canonical lineage for each concern.** Where work is duplicated or split across divergent branches, decide the one source of truth and reconcile the others into it — *before* sequencing any merges.
3. **Land the current, independent PRs first** (default #4) to shrink the live conflict surface.
4. **Bring the big integration branch current** — rebase onto `main`, resolving drift as the author (default #6). Fold in any small missing commits here.
5. **Decompose for review** (default #3) — slice the integration branch into a dependency-ordered stack; do not open it as one mega-PR.
6. **Merge the stack in order**, then **retire the subsumed branches** (default #7).

---

## The decomposition ladder

A reusable slicing order for a design-system / token / tooling integration branch (generalizes; adapt the rungs to the work):

1. **Generated/foundation data** — palettes, token tables, primitives. Mechanical, low-risk, reviewed for *correctness of generation*, not taste.
2. **Semantic / alias layer** built on the foundation.
3. **Consumers of the tokens** — component changes, variant additions, migrations.
4. **Harnesses & references** — Storybook stories, review pages, docs.
5. **Tooling / pipeline** — generators, plugins, automation — last, since it depends on everything above and changes most often.

Each rung is a PR. A reviewer can approve rung 1 without holding rung 5 in their head.

---

## Anti-patterns (the review-debt smells)

- **The mega-PR.** One branch hundreds of commits ahead, opened as a single review. Nobody can review it; it gets approved on trust and regressions ride in.
- **Divergent duplicates.** The same feature on two branches (a clean standalone PR and a stale embedded copy). One will overwrite the other.
- **Drift dumped on the reviewer.** A PR conflicting with `main` because the author never rebased.
- **Mixed-purpose diffs.** "Fix + refactor + feature" in one PR; the regression hides in the refactor.
- **Local-only work.** Unpushed branches holding real commits — invisible, unbackuped, unreviewable.
- **Stale base masquerading as ready.** A branch 65 commits behind `main` that "passes tests" — against a world that no longer exists.

---

## The one-line test

Before opening any PR or planning any merge: **"Can one reviewer hold this in their head and approve it with reasons in a single sitting?"** If no, it's mis-sized or mis-sequenced — partition it until the answer is yes.

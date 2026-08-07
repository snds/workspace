# Init — project render contracts

Create the three contract files every other command reads. Do not invent a parallel format.

## When

- First realtime-photoreal session on a project
- Forced setup: any command finds `RENDER.md` / `BUDGET.md` / `NORTHSTAR.md` missing
- Refresh requested after a major look or performance pivot

## Steps

1. **Locate existing contracts.** Search project root, `docs/`, `.agents/context/` (case-insensitive). Note what exists.
2. **Decision tree**
   - **None exist** → write all three from templates (steps 3–5).
   - **Some exist** → fill only the gaps; never silently overwrite. Confirm before refreshing a filled file.
   - **All exist and look current** → report paths; recommend `shape` or the user's original command. Stop.
3. **Write `RENDER.md`** from [`../templates/RENDER.md`](../templates/RENDER.md). Fill what the repo already proves (engine, platforms, known poses). Leave fidelity contract and technique ladder as interview prompts if unknown.
4. **Write `BUDGET.md`** from [`../templates/BUDGET.md`](../templates/BUDGET.md). Set FPS floor = 60, uncapped default, real ~14–15 ms GPU budget at 60 Hz unless native/other engine says otherwise. Stub pass rows; do not invent measured ms.
5. **Write `NORTHSTAR.md`** from [`../templates/NORTHSTAR.md`](../templates/NORTHSTAR.md). If the user already named film/game refs in chat or docs, seed the tables. Otherwise leave rows empty and flag `shape` as mandatory next.
6. **Point next action.** After init, the default is `shape` (lock contract + northstar + poses/paths). If init blocked another command, resume that command after shape when the brief was incomplete.

## Interview (only what you cannot infer)

Ask 2–3 per round, then stop:

- Fidelity bar: Literal vs Spirit vs Intent? Named movie / game refs?
- Hardest visual claim (atmosphere, scale traversal, materials, night side…)?
- Weakest GPU / target refresh?

## Done when

- All three files exist on disk with project name + engine filled
- Absolute bans section present (framework defaults + any project adds)
- User knows the path to each file and the next command

## Do not

- Skip `NORTHSTAR.md` because "we'll pick refs later"
- Put measured frame times into `BUDGET.md` without a harness run
- Call the look "photoreal" in `RENDER.md` without a contract type checked

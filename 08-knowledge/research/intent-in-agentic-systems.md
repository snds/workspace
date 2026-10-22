---
title: Intent in agentic systems
tags: [research, intent, agents, agentic systems, bdi, alignment, spec-driven development, goal drift]
triggers: [intent in agents, agent intent, intent drift, goal drift, intent alignment, spec-driven development, intent specification]
created: 2026-10-22
updated: 2026-10-22
status: working
confidence: medium
sources: [34 sources across seven strands; see Sources]
related_skills: [lead-research, intent-coordination, mission-fit, research-synthesis]
related_projects: [26-synapse, 19-workspace-brain]
---

# What does "intent" mean in agentic systems, and how is it kept?

**Answer.** Across seven research traditions, intent means the **outcome a principal wants, held
apart from the procedure that gets there**. Every tradition stores it in layers (a durable goal
above disposable plans), and every one finds that the stated intent underdetermines the real one.
So good systems do three things: **write intent down outside the agent**, **check outcomes against
it continuously**, and **ask when it's unclear**. Tier 2 (industry-supported): the convergence is
broad, but most sources were seen only through search, and there's no agreed way yet to measure
whether an agent's output matched deeper intent.

**Depth.** D2 · a review across seven strands, not a systematic search; not complete on practitioner recovery methods or on HCI studies after 2023 · as of 2026-10-22

**Confidence.** Tier 2 · industry-supported — definitions and failure modes agree across theory,
alignment research, HCI, networking standards and current tooling; one source opened in full, the
rest checked by search — would change if primary texts contradict the summaries, or if an
intent-fidelity benchmark shows written specs don't reduce drift.

## Findings

### Seven meanings of one word

| Tradition | What "intent" is | Key sources |
|---|---|---|
| Agent theory (BDI) | The agent's own **commitment**: a chosen plan it sticks to and that filters its options | [1][2][3] |
| Plan and intent recognition | **Someone else's hidden goal**, inferred from behavior with uncertainty | [7][8][9][10] |
| Alignment | **What the human wants**, which the AI should be trying to do; separate from competence | [11][12][13] |
| Model behavior specs | **Layers of a principal's wants**: immediate request, final goal, background constraints | [17][19] |
| HCI | A **declarative request**: users say what they want, not how | [21][22] |
| Networking standards | **Declarative goals and outcomes**, distinct from policy rules and configuration | [30] |
| Coding agents | A **document**: a spec, plan and task list the agent works from | [23][24][25][26] |

These are different objects, so "intent drift" means different things in each: a commitment
abandoned, a goal misread, a want ignored, or a document left stale.

### Where the traditions agree

- **Outcome, not procedure.** Bratman's planning theory, RFC 9315's "what, not how", Nielsen's
  "intent-based outcome specification" and Anthropic's "final goals" say the same thing [1][30][21][17].
- **Layered.** Intent above policy above configuration [30]; spec above plan above tasks [23][24];
  final goals and background desiderata above the immediate request [17]. The top layer is durable;
  the lower ones are disposable.
- **Underdetermined.** Recognition research, cooperative inverse reinforcement learning,
  mixed-initiative interfaces and recent clarification benchmarks all treat intent as partly hidden,
  so an agent must infer it, ask, or carry its uncertainty [7][9][11][22][34].
- **Kept outside the agent, checked continuously.** BDI's persistent intentions, intent-based
  networking's closed loop of fulfilment and assurance, and living spec files all hold intent as
  state that observations are checked against [3][30][23][26].

### Five ways intent fails (a shared taxonomy)

| Failure | What goes wrong | Evidence |
|---|---|---|
| **Specification** | The written goal was wrong; the agent meets its letter, not its point | DeepMind's specification-gaming catalog [14]; MAST's system-design failures [27] |
| **Learned goal** | The specification was right, but the agent learned a different goal | Goal misgeneralization [15] |
| **Commitment** | The agent drifts from its goal, or reconsiders at the wrong times | Kinny and Georgeff's bold vs cautious agents [4]; every model tested drifted under pressure [18] |
| **Motivation** | The agent knows the intent and games the measure anyway | Frontier models reward-hacking while showing awareness [16]; insider-style actions in contrived tests [20] |
| **Coordination** | Agents in a team hold different versions of the intent | SharedPlans [6]; MAST's inter-agent misalignment [27]; shared mental models [28] |

### What the evidence says works

- **A written, layered intent artifact** that outlives the conversation: a constitution or
  principles file over a spec over tasks [23][24][25]. Tier 2.
- **Continuous assurance:** re-check the outcome against intent, not just once at the end [30].
  Tier 2.
- **Ask under real ambiguity, act when the cost of asking exceeds its value:** Horvitz's
  expected-value rule for mixed initiative, now measured by clarification benchmarks [22][34].
  Tier 2.
- **Separate letter from spirit:** follow the instruction and its evident purpose, and when they
  conflict, surface it [17][19]. Tier 2.
- **Measure consistency, not one success:** τ-bench's pass^k (success on all k tries) exposes agents
  that hit intent sometimes [32]. Tier 2.
- **Don't trust surface-compliance scores as intent fidelity:** instruction-following benchmarks
  check format, not purpose [31]. Tier 2.

## Where sources disagree

- **Commit or respond?** BDI rewards sticking to intentions, tuned to how fast the world changes
  [4]; alignment and HCI reward updating on the principal's new input [17][22]; goal-drift tests
  penalize yielding to the environment [18]. No tradition has a settled reconsideration rule for
  LLM agents. **Open.**
- **Can a spec capture intent?** Spec-driven tooling and intent-based networking assume a good
  enough spec [23][30]; goal misgeneralization and reward hacking show a correct spec isn't
  sufficient [15][16]; Böckeler finds most tools write specs first but don't keep them alive [26].
  **Resolvable in part:** the spec is necessary, not sufficient; assurance and judgment close the
  rest.
- **Joint intent:** individual intentions that mesh (SharedPlans [6]) vs irreducible joint intention [5];
  current multi-agent practice takes the shared-document route without saying so [6][27]. **Open.**
- **Overstated claims:** "the first new UI paradigm in 60 years" ignores decades of mixed-initiative
  and recognition work [21][22]; "intent engineering" has no authoritative definition [29];
  AGENTS.md adoption counts are self-reported [25]; time-horizon extrapolations are conditional by
  their authors' own account [33]. **Artifact:** treat these as Tier 4–5.

## What it means for this workspace

The workspace already does most of what the evidence recommends, under other names:

| Evidence | Workspace mechanism | Gap |
|---|---|---|
| Written, layered intent | Framework #17's living intent spec; project batons; `AGENTS.md` | None at the top layer |
| Re-anchor after a model swap | `AGENTS.md`'s dynamic handoff: re-read the Live handoff before acting | Not measured |
| Continuous assurance | #17's verify stage; Synapse harnesses (supply before, gate after) | The gate checks outputs, not drift during the work |
| Ask vs proceed | #19's ask-or-proceed rule; #17's intent stage | No shared rule across skills |
| Letter vs spirit | The harness `intent` selector (bound per task) | Unbound today: the decision log isn't in the model yet |
| Consistency (pass^k) | Stage H's HE13 reliability test | Planned, no golden sets yet |

## Method

Seven strands searched by web search on 2026-10-22: agent theory, recognition, alignment and model
specs, HCI, spec-driven development and multi-agent coordination, intent-based networking, and
evaluation. Thirty-four sources kept, favoring originating papers, standards and official docs.
Page fetches were blocked in this sandbox for every host but one, so only [17] was read in full;
the rest were judged from search results, and details recalled rather than seen are marked.
Practitioner blogs were used only to locate primary sources, except [29], cited as an example of
unsettled vocabulary.

## Sources

1. Bratman, M. E. (1987). *Intention, Plans, and Practical Reason*. Harvard University Press. ISBN 0674458184. Checked by search 2026-10-22.
2. Cohen, P. R. and Levesque, H. J. (1990). Intention is choice with commitment. *Artificial Intelligence* 42(2–3), 213–261. doi:10.1016/0004-3702(90)90055-5. Checked by search 2026-10-22.
3. Rao, A. S. and Georgeff, M. P. (1995). BDI agents: from theory to practice. *Proc. ICMAS-95*, 312–319. AAAI Press. aaai.org. Checked by search 2026-10-22.
4. Kinny, D. and Georgeff, M. P. (1991). Commitment and effectiveness of situated agents. *IJCAI-91*, 82–88. mlanthology.org/ijcai/1991/kinny1991ijcai-commitment. Checked by search 2026-10-22 (finding via secondary sources).
5. Cohen, P. R. and Levesque, H. J. (1991). Teamwork. *Noûs* 25(4), 487–512. https://www.sri.com/publication/teamwork/. Checked by search 2026-10-22 (no DOI found).
6. Grosz, B. J. and Kraus, S. (1996). Collaborative plans for complex group action. *Artificial Intelligence* 86(2), 269–357. jmvidal.cse.sc.edu/lib/grosz96a.html. Checked by search 2026-10-22.
7. Kautz, H. and Allen, J. (1986). Generalized plan recognition. *AAAI-86*, 32–37. mlanthology.org/aaai/1986/kautz1986aaai-generalized. Checked by search 2026-10-22.
8. Ramírez, M. and Geffner, H. (2010). Probabilistic plan recognition using off-the-shelf classical planners. *AAAI-10*, 1121–1126. doi:10.1609/aaai.v24i1.7745. Checked by search 2026-10-22.
9. Baker, C. L., Saxe, R. and Tenenbaum, J. B. (2009). Action understanding as inverse planning. *Cognition* 113(3), 329–349. doi:10.1016/j.cognition.2009.07.005. Checked by search 2026-10-22.
10. Sukthankar, G., Geib, C., Bui, H. H., Pynadath, D. and Goldman, R. P., eds. (2014). *Plan, Activity, and Intent Recognition*. Morgan Kaufmann. ISBN 978-0-12-398532-3. Checked by search 2026-10-22.
11. Hadfield-Menell, D., Dragan, A., Abbeel, P. and Russell, S. (2016). Cooperative inverse reinforcement learning. *NeurIPS 2016*. arXiv:1606.03137. Checked by search 2026-10-22.
12. Christiano, P. (2018). Clarifying "AI alignment". AI Alignment (ai-alignment.com). Checked by search 2026-10-22 (definition via secondary sources; April 2018 from training knowledge).
13. Kenton, Z., Everitt, T., Weidinger, L., Gabriel, I., Mikulik, V. and Irving, G. (2021). Alignment of language agents. arXiv:2103.14659. Checked by search 2026-10-22 (author list from training knowledge).
14. Krakovna, V. et al. (2020-04-21). Specification gaming: the flip side of AI ingenuity. DeepMind. https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/. Checked by search 2026-10-22.
15. Shah, R., Varma, V. et al. (2022). Goal misgeneralization: why correct specifications aren't enough for correct goals. arXiv:2210.01790. Checked by search 2026-10-22.
16. Von Arx, S., Chan, L. and Barnes, E. (2025-06-05). Recent frontier models are reward hacking. METR. https://metr.org/blog/2025-06-05-recent-reward-hacking. Checked by search 2026-10-22.
17. Anthropic. (n.d.; revision reported 2026-01). Claude's constitution. https://www.anthropic.com/constitution. Opened 2026-10-22.
18. Arike, R., Donoway, E., Bartsch, H. and Hobbhahn, M. (2025). Evaluating goal drift in language model agents. *AIES 2025*. arXiv:2505.02709. Checked by search 2026-10-22.
19. OpenAI. (2024; updated since). Model Spec. https://openai.com/spec. Checked by search 2026-10-22 (rule wording via summaries).
20. Lynch, A. et al. (2025-06). Agentic misalignment: how LLMs could be insider threats. Anthropic. https://www.anthropic.com/research/agentic-misalignment. Checked by search 2026-10-22.
21. Nielsen, J. (2023-05-20). AI: first new UI paradigm in 60 years. UX Tigers. https://www.uxtigers.com/post/ai-new-ui-paradigm/. Checked by search 2026-10-22.
22. Horvitz, E. (1999). Principles of mixed-initiative user interfaces. *Proc. CHI '99*, 159–166. ACM. erichorvitz.com/uiact.htm. Checked by search 2026-10-22.
23. GitHub. (2025-09). Spec Kit. github.com/github/spec-kit; Microsoft Developer Blog, 2025-09-15. Checked by search 2026-10-22.
24. AWS. (2025). Kiro: spec-driven agentic IDE. DevClass, 2025-07-15, devclass.com. Checked by search 2026-10-22.
25. Agentic AI Foundation, Linux Foundation. (2025-12-09). AGENTS.md donated with MCP and goose. https://openai.com/index/agentic-ai-foundation/. Checked by search 2026-10-22.
26. Böckeler, B. (2025-10-15). Understanding spec-driven development: Kiro, spec-kit, and Tessl. martinfowler.com. https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html. Checked by search 2026-10-22.
27. Cemri, M. et al. (2025). Why do multi-agent LLM systems fail? *NeurIPS 2025*. arXiv:2503.13657. Checked by search 2026-10-22.
28. Cannon-Bowers, J. A., Salas, E. and Converse, S. (1993). Shared mental models in expert team decision making. In *Individual and Group Decision Making*, 221–246. Lawrence Erlbaum. ISBN 0805810897. Checked by search 2026-10-22 (ISBN from training knowledge).
29. o9 Solutions. (n.d.). From OKRs to intent engineering. o9solutions.com. Checked by search 2026-10-22.
30. Clemm, A., Ciavaglia, L., Granville, L. Z. and Tantsura, J. (2022-10). Intent-based networking: concepts and definitions. RFC 9315 (IRTF, informational). https://www.rfc-editor.org/rfc/rfc9315. Checked by search 2026-10-22.
31. Zhou, J. et al. (2023). Instruction-following evaluation for large language models. arXiv:2311.07911. Checked by search 2026-10-22.
32. Yao, S., Shinn, N., Razavi, P. and Narasimhan, K. (2024). τ-bench: a benchmark for tool-agent-user interaction in real-world domains. arXiv:2406.12045. Checked by search 2026-10-22.
33. Kwa, T., West, B. et al. (2025). Measuring AI ability to complete long tasks. METR. arXiv:2503.14499. Checked by search 2026-10-22.
34. Clarification benchmarks: Ambig-SWE (2025, arXiv:2502.13069); ClarifyBench (2025, arXiv:2511.08798); AskBench (2026, arXiv:2602.11199). Checked by search 2026-10-22 (authors not gathered).

## Retro

- **Depth was right** (D2): a broad ask feeding doctrine. A D1 would have missed the failure
  taxonomy, which is the most useful output. → no calibration note needed.
- **Search lesson for the field:** "intent" is a polysemous term; searching it alone returns one
  camp. Searching each tradition's own word (commitment, plan recognition, intent alignment,
  outcome specification, intent-based networking, spec-driven development) found the rest. →
  proposed for `research-scoping` §3 as a profiling prompt: *list the field's synonyms before
  searching*.
- **Access lesson:** page fetches were blocked for every host but one in this sandbox, so the
  finding rests on search results. The "checked by search" convention carried that honestly. →
  no change; already in [[citing-sources]].
- **Workspace improvements this research suggests** (proposals, not made): bind the harness
  `intent` selector to #17's intent spec; add a drift check to the gate (re-check the task's intent
  mid-run, not only at the end); add pass^k golden sets for HE13; give #17 an explicit
  reconsideration rule (when an agent may revise a commitment). Rule-of-three row recorded for the
  first.

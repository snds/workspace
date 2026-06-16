# Bootstrap Generator

**An AI that interviews you, then builds you your own "second brain" — notes, knowledge, and a personal assistant that actually knows you.**

> ⚠️ **Early days.** This is a real project, but it's just getting started. The design is written down (see [SPEC.md](SPEC.md)), and the building has only just begun. Read this as *"here's the plan and how it will work,"* not *"here's a finished app you can install today."* Where something doesn't exist yet, this README says so plainly.

---

## What this is

A while back, one person (Sean) built himself a personal setup: a single folder that holds all his notes and knowledge, syncs across his computers and phone, and is wired into his AI assistant so that every time he opens it, the assistant already *knows him* — his work, his projects, how he likes to be talked to.

His friends saw it and asked: *"How did you make that? Can I have one?"*

This is the answer, repackaged so a **non-technical person** can use it. You don't build it by hand. Instead, an AI **interviews you** — a friendly conversation about your devices, your job, your skills, your personal life, and your preferences — and then **generates the whole thing for you**, personalized to who you are.

There's no assumption that you write code, know what a "terminal" is, or have ever heard the word "repository." Every techie term in this document is explained in plain language, with a quick "learn more" link if you're curious.

---

## What you'll end up with

One folder on your computer. That single folder does three jobs at once:

1. **It's your notebook (a "vault").** All your notes and knowledge, saved as plain, readable text files you can browse like your own private Wikipedia. You read and edit them in a free app called Obsidian.
2. **It remembers every version (a "git repo").** It quietly keeps a full history of every change and syncs across all your devices — like the version history in Google Docs, but for the whole folder.
3. **It teaches your AI assistant who you are.** It's connected to your AI tools so that, every session, the assistant already knows your work, your projects, and how you like to work — no re-explaining yourself each time.

Same folder. Three superpowers. The rest of this README explains each idea in plain words.

---

## The ideas in plain language

Don't worry about memorizing these. Each one is a single simple idea wearing a technical-sounding name.

### 🧠 A "second brain"
A **second brain** is just your notes, ideas, and knowledge kept in one organized place *outside your head* — so you don't have to remember everything. The folder this tool makes is your second brain.
*Learn more: [Building a Second Brain](https://www.buildingasecondbrain.com/) — the popular name for this idea. (Heads up: that page is also selling a course, so read it for the concept, not as a how-to.)*

### 📓 A "vault"
A **vault** is simply a normal folder of text notes on your computer. The free app **Obsidian** opens that folder and turns it into a friendly, wiki-like reader and editor. Nothing is locked away — the notes are plain text you could open in any app.
*Learn more: [What a vault is (Obsidian Help)](https://obsidian.md/help/vault).*

### 🔗 "Wikilinks"
Inside your notes, typing `[[Note Name]]` makes a clickable link to another note — like building your own personal Wikipedia where everything connects. That's it.
*Learn more: [Internal links (Obsidian Help)](https://obsidian.md/help/links).*

### 🧩 "Skills"
A **skill** is a labeled folder of instructions that your AI opens *only when it's relevant* — like a recipe card it pulls out of a drawer just when it needs that recipe. Because they only load when needed, you can have lots of them ready at no real cost. This tool builds skills tailored to *your* expertise.
*Learn more: [What are skills? (Anthropic Help)](https://support.claude.com/en/articles/12512176-what-are-skills) · the open standard at [agentskills.io](https://agentskills.io).*

### 🏢 "Hubs" and "spokes"
Skills are organized like a company. A **hub** is a broad area — say, "photography." Its **spokes** are the specialists inside it — "lighting," "color grading," "printing." The hub is the department; the spokes are the experts in it. This keeps things tidy and lets the AI reach for exactly the right specialist.

### 🗂️ "Context" (and keeping it private)
**Context** is your personal and work information, saved as plain text files, so the assistant actually knows your situation. It's kept **walled by default**: your work life and personal life are stored separately, and your *personal* context stays **private and on your own computer** — never synced or shared — unless you choose to open it up. (More in [Privacy](#privacy) below.)

### 🕓 "Git" and syncing
**Git** is a tool that tracks every change to your folder and keeps a full history you can rewind through — version history for a whole folder, not just one document. **GitHub** is the matching online service that stores a copy in the cloud so your devices stay in sync. This is the part that lets you start a note on your laptop and pick it up on your phone.
*Learn more: [About GitHub and Git (plain-language)](https://docs.github.com/en/get-started/start-your-journey/about-github-and-git).*

### 🔌 "MCP"
Think of **MCP** as a **USB-C port for AI** — one standard plug that lets your AI assistant connect to your files and to other tools (and to other AI apps like Cursor). Set it up once, and many tools light up.
*Learn more: [What is MCP? (official intro)](https://modelcontextprotocol.io/docs/getting-started/intro).*

### ✍️ "Markdown" and "YAML" (the file formats)
Your notes are written in **Markdown** — plain text with light formatting, like using `*` for a bullet or `#` for a heading. Some settings are stored in **YAML** — a simple, human-readable list of settings, like a labeled shopping list. You rarely need to touch either directly.
*Learn more: [Markdown cheat sheet (CommonMark)](https://commonmark.org/help/) · [What is YAML? (Red Hat)](https://www.redhat.com/en/topics/automation/what-is-yaml).*

---

## What you'll need first

Honest heads-up: **some of this setup is technical today.** That's exactly what this project wants to smooth out over time, but for now you'll touch a few tools that weren't built for beginners. Where there's a gentler, point-and-click option, this README points you to it.

Here's the shopping list:

| You'll need | What it's for | How hard (today) |
|---|---|---|
| **Claude** (the AI) | The assistant that runs your interview and becomes your "brain." | Easy to install; **needs a paid Claude plan** for the file-creating features. |
| **Obsidian** | The free app you read and edit your notes in. | Easy. |
| **Git + GitHub** | Syncs your folder across devices and keeps history. | The most technical part — use **GitHub Desktop** to avoid typing commands. |
| **A terminal** | A text-command window, needed for a couple of setup steps. | Mildly techie; only used briefly. |

### Claude (the AI assistant)
There are two doors into the same house:
- **The easy door — the Claude desktop app.** Install it, sign in, done. No commands. [Download Claude](https://claude.com/download) (Mac, Windows, iOS, Android).
- **The more powerful door — Claude Code.** This is the version that can *create and sync files* for you (your folder, your notes, your skills). It's a little more technical. [Claude Code overview](https://code.claude.com/docs/en/overview) · [install & requirements](https://code.claude.com/docs/en/setup).

Two honest notes:
- **It costs money.** Claude Code (and the desktop app's file-creating features) need a **paid Claude plan** — the free tier doesn't include them.
- **You do *not* need to install "Node.js."** You may see that mentioned online; the recommended installer doesn't require it. Skip that worry.

### Obsidian (your notebook)
Free for personal use. This is where your folder comes alive as a browsable, linked notebook. [Download Obsidian](https://obsidian.md/download).

### Git + GitHub (sync) — the techie bit, made gentler
Syncing a folder across devices with Git is genuinely **the most technical part of this setup today.** The friendly way in is a free point-and-click app:

- **Recommended: [GitHub Desktop](https://github.com/apps/desktop)** — use Git and GitHub by clicking buttons instead of typing commands. This is the on-ramp for non-engineers.
- Want to understand the words first? [About GitHub and Git](https://docs.github.com/en/get-started/start-your-journey/about-github-and-git) explains "repo" and "version control" in two short paragraphs.
- Optional confidence-builder: GitHub's browser-based [Hello World tutorial](https://docs.github.com/en/get-started/start-your-journey/hello-world) (no command line — though note it works in your browser, not on your own files yet).
- *Power-user alternative, only if you're comfortable:* the [Obsidian Git plugin](https://github.com/Vinzent03/obsidian-git) can sync from inside Obsidian — but it still needs Git installed and is fiddly on mobile, so most people should prefer GitHub Desktop.

*Where Git itself comes from, if you ever go deep: [git-scm.com](https://git-scm.com/) (warning: that site is written for programmers).*

---

## How to get started

This is the **intended flow**. Some pieces work today and some are still being built — each step says which.

**The shape of it:** you talk to the **brain** (a Skill that runs the interview and makes the judgment calls), and the brain directs the **hands** — a small command-line helper called **`wsx`** that actually creates files, syncs them, and double-checks everything. You mostly talk to the brain; the hands do the plumbing.

> 🚧 **Status: early.** The design for all of this is written ([SPEC.md](SPEC.md)). The actual tool — the Skill and `wsx` — is **just starting to be built**, so you can't run the full flow end-to-end yet. The steps below are the planned path.

1. **Install the prerequisites.** From the list above: Claude, Obsidian, and GitHub Desktop. *(Available now — these are existing apps.)*

2. **Get the generator.** This tool is becoming its **own standalone, shareable package** — its own folder you'll be handed or download. *(🚧 Not published yet — the standalone package is in progress. Note: it is **not** the same as Sean's personal workspace, which lives in a private repo you can't copy.)*

3. **Start the interview.** You tell the AI to begin, and the **brain** (the Skill) walks you through a friendly conversation in **five parts** — think of them as five "movements":
   - **1. Your tools & devices** — what computers, phone, and apps you use.
   - **2. Your work** — your job and what you actually do day to day.
   - **3. Your professional craft** — expertise you have *beyond* the day job.
   - **4. Your personal life** — hobbies, dream projects, and life admin like finances, health, or learning. *(Suggested gently — never pushed. You skip anything you don't want.)*
   - **5. Your preferences** — how you like to be talked to and how you want it all to run.

   *(🚧 The interview Skill is in progress.)*

4. **The tool generates your folder.** Behind the scenes, the **hands** (`wsx`) create your one folder — already a vault, already version-tracked, already wired to your AI. For your skills, it works smartly: it will **pull** a ready-made skill when a good one already exists, **adapt** one that's close, or **generate** a brand-new one for expertise that's uniquely yours. *(🚧 In progress.)*

5. **Open it and use it.** Point Obsidian at the new folder to browse your notes. Open your AI assistant — and it already knows you. From here it grows with you: every session adds to your second brain. *(🚧 In progress.)*

---

## How it works under the hood (optional)

You can skip this section entirely. In short: the **brain** is a "Skill" (a folder of instructions the AI loads for this task) that conducts the interview and makes the judgment calls, while the **hands** are a small command-line tool, `wsx`, that does the mechanical work — creating files, syncing through Git, and verifying nothing's broken. The output folder is built to be three things at once (a readable Obsidian vault, a version-tracked Git repo, and an AI-aware context store), and it reaches multiple AI tools through MCP, the "one standard plug" described above. The full design — every decision, format, and guardrail — lives in **[SPEC.md](SPEC.md)**.

---

## Privacy

Privacy is a default here, not an afterthought.

- **Walled by default.** Your **work** information and your **personal** information are kept separate.
- **Personal stays local.** Your personal context lives **on your own computer only** — it is **not synced and not shared** unless *you* explicitly choose to include it.
- **Plain text you control.** Everything is readable files on your machine. Nothing is hidden in a format you can't open, and nothing leaves your computer without your say-so.

In short: the tool errs on the side of keeping your private life private, and asks before changing that.

---

## Status & what's next

**Where things stand (mid-2026):**
- ✅ **The design is written.** The spec is at version 0.2 — see [SPEC.md](SPEC.md).
- 🚧 **The build is just starting.** The brain (the interview Skill) and the hands (`wsx`) are early. You can't yet run the full interview-to-folder flow.
- 📦 **Packaging is in progress.** This will become its own shareable download, separate from any private workspace.

**What's next, roughly:**
- A working interview Skill you can actually talk to.
- A first version of `wsx` that creates and syncs your folder.
- A smoother, less-technical setup path (the goal is to retire the "this part is techie" warnings).

Current working state and notes are tracked in **[SESSION-STATE.md](SESSION-STATE.md)**.

---

## FAQ

**Do I need to know how to code?**
No. The whole point is that an AI interviews you and builds it for you. The honest catch: a few *setup* steps today still feel technical (mostly the Git sync part). GitHub Desktop and the Claude desktop app are the gentlest ways through, and smoothing this out is a top priority.

**Does it cost anything?**
Obsidian and GitHub Desktop are free. The catch is the AI: Claude Code and the file-creating features need a **paid Claude plan** — the free tier won't run them.

**Is my personal life going to end up online?**
No, not unless you choose it. Personal context is **walled off and kept local by default** — never synced or shared automatically. See [Privacy](#privacy).

**Can I just copy Sean's setup instead?**
No — his personal workspace lives in a **private** repository you can't copy, and it's hand-built for him. This generator is the shareable, *make-your-own* version. That's the whole reason it exists.

**Can I really use this today?**
Not the full thing yet — it's **early**. The design is done; the tool is being built. You can install the prerequisites now and read the plan in [SPEC.md](SPEC.md), but the start-to-finish flow isn't ready. Watch [SESSION-STATE.md](SESSION-STATE.md) for progress.

---

## Links & references

**The plan (in this folder)**
- [SPEC.md](SPEC.md) — the full design (v0.2).
- [SESSION-STATE.md](SESSION-STATE.md) — current working state and progress.

**Your notebook (Obsidian)**
- [Download Obsidian](https://obsidian.md/download)
- [What a vault is](https://obsidian.md/help/vault)
- [Internal links / wikilinks](https://obsidian.md/help/links)
- [Obsidian Git plugin](https://github.com/Vinzent03/obsidian-git) *(power-user option)*

**Sync & history (Git + GitHub)**
- [GitHub Desktop](https://github.com/apps/desktop) *(recommended, point-and-click)*
- [About GitHub and Git](https://docs.github.com/en/get-started/start-your-journey/about-github-and-git)
- [Hello World tutorial](https://docs.github.com/en/get-started/start-your-journey/hello-world)
- [git-scm.com](https://git-scm.com/) *(for programmers)*

**Your AI assistant (Claude)**
- [Download Claude (desktop & mobile)](https://claude.com/download)
- [Claude Code overview](https://code.claude.com/docs/en/overview)
- [Install & requirements](https://code.claude.com/docs/en/setup)

**The concepts (skills, MCP, formats)**
- [What are skills? (Anthropic Help)](https://support.claude.com/en/articles/12512176-what-are-skills)
- [Agent Skills overview (Anthropic docs)](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Using skills in Claude Code](https://code.claude.com/docs/en/skills)
- [agentskills.io](https://agentskills.io) — the open skill standard
- [anthropics/skills](https://github.com/anthropics/skills) — official example skills *(browse, don't worry about copying)*
- [skills.sh](https://skills.sh) — community skill directory *(useful, but **not** officially vetted — check before installing anything)*
- [What is MCP?](https://modelcontextprotocol.io/docs/getting-started/intro)
- [Introducing MCP (Anthropic)](https://www.anthropic.com/news/model-context-protocol)

**Big-picture ideas (optional reading)**
- [Building a Second Brain](https://www.buildingasecondbrain.com/) *(concept only — it also sells a course)*
- [Markdown cheat sheet](https://commonmark.org/help/)
- [What is YAML?](https://www.redhat.com/en/topics/automation/what-is-yaml)

---

*Built with care, and honestly still being built. If a step here doesn't exist yet, this README will tell you so — no pretending. Questions and patience both welcome.*

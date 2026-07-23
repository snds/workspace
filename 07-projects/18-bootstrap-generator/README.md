# Bootstrap Generator

**An AI that interviews you, then builds you your own "second brain" — notes, knowledge, and a personal assistant that actually knows you.**

*Works with your AI assistant of choice. **Claude recommended** (it's what this was built and tested with), but the workspace it creates is truly AI-agnostic — it speaks open standards, not one company's format.*

> ⚠️ **Early days.** This is a real project, but it's just getting started. The design is written down (see [SPEC.md](SPEC.md)), and the building has only just begun. Read this as *"here's the plan and how it will work,"* not *"here's a finished app you can install today."*
>
> **Today you can:** install the apps below and read the plan. **Coming soon:** the AI interview that builds your folder *for* you. So this README is part how-to, part preview — and where something doesn't exist yet, it says so plainly.

---

## What this is

A while back, one person (Sean) built himself a personal setup: a single folder that holds all his notes and knowledge, syncs across his computers and phone, and is wired into his AI assistant so that every time he opens it, the assistant already *knows him* — his work, his projects, how he likes to be talked to.

His friends saw it and asked: *"How did you make that? Can I have one?"*

This is the answer, repackaged so a **non-technical person** can use it. You don't build it by hand. Instead, an AI **interviews you** — a friendly conversation about your devices, your job, your skills, your personal life, and your preferences — and then **generates the whole thing for you**, personalized to who you are.

And because it's built on **open standards** rather than one company's private format, the result isn't locked to a single AI. You can use it with Claude (the recommended, smoothest path) or with other assistants — and switch later without rebuilding.

There's no assumption that you write code, know what a "terminal" is, or have ever heard the word "repository." Every techie term in this document is explained in plain language, with a quick "learn more" link if you're curious.

---

## What you'll end up with

One folder on your computer. That single folder does three jobs at once:

1. **It's your notebook (a "vault").** All your notes and knowledge, saved as plain, readable text files you can browse like your own private Wikipedia. You read and edit them in a free app called Obsidian.
2. **It remembers every version (a "git repo").** It quietly keeps a full history of every change and syncs across all your devices — like the version history in Google Docs, but for the whole folder.
3. **It teaches your AI assistant who you are.** It's connected to your AI tools so that, every session, the assistant already knows your work, your projects, and how you like to work — no re-explaining yourself each time.

Same folder. Three superpowers. And it's **AI-agnostic by design** — see ["Your AI assistant"](#your-ai-assistant--claude-recommended-others-supported) below for how Claude and other agents all plug into the same folder.

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
Skills are organized like a company. A **hub** is a broad area — say, "photography." Its **spokes** are the specialists inside it — "lighting," "color grading," "printing." The hub is the department; the spokes are the experts in it.
**You won't manage any of this yourself** — the tool sets it up. This is just what's happening behind the curtain when your assistant suddenly "knows" a specialist topic. You're the passenger here, not the mechanic.
*Learn more: [agentskills.io](https://agentskills.io) — the open standard these skills follow.*

### 🗂️ "Context" (and keeping it private)
**Context** is your personal and work information, saved as plain text files, so the assistant actually knows your situation. It's kept **walled by default**: your work life and personal life are stored separately, and your *personal* context stays **private and on your own computer** — never synced or shared — unless you choose to open it up. (More in [Privacy](#privacy) below.)

### 🕓 "Git" and syncing
**Git** is a tool that tracks every change to your folder and keeps a full history you can rewind through — version history for a whole folder, not just one document. **GitHub** is the matching online service that stores a copy in the cloud so your devices stay in sync. This is the part that lets you start a note on your laptop and pick it up on your phone.
*Learn more: [About GitHub and Git (plain-language)](https://docs.github.com/en/get-started/start-your-journey/about-github-and-git).*

### 🌐 "Open standards" (why it isn't locked to one AI)
Here's the thing that makes this **AI-agnostic**: it's built on a handful of *open, vendor-neutral standards* that many AI tools already understand — chiefly **[AGENTS.md](https://agents.md)** (a shared way to give any coding agent instructions, used by 60,000+ projects and backed by the Linux Foundation), plus **MCP** and the **Agent Skills** format below. Because your workspace "speaks" these common languages instead of one company's private format, you're not married to a single AI — switch assistants and your folder comes with you.
*Learn more: [AGENTS.md](https://agents.md) — the open standard, supported by Cursor, GitHub Copilot, OpenAI Codex, Google Gemini, and 20+ others.*

### 🔌 "MCP"
Think of **MCP** as a **USB-C port for AI** — one standard plug that lets your AI assistant connect to your files and to other tools. Set it up once, and many different AI apps light up. It's another reason the same folder works across assistants.
*Learn more: [What is MCP? (official intro)](https://modelcontextprotocol.io/docs/getting-started/intro).*

### ✍️ "Markdown" and "YAML" (the file formats)
Your notes are written in **Markdown** — plain text with light formatting, like using `*` for a bullet or `#` for a heading. Some settings are stored in **YAML** — a simple, human-readable list of settings, like a labeled shopping list. You rarely need to touch either directly.
*Learn more: [Markdown cheat sheet (CommonMark)](https://commonmark.org/help/) · [What is YAML? (Red Hat)](https://www.redhat.com/en/topics/automation/what-is-yaml).*

---

## What you'll need first

Honest heads-up: **some of this setup is technical today.** That's exactly what this project wants to smooth out over time, but for now you'll touch a few tools that weren't built for beginners. Where there's a gentler, point-and-click option, this README points you to it.

Here's the shopping list:

| You'll need | What it's for | How hard (today) | Cost |
|---|---|---|---|
| **An AI assistant** (Claude recommended) | The assistant that runs your interview and becomes your "brain." | Easiest via Claude's desktop app; others vary. | Depends — see below. |
| **Obsidian** | The free app you read and edit your notes in. | Easy. | Free. |
| **GitHub Desktop** | Syncs your folder across devices and keeps history. | The most technical part — but point-and-click. | Free. |

> **About the "scary" parts:** a couple of one-time setup steps (mainly first-time Git sync) may involve pasting a command or two — but the assistant walks you through them, and you **never operate `wsx` (the file-making tool) yourself**; the AI drives it for you. You don't need to learn the command line to use this.

### Your AI assistant — Claude recommended, others supported

**Recommended: Claude.** This generator was built and tested with Claude in mind — it's the smoothest, most complete path, and the "brain" that runs your interview installs as a native Claude **skill**. The gentlest way to get it: **download the Claude desktop app**, which now includes Claude Code (the part that can create and sync files). Install it, sign in, and you're set — no command line required.

- [Download Claude](https://claude.com/download) (Mac, Windows, mobile) — the desktop app includes Claude Code.
- *Prefer the terminal? The standalone command-line version lives at [Claude Code overview](https://code.claude.com/docs/en/overview) · [install & requirements](https://code.claude.com/docs/en/setup).*
- **Cost:** Claude Code is included in Claude's paid plans — the entry **Pro** plan is about **$20/month** (~$17/month billed annually) as of mid-2026. Check [current pricing](https://claude.com/pricing). *You do **not** need to install "Node.js"; the recommended setup doesn't require it.*

**Also works with other AI agents.** Because your workspace follows open standards, the generator can produce the right "adapter" for whatever assistant you prefer:

| Your AI assistant | How it connects | Notes |
|---|---|---|
| **[Claude](https://claude.com/download)** ⭐ *recommended* | Native skill + `AGENTS.md` + MCP | Smoothest, fully tested path. |
| **[Cursor](https://cursor.com)** | `AGENTS.md` + `.cursor/rules` + MCP | Popular AI code editor. |
| **[GitHub Copilot](https://github.com/features/copilot)** | `AGENTS.md` | Works in many editors. |
| **[OpenAI Codex CLI](https://github.com/openai/codex)** | `AGENTS.md` | Open-source; free to run (needs your own API access). |
| **[Google Gemini CLI](https://github.com/google-gemini/gemini-cli)** | `AGENTS.md` + MCP | Open-source; generous free tier. |
| *…and 20+ more* | `AGENTS.md` | See the [full list at agents.md](https://agents.md). |

*Cost varies by assistant: Claude needs a paid plan (~$20/mo); some open-source agents (Gemini CLI, Codex CLI) are free to run but use your own API key. Pick whichever suits you — the folder works the same.* *(🚧 The non-Claude adapters are part of what's still being built — see [Status](#status--whats-next).)*

### Obsidian (your notebook)
Free for personal use. This is where your folder comes alive as a browsable, linked notebook. [Download Obsidian](https://obsidian.md/download).

### GitHub Desktop (sync) — the techie bit, made gentler
Syncing a folder across devices with Git is genuinely **the most technical part of this setup today.** The friendly way in is a free point-and-click app:

- **Recommended: [GitHub Desktop](https://github.com/apps/desktop)** — use Git and GitHub by clicking buttons instead of typing commands. This is the on-ramp for non-engineers.
- Want to understand the words first? [About GitHub and Git](https://docs.github.com/en/get-started/start-your-journey/about-github-and-git) explains "repo" and "version control" in two short paragraphs.
- Optional confidence-builder: GitHub's browser-based [Hello World tutorial](https://docs.github.com/en/get-started/start-your-journey/hello-world) (no command line — though note it works in your browser, not on your own files yet).
- *Power-user alternative, only if you're comfortable:* the [Obsidian Git plugin](https://github.com/Vinzent03/obsidian-git) can sync from inside Obsidian — but it still needs Git installed and is fiddly on mobile, so most people should prefer GitHub Desktop.

*Where Git itself comes from, if you ever go deep: [git-scm.com](https://git-scm.com/) (warning: that site is written for programmers).*

---

## How to get started

> **The one thing that trips everyone up:** *this folder is the **generator** — the tool itself. It builds a **separate** workspace folder for you.* So don't run things inside this folder expecting your notes to appear here — your workspace is a brand-new folder the tool creates (e.g. `~/Documents/Projects/Workspace`).

First, the two things you need (details in [What you'll need](#what-youll-need-first)): an **AI assistant** (Claude recommended) and **[Obsidian](https://obsidian.md)** — plus **[GitHub Desktop](https://github.com/apps/desktop)** if you want sync. Then pick the path that fits you. They all produce the same thing.

### Path A — Easiest: let your AI do it ⭐ recommended
You don't type anything technical — your AI runs the tool for you.
1. **Open this generator folder in your AI assistant.** In Claude Code: open the folder (or run `claude` from inside it). In Cursor: open the folder.
2. **Say:** *"set up my workspace."* In Claude Code the generator ships as a registered skill, so that phrase alone triggers it — no need to name any file. *(On other assistants, or if it doesn't catch, nudge it: "Read `brain/SKILL.md` and set up my workspace for me.")*
3. Your AI **interviews you** (see [below](#what-the-interview-covers)), then creates your workspace and tells you where it is.

*(🚧 The guided interview is **early**. In Claude Code the trigger is wired; elsewhere the nudge above always works. If it stalls, use Path B — it never depends on the AI.)*

### Path B — One double-click (no AI, nothing to type)
1. **macOS:** double-click **`start.command`**. *(The first time, macOS may say "unidentified developer" — right-click the file → **Open** → **Open**. Just once.)*
   **Windows:** double-click **`start.bat`**.
2. It checks you have Python (preinstalled on Macs), then asks **two questions** — where to put your workspace and your name.
3. It creates your workspace and prints where it is + what to do next. Done.

### Path C — One command (if a terminal doesn't scare you)
From **inside this generator folder**:
```bash
python3 generator/bin/wsx init ~/Documents/Projects/Workspace --name "Your Name"
```
Stuck or unsure what to do next? Run `python3 generator/bin/wsx doctor` — it tells you where you are and the exact next step.

### What the interview covers
A friendly conversation in **five parts** — suggested gently, and you skip anything you want:
**1.** your tools & devices · **2.** your work · **3.** your professional craft (expertise beyond the day job) · **4.** your personal life (hobbies, dream projects, life admin — never pushed) · **5.** your preferences (how you like to be talked to).

### Then — open and use it
- **Browse it:** open your **new** workspace folder in **[Obsidian](https://obsidian.md)**.
- **Use it:** open that folder in your AI assistant — and it already knows you. Every session adds to your second brain.

> 🚧 **Honest status.** Paths B and C **work today** — they create a real, AI-ready workspace folder right now. Path A now **auto-triggers in Claude Code** (the generator is a registered skill), and generated skills come out as *guided skeletons* — sectioned forms your AI fills with your actual know-how, not empty stubs (the tool refuses to call a workspace done while those forms are still blank). Still early: some registry features (pulling ready-made community skills, the MCP runtime) are not built yet, so parts of a fresh workspace are things you and your AI grow into. That's the next thing being built.

---

## How it works under the hood (optional)

You can skip this section entirely. In short: the **brain** is the interview — instructions the AI loads for this task — that conducts the conversation and makes the judgment calls, while the **hands** are a small tool, `wsx`, that does the mechanical work: creating files, syncing through Git, and verifying nothing's broken. The output folder is built to be three things at once (a readable Obsidian vault, a version-tracked Git repo, and an AI-aware context store).

The agnostic magic is that `wsx` can **emit** your workspace into whatever format your AI assistant speaks — a Claude skill, an `AGENTS.md` file, Cursor rules, an MCP connection, or a plain "context pack" you can paste anywhere. One canonical workspace, many adapters. The full design — every decision, format, and guardrail — lives in **[SPEC.md](SPEC.md)**.

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
- 🛠️ **The tool runs today.** The `wsx` CLI scaffolds your workspace, makes it AI-ready, and verifies it (Paths B & C above). What's still early is the *guided interview* that fills it in automatically for you.
- 🚧 **Agnostic adapters in progress.** The Claude path is the first target; the `AGENTS.md`, Cursor, MCP, and context-pack adapters come next.
- 📦 **Packaging is in progress.** This will become its own shareable download, separate from any private workspace.

**What's next, roughly:**
- A working interview you can actually talk to.
- A first version of `wsx` that creates and syncs your folder.
- The adapters that let it target any AI assistant, not just Claude.
- A smoother, less-technical setup path (the goal is to retire the "this part is techie" warnings).

Current working state and notes are tracked in **[SESSION-STATE.md](SESSION-STATE.md)**.

---

## FAQ

**Do I need to know how to code?**
No. The whole point is that an AI interviews you and builds it for you — and you never operate the file-making tool (`wsx`) yourself. The honest catch: a few *setup* steps today still feel technical (mostly the Git sync part). GitHub Desktop and the Claude desktop app are the gentlest ways through, and smoothing this out is a top priority.

**Does it only work with Claude?**
No. **Claude is recommended** because it's what this was built and tested with — the smoothest path. But the workspace it creates is **AI-agnostic**: it's built on open standards ([AGENTS.md](https://agents.md), MCP, [Agent Skills](https://agentskills.io)) that many assistants understand, so it also works with tools like Cursor, GitHub Copilot, OpenAI Codex, and Google Gemini — and you can switch later without rebuilding. *(The non-Claude adapters are still being built.)*

**Does it cost anything?**
Obsidian and GitHub Desktop are free. The only paid piece is the AI — and that depends on which you pick. The recommended Claude path needs a paid plan (entry **Pro** ≈ **$20/month**, ~$17 annually, as of mid-2026 — see [current pricing](https://claude.com/pricing)). Some open-source agents (Google Gemini CLI, OpenAI Codex CLI) are free to run but use your own API access.

**Is my personal life going to end up online?**
No, not unless you choose it. Personal context is **walled off and kept local by default** — never synced or shared automatically. See [Privacy](#privacy).

**Can I just copy Sean's setup instead?**
No — his personal workspace lives in a **private** repository you can't copy, and it's hand-built for him. This generator is the shareable, *make-your-own* version. That's the whole reason it exists.

**Can I really use this today?**
Not the full thing yet — it's **early**. The design is done; the tool is being built. You *can* install the prerequisites now and read the plan in [SPEC.md](SPEC.md), but the start-to-finish flow isn't ready. Watch [SESSION-STATE.md](SESSION-STATE.md) for progress.

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

**Your AI assistant**
- ⭐ *Recommended* — [Download Claude (desktop & mobile)](https://claude.com/download) *(includes Claude Code)* · [Claude Code overview](https://code.claude.com/docs/en/overview) · [Install & requirements](https://code.claude.com/docs/en/setup) · [Current pricing](https://claude.com/pricing)
- *Other supported agents* — [Cursor](https://cursor.com) · [GitHub Copilot](https://github.com/features/copilot) · [OpenAI Codex CLI](https://github.com/openai/codex) · [Google Gemini CLI](https://github.com/google-gemini/gemini-cli)

**The standards that make it agnostic**
- [AGENTS.md](https://agents.md) — the open, vendor-neutral instruction standard (60k+ projects)
- [agentskills.io](https://agentskills.io) — the open skill standard
- [What is MCP?](https://modelcontextprotocol.io/docs/getting-started/intro) · [Introducing MCP (Anthropic)](https://www.anthropic.com/news/model-context-protocol)

**The concepts (skills)**
- [What are skills? (Anthropic Help)](https://support.claude.com/en/articles/12512176-what-are-skills)
- [Agent Skills overview (Anthropic docs)](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Using skills in Claude Code](https://code.claude.com/docs/en/skills)
- [anthropics/skills](https://github.com/anthropics/skills) — official example skills *(browse, don't worry about copying)*
- [skills.sh](https://skills.sh) — community skill directory *(useful, but **not** officially vetted — check before installing anything)*

**Big-picture ideas (optional reading)**
- [Building a Second Brain](https://www.buildingasecondbrain.com/) *(concept only — it also sells a course)*
- [Markdown cheat sheet](https://commonmark.org/help/)
- [What is YAML?](https://www.redhat.com/en/topics/automation/what-is-yaml)

---

*Built with care, and honestly still being built. If a step here doesn't exist yet, this README will tell you so — no pretending. Questions and patience both welcome.*

---
name: delegation-model-routing
description: How the main session orchestrates instead of executing - when and how to dispatch work to sub-agents (Agent tool), which model tier to pick (haiku / sonnet / opus / fable) so the heaviest model is reserved for hard reasoning, a copy-paste brief template, parallelization and file-ownership rules, verifying sub-agent output, and how to report it. Use for every non-trivial task to decide whether/how to delegate to sub-agents and which model tier to use, and whenever usage limits, token spend or cost are a concern (סוכן משנה, האצלה, חיסכון בטוקנים, מגבלות שימוש, ניתוב מודלים, איזה מודל).
---

# Delegation & model routing

## Principle
Standing policy set by the user (adopted from a social-media tip): **1) don't do the work yourself - dispatch sub-agents; 2) don't use Fable for everything - use Opus for easier tasks.** Goal: stop burning usage limits on the most expensive model for every task.
- Pick the **cheapest model that does the job right the first time**. Judge cost per finished task: a cheap run that needs two retries is not cheap.
- The tip's savings claims are the author's and **unverified** - compare the plan's usage meter before and after on comparable work.
- The orchestrator's own model is the user's choice (`/model`); this policy governs the sub-agents it spawns.

## Orchestrator duties
1. **Understand** the request; ask the user when it is ambiguous (never delegate the conversation).
2. **Plan:** split into tasks, mark dependencies, decide what runs in parallel.
3. **Route:** pick a model per task (table below) and set `model` explicitly on every Agent call.
4. **Brief** each agent with the template below.
5. **Verify** the real output yourself (see Verification).
6. **Integrate, decide, report** to the user.

Keep for yourself: decisions, trade-offs, user communication, final verification. Delegate: execution.
**If you are a sub-agent:** do your brief yourself; do not re-delegate.

## Model tiers
API list-price ratio, Oct 2026 snapshot (same for input and output): **haiku 1 : sonnet 20 : opus 40 : fable 100.** Plan usage limits roughly follow price; re-check, prices drift.

| Tier | `model` | Use for | Examples from this KB |
|---|---|---|---|
| Trivial | `haiku` | Mechanical, zero judgment, easy to check | find which skills mention a term; validate JSON/frontmatter; list changed files; pull a value from a log; run a command and report output |
| Routine | `sonnet` | Well-specified work with exact instructions | update skill counts/index tables; add router keywords; reformat a skill to the template; SRT captions from a fixed script; summarize given files |
| Standard (default) | `opus` | The user's "easier tasks": needs judgment, not deep design | render + QA stills review; write a new skill from a research brief (`sonnet` if the brief is fully prescriptive); build a landing-page section; debug with a clear repro; grounded research with sources; Hebrew copy editing |
| Hard | `fable` | Deep reasoning where errors are costly or subtle | architecture of an agent system or automation with approval gates; security review of hooks/guards/secrets handling; gnarly multi-cause debugging (intermittent render failures); deep research synthesis across conflicting sources |

- **Unsure between two tiers:** lower tier for reversible, easily checked work; higher tier when mistakes are costly or hard to detect.
- **Escalate** one tier when the lower one failed twice, or the task turned out to need design decisions - and say so.
- **Using fable:** write one line why ("fable: security-critical review of guard hooks").

## Brief template
```
Goal: <one-sentence outcome>
Context: <why; what is already decided; background the agent cannot infer>
Files: <absolute paths to read / edit / create>; do NOT touch: <paths>
Constraints: <no commit/push, no CPU-heavy commands, language/style, size limits>
Skills: <skill names to load, e.g. motion-toolkit> (point to them; don't paste them)
Deliverable: <exact output - files + short report; format; max length>
Verify: <how to prove done - command/check to run; report what was NOT verified>
Report back: files changed, checks run with results, doubts/assumptions.
```

## Parallelization & file ownership
- Independent tasks: several Agent calls **in one message**. Dependent tasks: in sequence, passing paths to the previous output, not a retelling of it.
- **One owner per file.** Never two agents editing the same file - including shared files (READMEs with counts, `router-rules.json`, `global-CLAUDE.md`). Give shared files to one agent, or edit them yourself afterwards.
- Heavy jobs (renders, builds) run once, in the background; don't start CPU-heavy work in parallel agents on the same machine.
- Tell each agent which paths are in scope; anything else is read-only.

## Verification
- Read the actual files/diffs, run the validators (JSON, tests, frontmatter check), open the stills/render. A report saying "done" is a claim, not proof.
- Check scope: nothing changed outside the allowed paths (`git status`, `git diff --stat`).
- Mechanical checks can go to a `haiku` agent, but read its result and spot-check at least one item yourself.
- Anything not checked is reported as **not verified** (`verify-and-safety-gates`).

## Exceptions - act directly when
- The answer is one line, or you need a clarifying question.
- It is a single trivial tool call whose spawn overhead exceeds the work (read one file, `git status`).
- The Agent tool is unavailable (you are a sub-agent, or the surface lacks it).
- The user explicitly says to do it directly.
- You are doing your own verification reads.

## Anti-patterns
- **Vague briefs** ("fix the video") - the agent guesses and you pay for a retry.
- **Delegating understanding** - asking an agent what the user wants or which option to choose; that is the orchestrator's job.
- **Nested spawning** - sub-agents spawning sub-agents: cost multiplies and nobody verifies.
- **Many tiny agents** for related work - each starts cold and re-reads the context; batch into one.
- **Fable by reflex** - "important" is not "hard".
- **Haiku for judgment** - a cheap failure is not cheap.
- **Trusting reports** - relaying "done" without opening the files.
- **Two agents, one file** - lost edits and conflicts.

## Report format to the user
In Hebrew (per global rules), short:
```
מה הואצל:
- סקירת סטילס של הרינדור -> opus
- עדכון ספירות ואינדקסים -> sonnet
- סקירת אבטחה של ה-hooks -> fable (קריטי לאבטחה)
מה אימתתי בעצמי: JSON תקין, 34 תיקיות סקילים, הסטילס נבדקו
לא אומת: <...>
איפה התוצאה: <נתיבים / קישורים>
```

---
name: agentic-build-discipline
description: Disciplined method for building apps, tools, scripts, games, bots and pipelines with a coding agent - the 4-part task prompt (outcome, source, boundaries, verification), smallest-working-version-first, one-change-at-a-time iteration, test-case design, recovery when stuck, handoff notes, local vs cloud, and architecture for message/WhatsApp agents and media pipelines with approval gates. Use whenever starting or continuing any app/tool/automation build (פיתוח אפליקציה, כלי, בוט, סוכן, פרויקט קוד).
---

# Agentic build discipline

Define the result, not just the question. Chat explains; an agent produces files you can verify.

## The 4-part task prompt
1. **Outcome** - what must exist/be saved at the end (file names, formats).
2. **Source** - materials/data it may rely on (and what to do if missing: ask or mark gaps, never invent).
3. **Boundaries** - folder it may touch, no deletion/overwrite, save versions, no publish/send/buy, ask before paid actions.
4. **Verification** - how completion is proven (run it, open file, test cases) and what to report: what was produced, where, what was checked, what was NOT checked.

Add Context / Role / Expectation (the 3-part prompt) when scoping a new topic.

## Working habits
- **Plan first** for anything new; approve the plan; build the smallest working version (one can, one room, three objects, one landing page).
- **Each stage's output is the next stage's input;** check each before moving on.
- **One change per iteration**, named precisely ("the handlebar hides the road"), saved as a new version; keep a known-good version before large changes.
- **Separate observations from recommendations** (broken button = fault; headline idea = hypothesis).
- **Verify real output:** open the file/app yourself; a number in chat or a screenshot is not proof. Reopen saved project files; check keyboard access; for tools test a valid case, an invalid case and boundary values (e.g. 200 at 10% -> 180; 0% unchanged; 100% -> 0; empty, negative, 110% rejected).
- **Distinguish automatic checks** (file exists) **from manual play-through checks** (character can reach the crystal, sound actually plays).
- **Mechanics -> materials -> sound** for games; verify in the running game, not only the renders.
- **Local vs cloud:** local tasks need the machine on and its files/software; cloud tasks run in a separate environment with different access. Test in the environment you will actually use.
- **Permissions:** grant only the apps/data the task needs; a written "don't delete" is not enforcement - permissions and backups are. Close unrelated windows/password screens.
- **Costs:** subscriptions, API usage and paid services are billed separately; test one small task and check usage before scaling.

## Handoff & recovery
- `HANDOFF.md` at the end of every session: goal, approved decisions, key files, what works, what was tested, what is open, next step, no secrets. Next session starts by reading it and checking actual files.
- **Stuck prompt:** "Stop. Summarise what was created and saved, what failed and which check proves it, the smallest next step, and whether a permission/tool is missing." Don't delete the project or restart before saving this.
- Output wrong? separate causes (model, lighting, camera / data, logic, UI). Ask for a smaller preview before a full render/run.

## Pipeline with approval gates (media/automation)
`input -> clean -> plan artefact (storyboard/spec/plan table) -> HUMAN APPROVAL -> expensive step -> QA -> deliver`. Always test one unit before the batch; collect API keys via terminal, never chat; clear errors with next actions (credits, connection, invalid key); keys with expiry.

## Message-agent architecture (WhatsApp / chat)
Customer -> WhatsApp provider -> your webhook (hosted serverless) -> model + approved tools -> reply via provider. The coding agent is only the *build tool*; it does not run the live agent.
Build in versions: V1 text replies only -> approved knowledge doc -> calendar availability -> booking with explicit confirmation -> optional persistent memory.
Safeguards: verify webhook signature; dedupe by event ID in persistent storage (not process memory); inbound only (avoid loops); no shell/personal files for the agent; answer only from approved knowledge else offer human contact; no invented prices/times; never say "booked" until the calendar tool succeeded; per-sender data isolation; rate limits; retention/deletion policy; test with test numbers/calendar only. Troubleshoot in order: webhook arrival -> model call/key -> send result -> duplicates -> calendar IDs. "Deployment ready" only means code deployed.

## Test-suite habit
Record for every test: expected, actual, evidence. Never mark a test passed unless it was run. Include abuse cases (attempts to extract secrets/other customers' data), failures of each dependency, duplicates, two concurrent users.

## Code review
The tool that wrote the code is not its best reviewer: have a second pass (another tool/fresh session) with "make no changes; summarise recent changes; look for bugs, leftover placeholders/demo data, exposed secrets, buttons with no target; rank must-fix / should-fix / low; propose fixes without applying".

See also: `claude-setup-architecture`, `web-build-harden`, `verify-and-safety-gates`, `automation-scoping`.

---
name: automation-scoping
description: Decide what to automate and how - find time-wasting repetitive work, score solutions on impact vs effort, assess agent-vs-automation-vs-chatbot fit, design a small measurable pilot with human approval gates, least-privilege access, logging, exception routing and handoff. Use when the user asks where AI/automation helps, wants an agent/workflow/n8n/Make/Zapier design, or is overwhelmed by tools (אוטומציה, סוכן AI, תהליך חוזר, איפה להתחיל).
---

# Automation scoping

Start from the waste, not the tool. A new tool that doesn't solve a defined problem adds learning and maintenance cost.

## Definitions
- **Automation:** fixed path - event -> predefined action. **AI inside automation:** understanding/classifying/summarising steps. **Agent:** goal + context + tools + several steps inside limits. **Chatbot:** answers from prepared content, hands follow-up to a person. **Human-in-the-loop** for sensitive decisions/exceptions.

## Process
1. **Find where time is lost:** observe people doing the work; list repetitive tasks, bottlenecks, information stuck between systems. Be precise ("40 min/day scanning long emails").
2. **Pick ONE process**, one success metric (time, errors, handoffs, completion), measure before.
3. **12 solutions map:** ask for 12 varied options with specific tool names; rate each:
   - technical difficulty 1-4 (1 chat, 2 dedicated tools/add-ons, 3 advanced automation, 4 agents/code)
   - pricing model (verify on official site)
   - impact 1-4 with a one-line time estimate
   - how to start (2-3 sentences)
   Then add **your own effort score** (depends on permissions, systems, skills) and sort into quadrants: Quick Wins / Major Projects / Fill-ins / Thankless. Start with Quick Wins. If the table is too long, ask for top 3 by impact/effort.
4. **Check existing tools first** (the org's approved chat tool can already summarise, draft, sort, build tables, plan). If org data is needed, check permissions/data policy - don't hunt for workarounds.
5. **Fit test.** Good: high-volume, repetitive, clear inputs/rules, accessible organised data, measurable. Stop & check: mostly exceptional cases needing professional judgment; no reliable data source; sensitive actions without approval; no staff owner for review/maintenance.
6. **Define actions & limits:** what the agent can read/do, when it must hand off.
7. **Build a focused pilot** on real examples; connect only needed systems; run alongside the existing process.
8. **Measure & decide:** expand only on proven use; stop failed experiments without theatre.

## Agent loop and controls
Understand -> Check (access defined systems) -> Act (reply/update/coordinate/escalate) -> Log.
- **Scoped permissions** (read-only first, then draft/pause states, then writes).
- **Approval gates** before payments, sensitive sends, data changes, pricing/commitments, publishing.
- **Logging & monitoring:** actions, results, errors, costs. Failure alerts + recovery path + a way to pause.
- **Handoff path** with gathered context for unusual cases; **exception routing**.
- **Process map + success definition + documentation + team training** as deliverables.

## Typical use cases
WhatsApp/customer service; lead screening + CRM logging + follow-up; scheduling; back-office document->system updates and reports; internal knowledge answers; proposals with human approval before sending; weekly report: pull data -> check gaps -> summarise anomalies -> draft for approval.

## Vocabulary: do not mix up
**Plugin/connector** = access to a service. **Skill** = how to do a task. **Project** = workspace with context/files. **Scheduled task** = when to run. A skill grants no access; a plugin knows no standards; a schedule doesn't check quality. Add scheduling only after a successful manual run; set time zone; show how to pause; test local vs cloud environment.

## Scheduling prompt essentials
"Run every [day] at [time] [time zone] using skill X and source Y, save with run date in the name, don't publish/send, if source unavailable or nothing new report the gap instead of inventing; show saved schedule, time zone, environment and how to pause."

## Common problems
No access to document -> account/link/permissions. Plugin connected but nothing read -> plugin lacks data access. Wrong output location -> state exact destination and open it. Scheduled task not running -> status, time zone, environment. Repetitive output -> define what counts as new. Excess usage -> narrow inputs, small outputs, fewer reruns.

See also: `agentic-build-discipline`, `verify-and-safety-gates`, `claude-setup-architecture`.

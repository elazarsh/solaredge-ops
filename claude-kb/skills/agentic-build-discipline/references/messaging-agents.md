# Messaging & voice agent stacks (WhatsApp etc.)

Pick one stack; the pattern is the same: **channel -> webhook server -> model + approved tools/knowledge -> reply**. The coding agent only builds it; it does not run the live agent.

## Stack A (build with Claude Code / Codex)
WhatsApp API provider (e.g. Kapso) -> serverless host (Vercel) -> model API (billed separately from chat subscriptions) -> optional calendar connector (Maton) -> optional Supabase for history/dedupe/leads. Business knowledge lives in a separate approved document.

## Stack B (voice agent, built in Antigravity)
Antigravity (builder, Planning vs Fast modes) + Green API (WhatsApp send/receive text+voice via QR-linked number; no MCP -> feed docs or Context7) + Supabase (messages, contacts, knowledge files; MCP) + Mastra (agent framework with memory/tools; MCP) + Grok or another current LLM + ElevenLabs V3 (Hebrew TTS) + Context7 (docs MCP) + Vercel (24/7 hosting; until deployed it runs only while your computer is on).
Voice behaviour: accepts text and voice notes; replies text, voice or both (voice only when asked); memory in DB; answers grounded in uploaded knowledge.

## Build order
1. Test number/SIM dedicated to the experiment (never your main business number). 2. V1 text replies only. 3. Knowledge doc (stable facts separated from changing info like dates; approved before deploy). 4. Deploy + point webhook to deployed URL; real round-trip test from your phone. 5. Calendar availability, then booking with explicit confirmation + re-check + duplicate prevention. 6. Memory (decide what/how long; isolate per sender; test deletion). 7. Voice (optional). 8. Pilot with a small allowlist.

## Safeguards checklist
Webhook signature verified; dedupe by event ID in persistent storage; inbound-only processing (avoid loops); no shell/personal files for the agent; answers only from approved knowledge, else offer human contact; no invented prices/times/promises; never claim "booked" before the tool succeeded; allowlisted numbers for personal-assistant modes; per-sender isolation; rate limits + spend cap (check whether a cap alerts or actually stops); retention/deletion policy; keys in env vars only, `.env` git-ignored (gitignore does not purge history - rotate leaked keys); platform messaging rules for broader audiences; serverless time limits -> queue for long tasks.

## Tests (record expected/actual/evidence)
Single reply; knowledge hit and miss; unknown question handoff; calendar availability; booking only after confirmation; invalid signature; duplicate event; two senders; extraction attempts (secrets, other customers' data); provider failures; voice reply generation; "Deployment ready" is NOT proof of function.

## Troubleshooting order
Webhook arrives? -> model call/key valid? -> send result at provider? -> duplicates? -> calendar IDs/permissions? Give the agent the exact error text or a screenshot; never print keys in logs.

## Email triage skill (example)
Ask clarifying questions first; define categories (urgent, new lead, existing customer, info only); output fields (category, recommended action, draft reply); NEVER send/delete/archive/relabel; test an ambiguous case.

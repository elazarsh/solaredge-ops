---
name: automation-recipes
description: Concrete business automation recipes with triggers, steps, tools, safeguards, error handling and test plans - meeting transcript to tasks, Drive permissions audit, review collection, employee onboarding, refund processing, email attachment filing, Sheets backup, lead/WhatsApp flows. Use when the user wants to implement a specific back-office automation in Make/Zapier/n8n/Apps Script/code (אוטומציה, מייק, זאפייר, Apps Script, גיבוי, חשבוניות).
---

# Automation recipes

First decide *whether* to automate with `automation-scoping`. Every recipe below: start read-only/draft, add human approval for risky steps, log runs, alert on failure, pilot on a few real cases, then expand. Add the gaps the sources left open: **retries, failure alerts, output validation, and a manual fallback**.

## Common design template
`Trigger -> Filter (narrow) -> Validate input -> Transform/AI step (fixed prompt, no inventing) -> Write destination -> Notify -> Log`
Error path: malformed input -> "manual handling" folder + alert; duplicate guard via idempotency key; kill-switch/pause; owner named; monthly integrity check (links, permissions, quotas).

## 1. Meeting transcript -> summary + tasks + CRM + chat notification
Trigger: new transcript file in a dedicated Drive folder (only if recording/transcription was on). Steps: read -> strip small talk -> LLM with fixed system prompt (role: project manager; do not invent; 2-sentence summary + numbered tasks with owner and date only if stated; Hebrew) -> write to Sheet/CRM -> short message to team chat. Safeguards: least-privilege folder access, human approval before anything goes to an external client, no sensitive/payment/medical data through public models without consent, ask participants to state names, monthly folder/permission check. Setup ~45-60 min.

## 2. Drive permissions audit
Trigger: scheduled (night). Steps: connect via admin/service account -> find files shared "anyone with link" or with external domains -> log rows (file, owner, share type, scan date) -> weekly summary of top-5 sensitive files; immediate alert if > 10 exceptions/day. Safeguards: **report only for the first month** (no auto-changes), whitelist public/marketing files, keyword filter (salary, contract, password) if noisy, no delete rights without manual approval. Pilot on one closed folder.

## 3. Customer review collection
Trigger: project/invoice status = completed. Steps: wait ~3 h, send only in a polite window (e.g. 10:00-19:00) -> short personal message -> ask internal feedback question first; negative answers go to the manager, positive get the public review link (shortened, tracked). Guardrails: skip open tickets/complaints, max one request per customer per year, use official messaging API and rate limits, **respect consent/opt-out rules** (the source didn't address them), pilot on 5 recent satisfied customers, expect click-through ~>15% else adjust timing/wording. Treat vendor performance numbers as unverified.

## 4. Employee onboarding
Stages: map required data (ID, bank, NDA) and target systems -> intake form -> central data store -> e-signature -> downstream (payroll, equipment, email/training welcome). Trigger: candidate marked hired. Safeguards: sensitive contracts need human review, restrict access to ID/tax docs, personal email until corporate mailbox exists, manual fallback if signature stalls, periodic connection checks. Test end-to-end with a test address.

## 5. Refund processing
Trigger: ticket "refund approved" or approved form. Validate: original transaction ID, policy window (30/90 days), amount <= paid, no double refund; partial refund via variable amount. Output: payment provider refund + credit invoice in accounting + customer notice. Controls: **human approval above a threshold (define it)**, idempotency, audit log (who approved, when), PCI-DSS awareness, sandbox pilot on 5 transactions. Add rollback/alerts yourself.

## 6. Email attachment -> renamed -> filed
Narrow trigger (subject/attachment matches invoice/receipt keywords incl. Hebrew חשבונית/קבלה). Optional small AI check that it is truly an invoice. Rename `YYYY-MM-DD_supplier_amount`; file to pre-created Drive folder or accounting/CRM. Errors: corrupt/unsupported -> "לטיפול ידני" folder + alert. Test 10 real emails, one supplier first, one week clean before expanding.

## 7. Google Sheets daily backup (Apps Script)
Time-driven trigger nightly; copy spreadsheet to a private backup folder named `<name>_backup_<YYYY-MM-DD_HH-mm>` (Asia/Jerusalem); retention: 14 daily + 2 months weekly, delete older (add that logic); admin-only folder; failure emails go to owner; **do a real restore test** monthly. Cost: free, ~7 min.

## 8. Lead / WhatsApp / scheduling flows
See `agentic-build-discipline` (messaging-agent architecture and `references/messaging-agents.md`) and `automation-scoping` (agent loop, approvals).

## Test plan (all recipes)
Sample inputs incl. empty/malformed/duplicate; expected output per case; dry-run mode that writes only to a log; run alongside the manual process for 1-2 weeks; compare time before/after; keep change log; define owner and review date.

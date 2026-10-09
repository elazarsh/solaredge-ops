# Misc. workflows (lower priority)

## Daily job search with Claude + a scraping connector
Setup: install scraping connector (e.g. Apify) in Connectors, add API token, new chat, upload résumé, paste prompt.
Prompt essentials: analyse résumé (skills, seniority, role types) -> search postings from last 24h on LinkedIn/Google/local boards -> score each 1-10 (fit, responsibilities, skills, experience, seniority) -> table (role, company, date, source, score, link) -> rules: only <=24h, score >= 7, max 10, sorted by recency then score, strict scoring.
Tips: match by content not job title; run once each morning; tune window (48h/week) or cutoff (6) if results are thin; set location per field. Verify listings yourself (scraped data may be stale). Read any one-line install script before running it. Alternative: built-in browsing.

## Moving memory between assistants
Direct memory import is often unsupported: ask the old assistant to summarise who you are/your projects/preferences as a document, review and prune it (privacy), then upload to the new assistant. See also the `anthropic-skills:import-memory` skill.

## Reusable "personal brief" for agents
A one-page business/person summary (PDF/Doc) you can upload to any agent tool to personalise it; refresh quarterly; no secrets.

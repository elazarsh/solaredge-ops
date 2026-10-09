# Search & research tool tactics

## Perplexity-style answer engines
- Loop: detailed prompt -> choose model (or Best) -> pick source scope (web / academic / social) -> **open every cited source**.
- Detailed prompts beat short ones; have another LLM draft the prompt; limit the time range ("last 3 years").
- Operators: `site:` (one domain), `after:` (date), `file:` (inside a large document), academic mode for scholarly sources (often abstracts only; medical -> professional databases).
- Deep Research for multi-source reports (daily allowance on free tier). Spaces = project workspace (files + instructions + persona). Pages = turn an answer into an HTML page.
- Pipeline: answer engine -> NotebookLM (summary, slides, audio).
- Hallucinations still happen (invented destinations/sources). Paid subscriptions elsewhere don't unlock premium here.

## NotebookLM
One notebook per topic; clear source names with date/version; Hebrew output set in settings; check extraction; select only relevant sources; Studio outputs (audio overview, reports, mind maps, flashcards, quizzes, tables, slides, infographics) are drafts; verify before using. Free tier example (Sept 2026 per source): 100 notebooks, 50 sources/notebook, 50 chat queries/day, 3 audio overviews/day, 10 Deep Research/month - re-check.

## Prompt for the answer engine
"Research [question] for [reader]. Only sources from [date range] on [site/type]. For each claim give source, date, and quote location. Separate facts, interpretation and unknowns. Table of findings, then 5 open questions."

## Verification pass
Open the cited page; confirm the passage supports the sentence; check publication date/entity; look for a second independent source for any number that drives a decision.

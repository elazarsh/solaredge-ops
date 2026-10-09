---
name: grounded-research
description: Source-grounded deep research and analysis method - supplied-sources-only, fact vs hypothesis vs missing-information separation, dated citations, claim-verification tables, source-quality checks, multi-source comparison documents, NotebookLM-style notebooks, and research-to-report packaging. Use for any research, market/competitor scan, literature review, summarising documents or building a evidence-based report (מחקר עומק, סיכום מסמכים, השוואה, דוח).
---

# Grounded research

The model fills gaps with clichés unless it is given real sources and told what to do when they are missing.

## Rules
1. **Use only supplied/retrieved sources.** Don't invent data, categories, reviews, rankings, quotes, prices, laws.
2. **Three buckets in every output:** verified findings, hypotheses, missing information. Observation != interpretation != recommendation.
3. **Every metric/claim gets: source, date, population/conditions, limits.** Unknown stays "unknown" - not "no".
4. **Report sample size and time window** for anything counted (e.g. "last 50 reviews", "3 months of data").
5. **Ask rather than guess:** up to 3 focused questions if key information is missing, or mark gaps.
6. **Drafts only;** approval before publishing, sending, or changing live systems.
7. **No secrets in prompts.** Attach files again in new chats. Test with copies; originals unchanged.
8. **One step at a time,** save each table and decision so later steps build on them.

## Workflow
1. **Context once per session:** who/what/audience/goal/constraints/available data/work already done. Read sources first, then flag gaps.
2. **Define the question** (one decision it must support) and the output form (one-page summary, comparison table, brief, memo).
3. **Collect sources.** Check author, date, relevance. "Deeper research" does not guarantee better sources. Name each source clearly with date/version. Re-sync if originals change.
4. **Extract:** open each source and confirm text, headings, numbers survived extraction (scanned/unreadable PDFs give weak summaries).
5. **Select only relevant sources** and ask one focused question first; add sources for comparison afterwards.
6. **Synthesize** with a reference for each factual claim.
7. **Verify:** produce a claim table `claim | supporting reference | caveats in source | corrected wording`; remove or mark unsupported claims as questions. A well-formatted quote does not prove the sentence is right; check year, population, dropped conditions; page numbers in files may differ from printed pages.
8. **Package:** summary, evidence table, open questions, next actions. Nothing is published or sent.

## Multi-source comparison document
Open 3 pre-selected pages -> extract fixed fields (name, purpose, stated limits, price if stated) -> table with source links and "not found" for missing -> reopen the document and confirm nothing existing was altered.

## Public-page audit (first-time visitor)
Identify headline offer and main CTA, check each button goes where the label says, submit nothing, pay nothing. Report: faults (reproducible) vs suggestions; what could not be checked. Reproduce one finding yourself.

## Reusable prompts
- **Summary:** "Using only the selected sources, write a [language] summary for [reader]: five key conclusions, what each means in practice, open questions. Cite a source for each claim. Separate explicit facts from interpretation. State missing information instead of guessing."
- **Verification:** "Check the draft against the sources. Table: claim, reference, caveat, corrected wording. Flag anything without support. Don't treat interpretation as fact."
- **File summary:** five key points, three action items, missing details needed for a decision; reference the section for each; no outside facts; say if a table/page was unreadable.
- **Targeted revision:** keep approved parts unchanged, revise only item N, show updated version, mark what changed.
- **Status:** three lists - verified / unchecked / information still needed. Never say "everything works" without describing tests.

## Notebook-style tools (e.g. NotebookLM)
One notebook per topic; set output language explicitly (feature support in Hebrew varies: e.g. interactive voice may be English only); outputs include summary with citations, audio overview, reports, mind maps, flashcards, quizzes, tables, slides, infographics. Treat every generated artefact as a draft: verify names/numbers/conclusions against originals before using; verify a saved note before converting it into a source (errors propagate); check upload/sharing policy for confidential or client material; limits and tiers change - read the current table.

## Data-gap rules for quantitative work
Missing baseline is not zero. Log change dates and attribution limits. Measure at fixed intervals (30/60/90 days). Say which numbers are measured vs estimated.

## When sensitive
Run the 7-question check in `verify-and-safety-gates` (consent, data uploaded, consumer vs enterprise plan, retention/training, privacy policy, human review, verification).

See also: `deck-and-doc-craft`, `human-writing-hebrew`, `seo-geo-playbook`.

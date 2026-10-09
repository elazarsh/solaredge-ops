---
name: human-writing-hebrew
description: Write and edit clear, specific, natural text (Hebrew first, English too) and remove "AI-sounding" patterns - inflated significance, vague attribution, buzzwords, manufactured contrasts, forced triads, over-formatting, chat residue, tool artifacts, unsupported citations. Use for any copywriting, article, email, post, report, website copy, or when asked to humanize, sharpen, proofread, or detect/clean AI writing (כתיבה, עריכה, נשמע כמו AI, ניסוח טבעי).
---

# Human-quality writing (Hebrew-first)

No single word, dash or detector score proves AI authorship; these patterns signal *weak, unsupported or unedited* writing - in humans too. Fix substance, not surface.

## Method: brief -> verify -> structure -> edit -> compare
1. **Brief:** audience, the reader's question, what cannot be promised, real source material. Without sources you get clichés.
2. **Verify facts** and attribute precisely (source, date, metric, population, limits). Unverifiable = remove or say what is known/unknown.
3. **Structure:** open with the answer or the reader's problem; one concrete example from approved material (label hypotheticals; never invent personal experiences, clients, results).
4. **Edit** for concrete, plain language (below).
5. **Compare final vs source:** no number, condition or caveat lost.

## Content patterns to remove
1. Inflated significance without facts ("milestone", "revolution") -> say what changed, for whom.
2. Vague credit ("wide recognition") -> named outlet/date.
3. Analysis that sounds deep but explains nothing -> show the missing link; separate fact / interpretation / hypothesis.
4. Promotional adjectives everywhere ("powerful", "unprecedented").
5. "Studies prove / experts say / many believe" with no source.
6. Formulaic limitation + optimism ("despite challenges the future is bright") -> name the real constraint and action.
7. Categories personified as actors in titles/openers.
8. Filler awards/credentials.
9. Abstract buzz Hebrew: לנמף, להעצים, נוף משתנה, תובנות עמוקות -> concrete verb + object.
10. Heavy verbs: משמש כ / מהווה / מגלם -> simple verb ("it shows", "זה מראה").
11. Vague relations: קשור ל / מתכתב עם -> owns / partners / influenced by / merely similar.
12. Manufactured contrast "it's not just X, it's Y".
13. Forced triads and equal-length symmetrical sections.

## Formatting & residue
- Over-formatting: excess bold, bold-header bullets, dividers, needless tables, em dashes, decorative emoji, skipped heading levels. Test: remove formatting - does it still make sense? Use tables for real multi-dimensional comparison, lists for sequential steps.
- Chat residue: "Certainly, here's...", closing offers, editor instructions, unfilled placeholders.
- Knowledge-cutoff phrases presented as world facts; a failed search proves nothing.
- Tool artefacts: citation tokens, stray asterisks, broken markdown/wikitext, tracking params.
- Sources: a link that opens doesn't support the sentence - check it exists, is the right publication, contains the info, keeps conditions. Citation lists must tie to sentences (no unused/undefined refs, no bare homepages). Broken DOIs/ISBNs = warning.
- Sudden shifts in tone, terminology, units, dates, name spelling, gender forms inside one text.
- Summary at the end of every section, uniform paragraph length, refusals/disclaimers - weak signals only.

## Editing rules
- Specific > grand. Ask "compared to what?" and "so what?" of each claim.
- Plain verbs; remove filler; title for the reader's need.
- Keep one set of terms/units/names/dates. Label buttons/headings by real outcome.
- State real limits and conditions.
- Don't fake humanity (typos, invented anecdotes). Improve accuracy and usefulness.
- Clean-up pass before publish: chat openers/closers, placeholders, markers, broken markup.

## Detection caveats
Detector scores are not probabilities nor share of AI words; one vendor withdrew its own classifier for poor accuracy; check any detector was evaluated on Hebrew and your text type; don't harm someone on a score; a chatbot answering "did you write this?" is not a record. Don't upload confidential text without checking terms.

## Prompts for quick use
- "Rewrite for [reader]. Keep every fact and number. Replace abstractions with concrete verbs. Remove filler and unsupported attribution. Do not add facts. Return the text and a list of claims you could not verify."
- Voice match: give 1 real past example (email/post that worked); "match structure and tone, do not copy sentences."

See also: `prompt-modifiers` (/humanize, /anti-fluff, /voiceprint), `hebrew-rtl-output`, `web-build-harden`.

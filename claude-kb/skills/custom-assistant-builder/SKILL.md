---
name: custom-assistant-builder
description: Design reusable custom assistants (Gemini Gems, Custom GPTs, Claude Projects, system prompts) - role, method, clarifying questions, fixed output format, hard rules, knowledge sources, testing and maintenance; plus Workspace/Gmail automations in plain language. Use when the user repeats a task weekly, wants a reusable assistant/prompt builder, or asks to write system instructions (ג'ם, GPT מותאם, פרומפט מערכת, עוזר חוזר).
---

# Custom assistant builder

Create an assistant for any task repeated more than once a week.

## Creation steps (Gem-style; same logic for Custom GPT / Project)
1. Name clearly ("Presentation prompt builder"); one-line description.
2. Write **Instructions** (below). Easiest: describe task, user, audience, tone, output format to a strong model and ask it to *write the system prompt without running it*.
3. Enable only needed tools (image creation, canvas, deep research).
4. Add **Knowledge** (documents, a notebook) when it must rely on your material.
5. **Test in preview** with normal, ambiguous and out-of-scope inputs; save; remember to click Update after later edits.
6. Review outputs after several uses and refine.

## Instruction structure (5 parts)
1. **Role** - who it is and what it produces (and what it does NOT do).
2. **Working method** - steps it follows each time.
3. **Clarifying questions** - what to ask first if info is missing (one message, or one question at a time).
4. **Fixed output format** - identical structure each time.
5. **Hard rules** - answer in [language]; only from sources; do not invent; mark "needs verification"; one follow-up if unclear.

Add: examples of good output, banned phrases, refusal behaviour for out-of-scope requests, a reminder of audience.

## Example specs
- *Presentation prompt builder:* asks topic+audience, purpose+style, slide count, sources -> outputs a full prompt (role, context, audience, slide structure opening/sections/closing with next steps, style) for NotebookLM/Gemini; Hebrew; sources only. Advanced: given a website URL it extracts a design system and embeds it in every prompt.
- *Workshop Q&A assistant:* knowledge = transcripts + docs; answers with references.
- *Social writer in my voice:* knowledge = past posts; builds a voice guide; drafts per platform.
- *Banner maker:* asks a few questions, outputs banner prompt in fixed format + matching group message.
- *Packshot / storyboard assistants:* see `image-generation-playbook`.

## Pitfalls
Vague instructions -> inconsistent output; skipping preview; forgetting Update; admin-blocked tools on org accounts (permissions, not a bug); uploading sensitive/personal data; creating on mobile (use desktop); never refining.

## Workspace-style automations (describe in plain language, assistant builds multi-step flow)
Save invoice attachments into Drive folders by month; summarise incoming mail, judge relevance, label; sort mail by sender/keyword/project; flag urgent mail from a manager and alert; daily news digest. See `automation-recipes` for safeguards.

## Same idea in code-agent tools
A skill (`SKILL.md`) is the code-agent equivalent of a Gem: put role/method/format/rules there and a trigger-rich description (see `claude-setup-architecture`).

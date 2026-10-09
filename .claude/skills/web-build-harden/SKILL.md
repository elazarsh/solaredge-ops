---
name: web-build-harden
description: Build, review and harden websites, landing pages and small web apps made with an AI coding agent - brief, Plan Mode, section-by-section build, honest copy, design system, Hebrew/RTL, mobile, forms, accessibility, privacy/terms pages, SEO, deployment (Vercel/Supabase/GitHub), and an evidence-based publication gate. Use for any request to create a site/landing page/tool, improve an "AI-looking" site, convert Figma to code, or prepare a site for launch (אתר, דף נחיתה, בניית אתר, נגישות).
---

# Web build & harden

A site that looks polished proves nothing. Credibility = accurate content + working functions + verified accessibility + an honest report of what was and was not tested.

## Build flow

1. **Preparation:** one sentence for who the page is for; ONE primary action (inquiry / signup / existing purchase link); only assets you have rights to; only verifiable proof points; success criteria ("every button goes to the right link, readable on mobile").
2. **Interview first** (for new sites): business, audience, problem, deliverables, what happens after contact, tone, colours, languages. Missing facts = placeholders `[להשלים]`, never invented.
3. **Plan Mode:** show colours, fonts, section order, components; user approves; then build **section by section**. Small targeted change requests ("make this one button smaller").
4. **Inspiration, not copying:** give URL + full-page screenshot, inspect DOM, replicate structure only; replace content, images, products, optionally colours/fonts. UI component libraries (e.g. 21st.dev "copy prompt") - fewer, coherent components beat many mismatched.
5. **Local preview** (localhost) -> review -> deploy only on approval. Back up to a private GitHub repo after each working state (roll back via commit history / previous deployment).
6. **Infra trio** (add only when needed): hosting (Vercel), database/auth/storage (Supabase) for forms/leads, GitHub for backup. Secrets in env vars, `.env.example` with names only, never in client code or logs.
7. **Domain:** DNS records at the registrar; verify HTTPS and www/non-www canonical.

## Content rules (publication blockers)
- No fabricated testimonials, client logos, counts, prices, results, or fake urgency/countdowns.
- Headline states the concrete service/audience/result; a stranger should be able to explain the offer back. Sub-line = how it works; button = the actual action.
- Sections answer visitor questions: what is it, is it for me, what do I get, how does it work, why trust, how to proceed. No "customers say" without real content.
- Plain specific writing; remove filler, "not only... but also" loops, unsourced "experts say", leftover chatbot text (see `human-writing-hebrew`).
- A form needs a real destination and a **tested submission**; a form that only shows fields is not a connection.

## Design rules
- Small design system (see `design-system-first`): one action colour, text/background colours, status colours, a Hebrew font with fixed weights/sizes, 8px spacing. Measure contrast in every state incl. hover/focus (4.5:1 / 3:1).
- Real imagery only (approved photos); else typography or plain diagrams. One icon family; no emoji as icons.
- Motion only as feedback (menus, states). No custom cursors, scroll hijacking, content hidden until animation ends; honour reduced-motion.
- Images: accessible URLs not local paths; set dimensions to avoid layout shift; alt text only where the image carries information.

## Hebrew / mobile / function
- `lang="he" dir="rtl"`; check numbers, links, punctuation, mixed English (see `hebrew-rtl-output`).
- Test widths 360, 390, 768, 1440 + a real device: horizontal scroll, text overflow, sticky elements covering content, enlarged text, long names/addresses.
- Forms: empty, invalid, service failure, double submit; success message on screen != delivery. Confirm data really persists (not just preview).
- Accessibility in practice: keyboard-only, visible focus, heading order, labels, error messages, alt text, contrast. Automated tools help but don't replace manual checks. Overlay widgets are not accessibility. The accessibility statement describes what was actually tested and its limits. Legal requirements depend on context - verify with official sources/professional.
- Privacy / terms / accessibility pages reflect real behaviour: data collected, purposes, third parties, retention, contact. Don't invent retention periods or legal claims; draft with AI, professional review.

## SEO & performance
Unique title + meta, one H1, descriptive subheadings, canonical, internal links, no accidental `noindex`, structured data only for visible content (no invented ratings), sitemap/robots, favicon from logo, share image, PageSpeed on real mobile. No promise of rankings. See `seo-geo-playbook`.

## Fix priority
1. Publication blockers (fabrication, exposed data, broken forms, false accessibility claims) 2. Comprehension (vague headline/buttons) 3. Usability (mobile scroll, labels, focus, menus) 4. Consistency 5. Polish.

## Publication gate (evidence report)
Backup/commit -> domain, favicon, three policy pages -> blockers fixed -> report table: route, device/width, action, expected, actual, evidence (screenshot); untested = "not tested". After launch: open the public URL logged out / private window, direct sub-page access, links, images, live form delivery; rollback version ready.

## Follow-up review prompt
"Compare the updated site with the previous requirements; retest affected routes and shared components; report only findings with location, description, reproduction steps and suggested fix; separate bugs / missing information / design preferences; list remaining publication blockers."

## Figma -> site
Read-only Figma token (90 days, no write scopes), MCP connection, Dev Mode link, implement-design agent, review localhost incl. hover/mobile, then private repo -> Vercel -> domain -> analytics -> SEO/security (HTTPS, no secrets in code, CSP headers). Agents per project <= 5-7: copywriter, developer, critic, launcher, design-sync.

See also: `agentic-build-discipline`, `verify-and-safety-gates`, `hebrew-rtl-output`.

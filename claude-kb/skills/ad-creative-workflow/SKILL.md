---
name: ad-creative-workflow
description: Plan and produce ad creative and campaigns with AI - angle-first briefs, copy variants, visual briefs, placement adaptation (1:1, 9:16), landing-page promise matching, ad-library research, and a safe read-only-first workflow for ad platforms such as Meta Ads MCP. Use for any ad, social creative, UGC-style video ad, campaign brief or ad performance review (מודעה, קמפיין, קריאייטיב, פייסבוק, אינסטגרם).
---

# Ad creative workflow

AI covers **creative production and analysis**. It cannot verify landing pages, lead handling, measurement or account permissions - a human owns those.

## Roles (small teams may share, but document each review)
Business owner approves offer/budget; account lead verifies account/placements; marketing lead approves message/audience; designer checks hierarchy, legibility, brand fit; launch owner checks files/placements; measurement owner verifies results.

## Steps

1. **Business brief** (handoff doc): product (what is / isn't included), audience + problem, verified offer terms, usable proof, style examples (and words to avoid), destination page with ONE action, budget and dates *as supplied*. Mark missing items as gaps. Never infer prices/budget from examples.
2. **Brief check prompt:** summarise brief, separate facts from assumptions, list missing details that affect the promise. Do not write ads yet.
3. **Angle before words:** 3 genuinely different angles (each = a different reason to care): audience, problem solved, supportable promise, proof needed. Reject "variants" that only swap the opening line.
4. **One ad per angle:** main text, short headline, CTA. No guaranteed results, no unsupplied numbers.
5. **Visual brief:** scene, focal point, essential text, lighting, colours, headline space, feed + story versions; real approved product photo as reference; do not add features the product lacks. Live text goes in a separate design layer (typo-fixable). For video: opening / demo / CTA.
6. **Placement adaptation:** 1:1 and 9:16 working files; check that product, faces, headline are not cropped and platform UI does not hide key content.
7. **Promise match:** compare ad copy to landing page; flag gaps in product, terms, CTA; test mobile layout and button in a browser, not by reading text.
8. **Ad-library research (if available):** per example record source link, core message, offer, format, CTA. Separate observation from interpretation; do **not** infer profitability from how long an ad runs. Then propose five original angles and what each must prove.
9. **Variation test design:** change ONE defined variable per test (hook, image, CTA). Fixed everything else. Name variants after angle + brief (A-vertical, B-wide).
10. **Pre-launch checklist:** every claim traces to the brief; Hebrew verified inside images; image matches the real product/person/offer; one CTA; landing page continues the promise and works on mobile; each variant uniquely named with matching copy+media.

## Brand consistency
One brand doc (colours, fonts, logo placement + clear space) referenced in every brief; approved product photos as source; same typography/spacing/logo across versions; archive original + approved with date, product, angle, approver; log rejected wordings and why; store the brief+prompts that produced each approved asset so the next round starts from the updated brief.

## Design basics for creatives
Decide what is seen first (product or headline) -> support -> CTA. Start from brand colours and check text contrast. Readable consistent Hebrew font; check alignment, punctuation, Hebrew+numbers+English mixing. Space around headline and logo; preview at phone size without zooming.

## Platform agents (Meta Ads MCP and similar)

- Order: connect -> confirm correct business/account (list, then select ONE) -> **read-only** pull -> analyse -> only then drafts. Writes (budget, status, copy) change real money: state explicitly what the agent may/may not do.
- Rank the winner by CTR, CPC, conversion rate, cost per result and spend; explain gaps between pre-click and post-click performance.
- Create campaigns in **PAUSED** status only; re-read structure afterwards and report IDs, status, budget, audience, link, previews; log partial success before any retry (avoid duplicates).
- Budget != target cost. Verify currency/units (minor units in API), measurement (pixel/CAPI, deduplication, UTMs) and that an event reflects a real lead.
- Don't trust invented audiences - check each targeting option exists. Don't fix delivery problems by just raising budget.
- Keys are entered in the terminal; images come from a separate image tool; ads are uploaded by a human unless explicitly engineered otherwise.

## Image -> video ad pipeline (product photo to 9-scene storyboard to video)
Phone photo -> cleaned studio shot (image model) -> single 9:16 image with 9 numbered scenes + director notes (action, camera, light, mood) -> **human approval gate** -> video model -> optional local dashboard (drag-drop photos, product description, length/quality/sound, one button, stage status with timers, download). Test one scene first; show clear errors (credits, connection, invalid key) with next steps.

See also: `visual-codes`, `video-camera-codes`, `code-driven-video`, `verify-and-safety-gates`.

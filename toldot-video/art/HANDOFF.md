# Current handoff — art delivery

The inherited production below has been continued on `gpt/art`. **Read `STATUS.md`, `QA_REPORT.md`, `assembly_map.csv` and `DONE.md` first.**

- 54 manifest assets, 52 approved, all 76 beats have reviewed approved asset routes.
- P02 and P26 remain weak after one correction each; use the documented separate-layer alternatives.
- 47 generations in this session; 5 additional ribbon files are crops, not new generations.
- Exact prompts for new images are retained. Five recovered old references lack original prompts and are honestly marked as such.
- Strict validator and approved-only audit pass; final contact sheets and validation hashes are saved.
- Art is ready for Claude assembly. No film/animation was rendered or checked here.
- Batch commits are pushed. PR creation is blocked by api.github.com CONNECT 403; network addition is saved in environment draft, not confirmed applied. PR_DESCRIPTION.md is ready; no PR has been opened.

---

## Historical handoff (before this continuation)

# Handoff — art production

The user is transferring the task to Codex. Work only under toldot-video/art/ on gpt/art; read toldot-video/AGENTS.md and its referenced project files first. The current user explicitly directed uninterrupted production, without asking for approval after every batch; T1 correction may be deferred if needed. Do not mark work finished until the definition of done in AGENTS.md is actually satisfied.

## Current state

- Branch: gpt/art, based on ccr-09182f34-4lw44m.
- art/plan.md: draft mapping of beats 0–75; estimate 37 images, subject to real QA and sprite splitting.
- art/manifest.json: 9 plates, all draft or weak, none approved. Some beat mappings are aspirational and must be checked against actual visual content.
- art/refs/: 6 rejected-aspect draft images P05, P10, P11, P12, P14, P15. They are not manifest plates. Inspect them; crop only if the important subject remains intact, then add them to the manifest if usable. Retain honest provenance and QA.
- 6 initial tests T1–T6 were generated in a prior conversation and were not committed to this branch. Do not treat them as approved or regenerate blindly.
- 21 images generated in total: 6 earlier tests, 9 manifest plates, 6 reference drafts. No sprites, final contact sheets, QA_REPORT.md or DONE.md yet.
- Last validator run: non-strict validator returned OK, with warnings that P01 is 2:3 and 46 beats lack any manifest entry. Passing this validator does not establish artistic correctness or complete coverage. Strict coverage has not passed.
- Important shortcomings: P01 Isaac is blue instead of cream and the composition is unsafe to crop; P02 fingers/crown action are unclear; P03 the crown shadow is partly rectangular; P06 sleeves are blue; P07 and P09 hands are ambiguous. P04, P08, P13 are drafts. Inspect every image before approval.

## Next

1. Verify Git branch/head and repo state; inspect AGENTS.md, art/plan.md, art/manifest.json and art/refs/ before work.
2. Resolve aspect ratios, compare visual consistency and motifs, and fix or mark weak without silently presenting failures as approved. Honor the user's direction to postpone T1 if appropriate.
3. Generate remaining plates and clean separate sprites, with no faces, text or weapons. Follow the established riso paper style, character colors, intact/broken ring, distinct chairs and crown-shadow change. Give attention to the green background and separating sprites.
4. Save and commit each batch under art/, update STATUS.md and manifest.json and run the validator. Document exact prompts and honest QA. Check all 0–75 beats for actual visual coverage, not just manifest labels.
5. Only after completion: contact sheets, visual QA, strict coverage, QA_REPORT.md, DONE.md, then the requested PR. Do not create DONE.md prematurely.

## Earlier test files (outside repository)

These are the six previously generated test images in ChatGPT; access to these links may require the user's session. They have known QA issues and are not approved.

- T1: https://chatgpt.com/library?file_id=libfile_d58753f6ef148191ba7d3a61bf1f36c0&account_id=personal
- T2: https://chatgpt.com/library?file_id=libfile_41a6c0b7d054819199d47991aaf723c0&account_id=personal
- T3: https://chatgpt.com/library?file_id=libfile_1c77d55696f48191a499401775f2cdbc&account_id=personal
- T4: https://chatgpt.com/library?file_id=libfile_402ebec61444819191d4b2577b5c8ab6&account_id=personal
- T5: https://chatgpt.com/library?file_id=libfile_44d85c831ea8819191ae9796270b2b94&account_id=personal
- T6: https://chatgpt.com/library?file_id=libfile_f45da3409f3c81919564c712efc09ffb&account_id=personal

No API keys or credentials are included.

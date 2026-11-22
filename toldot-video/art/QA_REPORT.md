# Art QA — בין כוח לברכה

## Delivery

54 manifest assets: 29 plates and 25 sprites. **52 approved; P02 and P26 remain weak and must not be used as final art.** All 76 beats (0–75) have an approved asset route in `assembly_map.csv`. This is a still-art delivery, not a rendered film or a claim that the animation already works.

47 image-tool generations in this session, including corrections and the intact-ring/blue-chair variants. Combined with the 21 generations reported by the inherited handoff: **68 generations historically reported**. Five ribbon crops are derivatives, not new generations. No dollar cost or remaining quota was exposed by the tool; none is invented here. The old 37-image estimate grew through separate animation layers, two additional narrative plates and retained weak drafts.

## Visual review performed

Reviewed the existing set, every new generation/correction, and the final contact sheets. Approved images have no visible facial features or profiles, lettering/numerals, weapons, flags, logos or real people. Walking staffs and blunt farm tools are not weapons. Views include overhead motifs, close hands, wide landscapes and symbolic scenes. Plates are actual JPEGs at quality 95 after documented 9:16 crops where needed; sprites are PNGs on bright green.

Cream Isaac, pink Rebecca, orange Esau, slender blue Jacob, cold grey-green Laban hand and green dissenting brother remain the identifying colors. Shadows themselves are monochrome/ink silhouettes. Some hands have naturally occluded fingers; see per-image notes rather than assuming every fingertip is independently visible. S03, S10, S15 and P13 provide particularly clear hand assets.

The gold ring has separate intact/broken sprites S18/S13. Orange square chair S05 stays outside after violence; green rounded chair S11 is the dissenting brother's different chair. S25 is Jacob's blue place in the opening debate. S14/S15 supply fist/open-hand crown-shadow states. Keep the same shadow anchor and scale when morphing. Crown plates show varying numbers of visible points; S01 is the canonical moving crown.

## Excluded weak work

| Asset | Remaining problem after its one allowed correction | Approved route |
| --- | --- | --- |
| P02 | Crown lift/thread direction and small hand shapes do not clearly express the debate action. | S04 tabletop, S16/S17 parents, S10 hand/staff, S01 crown, S05/S25 chairs, S18 ring. Animate the thread specifically toward the blue place. |
| P26 | Cream color corrected, but blue receiving hand has only four clearly separated digits. | P09 protective pink hand on blue Jacob, S10 cream hand, S03 blue open hand, S01 crown and P05 crowd. |

No second correction was made to either weak plate. Earlier versions remain in `refs/` or Git history. T1 correction and the old T1–T6 approval process were deferred under the inherited authorization; the inaccessible external tests were neither downloaded nor treated as approved.

## Approved with explicit limitations

- P01 is now actual tent-cloth shadows. Beat 67's changed shared direction is an animation/masking task; a distinct second pose was not generated.
- P05, P10, P11, P12 and P15 were recovered by safe crops from inherited references. Their **original exact prompts were not saved**: manifest `prompt` is null, provenance says so, and engine attribution is inherited rather than independently verified. No prompt was fabricated.
- P05's outer canopy and P10/P09's tent edges meet or extend past crop edges; the important figures, hands and motifs survive. P19's secondary house is partly clipped, while its hand/ledger/coins remain usable. P28 has narrow side margin around the spade.
- P04 scales are static and balanced; collapse/tipping is not baked into the image. P08's fist is a paper object, not a shadow: project S14 as the shadow. P18 is a night-to-dawn scene, not a separate all-night shot. P24 includes an inverted sheep; houses need rotation in animation. P15 is a filled house rather than only an outline.
- P23's younger thumb is naturally hidden by the older hand. No extra/malformed digit was observed, but five separate blue fingertips cannot be certified. Use S03 where a fully spread five-digit blue palm is required.
- No single image contains the long dining table of beat 19 or the complete final parental handoff. Those are **explicit multi-layer compositions**, not falsely labelled finished plates. The CSV identifies their approved component assets and remaining staging.
- S11 is deliberately dark forest green against vivid lime green. Key only the background color range; a blanket rule deleting every green-dominant pixel would damage the chair. No other sprite requires preservation of green foreground. S20–S24 are clean individual crops of the five S09 strips.

## Checks

`python3 toldot-video/art/validate_art.py --strict-coverage` and `python3 toldot-video/art/asset_tools.py audit` pass. The latter counts only approved assets. The legacy validator counts drafts too, so its success alone was never used as evidence of completed art. Cross-check the 76 CSV entries against the narration/visual descriptions, and keep P02/P26 excluded.

Additional final checks verify file/manifest parity, real image encoding, plate aspect, nonempty image dimensions, green corners, 76 unique assembly entries and approved references. Final contact sheets are `sheets/plates_01.jpg` through `plates_03.jpg`, and `sheets/sprites_01.jpg` through `sprites_03.jpg`.

Not checked here: keyed/composited animation, temporal morph quality, narration sync, typography, music, final render, audience review, fresh-task snapshot restoration. These belong to the assembly stage. The green originals are retained for that work.

## GitHub / environment

All work is confined to `toldot-video/art/` on `gpt/art`. Batch commits were pushed without force. The original base `ccr-09182f34-4lw44m` is not an ancestor of current main, so it remains the intended PR target.

Git read/push works. `gh pr list` and a fresh API connection failed with an HTTP CONNECT 403 for `api.github.com`. The required domain addition is saved in the environment draft; saving does not apply or publish it. **No PR has been opened.** PR text is ready in `PR_DESCRIPTION.md`. No token was requested or printed.

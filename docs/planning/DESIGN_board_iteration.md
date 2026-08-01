# DESIGN — Iterating on a generated storyboard (the Vision phase)

> **Status: PROPOSAL for Jayon's confirmation (2026-07-29).** Answers: *the sheet is generated, I want to change something — do I edit the image, or go back to the screenplay?* Companions: `PIPELINE.md` (the lock-and-compiler principle) · `TREATMENT.md` (ownership of the visual system) · `DESIGN_studio_ux.md` (phases).

---

## 1 · Why this question is load-bearing
Both obvious answers are wrong:

- **"Always edit the image."** The panel and the screenplay diverge. The video prompt is compiled *from the screenplay*, so it will then describe something different from the panel attached to it — and the video model receives **two contradictory instructions for the same shot**. This is precisely the drift the whole architecture exists to prevent.
- **"Always go back to the screenplay."** A mutated hand has nothing to do with the screenplay. You would be editing a story document to fix a rendering glitch, and re-rolling an entire sheet to fix one finger.

**The panel is not the final product.** It is a **reference fed to the video model**. That single fact decides everything below: a panel is only useful while it *agrees* with the screenplay.

## 2 · The rule
> **Anything the screenplay describes must be changed in the screenplay. Anything it does not describe may be fixed in the image.**

### Ownership map
| Layer | Owns |
|---|---|
| **Screenplay** (the lock) | who is present · blocking · action · gaze · expression · what they hold · shot size · angle · camera move · dialogue · duration |
| **Treatment** | medium · lens · camera law · colour · lighting law · negatives |
| **Location layer** | the set and its permanent contents |
| **The image itself** | nothing semantic — **rendering only** |

If you can name the thing you dislike using a screenplay field, it is a screenplay edit. If you cannot, it is either a Treatment matter, a location matter, or a rendering fault.

## 3 · The four change types — and where each is routed
### Type A · The screenplay is wrong
*"He should be looking away, not at her." · "She shouldn't be holding the bag yet."*
The panel faithfully renders what was written; the writing was wrong.
→ **Edit the lock.** Change the shot's field → the sheet prompt recompiles → regenerate that sheet. **This is the designed path**, and the propose→confirm→apply mechanism already does it.

### Type B · The screenplay is right; the prompt lost it
*The screenplay says "left foreground" and the panel put him centre.*
Nothing is wrong with the story — the compilation dropped or under-weighted something.
→ **Fix the compilation, not the story.** Re-run the sheet prompt with a targeted emphasis; no screenplay change.
→ **If the same loss recurs across episodes, that is a skill bug, not an episode problem** — fix the compiler (a `/tune` on skill-2b) so it stops happening to everyone.

### Type C · Everything was right; the model failed
*Extra limb · mutated hand · blurred face · a texture that ignored the material law.*
Nothing upstream is wrong.
→ **Regenerate, or make a targeted image edit.** This is the **only** case where editing the image directly is legitimate, because nothing in the screenplay describes how many fingers a character has.

### Type D · A new idea that isn't in the screenplay
*"Add a poster on the wall."*
→ **Ask what it is for.** If it carries meaning — someone uses it, it pays off later, it tells us something — it is a **prop and belongs in the screenplay**. If it is pure set dressing, it belongs in the **location layer**, so it appears in *every* future scene at that location rather than in one panel.
→ **Never let it live only in the panel.** A detail that exists only in the image vanishes the moment the video is generated, because the video prompt never heard about it.

## 4 · What the Vision agent actually does
Its job is **not** "edit images". Its job is **diagnosis**:
1. Read what Jayon said, look at the panel, and compare against the screenplay and the prompt that produced it.
2. **Classify the change** (A / B / C / D).
3. **Propose the routed fix** with its consequences — *"this is a screenplay change: it edits shot 2's gaze, recompiles this sheet and this segment's video prompt"* versus *"this is a render fault: I'll regenerate this panel only; nothing else changes."*
4. Apply on confirmation.

**That is the brilliance being asked for** — not image manipulation, but knowing which layer owns the problem. It is also a well-defined, checkable task rather than a vague one.

## 5 · Practical rules
- **Regenerate at sheet level, edit at panel level.** A change that affects composition or who's in frame means re-rolling the sheet (so the panels stay mutually consistent). A rendering fault confined to one panel can be fixed on the sliced panel alone.
- **Never accept a panel that contradicts the screenplay.** If a generation is beautiful but wrong, it is wrong. Either update the screenplay to match it (a deliberate, recorded decision) or regenerate.
- **Approved panels are locked** and become the video references. Re-opening one re-opens its segment's video prompt.
- **Keep the rejects.** A rejected generation plus the reason is evidence about what the prompt or the treatment is failing to convey.

## 6 · ⧖ What needs research before implementing
The architecture above is settled; the **mechanics of the image model are not**, and these determine what is actually possible:
- Can Nano Banana Pro perform a **targeted edit on one panel** without disturbing the others in a sheet?
- Does its **edit mode preserve character identity** as reliably as a fresh generation with references?
- Does re-generating with the same references **converge** or drift?
- Is there **masking/inpainting**, and is it usable at panel scale?
- Any **seed or reproducibility** control?
- The best phrasing for **iterative refinement** ("keep everything, change only X").
These are the subject of `DEEP_RESEARCH_PROMPT_nanobanana.md`, whose output becomes a canon file — `prompting_guidelines_nanobanana.md` — the image-model equivalent of the Seedance guidelines, which today **does not exist** (NBP guidance is scattered across skill-2b, `TREATMENT` and research files).

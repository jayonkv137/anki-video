# Content Strategy — Instagram structure (Jayon's design, 2026-07-17)

**Status:** DRAFT concept — the leading candidate for how episodes appear on the page. Needs the research marked ⌕ (see RESEARCH_BACKLOG.md) before locking at C6.

## 1. The daily TRIPTYCH (one grid row per word-batch)

Anki's card anatomy, rebuilt as an Instagram grid row (3 posts):

| Post | Format | Content | Anki equivalent |
|---|---|---|---|
| **1 — FRONT** | Carousel, 10 cards | The 10 words, WORD ONLY (no meaning). Cover card: "Rate mal!" instruction. Branded template per character-of-the-day. | Card front (recall attempt) |
| **2 — EPISODE** | Reel (center) | The full combined story video, subtitled. THE product. | The "lesson" |
| **3 — BACK** | Carousel, 10 cards | Word + article + example sentence + EN translation + one micro grammar-tip. | Card back (verification) |

Users can consume in Anki order (guess → watch → verify), and the page becomes an **evergreen course**: start at post 1, work forward — "learn 500 words with us" as a standing promise. ⌕ Research: is triptych-per-day optimal vs alternatives (single reel + pinned guides, stories-quiz, etc.) — carousel saves-rate is high (saves = strongest algo signal), but posting 3×/day has costs.

## 2. Launch sequence — building the universe

Episodes 1–4 introduce the cast ONE character at a time (order: Bert → Rolf → Kati → Müller, Jayon may reorder). Each character owns an accent COLOR + design accents; their intro row(s) use it. Grid slowly becomes a striped world map of the cast. ⌕ Research: character-intro launch patterns on IG.

## 3. Branding & the word-card design system

- Jayon plans a designer collaboration for: page visual language, word-card templates (front/back), per-character color system, subtitle style. Design ONCE with a human → then templated automation.
- **New pipeline branch (stage 6b): CARD GENERATOR** — 10 front-cards + 10 back-cards per episode, generated from the locked template (Creatomate image templates or HTML-to-image; NOT freeform AI art — text must be pixel-accurate for a language brand). MVP decision pending: triptych in MVP or reel-only first?

## 4. Video requirements added (feed into C2/C3/C5)

- **Subtitles are a hard requirement**: on-screen German dialogue text, styled per brand (⌕ research reels subtitle best practice: word-timed vs line; A1 readers need slower, high-contrast).
- **HOOK rule**: scene 1 of every episode must function as a hook (first 1–2s). ⌕ Research: hooks/retention/IG algorithm — then encode as a story-stage rule + checklist item.
- Target-word emphasis on screen (e.g., color/bold when spoken) — design step with subtitle system.

## 5. Story-stage refinements (feed into C2 design)

1. **Scenario-first generation:** with the 10 words, FIRST choose the situation/scenario (criteria doc to write in C2), THEN cast (1–2 mains + optional cameos), then story. Formats beyond "story": situations, interactions, news-desk bits, festivals, TV-parodies, everyday German scenes — anything **stereotypically German, subtle not caricature**, relatable + funny.
2. **Language realism rule:** sentences must be practical everyday German people actually say (not weird constructions) — pedagogy over plot convenience.
3. **Optional Jayon input step** after words: a free-text "tonight make it about X" parameter into the story LLM (pipeline supports empty = fully auto).
4. **One environment per episode** (Jayon's instinct — also cuts consistency risk + cost). Adopt as default rule, allow exceptions.
5. **Visual identity direction: "Ted in the real world"** — the puppets physically exist in real German locations, real physics, real lighting; uniqueness comes from recurring visual nuances (lighting/tone/framing/elements). This sharpens RESEARCH_art_style_system.md §3 and feeds Jayon's STYLE_SYSTEM draft.

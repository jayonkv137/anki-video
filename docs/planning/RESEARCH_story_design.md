# Research: Story Design for the B2 Story Stage

**Date:** 2026-07-13 · **Question:** given 10 deck words/day, what story design maximizes language learning, comprehension, and retention — for THIS deck?

---

## 1. What the research says

**a) TPRS — the proven story-based teaching method.** Teaching Proficiency through Reading and Storytelling (Blaine Ray, built directly on Krashen's comprehensible input) is the closest existing practice to what we're automating. Its pillars: establish meaning of the target words first *(our Anki recall step already does this!)*, then a **short, personalized, problem-driven mini-story** that uses the targets with **heavy deliberate repetition**, kept fully comprehensible at learner level. Proponents report intermediate proficiency in 60–100 hours vs 400–600 traditional ([Wikipedia/TPRS](https://en.wikipedia.org/wiki/TPR_Storytelling), [BYU methods overview](https://methodsoflanguageteaching.byu.edu/teaching-proficiency-and-reading-through-storytelling-tprs), [Sanako](https://sanako.com/teaching-proficiency-through-reading-and-storytelling-approach)). Our recall→video flow is structurally a TPRS lesson: meaning first, story second.

**b) Exposure frequency — repetition inside the story matters.** Incidental-learning research: gains are largest in the **first few exposures** and decay after; ~3–7 encounters drive most semantic gains, 8–10 for reliable multi-aspect knowledge ([Hulme 2019, Language Learning](https://onlinelibrary.wiley.com/doi/10.1111/lang.12313), [word exposure frequency studies](https://www.tandfonline.com/doi/abs/10.1080/09571736.2016.1244217)). **Informative context beats raw repetition count for meaning-knowledge.** Design consequence: each target word should occur **2–3× in its own scene** in genuinely informative contexts (not echo-repetition) — combined with the Anki card views, the learner hits the effective 4–6 exposure zone on day one.

**c) Bizarreness works — but only when it's funny.** The bizarreness effect (unusual > mundane for recall) is real and **mediated by humor**: bizarre-and-funny beats bizarre-and-weird ([McDaniel et al., delayed recall](https://pubmed.ncbi.nlm.nih.gov/18433519/), [bizarreness effect overview](https://moresapien.org/bizarreness-effect/)). Caveat: emotional memory boosts are weaker in L2 than L1 ([embodiment study](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5362726/)) — humor should live in the *visual situation* (language-independent), not in wordplay the learner can't parse. Design consequence: **quirky, visually comic situations; plain simple language.**

**d) Story grammar — a FIXED narrative skeleton aids L2 comprehension.** Learners comprehend and recall better when stories follow the canonical schema: setting → character → problem → attempts → resolution; the schema must be **consistent across stories** for the comprehension benefit to compound ([story grammar & EFL comprehension](https://www.researchgate.net/publication/292545703_The_Effect_of_Story_Grammar_Instruction_on_EFL_Students'_Comprehension_of_Narrative_Text), [narrative intervention principles, ASHA](https://pubs.asha.org/doi/10.1044/2020_LSHSS-20-00015), [Windward Institute](https://www.thewindwardschool.org/institute-blogs/story-grammar-frames-the-recipe-for-understanding-narrative-text/)). Design consequence: **every daily story uses the same episode template** — predictability is a feature, not a creative failure.

## 2. This deck's specific reality (words 1–625)

- **Batches are semantically random** — the deck is ordered alphabetically *by English* (actor, adjective, adult, April, …). No topic coherence within a day's 10. The story must *manufacture* coherence.
- **Meta/abstract words exist** (das Adjektiv!, 36 Zahlwörter, 7 Pronomen). Escape hatch: **dialogue**. Characters can *say* anything naturally ("Der Lehrer sagt: 'Groß ist ein Adjektiv!'") — speech makes un-filmable words filmable and un-storyable words storyable.
- **Every word ships with a demonstrated usage** (sentence_de/sentence_en) — feed these to the LLM as sense anchors and usage patterns.
- **395/605 are nouns** with articles included — visually concrete, easy scene material; verbs (85) are where video shines per our efficacy research.

## 3. The design this implies (proposed strategy)

1. **Recurring cast + story world** — a fixed protagonist (+ sidekick) in a consistent setting. Manufactures coherence over random words, compounds comprehension (schema), builds parasocial attachment (affective filter ↓), and — decisive side-benefit — **recurring characters are exactly what makes video consistency (B3/B4) tractable and cheaper** (reference images).
2. **Fixed episode template** (story grammar): Scene 1 = setting + spark of a small problem → scenes 2–9 = attempts/developments → scene 10 = resolution. Same skeleton daily.
3. **Word-to-scene assignment is the LLM's creative freedom**: each of the 10 words *owns* one scene (appears 2–3× in it, informatively), but the LLM chooses **which word goes to which scene slot** for narrative flow. The session then presents words in *scene order* (order within a day is pedagogically arbitrary — all are new).
4. **Language constraints (i+1):** A1/A2 vocabulary outside the 10 targets, short sentences (≤ ~10 words), mostly present tense, target-word senses locked by the deck's English gloss + example sentences.
5. **Tone: visually comic, linguistically plain.** Humor in situations (the bizarre-funny memory hook), never in puns/wordplay.
6. **Dialogue as the universal solvent** for abstract/meta words.

## 4. Open design decisions (Jayon's)

- Recurring cast: yes/no, and who are they? (defining the cast is a B3-adjacent creative act)
- Scene order = story order (LLM decides) vs deck order?
- Humor dial: how quirky?
- Repetition target: 2–3× per scene confirmed?

*Sources inline above.*

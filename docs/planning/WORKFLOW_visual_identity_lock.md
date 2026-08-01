# WORKFLOW — Locking the visual identity: the colour law + the location policy

> **Status: METHOD + RECOMMENDATION (2026-07-29), for Jayon to execute.** Answers the two open questions from `AUDIT_visual_identity.md` §3: (1) how to *discover and lock* a colour law that stays consistent while environments change day/night/indoor/outdoor, and (2) how locations should be handled by the agent. **Lighting law = CONFIRMED as ratios + named sources** (Jayon, 2026-07-29).

---

## PART 1 — THE COLOUR LAW

### 1.1 The principle: you cannot lock colours. You lock RELATIONSHIPS.
A fixed palette is physically impossible across a night street, an overcast bike path and a warm bathroom — and forcing one is exactly what produced the "pasted-in" look that got hardcoded lighting deleted on 2026-07-21. What every consistent-looking film actually locks is a **set of relationships** that survive any lighting condition. So the colour law has **four parts**, only one of which is a literal colour:

| Part | What it locks | Changes per episode? |
|---|---|---|
| **1. Character accents** | The cast's own material colours | **NEVER** — they're material properties, already in the CHAR_BLOCKs |
| **2. The relationship rule** | How the world relates to the cast (the load-bearing one) | **NEVER** |
| **3. Named tonal modes** | A small closed set of lighting/colour conditions | You pick ONE per segment |
| **4. The grade** | Shadow tint, highlight tint, saturation ceiling | **NEVER** |

### 1.2 Part 1 — the accents are already decided (extracted from the locked material laws)
| Character | Primary material colour | Secondary accents |
|---|---|---|
| Müller das Brot | golden flaky crust | navy bomber · white beanie · **red** grocery bag |
| Bert das Bier | **amber** liquid + clear glass | white foam · grey hat |
| Rolf die Wurst | reddish-brown translucent casing | jet-black hair + black blazer · silver |
| Kati die Kartoffel | starchy yellow-brown | blonde · **green** ties/lacing · brown leather · white boots |

**The decisive observation: all four characters are WARM EARTH TONES** — gold, amber, red-brown, yellow-brown. They are food; they cannot be otherwise. This isn't a preference, it's a constraint the cast already imposes, and it *dictates* the answer to part 2.

### 1.3 Part 2 — the relationship rule (RECOMMENDED, needs Jayon's yes)
> **"The world is cool and desaturated; the characters carry the warmth. The only saturated colour in frame belongs to a character or to something a character is holding."**

Why this specific rule:
- **It's forced by the cast** — warm characters against a cool world is maximum separation; they pop automatically in every single frame without any per-episode work.
- **It's culturally true** — northern Germany reads grey-blue: overcast skies, wet asphalt, concrete, grey-green, brick. The world we're depicting *is* that colour.
- **It survives every condition** — an overcast street, a night scene, a fluorescent office and a warm bathroom can all be graded cool-and-desaturated relative to the characters. The rule is *relative*, so it never fights the environment.
- **It's checkable** — "is anything in frame more saturated than a character?" is a rule an agent can gate a frame against, exactly as the treatment method demands.
- **It gives you a free dramatic lever** — when you *do* break it (one warm-lit room, a neon sign), it lands hard, because it's the only time.

### 1.4 Part 3 — named tonal modes (the closed set, ~4)
Modes are how the rule instantiates. Naming them makes palette reproducible across hundreds of generations (per the treatment method: *"Mode A — split-toned amber and emerald"*). Proposed starting set — you pick one per segment, and it pairs with the confirmed **ratios + named sources** lighting law:
- **Mode A — Overcast Day** (the default world): flat grey-blue northern daylight, soft shadow, sky as the named source, ~60:40 light-to-shadow.
- **Mode B — Warm Interior**: practical lamps as the only named source, warm pool falling off into cool shadow, ~70:30.
- **Mode C — Night Practical**: sodium/street/shop light as named sources, deep cool shadow, ~30:70 (dark-dominant).
- **Mode D — Hard Sun** (rare): direct sun, crisp shadow edge, ~85:15.

### 1.5 Part 4 — the grade (constant)
One sentence applied to everything, e.g.: *"cool grey-blue shadow tint, neutral-to-warm highlights, environment saturation held low; character material colours exempt from desaturation."*

---

### 1.6 THE DISCOVERY WORKFLOW — how to actually create and lock it

> **⚠ Correction first: do NOT do this in MidJourney.** MidJourney cannot ingest your locked character sheets as identity references. You would produce a beautiful palette you then cannot reproduce with your actual characters — and the whole point is that the palette must hold *with these four*. Do it in **Nano Banana Pro**, which takes the sheets as references (it's already our chosen storyboard model). MidJourney is fine for *pure mood exploration* with no characters, but it cannot be the thing you lock.

**Step 1 — Extract, don't invent.** The accents (§1.2) come from the cast that already exists. Nothing to decide.

**Step 2 — Confirm the relationship rule** (§1.3). One decision, and it's the load-bearing one.

**Step 3 — Gather REAL references, not generated ones.** For "warm characters in a cool, deadpan northern-European world," pull frames from real cinema — real photography is physically coherent in a way generated mood boards aren't, and it gives the agent something to attribute. Candidate reference space: contemporary German realism (*Toni Erdmann*, *Victoria*), Roy Andersson (deadpan static-camera, muted palette, absurdist comedy in mundane settings — arguably the closest tonal cousin to this show), Nordic grading generally. **You collect 10–20 frames; we extract the rule from them, not the reverse.**

**Step 4 — Generate the style plate in Nano Banana Pro.** *One* test scene, with the character sheets attached, rendered under Mode A: e.g. two characters on an overcast German street corner. Then re-render the *same* scene under Modes B/C to confirm the rule holds. The approved Mode-A image becomes **the locked style plate** — the global reference every later generation attaches (this closes the `pending — C1 style-lock` hole).

**Step 5 — Validate (this is also the never-run C1 win condition).** Generate the same character twice, independently, in two *different* environments under the rule. If both read as unmistakably the same character in the same show → the palette + identity system is locked. If not, the drift tells you exactly which sentence to strengthen — the cheapest possible place to learn it.

**Cost:** a handful of Nano Banana Pro generations. This is the highest-leverage spend available, because every one of the ~170 episodes inherits the result.

---

## PART 2 — THE LOCATION POLICY

**The question:** should the agent ask about locations, and should it go find references?

**The answer: ask once, then remember. Do not build reference-searching.**

- **Locations are per-episode variables** (already decided) — but **recurring locations become locked plates**, exactly as the cast is locked. The universe has a finite set of places; they accumulate.
- **The rule the agent follows:**
  - Location **already in `UNIVERSE_STATE`** → pull its locked plate + established description **silently**. Never re-ask, never re-invent. (This is invideo's "update the context once, the agent remembers for every episode.")
  - Location is **new** → the agent **asks you**: what is this place, time of day, weather, what's in it, which tonal mode. Exactly the conversation you described. Then it drafts a description, generates a plate, you approve → **locked into state**, and it never asks again.
- **Reference-finding: no.** Web-searching for location references mid-conversation is slow, adds a whole subsystem, and isn't needed — the palette rule + your description + the character sheets already constrain the look. **But** you can always *attach an image you found yourself*: a plain upload slot on the location, treated as an extra reference. That's a file input, not a research agent. (If it ever proves necessary, it's an easy add later.)
- **Why this is the KISS answer:** the agent gets smarter over time with no extra machinery — by episode 30 it stops asking about the bike path, the apartment and the bakery entirely, because they're locked. The asking naturally decays as the universe fills in.

---

## Execution order
1. Jayon confirms the relationship rule (§1.3) + the mode set (§1.4).
2. Jayon collects 10–20 real reference frames (§ Step 3).
3. We write the **Treatment** with the colour law + the confirmed ratios-and-named-sources lighting law inside it.
4. Generate + lock the **style plate** in Nano Banana Pro (§ Step 4).
5. Run the **two-generation validation** (§ Step 5) → visual identity LOCKED.
6. Location plates then accumulate naturally, one per new location, as the series is made.

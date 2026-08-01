# WORKFLOW — Locking the visual identity: the colour law + the location policy

> **Status: METHOD + FULL EXECUTION GUIDE (2026-07-29, v2).** Answers `AUDIT_visual_identity.md` §3. **Lighting law CONFIRMED as ratios + named sources** (Jayon).
> **v2 corrections (Jayon's push-back, both accepted):** (1) the "northern Germany = grey-blue" justification was **wrong** and is removed — the series moves across all of Germany and the cast is deliberately spread across regions (Rolf/Berlin · Bert/Bavaria · Müller/Hamburg-north · Kati/wherever is best to be seen). (2) A closed set of 4 tonal modes was a **creativity constraint** and is replaced by a **growing mode library**, exactly like the location policy.

---

## PART 1 — THE COLOUR LAW

### 1.1 The principle: you cannot lock colours. You lock RELATIONSHIPS.
A fixed palette across a Bavarian beer tent, a Berlin techno club, a Hamburg harbour and a bathroom is physically impossible — and forcing one is what produced the "pasted-in" look that got hardcoded lighting deleted on 2026-07-21. What consistent-looking films lock is a set of **relationships** that hold under any condition. Four parts, only one of them a literal colour:

| Part | Locks | Changes per episode? |
|---|---|---|
| **1. Character accents** | the cast's own material colours | **NEVER** (they're material properties, already in the CHAR_BLOCKs) |
| **2. The separation rule** | how the environment must behave *relative to* the cast | **NEVER** |
| **3. Tonal modes** | named, reusable lighting/colour conditions | you pick one; **the library grows** |
| **4. The grade** | shadow/highlight tint discipline + saturation hierarchy | **NEVER** |

### 1.2 Part 1 — the accents are already decided (extracted from the locked material laws)
| Character | Primary material colour | Secondary accents |
|---|---|---|
| Müller das Brot | golden flaky crust | navy bomber · white beanie · **red** grocery bag |
| Bert das Bier | **amber** liquid + clear glass | white foam · grey hat |
| Rolf die Wurst | reddish-brown translucent casing | jet-black hair + blazer · silver |
| Kati die Kartoffel | starchy yellow-brown | blonde · **green** ties/lacing · brown leather · white boots |

**The one hard fact:** all four are **warm earth tones** — gold, amber, red-brown, yellow-brown. They are food; they cannot be otherwise. Everything below follows from this, and from nothing else.

### 1.3 Part 2 — the SEPARATION RULE *(corrected)*
❌ **Struck from v1:** *"the world is cool and desaturated"* — justified by "northern Germany reads grey-blue." **That was wrong twice over:** the series roams all of Germany, and a *Bavarian beer garden at golden hour* or a *Berlin club in neon* is inherently warm/saturated. Forcing a cool world would fight the content and flatten exactly the regional variety the cast was designed for.

✅ **The rule that actually survives — it is about HIERARCHY, not hue:**
> **The cast always wins the frame.** In every shot, the characters are the most *present* thing in it — separated from their environment by at least one of: **value** (they sit lighter or darker than what's behind them), **saturation** (their material colour is more saturated than the surrounding surface), or **hue** (the environment sits in a different family from their warm earth tones). **The environment yields; character material colour is never desaturated to match a scene.**

Why this is the right invariant:
- **It's forced by the cast, not by geography** — warm earth-tone characters need separation from *whatever* is behind them; the rule states that requirement without dictating what the world looks like.
- **Every region stays open.** Bavarian beer tent (warm wood/amber world) → separate Bert by **value + saturation**: the wood goes deep and muted, his amber liquid and white foam stay bright. Berlin club (saturated neon) → separate Rolf by **value**: he's a dark silhouette against blown colour. Grey harbour → separation is automatic by **hue**. Same rule, four completely different-looking scenes.
- **It's checkable** — "does any surface out-compete a character for attention?" is something an agent can gate a frame against, which is what the treatment method requires.
- **It preserves the dramatic lever** — deliberately letting the world overwhelm a character (drowned in a crowd, lost in neon) becomes a *choice you can spend*, because the default is the opposite.

### 1.4 Part 3 — tonal modes as a GROWING LIBRARY *(corrected)*
❌ **Struck from v1:** a fixed set of four modes. You're right — that's a creativity cap, and it would have forced every future scene into one of four boxes decided before the series began.

✅ **Modes work exactly like locations:** a mode is **created the first time a condition appears**, then **reused every time it recurs**. The constraint is not *"you may only use these"* — it's *"once we have named a condition, we render it the same way forever."* Consistency without a ceiling.
- A mode records: **name · light sources (named, not moods) · the ratio · shadow tint · highlight tint · saturation note · how the separation rule is satisfied here.**
- The library starts **empty** and fills as the story goes. Episode 1 in a supermarket → create *"Supermarket Fluorescent."* Later, a beer tent → create *"Beer Tent Warm Practical."* A club → *"Club Neon Dark."* Reuse forever after.
- Stored in `UNIVERSE_STATE` beside locations; the Showrunner offers existing modes first and only asks for a new one when the condition is genuinely new.

### 1.5 Part 4 — the grade (constant)
The only global colour discipline: **environment saturation always yields to character material colour; shadows and highlights get a deliberate tint per mode, never a random one; character material colours are exempt from any scene-wide desaturation.** (The *direction* of the tint is a mode property — not a global fixed value.)

---

## PART 2 — THE FULL DISCOVERY WORKFLOW (how to actually execute it)

> **⚠ Tool correction, restated:** don't do this in **MidJourney** — it cannot ingest your locked character sheets as identity references, so it would produce a palette you cannot reproduce with the actual cast. Use **Nano Banana Pro** (already our storyboard model; takes up to 14 refs). MidJourney is fine for characterless mood exploration only.

### STEP 1 — Collect real reference frames (your job, ~1 hour)
**Goal:** 15–25 frames that show *how an environment can be handled so a character stays dominant* — across **different regions, times of day and interiors/exteriors**, because that variety is the point.

**Where to get them**
- **film-grab.com** — free, curated, browsable by film.
- **shotdeck.com** — the best tool for this (searchable by colour, lighting, shot type); paid, worth a month.
- **movie-screencaps.com** — exhaustive per-film caps.
- Real photography for German settings — Unsplash / Flickr for beer gardens, U-Bahn, supermarkets, Altbau interiors, harbours.

**What to look for** — *not* "is it beautiful," but these four things in each frame:
1. **Value** — is the subject lighter or darker than what's behind them?
2. **Saturation** — is the subject the most saturated thing in frame, or is something else competing?
3. **Hue relationship** — what family is the environment in versus the subject?
4. **Shadow tint** — are the shadows neutral, cool, or warm? Highlights?

**Deliberately include hard cases:** a warm interior (does the subject still separate?), a night/neon scene, a bright exterior, a crowded space. Those are the frames that prove a rule rather than flatter it.

**Where to put them:** `resources/style_references/` — filename convention `NN_source_condition.jpg` (e.g. `03_toni-erdmann_office-fluorescent.jpg`). Optionally a one-line note per frame: what you like about it.

**Tonal reference space (suggestions, not prescriptions):** contemporary German realism (*Toni Erdmann*, *Victoria*), **Roy Andersson** (deadpan static camera, absurdist comedy in mundane settings — the closest tonal cousin to this show), Aki Kaurismäki (deadpan + saturated blocks of colour), Jeunet (*Amélie*) if you want more stylisation, Fargo/*Barry* for comedy-in-a-real-world grading. **Bring anything you actually like** — including things nobody would predict; the extraction step works on whatever you give me.

### STEP 2 — Extract the rule from the frames (my job, 1 session)
You hand me the folder. I go through frame by frame and pull out the pattern: the recurring value structure, how saturation is distributed, the shadow/highlight tint discipline, and how each frame achieves subject separation. Output = **the filled colour law** (§1.2–1.5 with real specifics) + a first set of named modes drawn from the conditions your references actually contain. You correct it; we lock it.

### STEP 3 — Write the Treatment (my job)
The colour law + the confirmed **ratios + named sources** lighting law + the existing universal constants (§ `AUDIT_visual_identity.md` §1) get written as one enforceable rule document, with an **exceptions section** (Kati's polish, Bert's minimum identity, the felt-hat rewording) and a **quick-reference card**.

### STEP 4 — Generate the style plate in Nano Banana Pro (your job, ~6–10 generations)

**4a. The test scene.** Use ONE scene that stress-tests everything at once — **two characters + a real environment + a prop + a clear light source**. Recommendation: *Rolf and Müller at a U-Bahn platform / street kiosk, mid-shot, daylight.* Two characters = multi-identity test; contrasting silhouettes (thin cylinder vs round blob) = separation test; an ordinary German exterior = the everyday register of the show.

**4b. What to attach** (NBP takes up to 14): Rolf's **character sheet** + Rolf's **portrait**, Müller's **sheet** + **portrait**. Nothing else yet — the plate is what *creates* the style reference, so it can't attach one.

**4c. The prompt structure** — same architecture as our storyboard skill (reference binding first, style second, scene third, constraints last). Copy-paste template:

```
Using Image 1 (portrait) and Image 2 (multi-angle sheet) as the strict identity
references for Rolf die Wurst, and Image 3 (portrait) and Image 4 (multi-angle
sheet) as the strict identity references for Müller das Brot. Lock their exact
facial geometry, physical textures and wardrobe from these references only,
without altering them.

STYLE: High-end cinematic live-action cinematography integrated with
photorealistic CGI characters, macro-level tactile materiality, real physical
presence in a real-world environment. Shot on a 35mm anamorphic lens, eye-level
framing, locked-off camera on a heavy tripod, natural motion blur, subtle lens
halation and slight edge fringing.

COLOUR & LIGHT: [<-- the mode being tested: named light sources + the ratio +
shadow tint + highlight tint]. The characters are the most present thing in
frame — the environment is held back in value and saturation so their material
colours dominate. Character material colour is never desaturated.

SCENE: [environment, time of day, weather]. Rolf die Wurst stands left of frame
[action]; Müller das Brot right of frame [action]. 9:16 vertical.

NEGATIVE: cartoon rendering, 2D illustration, 3D animated movie style, Pixar
style, Dreamworks style, plastic skin, glossy CG, hyper-smooth interpolation,
floating objects, miniature scale, stop-motion, felt, clay, puppetry, visible
seams, text, watermarks, dynamic camera sweeps, impossible physics.
```

**4d. The runs.**
- **Run 1** — the scene in its natural daylight condition. Generate **3–4 variants**; pick the one that best *is* the show.
- **Runs 2–3** — the **same scene**, same prompt, only the COLOUR & LIGHT block swapped (a warm interior; a night practical). **This is the actual test:** if the characters still read identically and still dominate, the separation rule works and is not hue-dependent.
- **Run 4** — a **different environment + different two characters** (e.g. Bert and Kati in a beer garden). Proves it generalises across region and cast.

**4e. How to judge** — do not ask "is it pretty." Ask, in order:
1. Do both characters match their sheets exactly (geometry, texture, wardrobe)?
2. Does each character separate from the background — by value, saturation, or hue?
3. Do the materials read (crust displacement, casing translucency, glass IOR, foam scatter)?
4. Does anything on the AVOID list appear (plastic sheen, cartoon edges, seams)?
5. Is it plausibly the *same show* as the other runs?

**4f. Lock it.** The winning Run-1 image → `resources/style_plate.png`, registered as the global style reference every later generation attaches. This closes the `pending — C1 style-lock` hole. Also save the Run-2/3 winners as **mode plates** in the mode library.

### STEP 5 — Validate (the C1 win condition, never yet run)
Generate the **same single character twice, independently, in two different environments** under the locked rule and the style plate. Both must read as unmistakably the same character in the same show. **Pass** → the identity + colour system is locked, and real production can start. **Fail** → the drift tells you precisely which sentence of the treatment is too weak, which is the cheapest possible place to learn it.

### STEP 6 — Lock into canon (my job)
Treatment + colour law + mode library → written into canon, hash-pinned in `REGISTRY.md`, `global_aesthetic_rules` deleted from the screenplay schema (the treatment replaces it), the storyboard path fixed to substitute canon properly, and the mode library + locations seeded into `UNIVERSE_STATE`.

**Total cost:** ~10–15 Nano Banana Pro generations. Every one of the ~170 episodes inherits the result.

---

## PART 3 — THE LOCATION POLICY

**Ask once, then remember. Do not build reference-searching.**
- **Known location** → the agent pulls its locked plate + established description **silently**. Never re-asks, never re-invents.
- **New location** → the agent **asks you**: what is this place, time of day, weather, what's in it, which tonal mode (offering existing modes first). It drafts a description, generates a plate, you approve → **locked into `UNIVERSE_STATE` forever**.
- **Reference-searching: no.** Web-searching mid-conversation is slow and a whole subsystem for little gain — the separation rule + your description + the character sheets already constrain the look. **But** you get an **upload slot**: any reference *you* find can be attached to the location as an extra reference. That's a file input, not a research agent.
- **Why this is KISS:** the asking decays on its own. By episode 30 the agent no longer asks about the bike path, the apartment or the bakery — they're locked.

---

## Execution order
1. **Jayon confirms** the separation rule (§1.3) + the growing-mode-library approach (§1.4).
2. **Jayon collects** 15–25 reference frames → `resources/style_references/` (Step 1).
3. **Claude extracts** the colour law + first modes (Step 2) → Jayon corrects → lock.
4. **Claude writes** the Treatment (Step 3).
5. **Jayon generates** the style plate + mode plates in NBP (Step 4).
6. **Jayon runs** the two-generation validation (Step 5).
7. **Claude locks** it all into canon + state (Step 6). → Visual identity DONE; production can begin.

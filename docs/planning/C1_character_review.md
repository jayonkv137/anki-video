# C1 Character Review — Die Brotzeit-Bande (Claude's verdict, 2026-07-14)

Reviewed: `resources/Characters-Main-Sheet.md` + main reference images of all four characters, against production methodology for consistent AI characters (cast contrast, material gags, reproducibility, canon hygiene).

## Overall verdict: this cast is GOOD — production-grade thinking

**What's working (and why it matters):**

1. **The behavior bible is the strongest asset.** Belief+wound per character, voice checks ("if a line could be swapped between characters, rewrite it"), vocabulary-domain ownership per character, the comedy matrix, the stereotype safety rail — this is exactly the "definite rules foundation" the automated pipeline needs. Rule 2 (words assigned to the domain owner) and Rule 4 (end on the human beat) are genuinely clever pipeline constraints.
2. **Cast designed by contrast — textbook.** Silhouettes: round blob (Brot) / tall thin cylinder (Wurst) / hourglass (Kartoffel) / square mug with handle (Bier). Eye signatures all distinct (wide blue googly / heavy-lidded deadpan / sultry side-glance / bulging amber). Any character is identifiable from silhouette alone — the single best predictor of surviving AI drift.
3. **Real material gags everywhere:** the zipper carved into crust with exposed crumb (Brot), the dirndl carved from her own peel (Kartoffel), casing-knot toes + salami-marbling tattoos-on-skin (Wurst), foam as Einstein hair + moustache, glass arm as mug-holder, standing on beer coasters (Bier). These are characters, not objects in clothes.
4. **Puppet-photography realism** with matte organic textures (bread crumb, salami marbling, felt tongue) — the right style system, and the "deliberate, crafted" look that beats the slop competition.

## The two blockers (fix BEFORE any further generation)

**B1 — RESOLVED 2026-07-15.** Canon names FINAL: **Rolf die Wurst · Bert das Bier · Kati die Kartoffel · Müller das Brot** (grammar corrected per Jayon's language-accuracy principle: das Bier not Der Bier; die Wurst singular not die Wurste; lowercase articles; Müller with umlaut in text, ASCII 'Muller' in filenames). All folders, files, and docs renamed/synced in one commit. Original finding:  Main sheet says **Kurt** die Wurst / Professor **Sepp** (Bier) / **Fiete** das Brot; folders say **Rolf** die Wurste / **Bert** Der Bier / **Müller** Das Brot; Kati's image files are named **Pam-***. Grammar drift too: "Bert **Der** Bier" (das Bier), "die Wurste" (die Würste). For a pipeline that assembles prompts from canon files, ONE name per character must be law. → Jayon picks final names; we then rename folders/files and update every doc in one commit.

**B2 — Text errors rendered ON canon characters.** The Wurst's chest tattoo reads "DIE WURSTE" — missing umlaut (correct: WÜRSTE). For a German-teaching brand, native speakers will spot rendered spelling errors instantly and it undercuts the whole "deliberate quality" positioning. Fiete's bag text "ERSTMAL ZU BROT" should also be verified as intentional idiom-play vs error. → Fix via region-edit on the reference images (not full regeneration), or canonize deliberately as an in-world joke — but decide, don't drift.

## Watch-items (not blockers)

- **Kati style outlier — Jayon's ruling 2026-07-15: KEEP as creative choice / character trait** (her polish IS the character). Original observation:  smoother/more CG-doll render (glossy lips vs the matte rule), and the most humanoid proportions in the cast. Most human-like = most drift-prone in video + slight castmate mismatch next to the chunkier puppets. Options: (a) one cohesion pass rendering her in the exact puppet-photography system of the other three; (b) accept as her "polished" character trait. Jayon's call in the art-style step.
- **Bert props — Jayon's ruling 2026-07-15: identity core = beer-glass structure + foam hair (+ some ensemble); individual props (mini-mug etc.) may drop per scene.** Original observation:  (hat, feather, glasses, mini-mug, coasters). Fine for hero shots; for video consistency consider defining a "minimum Bert" (which props are identity-critical — suggest: foam hair + moustache + glasses) so scenes don't need all of them every time.
- **4 characters = 4× consistency risk (risk R1).** The bible's max-2-per-story rule already helps. For the MVP pipeline proof, consider launching with the 2 most render-stable characters (Bier and Brot — simplest silhouettes, strongest material identity) and introducing the other two once the pipeline holds. Jayon decides.

**Also noted 2026-07-15:** turnaround/reference sheets already exist in the character folders (Profiles/sheet images) — item 4 below is partially done; verify coverage (esp. back views) during the style step. Characters remain non-final until story drafting begins (Jayon).

## What C1 still needs (the remainder)

1. **Naming decision** (B1) → rename + one canon-sync commit.
2. **Text fixes** (B2) → region edits on refs.
3. **Art-style sheet / style board** (Jayon announced he's making this): the ONE style system paragraph every video prompt will carry — realism level, lighting, background world, camera feel, matte rules. The four mains already imply it; it needs to be written and locked.
4. **Turnaround + expression sheets** per character (front/side/back views, 3 expressions) — needed by C3 for image-to-video anchoring; back views especially (pure invention risk).
5. Then C1's win condition: regenerate each character from bible+refs twice → recognizably identical.

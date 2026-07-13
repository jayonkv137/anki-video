# MVP Build Plan — ordered sub-goals

**Status:** DRAFT — locked when Jayon confirms · **Created:** 2026-07-13
**Rule:** one phase at a time; a phase is done when its **win condition** is demonstrated, not when code exists. Each phase names its **learning objective** (Jayon must be able to explain the concept afterward) and its **just-in-time provisioning**. Design-heavy phases start with their own mini design step (research → try → decide), per the plan-as-we-go method.

---

## B0 — Engine heartbeat

Get the machine room running: Docker on the Mac, n8n container with persistent volume, one trivial scheduled workflow (cron → fetch something → notify).
- **Win:** a cron-triggered n8n workflow runs successfully on schedule, and survives a container restart.
- **Learn:** what Docker is (images/containers/volumes), n8n anatomy (nodes, triggers, executions).
- **Provision:** Docker Desktop. Cost: €0.

## B1 — Word source

Supabase project; `words` table; import the 625-deck export (word, translation, order); the "next 10 unseen words" query; n8n reads it.
- **Win:** the n8n workflow fetches exactly the right 10 words, and the next run fetches the *following* 10.
- **Learn:** relational basics (tables, rows, keys), what Supabase is, n8n credentials.
- **Provision:** Supabase (free tier). Cost: €0.

## B2 — Story stage

Prompt design for story + 10-scene script as strict JSON (scene = dialogue/narration in German + English visual description); validate → retry loop in n8n.
- **Win:** 3 consecutive runs on different word sets produce valid JSON with all 10 words genuinely used; Jayon (B1 German) spot-checks the German is level-appropriate.
- **Learn:** prompt engineering for structured output (few-shot, priming), JSON schema, the validate→retry pattern — the core automation skill.
- **Provision:** Anthropic API key. Cost: pennies/run.

## B3 — Video design stage ⭐ (the deferred decision + the creative challenge)

The dedicated design step from PRD §6: research → generate 2–3 sample scenes per candidate (Gemini Omni / Kling+ElevenLabs / Veo, + one cheap open model as baseline) → judge against the locked criterion (consistency > narration control > cost) → **decide model, style template, and scene composition** (subtitles? word on screen?). Update Engineering Requirements with the decision.
- **Win:** one sample scene Jayon is genuinely happy with + a written style template (prompt prefix, voice, composition rules) that produced it twice.
- **Learn:** video-gen APIs (async submit → poll → download), image-reference consistency techniques, TTS/SSML pacing.
- **Provision:** fal.ai; Google AI and/or ElevenLabs as tested. Cost: ~€10–20 of experiments — budget it deliberately.

## B4 — Scene pipeline

Wire B2's script through B3's chosen model: n8n loop over 10 scenes → generate (+ narration if separate TTS) → upload to Supabase Storage.
- **Win:** one full day's 10 scene videos generated and stored, hands-off, from one trigger.
- **Learn:** n8n loops (Split In Batches), handling long-running async jobs, object storage.
- **Provision:** nothing new.

## B5 — Assembly

Creatomate template: 10 scenes (+ audio overlay if applicable) → combined story video, stored alongside.
- **Win:** a watchable ~60–80s story video where scenes flow as one narrative.
- **Learn:** template-based rendering (composition JSON: tracks, clips, timing).
- **Provision:** Creatomate (verify pricing). Cost: ~cents/video.

## B6 — Session app

React + Vite PWA: today's session from Supabase → word card → recall → reveal + self-grade (written back) → scene video → story finale.
- **Win:** Jayon completes a real session on his phone, and his grades appear in the database.
- **Learn:** React state for a flow, Supabase JS client, HTML5 video, PWA install.
- **Provision:** Vercel (free) at deploy time.

## B7 — Daily automation (= MVP done)

The full chain on a nightly cron: fetch words → story → scenes → assembly → session row; failure notification to Jayon; "tomorrow is ready" guaranteed.
- **Win:** two consecutive mornings, untouched: open the app, that day's session is there. **This is the MVP definition of done.**
- **Learn:** error workflows in n8n, idempotency (safe re-runs), monitoring an autonomous system.
- **Provision:** nothing new (Mac-awake constraint accepted; upgrade trigger documented).

---

**Sequencing logic:** engine → data → text → (design!) → media at scale → assembly → consumption → autonomy. Each phase produces something demonstrable and nothing depends on a later phase. B3 sits deliberately *before* mass generation so style is designed, not inherited from defaults.

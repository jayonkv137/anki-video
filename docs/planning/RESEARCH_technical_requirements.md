# Research Output — Technical Requirements (evidence behind the decisions)

**Date:** 2026-07-13 · Companion to `PROJECT_SPEC_Engineering_Requirements.md` (which holds the decisions; this holds the proof).

## #3 Story LLM
- Claude family leads writing/instruction-following, July 2026: top Arena Elo 1508 — [BenchLM best-LLM-for-writing](https://benchlm.ai/blog/posts/best-llm-writing); highest prose scores in [novel-writing comparison](https://www.inkfluenceai.com/blog/best-ai-models-for-novel-writing-2026).
- JSON: OpenAI Structured Outputs = guaranteed schema; Claude reliable via prompting/priming; Gemini responseSchema middle ground — [structured-output guide 2026](https://crazyrouter.com/en/blog/ai-structured-output-json-mode-guide-2026).
- Gemini 3.1 Pro value pick ~$2/$12 per M tokens — [tech-insider comparison](https://tech-insider.org/claude-vs-chatgpt-vs-gemini-2026/).
- **Decision logic:** constraint-following + prose are scarce; JSON solvable in-workflow (validate→retry). → Claude Sonnet 5.

## #4/#5 Video + audio (deferred to prototyping; shortlist evidence)
- Kling 3.0 multi-shot storyboard: consistency across cuts — [Elser AI](https://www.elser.ai/blog/kling-ai-vs-veo-2026), [WaveSpeed Kling 3.0 Omni](https://wavespeed.ai/blog/posts/kling-3-0-omni-explained/); ~$0.029/s on fal.ai — [3DAI Studio](https://www.3daistudio.com/blog/best-ai-video-generator-2026).
- Veo 3.1: only model with 48kHz synced dialogue — [buildfastwithai](https://www.buildfastwithai.com/blogs/seedance-2-5-vs-veo-3-1-vs-kling-3-0-best-ai-video-2026); pricing sources conflict ($0.03–0.40/s) — verify.
- Gemini Omni (I/O May 2026): unified multimodal, 10s clips w/ native audio, conversational memory across generations — [vo3ai](https://www.vo3ai.com/gemini-omni), [TNW](https://thenextweb.com/news/google-gemini-omni-flash-video-model-io-2026), [review](https://www.buildfastwithai.com/blogs/gemini-omni-google-ai-video-model-review). API was "weeks away" at announcement — verify availability + German + pacing control.
- ElevenLabs German: near-human ratings, compound-word handling, 100+ voices — [ElevenLabs](https://elevenlabs.io/text-to-speech/german), [That Works Media](https://thatworksmedia.com/en/which-ai-voice-over-tools-exist-in-german/); ~$0.30/1k chars beyond plan — [pricing breakdown](https://www.cekura.ai/blogs/elevenlabs-pricing).
- Pedagogical constraint driving the split: CI narration must be slow with deliberate pauses (SSML) — native video-model audio offers little pacing control.
- ComfyUI ruled out for MVP: Mac can't run video diffusion; cloud-GPU ops orthogonal to goals; fal.ai serves the same open models (Wan ~$0.50/10s — [Atlas Cloud pricing](https://www.atlascloud.ai/blog/guides/cheapest-ai-video-generation-api-2026)). Revisit trigger documented in spec.

## #6 Assembly
- Creatomate: template JSON → MP4, official n8n tutorial — [Creatomate + n8n](https://creatomate.com/blog/how-to-automate-video-creation-with-n8n). FFmpeg = v1 learning swap.

## #1/#2/#7–#10 (no web research needed — settled ground)
- Python = AI-ecosystem default; n8n chosen for learning value (Jayon's call); Supabase/React/Vercel/Docker rationale in the spec doc. Supabase + SvelteKit/FastAPI stack pre-validated in `Context Docs From other chats/# The Comprehensible Engine.md` §8.

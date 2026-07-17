# **Advanced Prompting Architectures for Multimodal Video Synthesis: Optimizing Seedance 2.5 and Gemini Omni Flash for Screenplay Conversion**

## **The Paradigm Shift in Generative Cinematography**

The landscape of generative artificial intelligence has fundamentally transitioned from single-modality text-to-video extrapolation to native, multimodal joint generation. With the introduction of ByteDance’s Seedance 2.0 (and its subsequent 2.5 update) alongside Google’s Gemini Omni Flash, the industry standard has shifted toward models capable of utilizing a unified attention space to process text, image, video, and audio simultaneously1. This structural evolution results in highly controllable cinematic outputs featuring persistent character identity, precise camera choreography, and native audio synchronization2.  
For production studios and creative professionals, the challenge is no longer bound by the model's physical understanding of the world, but rather by the syntactic precision of the instructions it receives. The objective of this report is to exhaustively analyze the optimal prompting strategies, syntactic frameworks, and reference-mapping architectures required to extract maximum fidelity from Seedance 2.5 and Gemini Omni Flash. Furthermore, this analysis establishes the foundational logic necessary to construct a highly specialized "Claude Skill"—an automated, agentic workflow capable of parsing a standard cinematic screenplay, synthesizing predefined character sheets alongside specific style references, and outputting the mathematically optimized prompts required to maintain absolute character and stylistic consistency across an entire production sequence6.

## **Architectural Foundations and Operational Constraints**

To engineer effective prompts for professional cinematic workflows, one must first deconstruct how these specific models weight input tokens and process multimodal references. The architectural differences between Seedance 2.5 and Gemini Omni Flash dictate entirely different prompt engineering methodologies, necessitating distinct translation matrices when adapting a screenplay.

### **The Seedance 2 Ecosystem**

Developed by ByteDance, Seedance 2 operates on a unified audio-video joint generation architecture that accepts up to twelve reference assets in a single forward pass: up to nine images, three video clips (totaling 15 seconds), and three audio tracks2. The introduction of Seedance 2.5 in July 2026 expanded the model's capabilities to generate native 30-second clips utilizing up to 50 multimodal references, extending to three minutes in beta modes, while introducing targeted local editing features to alter specific regions without regenerating the entire temporal sequence1.  
Seedance 2 processes natural language prompts with a strict hierarchical weighting system. The inference engine prioritizes the first 20 to 30 words of the text prompt, utilizing this initial string to lock the primary subject and core action before processing subsequent stylistic or environmental data11. The model struggles with "adjective stacking" (e.g., "beautiful, stunning, gorgeous lighting"), which dilutes the attention mechanism; it favors single, concrete, highly descriptive terms within a hard token cap of 3,000 characters11. Furthermore, Seedance establishes a strict functional hierarchy among multimodal inputs: audio files dictate rhythm and phoneme-level lip-sync, video files transfer motion trajectories and camera behavior, and image files lock character identity and spatial aesthetics2.

### **Google Gemini Omni Flash**

Gemini Omni Flash, powered by Google's native multimodal architecture, represents a stark departure from traditional batch-generation pipelines. Operating at highly cost-efficient rates via the Gemini API, it generates 720p clips at 24 frames per second with a maximum duration of 10 seconds15.  
The defining characteristic of Gemini Omni Flash is its deep integration with Google’s Interactions API, which transitions video generation from a stateless transaction to a stateful, conversational editing process5. Rather than relying on a single, monolithic prompt to achieve flawless execution on the first attempt, Gemini Omni Flash retains the session history via a previous\_interaction\_id17. This permits the prompter to generate a base scene and issue subsequent natural language commands (e.g., "Change the subject's jacket to deep green," or "Add heavy rain") without altering the established character identity, spatial lighting, or temporal continuity of the original clip19.

### **Comparative Specifications and Input Boundaries**

Understanding the operational boundaries of each model is critical before designing automated prompt-generation systems. The following table delineates the core constraints and capabilities of both models.

| Specification Parameter | Seedance 2.5 | Gemini Omni Flash |
| :---- | :---- | :---- |
| **Maximum Native Resolution** | 1080p (Native 4K available via Pro tier)21 | 720p15 |
| **Maximum Output Duration** | 15s standard, 30s native in v2.5, 3m in beta1 | 10s maximum15 |
| **Multimodal Asset Limits** | Text, up to 9 Images, 3 Videos, 3 Audio2 | Text, up to 10 Images, Video (up to 10s for editing)15 |
| **Workflow Paradigm** | Multi-reference synthesis via @ tagging and explicit variable binding14 | Stateful conversational editing via Interactions API with iterative refinement5 |
| **Audio Integration** | Native generation, phoneme-level lip-sync, multi-track audio-visual synchronization2 | Native generation and sync derived from text cues or reference files19 |
| **Target Strengths** | Cinematic control, complex multi-character physics, hyper-realistic human motion13 | High-speed workflow, intelligent stateful editing, contextual world knowledge5 |

## **Architecting Absolute Character and Style Consistency**

The paramount objective when adapting a predefined screenplay is maintaining the visual integrity of specific characters, spatial environments, and artistic styles across dozens of individual scene generations. Consistency failure—often referred to as "temporal drift" or "identity hallucination"—occurs when the model's latent space is granted too much interpretive freedom between prompts.  
In the specific scenario where a production utilizes two distinct images for overarching artistic style influence, alongside multiple pre-designed character sheets, the prompting methodology must bind these assets to the text with mathematical precision.

### **Seedance 2: Explicit Tagging and Semantic Variable Binding**

Seedance 2 achieves character and style consistency through a highly structured syntax combining natural language definitions with explicit file tagging. When a user uploads a character sheet or a style reference, the platform assigns it an internal label (e.g., @Image1). However, simply placing @Image1 arbitrarily into a prompt is insufficient for complex, multi-subject scenes and will result in attribute blending.  
The optimal methodology requires explicit role binding using the Define syntax at the absolute beginning of the prompt. By instructing the model to "Define the woman wearing a red dress in @Image1 as Subject 1," the prompt establishes a locked semantic anchor27. In multi-character scenarios, this prevents the model from conflating features. A rigorous Seedance prompt establishes consistency by explicitly categorizing each asset's role prior to describing the action14.  
For the specific scenario involving two style images and character sheets, the reference mapping must be declared as follows: The prompt must explicitly designate @Image1 and @Image2 as the overarching environmental and aesthetic anchors. The prompt should state: "Use @Image1 and @Image2 as the global stylistic reference, matching the cinematic lighting, color palette, and atmospheric textures." Subsequently, the characters must be bound: "Define the tall man in @Image3 as John, and define the woman in @Image4 as Sarah"27.  
Throughout the remainder of the prompt, the terms "John" and "Sarah" must be used with absolute consistency27. Furthermore, "prompt mirroring" is critical to eliminating drift across different shots. The text describing a character must remain character-for-character identical across every generated clip33. Even minor variations (e.g., changing "dark jacket" in scene one to "dark jacket, slightly open" in scene two) signal to the model that it is permitted to alter the character's latent representation, leading to visual inconsistencies33.

### **Gemini Omni Flash: Source Declarations and Stateful Anchoring**

Gemini Omni Flash utilizes a different syntactic approach to image anchoring, relying on prefix tags paired with natural language instruction suffixes. Within the prompt, media assets must be explicitly assigned roles using specific bracketed tags to separate initial frames from stylistic or subject references34.  
The most effective syntax relies on the \<FIRST\_FRAME\> and \<IMAGE\_REF\_N\> tags. To enforce character and style consistency without forcing the assets into the literal first frame of the generated video, the prompter must declare the images as references and append specific guiding instructions34.  
For the specific scenario with two style images and character sheets, the optimal structure involves declaring the sources at the top of the prompt using an array configuration: \[\# References \<IMAGE\_REF\_0\>@Image1 \<IMAGE\_REF\_1\>@Image2 \<IMAGE\_REF\_2\>@Image3\]34. This must be followed immediately by a natural language suffix reinforcing the constraint: "Use Image 1 and Image 2 strictly as aesthetic references for the visual style, color grading, and lighting of the entire scene. Use Image 3 as a reference for the male character's identity. The images should not be used as literal initial frames"34.  
However, Gemini's greatest asset for long-form narrative consistency is its API statefulness. When translating a scene requiring multiple actions within the same environment, the optimal approach is to generate the master video, retain the previous\_interaction\_id, and issue conversational edits for subsequent narrative beats (e.g., "Keep the character and lighting identical, but change the object in her hand to a phone")17. The model executes the edit while guaranteeing that the underlying character identity and spatial environment remain mathematically identical to the previous generation, vastly reducing the identity drift associated with generating entirely new clips from scratch5.

## **Camera Language: The Grammar of AI Cinematography**

In AI video generation, camera movement is not merely a stylistic flourish; it is a fundamental control mechanism that dictates how the model renders three-dimensional space, calculates parallax, and enforces physical boundaries. A prompt lacking specific camera instructions defaults to a static medium shot, which frequently results in localized hallucinations as the AI struggles to impart dynamic energy to a stationary frame35. Directing the virtual camera requires exact terminology that translates the empathy mechanics of a screenplay into geometric motion.

### **Seedance 2 Cinematic Techniques**

Seedance 2 responds exceptionally well to 14 specific cinematic techniques. The model separates camera direction into three distinct parameters: Movement, Speed, and Stability36. The syntax Camera: \[move\] \+ \[speed\] \+ \[subject lock\] is universally effective for minimizing generation artifacts36.  
When a screenplay calls for an emotional realization or a moment of intimate discovery, the optimal command is a "slow dolly in" or "gentle push-in" combined with "smooth gimbal" stability36. This forces the AI to maintain a steady focal point on the character's face, significantly increasing render quality on facial micro-expressions. For high-action pursuit sequences, "tracking shot following \[Subject\], handheld documentary style, subtle camera shake" instructs the model to generate rapid background parallax while retaining the subject securely within the frame36.  
Advanced structural techniques involve compound movements. For establishing shots, the "Rise \+ Tilt \+ Pan" combination prompts the model to generate sprawling depth, revealing a landscape or cityscape progressively across the Z and Y axes37.

| Cinematic Intent | Screenplay Context | Optimized Seedance Camera Syntax |
| :---- | :---- | :---- |
| **Intimacy / Revelation** | Character discovers a critical clue or expresses deep emotion. | Camera: slow dolly in, smooth gimbal, steady motion, tight focus. \[cite: 36, 38\] |
| **Action / Pursuit** | Character flees through a crowded environment. | Camera: tracking shot following \[subject\], handheld documentary style, subtle shake. \[cite: 36\] |
| **Establishing Reveal** | Introducing a new, massive location. | Camera: slow pan left to right, tripod stable, wide angle lens feel. \[cite: 12, 36\] |
| **Disorientation / Panic** | Character experiences psychological distress. | Camera: Dolly Zoom effect, maintaining sharp focus on subject, background warping. \[cite: 37\] |
| **Scale / Dominance** | Emphasizing the power or size of a subject. | Camera: Low angle shot, smooth tracking, looking up at subject. \[cite: 37\] |

If the model exhibits unwanted optical distortion, the prompter must apply negative constraints such as "no zoom" and distance locks like "maintain subject size in frame." Seedance 2 frequently conflates physical dolly movements with focal length zooming when left unconstrained, which compromises the integrity of background textures36.

### **Gemini Omni Flash Camera Direction**

Gemini Omni Flash operates optimally when the camera movement is organically tied to the action description rather than separated into sterile, technical brackets. The official prompt guidelines explicitly discourage vague statements such as "make it move"18. Instead, the camera direction should read as a cohesive narrative production brief.  
To achieve a seamless cinematic look, the prompt must explicitly state the desired continuity constraint. Including phrases such as "In a single unbroken scene," "In a single continuous shot," or "No scene cuts" is vital, as Gemini Omni Flash's default behavior is to attempt to craft an engaging narrative by spontaneously inserting AI-generated cuts and varying shot angles within its 10-second window31. The model excels at executing fluid transitional instructions like, "The camera slowly pulls back to a medium shot, then gently orbits left," seamlessly transitioning between physical camera states while tracking the subject39.

## **The Screenplay-to-Prompt Translation Matrix**

The core objective is establishing the definitive logic required to convert a standard screenplay—complete with sluglines, complex action descriptions, and dialogue—into the exact prompt syntax demanded by these advanced models. A standard screenplay implies subtext, off-screen action, and multi-step choreography crammed into a single block of text. AI video models cannot interpret subtext; they require atomic visual beats. The conversion process requires dissecting the screenplay into distinct spatial and temporal layers27.

### **Translating for Seedance 2**

Seedance 2 requires a highly structured, layered prompt formula: Subject \+ Action \+ Camera \+ Environment \+ Lighting/Mood \+ Style \+ Quality Constraints11.  
When parsing a screenplay, the conversion logic must adhere to the following rigorous principles:

1. **Isolation of the Atomic Action:** Seedance 2 operates on a strict "one-action rule." If the screenplay dictates, "John walks to the table, picks up the glass, turns around, and waves," the AI will inevitably fail to render the sequence coherently, resulting in temporal morphing or ignored actions14. The conversion must split this into sequential shot prompts or distill it into the single most important action beat for that specific clip12.  
2. **Multimodal Asset Mapping:** If the screenplay references a specific character and style, the prompt must insert the Define \<Subject\_N\> syntax and map it to the corresponding character sheet images, while reserving designated images for environmental styling.  
3. **Dialogue and Audio Integration:** If dialogue is present in the scene, the spoken words must be enclosed in curly brackets {} to trigger the model's phoneme-level lip-sync capabilities (e.g., says {I am not afraid anymore})27. Environmental sounds are enclosed in angle brackets \<\> (e.g., \<rain falling heavily on the pavement\>)27.  
4. **Sequential Storyboarding:** For multi-shot sequences within a single generation, the prompt must utilize a timeline-based storyboard syntax: Shot 1: \[description\] Shot 2: \[description\] to force the model to execute a montage27.

**Definitive Prompt Template (Seedance 2):** \[Reference Assignments\] Use @Image1 and @Image2 as the global stylistic reference for lighting, color palette, and cinematic atmosphere. Define the woman in @Image3 as Sarah. Define the man in @Image4 as John.  
\[Shot Structure\] Shot 1: 0-5s. Sarah walks briskly down the hallway. Shot 2: 5-10s. John turns around, looking surprised. He says {What are you doing here?}  
\[Camera and Spatial Controls\] Camera: Shot 1 utilizes a smooth tracking shot from behind. Shot 2 utilizes a medium close-up, tripod stable. Environment: A dimly lit corporate hallway, fluorescent lights buzzing. Style: Cinematic realism, 35mm film quality, high detail texture, muted color grading. Audio: \<ambient office hum, footsteps clicking on linoleum\> Constraints: Consistent character identity, no extreme zooming, stable motion, highly realistic physics.

### **Translating for Gemini Omni Flash**

Gemini Omni Flash prompts must be written as cohesive, highly detailed production briefs prioritizing fluid natural language over rigid bracketed formulas. The ideal structure follows: Subject \+ Motion \+ Camera \+ Audio \+ Format19.  
The conversion logic for Gemini must adhere to the following principles:

1. **Concurrent Asset and Physics Integration:** Gemini handles image anchoring and physics holistically. The prompt must explicitly state the role of the audio in plain language (e.g., "Audio: pan sizzle, soft kitchen ambience, and a voice saying 'Service.'")19. Furthermore, Gemini possesses a robust understanding of real-world physics (gravity, fluid dynamics, kinetic energy)3. The prompt must direct the physics explicitly based on the screenplay's demands (e.g., "water dripping from the needles," "heavy droplets hitting leaves")19.  
2. **Temporal Resolution:** Because Gemini does not support video extension or interpolation, every action converted from the screenplay must logically resolve within the strict 3 to 10-second limit15.  
3. **Stateful Edits for Scene Continuation:** Rather than scripting a massive multi-shot prompt, the screenplay translation for Gemini should focus on establishing the perfect initial shot, utilizing the Interactions API to prompt subsequent beats through natural language edits5.

**Definitive Prompt Template (Gemini Omni Flash):** \[\# References \<IMAGE\_REF\_0\>@Image1 \<IMAGE\_REF\_1\>@Image2 \<IMAGE\_REF\_2\>@Image3 \<IMAGE\_REF\_3\>@Image4\] Use Image 1 and Image 2 strictly as aesthetic references for the visual style and moody color grading. Use Image 3 as a reference for the female character (Sarah) and Image 4 as a reference for the male character (John). These images should not be used as literal initial frames.  
A young woman (Sarah) walks briskly down a dimly lit corporate hallway. She stops suddenly as a man (John) steps out from a doorway. John turns, looking surprised, and speaks.  
Camera: A single continuous shot with no scene cuts. The camera tracks smoothly behind Sarah, then orbits to a medium two-shot as she stops. Lighting: Flickering overhead fluorescent light, soft shadows, photorealistic cinematic grade matching the style references. Audio: Ambient office hum, sharp footsteps clicking on linoleum, and a male voice saying 'What are you doing here?' Format: 10 seconds, 16:9.

## **Architecting the "Claude Skill" Workflow**

To automate this highly complex translation process, a programmatic "Claude Skill" must be developed. A Claude Skill (or Agent Skill) is a modular capability, defined by a SKILL.md file, which intercepts a user's intent and applies rigorous formatting, context tracking, and execution logic to the output6.  
For the purpose of converting screenplays into optimal AI video prompts tailored for Seedance and Gemini, the Claude Skill must operate as a multi-stage deterministic pipeline. The skill enforces the rules of prompt engineering, preventing the user from submitting overly complex actions or omitting critical spatial directions.

### **Skill Definition and System Instructions**

The SKILL.md file must begin with stringent persona and operational directives. The AI agent must be instructed to act as a hybrid cinematic director and AI prompt engineer. It must be programmed to recognize the target model based on the user's request and automatically route the processing logic to the corresponding syntactic template7. The architecture relies on progressive creation, where the context of previous episodes or shots is retained to ensure continuity45.

### **Stage 1: Ingestion and Asset Mapping**

The skill first parses the provided screenplay scene, isolating the spatial layer (the environment, lighting, wardrobe, style) from the temporal layer (the actions, dialogue, camera movement)11. Simultaneously, it inventories the available visual assets provided by the user. The skill automatically generates the precise syntax binding these assets to the prompt. If the user specifies two style images and a set of character images, the skill maps them into the variables {{style\_images}} and {{character\_images}}. For Seedance, it automatically generates the Define \<Subject\_N\> strings. For Gemini, it constructs the \[\# References \<IMAGE\_REF\_N\>\] header and the accompanying natural language exclusion clauses27.

### **Stage 2: Scene Deconstruction and Pacing**

Screenplay action lines are often excessively dense. The Claude Skill must algorithmically enforce the "One-Action Rule"14. It evaluates the complexity of a scene and divides a complex 30-second sequence into atomic 5-second to 15-second shots.  
If targeting Seedance 2, the skill structures these beats using the Shot 1: \[Action\] Shot 2: \[Action\] format to build a cohesive multi-shot montage within a single prompt41. If targeting Gemini Omni Flash, the skill ensures the action resolves within 10 seconds and appends the "single continuous shot" modifier to prevent unwanted hallucinatory editing by the engine19.

### **Stage 3: Cinematography and Lighting Enrichment**

Standard screenplays rarely dictate specific camera movements or lighting setups unless critical to the plot (e.g., they lack instructions like "dolly zoom" or "volumetric lighting"). If these are left blank, AI models default to uninspired static shots.  
The Claude Skill must cross-reference the emotional tone of the scene with an internal matrix of camera techniques—matching high-tension scenes with "handheld tracking, subtle shake" and intimate emotional scenes with "slow dolly in, smooth gimbal"36. It also appends specific lighting constraints (e.g., "high contrast noir," "golden hour") derived from the scene's location and time of day.

### **Stage 4: Syntactic Formatting and Output Generation**

Finally, the skill compiles the processed data into the strict structural formulas required by the respective models. It calculates character limits, prunes redundant adjectives to maintain "clarity over intensity," and returns the prompt to the user in a copy-paste ready Markdown code block, preceded by a brief breakdown of the creative choices and asset mappings11.

| Claude Skill Processing Stage | Action Executed by the Agent | Output Format |
| :---- | :---- | :---- |
| **Ingestion & Mapping** | Parses screenplay sluglines; assigns style images to global variables and character images to subject variables. | Generates @Image or \<IMAGE\_REF\> prefix tags. |
| **Temporal Deconstruction** | Splits dense action into atomic visual beats based on model duration limits (15s for Seedance, 10s for Gemini). | Shot 1, Shot 2 breakdowns or continuous shot constraints. |
| **Cinematic Enrichment** | Analyzes emotional tone; injects proper camera grammar (e.g., pan, dolly, crane) and lighting parameters. | Camera: \[move\] \+ \[speed\] \+ \[stability\] strings injected. |
| **Format & Restraint** | Applies negative prompts (e.g., "no zoom"), structures audio tags, and enforces token limits. | Final copy-paste ready code block for the specific AI engine. |

## **Mitigation of Generative Artifacts and Edge Cases**

Even with a perfectly automated Claude Skill, specific model behaviors require proactive mitigation strategies built directly into the prompt logic. The translation from text to video physics is inherently unstable, and the skill must preemptively address common points of failure.

### **Resolving Seedance 2 Hallucinations and Zoom Creep**

Seedance 2 is highly susceptible to "zoom creep," a phenomenon where the model incorrectly interprets a physical camera movement (like a dolly or track) as an optical focal length shift, resulting in warped perspectives and degraded background resolution36. The Claude Skill must aggressively append negative constraints such as "no zoom" and explicitly state "maintain subject size in frame" whenever panning or tracking shots are invoked36.  
Furthermore, Seedance strictly adheres to a 3,000-character limit per prompt11. The Claude Skill must calculate string lengths and actively prune redundant adjectives, enforcing the "clarity over intensity" rule. It must prioritize structural direction over excessive atmospheric descriptions, ensuring the model's attention mechanism remains focused on the primary subject and physical motion11. If a character transforms or undergoes a rapid state change, the prompt must rely on an "escalation arc" (Calm → Threat → Transformation → Aftermath) distributed across distinct numbered shots to prevent the physics engine from collapsing41.

### **Leveraging Gemini Omni Flash for Iterative Perfection**

The true paradigm shift with Gemini Omni Flash is that the initial prompt does not need to be flawless. Because the Interactions API maintains the generation state, errors can be corrected conversationally5.  
When designing the Claude Skill workflow for Gemini, the system must emphasize generating the base action, camera movement, and character identity perfectly in the first pass. If the lighting is incorrect or an unwanted object appears in the generated output, the user should not re-roll the entire prompt. Instead, the Claude Skill should offer a secondary "Refinement Prompt" generation feature. The skill can generate a subsequent prompt to send to the API using the previous\_interaction\_id: "Keep the character, motion, and camera identical. Remove the coffee cup from the table and shift the lighting to sunset"5. The Claude Skill documentation must advise the user that Gemini is best utilized as an iterative sculpting tool rather than a single-shot generator, preserving temporal continuity while allowing surgical edits5.

## **Strategic Synthesis**

The transition from purely text-driven video generation to multimodal synthesis demands a fundamental reimagining of prompt engineering. Translating a traditional screenplay into the latent space of models like Seedance 2.5 and Gemini Omni Flash requires an architecture that bridges narrative intent with rigorous geometric and syntactic instructions.  
Seedance 2.5 relies on a structured, hierarchical syntax where character definitions via @ tags, strict timeline segmentations (Shot 1, Shot 2), and exact camera terminologies govern the output. It is optimized for building complex, multi-shot sequences within a single prompt, provided the user strictly adheres to the one-action rule and explicit variable binding. Conversely, Gemini Omni Flash thrives on cohesive narrative descriptions, leveraging explicit image reference tags (\<IMAGE\_REF\_N\>) and the stateful retention of the Interactions API to iteratively sculpt scenes, demanding prompts that dictate physics and camera movement in natural, flowing language.  
By developing a programmatic Claude Skill that deconstructs a traditional screenplay, maps visual assets to specific model tags, injects professional camera language, and formats the output into model-specific syntax, creators can seamlessly integrate AI video generation into professional production pipelines. This systematic approach guarantees the preservation of character identity and stylistic coherence, transforming these advanced AI models from unpredictable generative engines into highly controllable, deterministic virtual production studios.

#### **Works cited**

1. Seedance 2.0 \- Wikipedia, [https://en.wikipedia.org/wiki/Seedance\_2.0](https://en.wikipedia.org/wiki/Seedance_2.0)  
2. Seedance 2 AI Video Generator — Multimodal 1080p Video \- Imgveo AI, [https://imgveo.com/seedance-2-ai-video-generator](https://imgveo.com/seedance-2-ai-video-generator)  
3. Nano Banana 2 Lite and Gemini Omni Flash available | Google Cloud Blog, [https://cloud.google.com/blog/products/ai-machine-learning/nano-banana-2-lite-and-gemini-omni-flash-available](https://cloud.google.com/blog/products/ai-machine-learning/nano-banana-2-lite-and-gemini-omni-flash-available)  
4. Gemini Omni Flash \- Model Card \- Google DeepMind, [https://deepmind.google/models/model-cards/gemini-omni-flash/](https://deepmind.google/models/model-cards/gemini-omni-flash/)  
5. Google Gemini Omni Flash 2026: The Future of AI Video Editing \- Labellerr, [https://www.labellerr.com/blog/google-gemini-omni-flash-2026-the-future-of-ai-video-editing/](https://www.labellerr.com/blog/google-gemini-omni-flash-2026-the-future-of-ai-video-editing/)  
6. Directory of Claude Agent Skills \- Awesome Claude, [https://awesomeclaude.ai/awesome-claude-skills](https://awesomeclaude.ai/awesome-claude-skills)  
7. I built a Claude skill that writes accurate prompts for any AI tool. To stop burning credits on bad prompts. We just hit 600 stars on GitHub‼️ : r/ClaudeAI \- Reddit, [https://www.reddit.com/r/ClaudeAI/comments/1rxyarx/i\_built\_a\_claude\_skill\_that\_writes\_accurate/](https://www.reddit.com/r/ClaudeAI/comments/1rxyarx/i_built_a_claude_skill_that_writes_accurate/)  
8. I Tried 100 Claude Skills. These Are The Best. \- DEV Community, [https://dev.to/suraj\_khaitan\_f893c243958/i-tried-100-claude-skills-these-are-the-best-1m4a](https://dev.to/suraj_khaitan_f893c243958/i-tried-100-claude-skills-these-are-the-best-1m4a)  
9. Seedance 2.0 Claims the AI Video Throne\! \- YouTube, [https://www.youtube.com/watch?v=\_o2MuUX9UYg](https://www.youtube.com/watch?v=_o2MuUX9UYg)  
10. Seedance 2.0: Try AI Video Generator for Free \- DeeVid AI, [https://deevid.ai/model/seedance-2](https://deevid.ai/model/seedance-2)  
11. Seedance 2.0 Prompt Guide: How to Prompt Like a Pro (With Examples) \- InVideo AI, [https://invideo.io/blog/seedance-2-0-prompt-guide/](https://invideo.io/blog/seedance-2-0-prompt-guide/)  
12. Seedance 2.0 Prompt Template: Copy-Paste Framework for Motion \+ Camera \+ Style, [https://wavespeed.ai/blog/posts/blog-seedance-2-0-prompt-template/](https://wavespeed.ai/blog/posts/blog-seedance-2-0-prompt-template/)  
13. Seedance 2.0: The Ultimate Guide to Multimodal AI Video Generation \- Hailuo AI, [https://hailuoai.video/pages/blog/seedance-2-multimodal-ai-video-generator](https://hailuoai.video/pages/blog/seedance-2-multimodal-ai-video-generator)  
14. How to Use Seedance 2.0: The Complete Guide to Creating Cinematic AI Videos (2026), [https://pixo.video/blog/how-to-use-seedance-2-0](https://pixo.video/blog/how-to-use-seedance-2-0)  
15. Gemini Omni Flash | Gemini API \- Google AI for Developers, [https://ai.google.dev/gemini-api/docs/models/gemini-omni-flash](https://ai.google.dev/gemini-api/docs/models/gemini-omni-flash)  
16. Gemini Omni Flash: Google's Talk-to-Edit AI Video Model Explained, [https://felloai.com/gemini-omni-flash/](https://felloai.com/gemini-omni-flash/)  
17. Interactions API | Gemini API \- Google AI for Developers, [https://ai.google.dev/gemini-api/docs/interactions-overview](https://ai.google.dev/gemini-api/docs/interactions-overview)  
18. Generate and edit videos with Gemini Omni Flash | Gemini API \- Google AI for Developers, [https://ai.google.dev/gemini-api/docs/omni](https://ai.google.dev/gemini-api/docs/omni)  
19. Gemini Omni Flash: Complete Guide, Prompts & Features \- Morphic, [https://morphic.com/resources/how-to/gemini-omni](https://morphic.com/resources/how-to/gemini-omni)  
20. How to Use the Gemini Omni Flash API for Conversational Video Editing \- MindStudio, [https://www.mindstudio.ai/blog/gemini-omni-flash-api-conversational-video-editing-2](https://www.mindstudio.ai/blog/gemini-omni-flash-api-conversational-video-editing-2)  
21. Free Seedance 2.0 — Multimodal AI Video Creator Online \- Dreamina, [https://dreamina.capcut.com/tools/seedance-2-0](https://dreamina.capcut.com/tools/seedance-2-0)  
22. Official Seedance 2.0 4K: Create Cinematic Videos Free \- Dreamina, [https://dreamina.capcut.com/seedance/seedance-2-0-4k](https://dreamina.capcut.com/seedance/seedance-2-0-4k)  
23. Seedance 2 \- Mitte – AI Creative Suite, [https://mitte.ai/flow/seedance-2](https://mitte.ai/flow/seedance-2)  
24. Gemini Omni Flash Preview | Gemini Enterprise Agent Platform | Google Cloud Documentation, [https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/omni-flash-preview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/omni-flash-preview)  
25. Seedance 2 AI Video Generator \- Cinematic AI Video with Native Audio, [https://www.seedance2ai.io/](https://www.seedance2ai.io/)  
26. Seedance 2.0 AI Video Generator by ByteDance \- Artlist, [https://artlist.io/ai/models/seedance-2-0](https://artlist.io/ai/models/seedance-2-0)  
27. Dreamina Seedance 2.0 series prompt guide--ModelArk-Byteplus, [https://docs.byteplus.com/en/docs/ModelArk/2222480](https://docs.byteplus.com/en/docs/ModelArk/2222480)  
28. How to make remarkable videos with Seedance 2.0 – Replicate blog, [https://replicate.com/blog/seedance-2](https://replicate.com/blog/seedance-2)  
29. Gemini Omni – Create & edit videos as easy as having a conversation, [https://gemini.google/overview/video-generation/](https://gemini.google/overview/video-generation/)  
30. Free Seedance 2.0 AI Video Generator Online \- Novi AI, [https://www.noviai.ai/ai-tools/seedance-ai-video-generator/](https://www.noviai.ai/ai-tools/seedance-ai-video-generator/)  
31. How to Use Gemini Omni Flash on PixVerse: Workflow Guide, [https://pixverse.ai/en/blog/how-to-use-gemini-omni-flash-on-pixverse](https://pixverse.ai/en/blog/how-to-use-gemini-omni-flash-on-pixverse)  
32. Seedance 2.0 Complete Guide: Step-by-Step Tutorial \- Morphic, [https://morphic.com/resources/how-to/seedance-2-guide](https://morphic.com/resources/how-to/seedance-2-guide)  
33. Seedance 2.0 character consistency across shots: what I've actually figured out after two weeks of testing \- Reddit, [https://www.reddit.com/r/aivideos/comments/1smtzb9/seedance\_20\_character\_consistency\_across\_shots/](https://www.reddit.com/r/aivideos/comments/1smtzb9/seedance_20_character_consistency_across_shots/)  
34. gemini-omni-flash-api | Agent Skills Library \- Awesome MCP Servers, [https://mcpservers.org/agent-skills/google-gemini/gemini-skills/gemini-omni-flash-api](https://mcpservers.org/agent-skills/google-gemini/gemini-skills/gemini-omni-flash-api)  
35. Seedance 2.0 camera movement prompts: the complete guide to cinematic AI video, [https://seedance2.so/blog/ai-video-camera-movement-prompt-guide](https://seedance2.so/blog/ai-video-camera-movement-prompt-guide)  
36. Seedance 2.0 Camera Movement Cheat Sheet: Prompt Syntax for Pan, Dolly, Tracking & More \- PromeAI, [https://www.promeai.pro/blog/seedance-2-0-camera-movement-cheat-sheet/](https://www.promeai.pro/blog/seedance-2-0-camera-movement-cheat-sheet/)  
37. Seedance 2.0 Camera Language Guide: 14 Cinematic Techniques With Prompt Examples, [https://www.jxp.com/blog/seedance-2-0-camera-language-guide](https://www.jxp.com/blog/seedance-2-0-camera-language-guide)  
38. seedance-2.0/skills/seedance-camera/SKILL.md at main · Emily2040/seedance-2.0 · GitHub, [https://github.com/Emily2040/seedance-2.0/blob/main/skills/seedance-camera/SKILL.md](https://github.com/Emily2040/seedance-2.0/blob/main/skills/seedance-camera/SKILL.md)  
39. Gemini Omni Flash Guide: Prompts, Safety Risks, SynthID and PixVerse Workflow, [https://pixverse.ai/en/blog/gemini-omni-video-model-review](https://pixverse.ai/en/blog/gemini-omni-video-model-review)  
40. Exclusive Seedance 2.0 Prompt Guide With 70 Ready-To-Use AI Video Prompts, [https://www.imagine.art/blogs/seedance-2-0-prompt-guide](https://www.imagine.art/blogs/seedance-2-0-prompt-guide)  
41. Seedance 2.0 — Complete Prompting Guide (Full Prompt Library) \- Higgsfield AI, [https://higgsfield.ai/blog/seedance-prompting-guide](https://higgsfield.ai/blog/seedance-prompting-guide)  
42. Das ist Gemini Omni \- Google Blog, [https://blog.google/intl/de-de/produkte/suchen-entdecken/gemini-omni/](https://blog.google/intl/de-de/produkte/suchen-entdecken/gemini-omni/)  
43. Seedance 2.0 Prompting Guide & Examples \[2026\] \- Fal.ai, [https://fal.ai/learn/tools/seedance-2-0-prompting-guide](https://fal.ai/learn/tools/seedance-2-0-prompting-guide)  
44. GitHub \- smixs/visual-skills: Professional Claude Skills for AI image and video prompting. Supports Nano Banana (Gemini 3 Pro/Flash), GPT Image 2, Seedance 2.0, Kling 3.0 (multi-shot \+ native dialogue), Veo. Works with Claude Code, Cursor, Windsurf, OpenCode, Hermes-agent., [https://github.com/smixs/visual-skills](https://github.com/smixs/visual-skills)  
45. AI Short Drama Scriptwriting Tool: Create Viral Scripts & Earn Money \- YouMind, [https://youmind.com/landing/x-viral-articles/ai-short-drama-script-skill](https://youmind.com/landing/x-viral-articles/ai-short-drama-script-skill)
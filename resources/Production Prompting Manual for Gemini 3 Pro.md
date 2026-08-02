# **Production Prompting and Iteration Engineering Manual for Google Nano Banana Pro (Gemini 3 Pro Image)**

The production of serialized short-video content requires strict visual continuity across extensive generation cycles. Unlike standard single-frame artistic generations where visual aesthetics are prioritized over strict dimensional adherence, a storyboard pipeline demands structured consistency across hundreds of sequential scenes. The utilization of Google’s Gemini 3 Pro Image architecture, commercially integrated as Nano Banana Pro, enables a production pipeline to bypass traditional parameter-efficient fine-tuning (such as LoRAs) by leveraging an advanced multimodal reasoning core. Rather than executing simple token-to-pixel mapping typical of CLIP-based diffusion models, Nano Banana Pro acts as a spatial simulation engine, calculating scene geometry, lighting paths, and material surfaces within a massive token-based context window before rendering output pixels. This manual provides a production-grade blueprint for engineers integrating Nano Banana Pro into serialized storyboard automation pipelines.

## **1\. Reference Conditioning and Identity Architecture**

Establishing stable character identity across serialized episodes without fine-tuning requires strategic management of the model's multimodal context window. Nano Banana Pro processes reference images not as mere style vectors, but as spatial grounding databases that guide the initial steps of the generation pipeline.

### **1.1 Multimodal Input Ceilings and Allocation Dynamics**

The Gemini 3 Pro Image engine natively supports up to 14 total reference images within a single request context. However, these inputs are processed through distinct attention pipelines optimized for character features, object structures, or aesthetic styles.

| Input Reference Category | Maximum Supported Files | Target Processing Mechanism |
| ----- | ----- | ----- |
| **Character Consistency** | 5 Human Reference Images | Preserves core facial geometry, micro-facial features, and anatomical proportions. |
| **Object Fidelity** | 6 Object Reference Images | Hard-surface props, complex wardrobe items, and branded assets. |
| **Style References** | 3 Style Reference Images | Color grading palettes, film stock grain, lighting physics, and contrast curves. |

For a four-character recurring cast, the input payload must dedicate four of its five available human reference slots to the character sheets. While the Gemini API natively allocates these slots based on image content, the precise neural weights applied to each category remain undocumented in Google's official developer schemas. The operational pipeline must assume that character references consume a significant portion of the spatial planning budget, requiring style references to be compressed or simplified to prevent token degradation.

### **1.2 Positional Indexing and Token Binding**

To prevent visual drift and attribute bleeding when multiple characters occupy the same frame, the generation pipeline must implement a rigid index-to-token binding protocol in the text prompt. Nano Banana Pro parses references in the sequential order they are attached to the API payload array (image\_urls or images).

**API Payload Example:**

```
image_urls[0] = "https://internal-storage.local/maya_face.png"
image_urls[1] = "https://internal-storage.local/leo_face.png"
```

The text prompt must bind these indices to highly distinct, hyphenated alphanumeric identifiers rather than common nouns to isolate the character's visual features from general pre-training weights.

*"Using the attached Image \[0\] strictly as the sole visual identity anchor for the facial features, bone structure, and expressions of 'Character-Maya', and the attached Image \[1\] strictly as the sole visual identity anchor for the facial features, bone structure, and expressions of 'Character-Leo'..."*

Descriptive phrases such as "the young woman" or "the athletic man" must be avoided, as they introduce semantic ambiguity and allow the model's text encoder to pull generic training data into the planning phase, leading to identity dilution.

### **1.3 Mechanisms of Attribute Blending and Spatial Isolation**

Attribute blending occurs when the visual features of one reference image bleed into another character's spatial boundaries during rendering. To counteract this, the prompt must enforce absolute spatial isolation boundaries:

*"Character-Maya (Image \[0\]) and Character-Leo (Image \[1\]) are physically separated in space. Render Character-Maya strictly with the dark blue denim jacket from Image \[0\] in all panels. Render Character-Leo strictly with the grey wool coat and silver wireframe glasses from Image \[1\] in all panels. Attribute mixing or visual crossovers between the two characters is strictly prohibited."*

### **1.4 Reference Ordering Priorities**

Attention weights are heavily biased toward the earliest elements in the reference array. Character references must occupy the initial indices (Indices 0 through 3). Style references must be positioned at the end (Indices 4 through 6).

### **1.5 Descriptive Boundaries for Visual Reference**

Over-describing reference images within the text prompt creates semantic conflict with the vision encoder. Reference images should *not* be described in detail; the prompt should only reference the index to bind the visual token.

### **1.6 Identity Degradation Triggers**

Character identity degrades rapidly under specific configurations:

* **Low-Resolution Face References**: Face resolutions fewer than 512 pixels result in face morphing.  
* **Extreme Contrast Demands**: Highly stylized lighting overrides the identity encoder.  
* **Sub-Optimal Temperature Configuration**: Setting temperature below 1.0 restricted reasoning, causing generic outputs.

## **2\. Multi-Panel Storyboard Sheets and Grid Geometry**

Generating multi-panel sheets in a single generation pass is the most reliable method for maintaining consistency in wardrobe and lighting.

### **2.1 Grid Specification and Spatial Partitioning**

The physical layout must be defined using precise graphic design terminology.

*"A single horizontal 16:9 cinematic storyboard sheet structured as three equal-sized, distinct 9:16 vertical panels arranged side-by-side in a 1x3 grid. The panels are physically separated by solid, clean, 20px wide white gutters. No characters, elements, or visual effects may cross or bleed over these white borders. Each panel depicts a completely distinct angle and shot of the scene."*

This structural prompt forces the reasoning core to divide the coordinate space into three bounding regions before initiating pixel generation, ensuring clean gutters and preventing adjacent panels from bleeding into one another \[cite: 4, 23\].

### **2.2 Panel Capacity Limits**

Effective visual resolution scales inversely with panel count. For standard 2K generation (2048x1152), quality behaviors are as follows:

Panel Horizontal Pixels=

Panel Count

Total Canvas Width−(Panel Count−1)⋅Gutter Width

​

For a standard 2K generation (2048x1152 for a 16:9 sheet) \[cite: 14\], the quality limits behave as follows:

* **3-Panel Sheets (Optimal)**: \~656 horizontal pixels per panel. Optimal for character storyboards.  
* **4-Panel Sheets (Marginal)**: \~487 horizontal pixels per panel. Suitable for landscapes, but facial details soften.  
* **5+ Panel Sheets (Unstable)**: Resolution drops below 380 pixels. Results in gutter collapse and artifacts.

### **2.3 Programmatic Mapping of Character Consistency**

The prompt must treat character actions as a sequential narrative mapped to specific panel locations. Defining coordinates ensures the tracking of visual features while varying angles.

"The storyboard depicts Character-Maya sequentially across three panels:  
\- Panel 1 (Left Panel): Close-up shot. Character-Maya is looking directly at the camera with a neutral expression, wearing her locked dark blue denim jacket (Image \[0\]).  
\- Panel 2 (Center Panel): Medium shot. Character-Maya is sitting at a wooden desk in the background, writing in a journal.  
\- Panel 3 (Right Panel): Low-angle wide shot. Character-Maya is walking toward a window on the right side of the room."

By defining the character's coordinates and actions sequentially within the panel hierarchy, the spatial planning engine tracks the visual features of `Character-Maya` across the entire sheet while varying the camera angles and poses \[cite: 6, 22\].

### **2.4 Grid Failure Modes and Corrective Prompting**

The following table lists layout failures and necessary prompt adjustments:

| Observed Failure Mode | Root Model Misinterpretation | Corrective Prompt Directive |
| ----- | ----- | ----- |
| **Gutter Absorption** | Gutters rendered as physical pillars. | "20px white gutters are strictly non-diegetic, flat graphic borders." |
| **Compositional Mirroring** | Identical compositions across panels. | "Each panel must utilize a completely distinct camera framing." |
| **Wardrobe Drift** | Clothing color/texture changes between panels. | "Dark blue denim jacket is visually invariant across the entire sheet." |

## **3\. Iterative Refinement and Editing Protocols**

Nano Banana Pro provides refinement via a dedicated image editing endpoint and stateful multi-turn conversational editing.

### **3.1 Targeted Maskless Conversational Editing**

The editing endpoint performs semantic edits without binary alpha masks by modifying spatial boundaries and recalculating environmental shadows.

To execute a targeted edit on a single panel while leaving the rest of the sheet untouched, the prompt must construct a spatial and semantic constraint boundary \[cite: 23\].  
"In the provided storyboard sheet, modify only Panel 3 (the rightmost panel). Keep Panel 1 (left) and Panel 2 (center) completely identical in character identity, facial features, layout, and composition. In Panel 3, change only the background from a wooden room to a modern concrete office. Adjust the ambient lighting on Character-Maya's face in Panel 3 to match the cool, blue-toned light of the new background, but do not alter her facial structure or expression."

### **3.2 Stateful Conversational History via API Thought Signatures**

Multi-turn iterations manage stateful context via the thoughtSignature token block, which ensures compositional locking.

Turn 1 API Response Payload:  
{  
  "role": "model",  
  "parts": \[  
    {  
      "inlineData": { ... },  
      "thoughtSignature": "e30\_enc\_signature\_data\_alpha"  
    }  
  \]  
}

To modify the generated image without triggering compositional drift or losing character details, the subsequent request must return the exact `thoughtSignature` from the response payload \[cite: 28\]. This allows the model to recall its previous calculations, ensuring that the edit is applied only to the target elements while leaving the rest of the canvas locked \[cite: 28\].

### **3.3 The Lock-Change-Constraint (LCC) Editing Framework**

Prompts must segregate scene elements into areas of responsibility:

* **Lock**: Define identical regions and character details.  
* **Change**: Specify the single modification.  
* **Constraint**: Prevent secondary changes.

1\. LOCK: "Maintain absolute visual identity and facial structure for Character-Maya as defined in the original image. Keep the camera angle, lens focus, and overall composition of all panels unchanged." \[cite: 6, 23\]  
2\. CHANGE: "In Panel 2, change the red mug on the desk to a green ceramic cup." \[cite: 23, 26\]  
3\. CONSTRAINT: "The shadow cast by the cup must align with the window light source from the left. Do not introduce hands into the frame. Do not alter the color grading of the panel." \[cite: 13, 23\]

By separating these directives, the reasoning core processes the modification as a local update rather than a global re-generation \[cite: 4, 26\].

### **3.4 Seed Control and Determinism**

Nano Banana Pro is fundamentally non-deterministic; identical inputs yield highly similar but not identical compositions. Lowering temperature below 1.0 to force determinism is strongly discouraged as it impairs spatial layout.

Lowering the `temperature` parameter below `1.0` in an attempt to force determinism is strongly discouraged \[cite: 19\]. It impairs the reasoning model's spatial layout calculations, leading to severe compositional errors, looping artifacts, and flat, synthetic lighting \[cite: 19, 31\].

### **3.5 Quantitative Edit-vs-Regenerate Decision Rule**

Decision Metric (M) calculation determines whether to perform an in-place edit (Action \= EDIT\_IN\_PLACE) or a fresh generation (Action \= REGENERATE\_WHOLE\_SHEET). If M \>= 0.66, regeneration is required.

Let N\_p be the total number of panels in the storyboard sheet (N\_p \= 3).  
Let E\_p be the number of panels requiring structural changes.  
Let C\_i be the character identity status (0 \= intact, 1 \= severely drifted).  
Let S\_d be the spatial layout degradation (0 \= clean gutters, 1 \= collapsed gutters/bleeding).

Calculate the Decision Metric (M):  
M \= (E\_p / N\_p) \+ C\_i \+ S\_d

If M \>= 0.66:  
    Action \= REGENERATE\_WHOLE\_SHEET (Execute fresh generation with raw character references)  
Else:  
    Action \= EDIT\_IN\_PLACE (Execute targeted semantic edit using /edit endpoint)

This decision protocol prevents a sheet from undergoing successive, minor edits that degrade the underlying composition over time \[cite: 17, 23\].  
**Inter-Scene Continuity via Generated References**  
To maintain environmental consistency from scene to scene, a previously generated storyboard sheet can be fed back into the next generation request as a style reference \[cite: 26\].  
While this technique maintains background details, it introduces a "photocopy degradation" effect if repeated sequentially across more than three generations \[cite: 17\]. Visual artifacts, contrast compression, and character facial drift accumulate with each successive generation loop \[cite: 6, 17\]. The correct workflow dictates that the pipeline must always ground character identity in the original source reference images (the raw character sheets), using the previously generated sheet strictly as a low-weighted style input \[cite: 6, 9\].  
\--------------------------------------------------------------------------------  
**Style Uniformity and Aesthetic Controls**  
decouples character identity from environmental aesthetics by routing style references and character sheets to separate modeling layers \[cite: 6, 22\]. The system can process up to 3 style reference images alongside 5 character references in a single generation request without cross-contamination \[cite: 9, 10\].  
**Deco-pling Style and Identity**  
To enforce a uniform visual style across hundreds of generations, the pipeline must utilize a hybrid style strategy consisting of both style reference images and a fixed text-based style clause \[cite: 9, 13\]. This approach anchors the global color palette and contrast curves to the style images, while the text-based style clause provides precise instructions regarding camera lens physics, film stock, and lighting \[cite: 9, 16\].  
Because the model's reasoning core processes visual assets and textual descriptions in parallel, the style references do not compete with the character references for attention, enabling highly stable, stylized outputs \[cite: 9, 10\].  
**Technical Photographic Terminology**  
Nano Banana Pro responds directly to professional photographic and cinematographic language, while generic qualitative descriptors (such as "cinematic," "stunning," or "hyper-detailed") degrade composition \[cite: 16, 23\]. The table below outlines the precise technical terminology to use versus the expressions to avoid:

| Avoid (Triggers Generic AI Style) \[cite: 23\] | Use (Triggers Accurate Physical Simulation) \[cite: 16, 23\] |
| ----- | ----- |
| "Beautiful golden hour lighting" | "Golden hour backlighting with long, high-contrast shadows cast toward the camera." |
| "Cinematic movie style" | "Shot on Fujifilm 35mm film stock, warm color science, muted teal-and-amber color grading." |
| "Extremely detailed camera shot" | "Captured on a Leica 50mm Summilux lens at f/1.8, shallow depth of field, sharp focus on subject." |
| "Dramatic studio lighting" | "Chiaroscuro lighting setup, a single high-contrast key light source from a 45-degree angle." |
| "Realistic texture" | "Matte ceramic surfaces, visible fabric grain, realistic material refraction index." |

\--------------------------------------------------------------------------------  
**Aspect Ratio, Resolution, and Output Specifications**  
To optimize storyboard panels for integration with downstream video models, the horizontal sheet layout must be configured to allow precise coordinate-based slicing \[cite: 14, 32\].  
**Supported Aspect Ratios and Dimensions**  
Nano Banana Pro natively supports 11 predefined aspect ratio options \[cite: 10, 14\].

| Aspect Ratio Preset \[cite: 14\] | Target Output Dimension (1K Base) | Primary Production Use Case |
| ----- | ----- | ----- |
| **9:16** | 576 x 1024 pixels | Single isolated vertical panel/shot. |
| **16:9** | 1024 x 576 pixels | 3-panel horizontal storyboard sheet. |
| **21:9** | 1024 x 440 pixels | Wide cinematic multi-panel sheet (4 panels). |
| **1:1** | 1024 x 1024 pixels | Square reference tiles/grid mockups. |

**Canvas-to-Panel Slicing Optimization**  
To generate three vertical 9:16 storyboard panels side-by-side, the generation must utilize the horizontal `16:9` aspect ratio preset at `2K` resolution (2048x1152) \[cite: 10, 14\].

Canvas Width=2048px,Canvas Height=1152px

When specifying 20px gutters within the prompt, the automated post-generation slicing script can isolate each panel using precise pixel offsets.  
\# Optimal 3-Panel Slicing Offsets (for a 2048x1152 Canvas with 20px Gutters)  
\# Canvas is divided into three 9:16 vertical slices of 656px width each.

Panel\_1\_Bounding\_Box \= (0, 0, 656, 1152\)  
Panel\_2\_Bounding\_Box \= (676, 0, 1332, 1152\)  \# Offset by 20px gutter  
Panel\_3\_Bounding\_Box \= (1352, 0, 2008, 1152\) \# Offset by second 20px gutter

Executing generations at `2K` ensures that each isolated panel retains approximately 656x1152 pixels of resolution, which falls well within the required detail threshold for downstream image-to-video models \[cite: 14, 26\].

## **4\. Negative Instructions and Prohibition Strategies**

Nano Banana Pro plans composition based on semantic directives and does not natively support separate "negative prompt" parameters.

**The Ineffectiveness of Negative Phrases**  
Using standard negative phrasing inside the main prompt (e.g., "no blurred faces, no bad hands, no extra limbs") often causes the model to generate the exact features intended for exclusion \[cite: 16\]. Because the model's multimodal parser processes the semantic concepts of "faces," "hands," and "limbs," it prioritizes these subjects during the spatial planning phase, inadvertently rendering them in the scene \[cite: 4, 10\].

### **4.1 The Constraints-Block Strategy**

A structured "Constraints" block at the end of the prompt reliably suppresses artifacts without triggering planning bias.

"Constraints and Prohibitions:  
\- The camera frame must remain entirely clear of any graphic overlays, watermarks, signatures, or burned-in text.  
\- No text characters may appear inside the panel scenes unless enclosed in literal quotation marks in the prompt.  
\- All human figures must render with physically accurate anatomy, including exactly five fingers on each hand.  
\- No duplicate or mirrored characters within a single panel.  
\- Ensure that backgrounds are sharp and free of unnatural Gaussian blur or noise artifacts." \[cite: 13, 23\]

By framing exclusions as logical constraints rather than descriptive negatives, the reasoning core successfully validates the final output against these rules before committing to pixel rendering \[cite: 4, 7\].

## **5\. Parameter Schemas and Operational Economics**

Deploying Gemini 3 Pro Image (Nano Banana Pro) at production scale requires understanding the parameter differences between Google's native API and third-party wrappers like fal.ai, as well as the corresponding rate limits and operational costs \[cite: 19, 33, 34\].  
**API Input Parameter Specification**  
The following tables detail input parameters and cost comparisons for production deployment.

| Parameter Name | Data Type | Permitted Values | Default Value | Operational Effect |
| ----- | ----- | ----- | ----- | ----- |
| `prompt` | String | UTF-8 plain text | *Required* | Defines the core scene composition \[cite: 14\]. |
| `image_urls` | Array of Strings | Valid image URIs \[cite: 14, 15\] | *Required for /edit* | Up to 14 references \[cite: 7, 26\]. |
| `aspect_ratio` | Enum | `auto`, `21:9`, `16:9`, `3:2`, `4:3`, `5:4`, `1:1`, `4:5`, `3:4`, `2:3`, `9:16` \[cite: 14\] | `1:1` (Gen), `auto` (Edit) | Enforces global canvas aspect ratio \[cite: 14\]. |
| `resolution` | Enum | `1K`, `2K`, `4K` \[cite: 14\] | `1K` \[cite: 14\] | 4K outputs incur a 2x rate multiplier \[cite: 10, 33\]. |
| `num_images` | Integer | `1` to `4` \[cite: 14\] | `1` \[cite: 14\] | Sets batch generation size \[cite: 14, 26\]. |
| `seed` | Integer | Any valid integer | Random | Best-effort random number generator initialization \[cite: 14, 30\]. |
| `output_format` | Enum | `png`, `jpeg`, `webp` \[cite: 14\] | `png` \[cite: 14\] | Compression format of returned binary \[cite: 14\]. |
| `safety_tolerance` | Enum | `1`, `2`, `3`, `4`, `5`, `6` \[cite: 14\] | `4` \[cite: 14\] | Content filter sensitivity (1 is strictest, 6 is least strict) \[cite: 14\]. |
| `enable_web_search` | Boolean | `true`, `false` \[cite: 14\] | `false` \[cite: 14\] | Adds $+0.015 per call \[cite: 10, 33\]. |

**Operational Cost Comparison**  
Deploying Nano Banana Pro in high-concurrency production workflows requires a thorough comparison of hosting environments.

| Metric | fal.ai API | AI Studio | Vertex AI |
| ----- | ----- | ----- | ----- |
| **Standard Cost** | $0.15/gen | $0.00 (Preview) | $0.12 \- $0.15 |
| **Latency** | 10 \- 20s | 15 \- 25s | 10 \- 18s |

**Native Google API vs. fal.ai Parameter Mappings**  
When migrating requests between direct Google Cloud Vertex AI and the fal.ai aggregator, the parameter structures must be translated:

* **Resolution Specification**: Direct Google API utilizes `image_size` inside the `response_format` configuration block to define output scale (e.g., `"image_size": "2K"`) \[cite: 9\]. fal.ai maps this to the top-level `resolution` parameter (with options `"1K"`, `"2K"`, `"4K"`) \[cite: 14\].  
* **Multimodal Granular Controls**: Native Google API provides granular, per-content-item control over input media resolution using the `media_resolution` parameter (`low`, `medium`, `high`, `ultra_high`), allowing developers to allocate fewer tokens to simple background references and more tokens to complex character sheets \[cite: 36, 37\]. fal.ai abstracts this, processing all reference images at standard input resolution \[cite: 14\].  
* **Thinking Levels**: Native Google API exposes `thinking_level` (`minimal`, `low`, `high`), letting developers constrain reasoning depth for faster, low-cost drafts \[cite: 19\]. The fal.ai endpoint exposes Nano Banana Pro only in its high-performance, maximum-thinking state, locking latency to the 10-20 second window \[cite: 10\].

\--------------------------------------------------------------------------------  
**Failure Modes, Diagnostics, and Automated Mitigations**  
The table below outlines the primary failure modes encountered in multi-panel, multi-character storyboard pipelines, along with corresponding engineering-level diagnostic signatures and programmatic fixes:

| Failure Mode | Visual Signature | Diagnostic Core Cause | Programmatic or Prompt-Level Mitigation |
| ----- | ----- | ----- | ----- |
| **Grid Collapse / Merging** \[cite: 17\] | Panels merge into a single panoramic shot; separating white lines are rendered as physical walls in the scene. | The reasoning core failed to isolate layout blocks during spatial planning \[cite: 4, 17\]. | Add explicit frame parameters: `"Divided strictly into three non-overlapping 9:16 vertical boxes separated by 20px non-diegetic solid white graphic borders."` \[cite: 13, 23\] |
| **Attribute Swapping** \[cite: 17\] | Character A has Character B's hair or wardrobe; color blending occurs across panel boundaries. | Positional indices in the `image_urls` array were not cleanly bound to distinct semantic name tokens \[cite: 13, 15\]. | Restructure the prompt using unique token strings: `"Character-Maya (Image [0]) and Character-Leo (Image [1])."` Avoid generic identifiers \[cite: 13, 16\]. |
| **Composition Mirroring** \[cite: 17\] | All three storyboard panels show identical camera angles and poses, ignoring shot-variation rules. | The prompt lacks localized kinetic directives for each panel, allowing global composition weights to dominate \[cite: 17\]. | Define localized, distinct actions and shot scales for each pane: `"Panel 1 (Left): Extreme close-up of face; Panel 3 (Right): Extreme wide-angle landscape."` \[cite: 13, 24\] |
| **Facial Melting / Softening** \[cite: 17\] | Facial features appear blurry, asymmetrical, or generic in wide-angle or multi-panel sheets. | Canvas resolution is too low relative to character scale, reducing face pixels below the encoder's detection threshold \[cite: 17, 20\]. | Step up output resolution to `2K` or `4K` in the API call, and instruct: `"Captured on an 85mm portrait lens with sharp focal plane alignment."` \[cite: 14, 16\] |
| **API Rejection / Blocker** \[cite: 14\] | API returns a safety block error code (rejection on safe prompts). | The safety filter misinterprets cinematic prompt terms (e.g., "shooting a scene," "bloody sunset") \[cite: 14\]. | Elevate the `safety_tolerance` parameter to `5` or `6` in the payload configuration, and swap dramatic terms for neutral descriptors \[cite: 14\]. |

## **6\. Strategic Model Routing**

While Nano Banana Pro is the premium solution for character consistency and complex layout reasoning, specific visual tasks are processed more efficiently by routing them to alternative models \[cite: 10, 18\].

### **6.1 Strategic Routing Matrix**

The table below outlines when to route tasks to alternative models:

| Model Selection | Use Case | Strategic Advantage |
| ----- | ----- | ----- |
| **Nano Banana Pro** | Production storyboards, multi-character consistency. | High-level reasoning and consistent lighting. |
| **Nano Banana 2** | Rapid prototyping, low-cost drafts. | Speed (4-8s) and lower cost. |

## **7\. Implementation Guide and Quick Reference**

This section provides a production-ready system architecture overview with a full JSON request body for a two-character, three-panel horizontal storyboard sheet, and the corresponding prompt structure.  
**Pipeline Architecture Overview**  
                   \+------------------------------------------+  
                    |            Character Sheets              |  
                    |  \- Maya (Index 0\)    \- Leo (Index 1\)     |  
                    \+--------------------+---------------------+  
                                         |  
                                         v  
                    \+------------------------------------------+  
                    |       Style Reference (Index 2\)          |  
                    \+--------------------+---------------------+  
                                         |  
                                         v  
\+----------------------------------------+-----------------------------------------+  
|                                    API Prompt                                    |  
|  \- Define unique tokens: 'Character-Maya', 'Character-Leo'                         |  
|  \- Enforce layout: '3 vertical 9:16 panels side-by-side with 20px white gutters' |  
|  \- Bind actions: Panel 1 (Maya), Panel 2 (Leo), Panel 3 (Both)                   |  
|  \- Set cinematic lighting & Leica lens specs                                    |  
\+----------------------------------------+-----------------------------------------+  
                                         |  
                                         v  
                    \+------------------------------------------+  
                    |           Nano Banana Pro API            |  
                    |  \- Model: gemini-3-pro-image             |  
                    |  \- Resolution: 2K      \- Temp: 1.0       |  
                    \+--------------------+---------------------+  
                                         |  
                                         v  
                    \+------------------------------------------+  
                    |      Canvas Output (2048 x 1152 px)      |  
                    \+--------------------+---------------------+  
                                         |  
                                         v  
                    \+------------------------------------------+  
                    |        Slicing & Extraction Script       |  
                    |  \- Cut Panel 1: \[0, 0, 656, 1152\]        |  
                    |  \- Cut Panel 2: \[676, 0, 1332, 1152\]      |  
                    |  \- Cut Panel 3: \[1352, 0, 2008, 1152\]     |  
                    \+--------------------+---------------------+  
                                         |  
                                         v  
                    \+------------------------------------------+  
                    |         Downstream Video Models          |  
                    |  \- Feed individual 9:16 panels as refs   |  
                    \+------------------------------------------+

**Complete JSON Payload for API Call (**`fal-ai/nano-banana-pro`**)**  
The following payload initiates a generation configured for three equal-sized 9:16 vertical panels side-by-side on a horizontal 16:9 canvas \[cite: 14\].  
{  
  "prompt": "Using the attached Image \[0\] strictly as the sole visual identity anchor for the face, bone structure, and identity of 'Character-Maya', and the attached Image \[1\] strictly as the sole visual identity anchor for the face, bone structure, and identity of 'Character-Leo'. The style, grain, and color palette must follow the attached aesthetic in Image \[2\]. A single horizontal cinematic storyboard sheet structured as exactly three equal-sized 9:16 vertical panels side-by-side in a 1x3 grid, physically separated by solid, clean, 20px non-diegetic white gutters. No cross-gutter bleed. Panel 1 (Left): Close-up shot of Character-Maya. She is looking directly at the camera with a neutral expression, wearing her locked dark blue denim jacket from Image \[0\]. Warm soft key light from the left. Panel 2 (Center): Medium shot of Character-Leo. He is wearing his grey wool coat and wireframe glasses from Image \[1\], sitting in a dim library. Cool shadow grading. Panel 3 (Right): Wide shot containing both characters. Character-Maya and Character-Leo are standing on opposite sides of a modern concrete living room, separated by space. Camera is a Leica 50mm Summilux at f/1.8 with sharp focal plane alignment. Style constraints: 35mm film stock, muted teal and amber color grading. Constraints: No watermarks, no duplicate characters within a single panel, hands must show exactly five fingers.",  
  "image\_urls": \[  
    "https://production-assets.internal/characters/maya\_character\_sheet.png",  
    "https://production-assets.internal/characters/leo\_character\_sheet.png",  
    "https://production-assets.internal/styles/cinematic\_fujifilm\_reference.png"  
  \],  
  "aspect\_ratio": "16:9",  
  "resolution": "2K",  
  "num\_images": 1,  
  "seed": 948201,  
  "output\_format": "png",  
  "safety\_tolerance": "4",  
  "enable\_web\_search": false  
}

\--------------------------------------------------------------------------------  
**One-Page Engineering Quick Reference Guide**  
This reference block summarizes the core syntax and operational rules for production deployment.

### **7.1 Character Identity Binding Formula**

*"Using the attached Image \[0\] strictly as the sole visual anchor for 'Character-Maya', and the attached Image \[1\] strictly as the sole visual anchor for 'Character-Leo'..."*

### **7.2 Core Parameter Rules**

A single horizontal cinematic storyboard sheet structured as exactly three equal-sized 9:16 vertical panels side-by-side in a 1x3 grid, physically separated by solid 20px white gutters. No gutter bleed \[cite: 13, 23\].

**Lock-Change-Constraint Editing Syntax (**`/edit` **Endpoint)**  
LOCK: Keep Panels 1 and 2 completely identical to the source image. Lock all facial structures \[cite: 6, 23\].  
CHANGE: In Panel 3, change the background to a concrete wall \[cite: 23, 26\].  
CONSTRAINT: No change in camera lens, grading, or character pose \[cite: 13, 23\].

**Structural Grid Slicing Logic (2K Canvas: 2048 x 1152 px)**

* **Panel 1 (Left Panel)**: Left boundary: `0px`, Right boundary: `656px` \[cite: 14\].  
* **Gutter 1 (Separation)**: Left boundary: `656px`, Right boundary: `676px`.  
* **Panel 2 (Center Panel)**: Left boundary: `676px`, Right boundary: `1332px`.  
* **Gutter 2 (Separation)**: Left boundary: `1332px`, Right boundary: `1352px`.  
* **Panel 3 (Right Panel)**: Left boundary: `1352px`, Right boundary: `2008px` \[cite: 14\].

**Core Parameter Constancy Rules**

* **Do Not Modify Temperature**: Keep locked to 1.0.  
* **Reference Order**: Characters at Indices 0-1, style at end.  
* **Constraint Blocks**: Use logical blocks instead of negative phrases.

\--------------------------------------------------------------------------------

1. Nano Banana Pro: Professional AI Image Generator by Gemini 3 \- Artlist, [https://artlist.io/ai/models/nano-banana-pro](https://artlist.io/ai/models/nano-banana-pro)  
2. Nano Banana Pro & Nano Banana 2 Free AI Image Generation & Editing, [https://www.nanobananapro.org/](https://www.nanobananapro.org/)  
3. Gemini 3 Pro Image \- AI Model | Layer, [https://www.layer.ai/models/google-gemini-3-pro-image](https://www.layer.ai/models/google-gemini-3-pro-image)  
4. Nano Banana Pro: State-of-the-Art AI Image Generation & Editing | fal, [https://fal.ai/nano-banana-pro](https://fal.ai/nano-banana-pro)  
5. Developers can build with Nano Banana Pro (Gemini 3 Pro Image) \- Google Blog, [https://blog.google/innovation-and-ai/technology/developers-tools/gemini-3-pro-image-developers/](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-3-pro-image-developers/)  
6. Enable strict facial consistency mode. Prioritize the facial features from the provided reference im \- Gemini Apps Community \- Google Help, [https://support.google.com/gemini/thread/404609614/enable-strict-facial-consistency-mode-prioritize-the-facial-features-from-the-provided-reference-im?hl=en](https://support.google.com/gemini/thread/404609614/enable-strict-facial-consistency-mode-prioritize-the-facial-features-from-the-provided-reference-im?hl=en)  
7. What Is Gemini 3 Pro Image? Google's Flagship AI Image Model | MindStudio, [https://www.mindstudio.ai/blog/what-is-gemini-3-pro-image](https://www.mindstudio.ai/blog/what-is-gemini-3-pro-image)  
8. Google models | Gemini Enterprise Agent Platform, [https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models)  
9. Nano Banana image generation \- Interactions API | Google AI for Developers, [https://ai.google.dev/gemini-api/docs/image-generation](https://ai.google.dev/gemini-api/docs/image-generation)  
10. Nano Banana Pro vs. Nano Banana 2: What's The Difference? \- Fal.ai, [https://fal.ai/learn/tools/nano-banana-pro-vs-nano-banana-2](https://fal.ai/learn/tools/nano-banana-pro-vs-nano-banana-2)  
11. nano-banana vs nano-banana-pro — comparison, examples, use cases \- AIModels.fyi, [https://www.aimodels.fyi/models/compare/nano-banana-fal-ai-vs-nano-banana-pro-fal-ai](https://www.aimodels.fyi/models/compare/nano-banana-fal-ai-vs-nano-banana-pro-fal-ai)  
12. Gemini 3 Pro Image \- Google AI for Developers, [https://ai.google.dev/gemini-api/docs/models/gemini-3-pro-image](https://ai.google.dev/gemini-api/docs/models/gemini-3-pro-image)  
13. Nano Banana Pro Prompt Guide: Best Nano Banana Prompts | LTX Blog \- LTX Studio, [https://ltx.io/blog/nano-banana-prompt-guide](https://ltx.io/blog/nano-banana-prompt-guide)  
14. Nano Banana Pro API \- Fal.ai, [https://fal.ai/docs/model-api-reference/image-generation-api/nano-banana-pro](https://fal.ai/docs/model-api-reference/image-generation-api/nano-banana-pro)  
15. Google Nano Banana 2 API \[image edit\]: AI Image Editor | fal, [https://fal.ai/models/fal-ai/nano-banana-pro/edit/api](https://fal.ai/models/fal-ai/nano-banana-pro/edit/api)  
16. Ultimate prompting guide for Nano Banana | Google Cloud Blog, [https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana)  
17. Gemini 3 Pro Image \- Model Card \- Googleapis.com, [https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Image-Model-Card.pdf](https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Image-Model-Card.pdf)  
18. Google Nano Banana Pro: Advanced AI Image Generator \+ Editor | fal, [https://fal.ai/models/fal-ai/nano-banana-pro](https://fal.ai/models/fal-ai/nano-banana-pro)  
19. Gemini 3 Developer Guide \- Interactions API | Google AI for Developers, [https://ai.google.dev/gemini-api/docs/gemini-3](https://ai.google.dev/gemini-api/docs/gemini-3)  
20. How to Use Nano Banana 2: Practical Tips for Better Images \- Fal.ai, [https://fal.ai/learn/tools/how-to-use-nano-banana-2](https://fal.ai/learn/tools/how-to-use-nano-banana-2)  
21. Gemini 3 Pro Image – Nano Banana Pro \- Google DeepMind, [https://deepmind.google/models/gemini-image/pro/](https://deepmind.google/models/gemini-image/pro/)  
22. Nano Banana Pro \- AI Image Generator | Gemini 3 Pro Image, [https://nanobanana-pro.studio/](https://nanobanana-pro.studio/)  
23. Nano Banana Pro Prompting Guide & Examples \[2026\] \- Fal.ai, [https://fal.ai/learn/tools/nano-banana-pro-prompting-guide](https://fal.ai/learn/tools/nano-banana-pro-prompting-guide)  
24. Nano Banana Pro image generation in Gemini: Prompt tips \- Google Blog, [https://blog.google/products-and-platforms/products/gemini/prompting-tips-nano-banana-pro/](https://blog.google/products-and-platforms/products/gemini/prompting-tips-nano-banana-pro/)  
25. Nano Banana | Google AI Studio, [https://aistudio.google.com/models/nano-banana](https://aistudio.google.com/models/nano-banana)  
26. Google Nano Banana Pro: State of the Art AI Image Editor | fal, [https://fal.ai/models/fal-ai/nano-banana-pro/edit](https://fal.ai/models/fal-ai/nano-banana-pro/edit)  
27. Google Nano Banana Pro: Advanced AI Image Editor | fal, [https://fal.ai/models/fal-ai/gemini-3-pro-image-preview/edit](https://fal.ai/models/fal-ai/gemini-3-pro-image-preview/edit)  
28. Gemini 3 Developer Guide \- Interactions API, [https://ai.google.dev/gemini-api/docs/generate-content/gemini-3](https://ai.google.dev/gemini-api/docs/generate-content/gemini-3)  
29. Nano Banana Pro AI Image Generator (Gemini 3 Pro) | PixMind, [https://www.pixmind.io/ai-image/nano-banana-pro](https://www.pixmind.io/ai-image/nano-banana-pro)  
30. Experiment with parameter values | Gemini Enterprise Agent Platform, [https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/prompts/adjust-parameter-values](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/prompts/adjust-parameter-values)  
31. accurate temperature support for Gemini models (e.g. Gemini 3 Pro needs to support temperature adjustment) · Issue \#953 · enricoros/big-AGI \- GitHub, [https://github.com/enricoros/big-AGI/issues/953](https://github.com/enricoros/big-AGI/issues/953)  
32. AI Cinema Storyboard Generator | Nano Banana Pro \- CloneViral, [https://www.cloneviral.ai/cinematic-storyboard-generator](https://www.cloneviral.ai/cinematic-storyboard-generator)  
33. How To Use Nano Banana Pro Like a Pro in 2026 \- Fal.ai, [https://fal.ai/learn/tools/how-to-use-nano-banana-pro](https://fal.ai/learn/tools/how-to-use-nano-banana-pro)  
34. Nano Banana Pro Image Generation \- API易文档中心, [https://docs.apiyi.com/en/api-capabilities/nano-banana-image/overview](https://docs.apiyi.com/en/api-capabilities/nano-banana-image/overview)  
35. Gemini 3 Pro Image (Nano Banana Pro) | Gemini Enterprise Agent Platform | Google Cloud Documentation, [https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-pro-image](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-pro-image)  
36. Media resolution | Gemini API \- Google AI for Developers, [https://ai.google.dev/gemini-api/docs/media-resolution](https://ai.google.dev/gemini-api/docs/media-resolution)  
37. Gemini 3 Developer Guide \- DEV Community, [https://dev.to/googleai/gemini-3-developer-guide-3j2k](https://dev.to/googleai/gemini-3-developer-guide-3j2k)  
38. Nano Banana 2 \- Next-Generation AI Image Generation & Editing by Google | fal \- Fal.ai, [https://fal.ai/nano-banana-2](https://fal.ai/nano-banana-2)  
39. Gemini 3 Pro Image Preview Alternative in 2026: What to Use Instead \- AI 
# CURRICULUM v2 — The Universe's Language Spine (A1 → B1), full lesson list

> **Status: DRAFT FOR LOCK (2026-07-29, v2).** v2 per Jayon's review of v1: **narrative removed entirely** (story lives in `NARRATIVE_BIBLE_seed.md` and is matched later, in-platform) and **every module decomposed into definite LESSONS** — each lesson = ONE 30–45s reel with ONE teachable pattern, so at creation time it is always exactly clear what a reel teaches. Basis: Jayon's four research docs + Goethe/BAMF milestones (A1 word list ≈650, verified) + Nicos Weg scale (~76 micro-lessons/level, verified) + the character bible's vocabulary domains.
> v1 (superseded): module-level matrix with narrative-affinity column.

## 0 · Locked design decisions (Jayon)
1 reel = 1 lesson (schema carries `format: single | mini_arc | campaign` for later expansion) · curriculum is **narrative-free** (matching happens in-platform) · stereotypes = tagged **encounter library** (tags live on the stereotype side, never on modules) · **guardrails not quotas** (skill-2q audits + flags).

## 1 · The 30–45s reality — what ONE reel can actually teach (the Lesson Law)
The physical container, from the research: at A1 pacing (80–100 WPM) a 30–45s reel holds **~40–75 spoken words ≈ 8–12 short lines** (A2 ~60–95, B1 ~75–110). Micro-learning laws: ONE objective per video · standalone nugget · new-word rate ~1.5/min. Therefore **one lesson =**
- **ONE target pattern** (a single sentence frame / structure), heard **2–3×** in natural variation (micro-redundancy);
- **≤3–5 new content words** (A1) / ≤6 (A2) / ≤8 (B1) — *everything else recycled*;
- one communicative **function** the pattern serves;
- one **exemplar target line** (the sentence the reel exists to teach — feeds the existing `target_line` contract);
- ends understood by a drop-in viewer with zero context.
A grammar **milestone** (e.g. Perfekt) is never one lesson — it spans several lessons chunk → pattern → contrast → productive (the spiral). Each module ends with a **Synthese** lesson: zero new items, pure recycling — these are the natural story-heavy slots.
**Vocab arithmetic (honest):** ~61 A1 lessons × ~4 new words ≈ **~250 actively taught** words vs the ~650-word Goethe A1 list — the remainder arrives passively (visual context + recycling). We are a comprehension-first series, not exam prep; if full list coverage ever becomes a goal, the `campaign` format absorbs it.

## 2 · The unit model
**Level** (A1/A2/B1) → **Module** (a thematic field + one grammar milestone cluster; 4–7 lessons) → **Lesson** (ONE reel, ONE pattern). Machine schema per lesson: `{id, module, title, pattern, function, exemplar_de, new_vocab_budget, recycles[], format:"single", status:"planned|made", episode_ref}`.

## 3 · THE LESSON LIST (the lock: 30 modules → 164 lessons)

### LEVEL A1 — 10 modules · 61 lessons
**A1.1 Ankunft** — sein (sg) · V2 · W-Fragen | greet, introduce, ask who/where
| id | Lesson | Teaches (ONE pattern) | Exemplar |
|---|---|---|---|
| A1.1.1 | Moin! | greetings + `Ich bin [Name]` | „Moin! Ich bin Rolf." |
| A1.1.2 | Wie heißt du? | `heißen`: question + answer (du) | „Wie heißt du?" — „Ich heiße Kati." |
| A1.1.3 | Wer bist du? | `du bist` / `Wer …?` | „Wer bist du?" — „Ich bin neu hier." |
| A1.1.4 | Was ist das? | deixis `Das ist …` | „Was ist das?" — „Das ist Bier." |
| A1.1.5 | Wo bin ich? | `Wo …?` + `in` + place | „Wo bin ich? Ich bin in Deutschland?!" |
| A1.1.6 | Woher kommst du? | `kommen aus` | „Woher kommst du?" — „Ähm … von weit weg." |

**A1.2 Wer bin ich?** — haben · Artikel · Negation · Zahlen | identify, deny, count
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| A1.2.1 | der, die, das | gender articles (the color-code debut) | „Der Zug. Die Straße. Das Brot." |
| A1.2.2 | ein / eine | indefinite article + sein | „Das ist eine Wurst. Ich bin eine Wurst!" |
| A1.2.3 | Ich habe … | `haben` + object | „Ich habe ein Problem." |
| A1.2.4 | kein / keine | negation with kein | „Ich habe kein Geld. Ich habe keine Idee." |
| A1.2.5 | nicht | negation with nicht | „Ich bin nicht wie sie." |
| A1.2.6 | Zahlen & Alter | numbers 1–100 + `Wie alt …?` | „Wie alt bist du?" — „Zweiundvierzig." |
| A1.2.7 | **Synthese: Wer bin ich?** | zero new — recycles the module | „Ich bin Bert. Ich bin ein Bier. Na und?" |

**A1.3 Essen & Trinken** — Akkusativ · möchten · bestellen | order, ask price, like
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| A1.3.1 | Hunger! | chunk `Hunger/Durst haben` | „Ich habe Hunger. Ich habe SO einen Hunger." |
| A1.3.2 | Ich möchte … | `möchten` + Akk (einen!) | „Ich möchte einen Kaffee." |
| A1.3.3 | Bitte & Danke | ordering ritual frame | „Einen Kaffee, bitte." — „Danke schön!" |
| A1.3.4 | Was möchtest du? | möchten question↔answer | „Was möchtest du?" — „Nichts. Egal." |
| A1.3.5 | Was kostet das? | `kosten` + prices (recycles Zahlen) | „Was kostet das?" — „Drei Euro fünfzig." |
| A1.3.6 | essen & trinken | present conjugation ich/du | „Ich esse das nicht. Ich trinke nur Bier." |
| A1.3.7 | **Synthese: Im Café** | zero new — full ordering scene | „Zwei Kaffee und ein Wasser, bitte." |

**A1.4 Orientierung** — feste Dativ-Präp. (zu/mit) · es gibt · Richtungen | ask/give the way
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| A1.4.1 | Wo ist …? | `Wo ist …?` + hier/da | „Wo ist der Bahnhof?" — „Da." |
| A1.4.2 | Ich gehe zu … | `gehen zu` + Dat (chunk) | „Ich gehe zum Bahnhof." |
| A1.4.3 | Mit dem Bus | `fahren mit` + Dat (chunk) | „Ich fahre mit dem Bus." |
| A1.4.4 | Es gibt … | existence frame | „Hier gibt es einen Club?!" |
| A1.4.5 | links, rechts, geradeaus | direction words (TPR-friendly) | „Immer geradeaus, dann links." |
| A1.4.6 | **Synthese: Der Weg** | zero new — asking the way scene | „Entschuldigung, wie komme ich zur Stadt?" |

**A1.5 Einkaufen** — Akk-Konsolidierung · Mengen · Sie-Frage | shop, pay, need
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| A1.5.1 | Ich brauche … | `brauchen` + Akk | „Ich brauche einen Plan. Und Brot." |
| A1.5.2 | Wie viel? | quantity + teuer/billig | „Wie viel kostet das? Das ist teuer!" |
| A1.5.3 | Ich nehme … | decision verb + Akk | „Okay. Ich nehme das." |
| A1.5.4 | Das Pfand | Pfand system vocab (Flasche, zurück) | „Die Flasche? Das ist Geld!" |
| A1.5.5 | Haben Sie …? | formal Sie-question in shops | „Haben Sie das auch in Schwarz?" |
| A1.5.6 | **Synthese: Im Supermarkt** | zero new — shopping run | „Ich brauche nur eine Sache …" |

**A1.6 Wohnen** — Possessive · Zimmer · erste Adjektive | describe home
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| A1.6.1 | mein & dein | possessives + sein | „Das ist mein Zimmer. Das ist dein Problem." |
| A1.6.2 | Ich wohne … | `wohnen in` + rooms | „Ich wohne jetzt hier. In einer Bäckerei." |
| A1.6.3 | Möbel | furniture nouns + es gibt (recycled) | „Es gibt ein Bett, einen Tisch — fertig." |
| A1.6.4 | steht & liegt | static position (light chunks) | „Der Schlüssel liegt auf dem Tisch." |
| A1.6.5 | groß, klein, schön | predicative adjectives | „Das Zimmer ist klein. Aber es ist schön." |
| A1.6.6 | **Synthese: Meine Wohnung** | zero new — home tour | „Willkommen! Das ist … alles." |

**A1.7 Mein Tag** — Uhrzeit · trennbare Verben · Wochentage | tell time, routines
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| A1.7.1 | Wie spät ist es? | clock time (full hours) | „Es ist sieben Uhr." |
| A1.7.2 | Um sieben Uhr | `um … Uhr` time adverbial | „Ich komme um sieben. Pünktlich!" |
| A1.7.3 | Ich stehe auf | FIRST separable verb (the bracket!) | „Ich stehe um sechs Uhr auf." |
| A1.7.4 | einkaufen & anrufen | separables consolidated | „Ich rufe dich an. Später." |
| A1.7.5 | Die Woche | weekdays + `am` | „Am Montag? Nein. Am Dienstag? Nein." |
| A1.7.6 | **Synthese: Ein Tag** | zero new — routine montage | „Aufstehen. Kaffee. Arbeiten. Schlafen." |

**A1.8 Regeln** — Modalverben (können/müssen/dürfen) · Imperativ Sie | rules & permission
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| A1.8.1 | Ich kann … | `können` + Inf (bracket) | „Ich kann das. Glaube ich." |
| A1.8.2 | Kannst du …? | können question + negative | „Kannst du helfen?" — „Ich kann nicht." |
| A1.8.3 | Ich muss … | `müssen` + Inf | „Ich muss nach Hause. Wirklich." |
| A1.8.4 | Man darf das nicht! | `dürfen` + `man` (the rules engine) | „Man darf hier nicht parken. NIE." |
| A1.8.5 | Warten Sie! | Imperativ Sie | „Warten Sie! Kommen Sie mit!" |
| A1.8.6 | **Synthese: Die Regeln** | zero new — rule-encounter gauntlet | „Regeln sind Regeln." |

**A1.9 Wetter & Small Talk** — es-Sätze · gern · Partikel-Chunks | comment, chat
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| A1.9.1 | Das Wetter | `Es regnet / Die Sonne scheint` | „Es regnet. Natürlich regnet es." |
| A1.9.2 | Kalt. | weather adjectives + `Es ist …` | „Es ist kalt." — „Jo. Kalt." |
| A1.9.3 | Ach so! Doch! | discourse particles as chunks | „Doch!" — „Ne." — „Doch." |
| A1.9.4 | Ich trinke gern … | `gern` (liking an activity) | „Ich trinke gern Kaffee. Allein." |
| A1.9.5 | Schönes Wetter, oder? | small-talk frame + tag `oder?` | „Schönes Wetter, oder?" — „…Jo." |
| A1.9.6 | **Synthese: Die Bushaltestelle** | zero new — small-talk scene | „Der Bus kommt nicht." — „Ich weiß." |

**A1.10 Zusammen** — wir · Einladung · Perfekt-Chunk | invite, accept, meet
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| A1.10.1 | Kommst du mit? | `mitkommen` invitation | „Kommst du mit?" |
| A1.10.2 | Ja, gern! / Leider nicht | accept & decline frames | „Ja, gern!" — „Nein, leider nicht." |
| A1.10.3 | Wir sind … | FIRST plural `wir` | „Wir sind … gleich?!" |
| A1.10.4 | Was ist passiert? | Perfekt as unanalyzed CHUNK | „Was ist passiert?!" |
| A1.10.5 | **Synthese A1: Wir vier** | zero new — level finale | „Wir sind nicht allein." |

### LEVEL A2 — 10 modules · 56 lessons
**A2.1 Was ist passiert?** — Perfekt | recount & recap
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| A2.1.1 | Ich habe … gemacht | Perfekt regular (haben + ge-t) | „Ich habe das nicht gemacht!" |
| A2.1.2 | gegessen, getrunken, gesehen | Perfekt irregular (common) | „Ich habe alles gesehen." |
| A2.1.3 | Ich bin gegangen | Perfekt with sein (movement) | „Ich bin einfach gegangen." |
| A2.1.4 | eingekauft & aufgestanden | separable participles | „Ich bin um sechs aufgestanden!" |
| A2.1.5 | Was hast du gemacht? | Perfekt questions | „Was hast du gestern gemacht?" |
| A2.1.6 | **Synthese: Der Rückblick** | zero new — the recap engine debut | „Also: Wir sind hier gelandet, und dann …" |

**A2.2 Unterwegs** — Wechselpräpositionen (wohin/wo) · Transit | navigate, complain
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| A2.2.1 | Einmal nach …, bitte | ticket frame + `nach` | „Einmal nach Hamburg, bitte." |
| A2.2.2 | Wohin? In die Stadt | direction = Akk | „Ich fahre in die Stadt." |
| A2.2.3 | Wo? In der Stadt | location = Dat (the minimal pair!) | „Ich bin in der Stadt. Schon wieder." |
| A2.2.4 | Umsteigen | transit verbs + Wo muss ich …? | „Wo muss ich umsteigen?" |
| A2.2.5 | Verspätung! | delay frames (recycles haben) | „Der Zug hat zehn Minuten Verspätung." |
| A2.2.6 | **Synthese: Die Reise** | zero new — journey scene | „Falscher Zug. Wieder." |

**A2.3 Die WG** — stellen/legen/hängen vs stehen/liegen/hängen · Dativpronomen | arrange, own
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| A2.3.1 | Ich stelle das hierhin | placement + Akk (stellen/legen) | „Ich stelle die Lampe in die Ecke." |
| A2.3.2 | Es steht da | position + Dat (stehen/liegen) | „Die Lampe steht in der Ecke. Perfekt." |
| A2.3.3 | hängen | both directions with hängen | „Ich hänge das Bild an die Wand." |
| A2.3.4 | Wer muss …? | chores + müssen recycled | „Wer muss die Küche putzen?" — Schweigen. |
| A2.3.5 | Das gehört mir! | Dativ pronouns mir/dir + gehören | „Das gehört mir!" — „Nein, das gehört uns." |
| A2.3.6 | **Synthese: Einzugstag** | zero new — moving-in scene | „Links mein Bereich. Rechts dein Bereich." |

**A2.4 Gesundheit** — Reflexive · weh tun · Imperativ du | describe symptoms, advise
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| A2.4.1 | Mein Kopf tut weh | `weh tun` + body parts | „Mein Kopf tut weh. Alles tut weh." |
| A2.4.2 | Ich fühle mich … | first reflexive (sich fühlen) | „Ich fühle mich nicht gut." |
| A2.4.3 | Was fehlt Ihnen? | doctor frame (Dat chunk) | „Was fehlt Ihnen denn?" |
| A2.4.4 | Du sollst … | `sollen` (advice) | „Du sollst im Bett bleiben." |
| A2.4.5 | Trink Tee! | Imperativ du | „Trink Tee! Schlaf! Jetzt!" |
| A2.4.6 | **Synthese: Krank** | zero new — sick-day scene | „Ich bin NICHT krank." — hustet. |

**A2.5 Arbeit** — wollen · weil (Verb-Ende!) | apply, give reasons
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| A2.5.1 | Ich arbeite als … | job frame + als | „Ich arbeite jetzt als Bäcker. Ironisch." |
| A2.5.2 | Ich will … | `wollen` (vs möchten) | „Ich will nach Hause. Ich will das wirklich." |
| A2.5.3 | …, weil ich Geld brauche | `weil` + VERB-FINAL (the big one) | „Ich arbeite, weil ich Geld brauche." |
| A2.5.4 | Warum? Weil … | weil-answers practice | „Warum bist du müde?" — „Weil ich arbeite!" |
| A2.5.5 | Ich suche einen Job | application small frames (recycles) | „Ich suche einen Job. Irgendeinen Job." |
| A2.5.6 | **Synthese: Der erste Arbeitstag** | zero new | „Der Chef sagt, ich bin zu langsam. Ich? Zu langsam?" |

**A2.6 Feste** — dass · Einladungen · Datum | invite, hope, celebrate
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| A2.6.1 | Ich lade dich ein | `einladen` (separable) + Akk | „Ich lade euch alle ein!" |
| A2.6.2 | Ich hoffe, dass … | `dass` + verb-final | „Ich hoffe, dass du kommst." |
| A2.6.3 | Am ersten Mai | dates + ordinals | „Das Fest ist am ersten Mai." |
| A2.6.4 | Prost! | toasting culture frames | „Prost! Auf uns! Auf Dienstag!" |
| A2.6.5 | Ich schenke dir … | Dat + Akk double object | „Ich schenke dir eine Flasche. Mit Pfand." |
| A2.6.6 | **Synthese: Das Fest** | zero new — the party | „Das ist … eigentlich schön hier." |

**A2.7 Früher & Heute** — Präteritum (war/hatte/Modalverben) | narrate the past
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| A2.7.1 | Ich war … | `war` | „Früher war ich glücklich. Glaube ich." |
| A2.7.2 | Ich hatte … | `hatte` | „Ich hatte alles. Ich hatte Freunde." |
| A2.7.3 | konnte, musste, wollte | modal Präteritum batch | „Ich konnte tanzen. Die ganze Nacht." |
| A2.7.4 | Früher …, jetzt … | contrast frame | „Früher Techno. Jetzt … Fahrpläne." |
| A2.7.5 | **Synthese: Unsere Welten** | zero new — flashback scene | „Erzähl. Wie war deine Welt?" |

**A2.8 Ämter & Papiere** — Formulare · „Ich hätte gern" (Chunk) · Prozesse | register, request politely
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| A2.8.1 | Das Formular | bureaucracy nouns + ausfüllen | „Füllen Sie das Formular aus. In Blockschrift." |
| A2.8.2 | Ich hätte gern … | Konjunktiv II as POLITENESS CHUNK | „Ich hätte gern einen Termin." |
| A2.8.3 | Der Termin | appointment frames + warten | „Sie brauchen einen Termin für den Termin." |
| A2.8.4 | Sie müssen zuerst … | process sequencing (zuerst/dann) | „Sie müssen zuerst zu Schalter B." |
| A2.8.5 | **Synthese: Der Antrag, Teil 1** | zero new — bureaucracy odyssey | „Nummer 87?" — „JA! Endlich!" |

**A2.9 Stil & Vergleich** — Komparativ/Superlativ · gefallen | compare, prefer, judge
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| A2.9.1 | Ich trage … | clothing + tragen | „Ich trage nur Schwarz." |
| A2.9.2 | schöner als … | comparative | „Das ist schöner als das. Objektiv." |
| A2.9.3 | am schönsten | superlative | „Und das ist am schönsten. Natürlich meins." |
| A2.9.4 | gern, lieber, am liebsten | preference scale | „Ich mag Tee gern, Kaffee lieber." |
| A2.9.5 | Das gefällt mir | `gefallen` + Dat | „Das gefällt mir. Nein. Doch. Nein." |
| A2.9.6 | **Synthese: Das Umstyling** | zero new — makeover scene | „Nein. Aber nett." |

**A2.10 Der Hinweis** — werden (Futur) · Spekulation | promise, speculate
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| A2.10.1 | Ich werde … | `werden` + Inf (future) | „Ich werde einen Weg finden." |
| A2.10.2 | Ich verspreche, dass … | promising (recycles dass) | „Ich verspreche, dass wir nach Hause kommen." |
| A2.10.3 | Vielleicht … | speculation adverbs (vielleicht/bestimmt) | „Vielleicht ist das ein Zeichen. Bestimmt!" |
| A2.10.4 | **Synthese A2: Der Hinweis** | zero new — level finale | „Da. Schaut. Was IST das?" |

### LEVEL B1 — 10 modules · 47 lessons
**B1.1 Der Plan** — Infinitiv + zu · um…zu | propose, commit
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| B1.1.1 | Es ist wichtig, … zu … | Infinitiv+zu | „Es ist wichtig, ruhig zu bleiben." |
| B1.1.2 | Wir versuchen, … zu … | verbs + zu (versuchen/anfangen) | „Wir versuchen, das zu verstehen." |
| B1.1.3 | um … zu … | purpose clause | „Wir sparen, um nach Hause zu kommen." |
| B1.1.4 | Zuerst, dann, danach | process ordering (recycled, denser) | „Zuerst der Plan. Dann das Geld. Danach: Heimat." |
| B1.1.5 | **Synthese: Der Plan steht** | zero new | „Das klappt nie." — „Doch." |

**B1.2 Die Bewerbung** — Relativsätze (Nom/Akk) · formelles Register | apply, self-present
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| B1.2.1 | Sehr geehrte … | formal register frames | „Sehr geehrte Damen und Herren …" |
| B1.2.2 | Der Mann, der … | relative clause Nominativ | „Ich bin jemand, der nie aufgibt." |
| B1.2.3 | Der Job, den ich … | relative clause Akkusativ | „Das ist der Job, den ich will." |
| B1.2.4 | Meine Stärke ist … | self-presentation frames | „Meine Stärke? Ich sage die Wahrheit." |
| B1.2.5 | **Synthese: Das Vorstellungsgespräch** | zero new | „Wo sehen Sie sich in fünf Jahren?" — „Zu Hause." |

**B1.3 Meinungen** — obwohl/trotzdem · zustimmen/widersprechen | argue politely
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| B1.3.1 | Ich finde, dass … | opinion frames (recycles dass) | „Meiner Meinung nach ist das falsch." |
| B1.3.2 | …, obwohl … | `obwohl` (concessive, verb-final) | „Ich bleibe ruhig, obwohl das Unsinn ist." |
| B1.3.3 | Trotzdem | contrast adverb pair | „Es ist schwer. Trotzdem machen wir weiter." |
| B1.3.4 | Ich stimme dir zu | agree/disagree + Dat | „Da bin ich anderer Meinung." |
| B1.3.5 | **Synthese: Die Debatte** | zero new — bleiben oder gehen? | „Abstimmung. Wer will bleiben?" |

**B1.4 Wie es funktioniert** — Passiv | explain processes
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| B1.4.1 | So macht man das | `man`-process (bridge, recycled) | „So macht man das hier. Immer so." |
| B1.4.2 | Es wird gemacht | Passiv Präsens | „Brot wird hier um vier Uhr gebacken." |
| B1.4.3 | Es muss gemacht werden | Passiv + Modal | „Das muss zuerst geprüft werden." |
| B1.4.4 | Es wurde gemacht | Passiv Präteritum | „Die Tür wurde geschlossen. Von wem?" |
| B1.4.5 | **Synthese: Die Maschine** | zero new — process explained | „Und DANN wird der Strom eingeschaltet." |

**B1.5 Der Antrag** — Genitiv · wegen/während | handle authorities
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| B1.5.1 | des & der | Genitiv possession | „Das ist der Anfang der Geschichte." |
| B1.5.2 | wegen | `wegen` + Gen | „Wegen des Wetters? Wirklich?" |
| B1.5.3 | während | `während` + Gen | „Während der Woche? Unmöglich." |
| B1.5.4 | Antrag stellen | official verbs (stellen/ablehnen/genehmigen) | „Ihr Antrag wurde abgelehnt." (recycles Passiv!) |
| B1.5.5 | **Synthese: Der Antrag, Teil 2** | zero new — the document quest | „Formular 12b. Natürlich." |

**B1.6 Was wäre wenn** — Konjunktiv II (voll) | dream, hypothesize, regret
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| B1.6.1 | Ich wäre / ich hätte | KII sein/haben | „Ich wäre jetzt im Club. Ich hätte Ruhe." |
| B1.6.2 | Ich würde … | würde + Inf | „Ich würde alles anders machen." |
| B1.6.3 | Wenn …, dann … | full conditional | „Wenn ich zu Hause wäre, würde ich tanzen." |
| B1.6.4 | Ich wünschte … | wish frame | „Ich wünschte, ihr wärt alle da gewesen." |
| B1.6.5 | **Synthese: Heimweh** | zero new — the KII heart | „Und wenn es keinen Weg zurück gibt?" |

**B1.7 Medien** — Relativsatz Dativ · indirekte Fragen | report, react
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| B1.7.1 | …, dem ich … | relative clause Dativ | „Der Typ, dem ich geholfen habe, hat gefilmt." |
| B1.7.2 | Ich weiß nicht, ob … | indirect questions (ob/wann/wo) | „Ich weiß nicht, ob das gut ist." |
| B1.7.3 | Es wird berichtet, dass … | media frames (recycles Passiv+dass) | „Im Internet wird berichtet, dass wir … seltsam sind." |
| B1.7.4 | **Synthese: Berühmt?** | zero new | „Eine Million Views." — „Von was?!" |

**B1.8 Herkunft** — Plusquamperfekt · nachdem/seitdem | layered past, reveal
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| B1.8.1 | Ich hatte … gemacht | Plusquamperfekt | „Ich hatte so etwas noch nie gesehen." |
| B1.8.2 | Nachdem … | `nachdem` + Plusq. | „Nachdem wir gelandet waren, war alles anders." |
| B1.8.3 | Seitdem | `seit/seitdem` | „Seitdem wir hier sind, träume ich laut." |
| B1.8.4 | **Synthese: Was vorher geschah** | zero new — the origin reveal | „Es hat nicht bei euch angefangen." |

**B1.9 Der Streit** — Konfliktsprache · damit · Reparatur | de-escalate, repair
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| B1.9.1 | Du hast immer … | accusation frames + Entschuldigung | „Es tut mir leid, dass ich laut war." |
| B1.9.2 | Was meinst du damit? | misunderstanding repair | „Was meinst du damit?" — „Ich meinte nur …" |
| B1.9.3 | …, damit … | `damit` (purpose, verb-final) | „Ich sage das, damit wir zusammenbleiben." |
| B1.9.4 | Lass uns … | reconciliation frame | „Lass uns nochmal von vorn anfangen." |
| B1.9.5 | **Synthese: Der Streit** | zero new — the dark night | Schweigen. Dann: „Bleibst du?" |

**B1.10 Die Entscheidung** — Abwägen · Synthese der Stufe | decide, justify, close
| id | Lesson | Teaches | Exemplar |
|---|---|---|---|
| B1.10.1 | Einerseits … andererseits | weighing frame | „Einerseits Heimat. Andererseits … ihr." |
| B1.10.2 | Ich habe mich entschieden | `sich entscheiden` + zu (recycles) | „Ich habe mich entschieden, zu bleiben." |
| B1.10.3 | Abschied & Bleiben | farewell/staying frames | „Das hier ist jetzt auch ein Zuhause." |
| B1.10.4 | **GRANDE SYNTHESE: Die Entscheidung** | zero new — series question answered in full spiral (KII + Passiv + Relativ) | „Wenn wir gehen würden — was wäre dann mit allem, was hier gebaut wurde?" |

**Totals: A1 = 61 · A2 = 56 · B1 = 47 → 164 lessons (+ Season 0 intro reels ≈ 168–170 total).**

## 4 · Guardrails (per level; skill-2q audits + flags)
| | A1 | A2 | B1 |
|---|---|---|---|
| Spoken words / reel (at pace) | ~40–75 | ~60–95 | ~75–110 |
| MLU (max words/sentence) | 8 | 12 | 15 |
| Pace (WPM) | 80–100 | 100–130 | 130–150 |
| New active words / lesson | ≤5 | ≤6 | ≤8 |
| Target pattern repetitions | ≥2 | ≥2 | ≥2 |
| Prohibited until introduced | Perfekt*, Nebensätze, Genitiv, Passiv, KII* | Genitiv, Passiv, KII (beyond „hätte gern"), Plusquamperfekt | — |
| Proper nouns | fixed cast; ≤1 new name/module | same | same |
*Chunks allowed exactly where the lesson list says so (spiral: chunk → analyzed → productive).

## 5 · Stereotype encounter library
Tags live on the STEREOTYPE side (never on modules): `cefr_band` · `module_affinity` (module ids whose *setting* hosts it) · `encounter_type` (rule/ritual/food/social/bureaucratic/transit/…). Showrunner offers 0–3 fitting encounters during lesson ideation; coverage tracked; unused is fine. Batch-tagging = an in-platform AI job after lock, human-reviewed.

## 6 · Post-lock build plan (unchanged)
`resources/curriculum.json` (this list, machine-readable, `status: planned|made` per lesson) + registry pin → `UNIVERSE_STATE` artifact → Showrunner agent (proposes next lesson + story options; Strategist chat consumes them) → Step 01 becomes "Next lesson" → skill-2q guardrail audit → stereotype batch-tagging.

## 7 · Open (deliberately)
All narrative (see `NARRATIVE_BIBLE_seed.md`) · Kati's intro · subtitle policy per level (static-clause vs karaoke conflict — decide at subtitle-engine revisit) · posting cadence · exemplar lines are *seeds*, freely rewritable at creation time.

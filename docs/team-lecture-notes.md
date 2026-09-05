# Lecture Notes: Understanding Our Project Completely
### For the whole team — read this once fully, then keep it as a reference

*How to use this: Read Part 1 first even if you already "get it" — it builds the shared mental model everyone needs to speak from the same page in front of judges. Then Parts 2–5 build outward from there.*

---

## PART 1: Understanding the Problem (Start Here)

**1.1 — The one-sentence version**
Different network devices (routers, firewalls, switches) from different companies (Cisco, Juniper, Palo Alto, etc.) each have their own "language" for settings. We're building a tool that reads any device's settings file, checks it against security rules, and — this is the important part — **teaches itself to understand brands it has never seen before**, instead of a programmer having to hand-code support for every single brand.

**1.2 — Why this is a real problem (not a made-up one)**
1. Big companies don't use one brand of device — they use a mix, built up over years.
2. Security rulebooks (CIS, NIST, STIG, ISO) tell you *what* good security looks like (e.g., "disable Telnet, use SSH version 2, log all admin logins").
3. Checking whether a device actually follows these rules today means either:
   - A human manually reading configuration files line by line (slow, boring, error-prone), OR
   - Buying expensive software that only understands one or two brands, and breaks the moment the company buys a new brand of device.
4. Every time a vendor releases a firmware update or a company buys a new type of device, existing tools need to be reprogrammed. That's expensive and slow.

**1.3 — The key insight our project is built on**
This is **not** really a "compliance checking" problem. Compliance checking (comparing a value against a rule) is the *easy* part — that's just an if-statement.
The **hard** part, and the part that makes this interesting, is: **"how do you understand text you've never seen the shape of before?"**
That's a language-understanding problem, which is why AI/NLP is genuinely necessary here — not just decoration to make the project sound fancy.

**1.4 — An analogy to hold onto**
Think of it like a **translator who is also a student**.
- If someone speaks Spanish or French, the translator already knows those — instant translation (this is like a device from a *known* vendor, e.g., Cisco).
- If someone speaks a language the translator has never heard, the translator doesn't just guess randomly and confidently mistranslate — they say "I don't know this word, can you tell me what it means?" and then remember it forever after (this is our "training loop" for *unknown* vendors).
- That's the whole product, in one image.

---

## PART 2: The Complete Solution, Explained Step by Step

*Walk through this exactly in order — this is the actual path a config file takes through our system, start to finish.*

**Step 1 — Upload**
- The user uploads a device's configuration file (a plain text file with settings) — either one file or many at once.
- Point: at this stage, we don't yet know exactly what device/vendor this is, but we make a smart guess (e.g., if we see the word "interface GigabitEthernet," that's a strong hint it's Cisco-style; if we see "set system," that's Juniper-style).

**Step 2 — Normalization (the "translator" step)**
- The system goes through the file line by line and tries to understand what each line *means* (not just what it *says*).
- It does this in three attempts, cheapest first:
  1. **Exact pattern match** — "I've seen this exact style of line before, I know exactly what it means." (Fast, free, certain.)
  2. **Similar-meaning match** — "I haven't seen this exact line, but it looks very similar in meaning to something I know." (Uses AI to compare meaning, not just exact words.)
  3. **Ask an AI model for a best guess** — only used as a last resort, and *never trusted automatically* — it's just a suggestion for a human to confirm.
- Every line ends up in one of two buckets: **understood** (mapped to a standard meaning) or **not understood yet** (flagged for training).
- Point: nothing is ever silently guessed and treated as fact — this is a deliberate design choice for trustworthiness.

**Step 3 — The Standard Format ("Security Baseline Model")**
- Whatever vendor the config came from, once Step 2 is done, we now have the *same* clean, standard format — a simple structured summary like: "SSH version = 2," "Telnet enabled = false," "Logging enabled = true," and so on.
- Point: this standard format is the heart of the whole system. Everything before it (Steps 1–2) exists to *produce* this. Everything after it (Steps 4–5) exists to *consume* it. If two people on the team disagree about anything, check: does it match this format? That resolves most confusion.

**Step 4 — Compliance Checking**
- We take that standard format and compare it against a checklist of rules from a chosen framework (for our demo: CIS).
- Example rule: "SSH version must equal 2." We check the standard format's SSH value against this rule. Pass or fail. Simple.
- This is deliberately built as a **checklist stored as data** (a spreadsheet/table of rules), not as code — meaning adding a new rule or a whole new framework later is just adding a new row/file, not rewriting the program.

**Step 5 — The Training Loop (our biggest differentiator — pay attention here)**
- If Step 2 found lines it couldn't understand, those get shown to a human on a simple screen: "Here's a line I don't understand — what does it mean?"
- The human picks from a list of categories (e.g., "this is about SSH," "this is about logging") or types a new category.
- The moment they confirm it, the system **immediately** re-checks the file and that line is now understood.
- Crucially: **we remember this forever.** The next time *any* config from that same vendor has a similar line, the system already knows it — no human needed again.
- This is what makes it "AI that learns" instead of "a static parser someone hardcoded."

**Step 6 — Reporting**
- Once everything is checked, we generate a clean PDF: which device, what passed, what failed, how serious each failure is, and exactly what command to type to fix it.
- Point: this is the "so what" of the whole system — a security team doesn't want raw data, they want "tell me what's broken and how to fix it," in a report they can hand to their boss.

---

## PART 3: Why We Made These Design Choices (in plain language)

**3.1 — Why not just use ChatGPT/an LLM for everything?**
- Cost: calling an AI model for every single line of every config, every time, adds up fast and is slow.
- Trust: AI models can be confidently wrong ("hallucinate"). If we let it silently decide pass/fail, one wrong guess could tell a company their firewall is secure when it isn't — that's dangerous, not just embarrassing.
- Our answer: use the cheap, certain method (pattern matching) first for the 80% of cases that are easy, and only reach for AI on the hard 20% — and even then, a human confirms it before we trust it.

**3.2 — Why do we insist a human confirms unknown lines, instead of the AI just deciding?**
- Because this is a *security* tool. A false "pass" is worse than no tool at all — it gives false confidence.
- Also, once one human confirms a mapping, the system never needs to ask again for that pattern — so we're not asking humans to do this forever, just once per new pattern.

**3.3 — Why store rules as data (spreadsheets/config files) instead of hardcoding them in the program?**
- Because the entire pitch of this project is "works with new vendors and new rulebooks without reprogramming." If our rules were hardcoded, we'd be exactly the kind of rigid, vendor-locked tool we're claiming to replace.
- Practical benefit for us: a non-programmer on the team (or a judge asking "can you add NIST right now?") can literally watch us add a new framework by adding a new file, live, in the demo if needed.

**3.4 — Why did we choose to demo with file upload instead of connecting live to real devices?**
- Connecting live to real devices needs credentials, network access, and works differently for every device brand — it's a lot of moving parts that could fail live on stage.
- Uploading a file is simpler, safer, and lets us focus the demo on what actually matters: the AI understanding and the training loop.
- We'll mention live connection as "what we'd build next" — this shows judges we understand the bigger picture without risking the demo.

**3.5 — Why did we pick only ONE framework (CIS) and 2–3 vendors for the actual working demo, instead of promising support for everything?**
- With 5 days, trying to build genuine depth across 4 frameworks and unlimited vendors means everything ends up shallow and broken.
- A judge is far more impressed by "watch it learn a brand-new vendor live, correctly, in front of you" than by "we support everything" said with a straight face and nothing working underneath.
- Depth on the hard part (the learning loop) beats breadth everywhere else.

---

## PART 4: Execution Plan — Phase by Phase

*This is what each person does, and in what order, over our 5 days. Read this as the "who does what, when."*

**Team roles (recap):**
1. **System Architect / Lead** — big picture, integration, architecture document.
2. **AI/NLP Engineer** — builds the "translator" (normalization engine).
3. **Backend Developer** — builds the compliance checker + PDF report generator.
4. **Frontend/UI Developer** — builds the upload screen, training screen, and results screen.
5. **Research + Presentation Lead** — researches the actual security rules, writes the PPT and documents.

**Phase 1 (Day 1) — Understand and Design**
- Everyone agrees on exactly what the "standard format" (Step 3 above) looks like — this is the single most important agreement of the whole project, because everyone else's work depends on it.
- Research lead picks the ~15–20 specific security rules we'll actually check (not all of CIS — a focused, meaningful subset).
- Architect sketches the full pipeline (Steps 1–6 above) as a diagram everyone can see.

**Phase 2 (Day 2) — Build the Core, Separately**
- AI/NLP engineer builds the first version of Step 2 (understanding known vendor lines).
- Backend developer builds Step 4 (checking the standard format against rules).
- Frontend developer builds Step 1 (the upload screen).
- Point: these three can work in parallel because they're all building *around* the standard format agreed in Phase 1 — this is why that agreement mattered so much.

**Phase 3 (Day 3) — Build the Differentiator**
- AI/NLP engineer and backend developer together build Step 5 (the training loop) — this is the trickiest part because it involves two people's code talking to each other in real time.
- Frontend developer builds the training screen (the "teach me" interface).
- Architect starts connecting all the pieces into one working pipeline.

**Phase 4 (Day 4) — Connect Everything and Test**
- Backend developer finishes Step 6 (PDF report).
- Whole pipeline gets tested end-to-end: upload → understand → check → (train if needed) → report.
- We deliberately test with a vendor config nobody has seen before, to prove the training loop actually works, not just in theory.
- Research lead finalizes the presentation slides and starts writing the demo script.

**Phase 5 (Day 5) — Polish and Rehearse**
- Full team rehearses the live demo at least twice.
- Final touches: PDF report formatting, slide visuals, demo video recording.
- Everyone should be able to explain **any** part of the system, not just their own part — because judges can ask anyone anything.

---

## PART 5: Be Ready to Answer These (Judges Will Ask)

Go through these out loud as a team — everyone should be able to answer any of these, not just the "owner" of that part:

1. **"What happens if I upload a config from a vendor you've literally never mentioned?"**
   → It gets scanned with what we know, unknown lines get flagged, and we can train it live, right now, in front of you.

2. **"How is this different from just using ChatGPT to read the config?"**
   → Cost, speed, and trust — we only use AI as a last resort suggestion that a human confirms, not as the sole decision-maker.

3. **"How do I know your pass/fail result is actually correct?"**
   → Every result traces back to the exact line in the original file that caused it — nothing is a black-box guess.

4. **"What if the AI learns something wrong from a bad human input?"**
   → A human explicitly confirms every new mapping before it's saved — nothing is auto-learned without confirmation.

5. **"Can this scale to hundreds of devices / real enterprise use?"**
   → Yes — architecture is modular, rules are stored as data not code, and the same pipeline works whether it's 1 device or 1,000; live device polling (rather than file upload) is our next-phase roadmap item.

6. **"Why did you only support one framework (CIS) in the demo?"**
   → We built one solid taxonomy of security controls and map it to CIS for this demo — the same taxonomy maps to NIST, STIG, and ISO by adding new mapping files, which we can show.

---

## Closing Point for the Team
If you remember nothing else from this document, remember this one sentence, because it's the answer to almost every question you'll get:
**"We built a system that understands new things it's never seen before, admits when it doesn't know something instead of guessing, and gets smarter every time a human teaches it — once."**
Everything else in this project exists to make that one sentence true and demonstrable.

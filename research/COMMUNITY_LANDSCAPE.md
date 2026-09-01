# Adjacent Community Landscape Scan

**Task:** R3 (Wave R) — positioning input for Practice
**As of:** 2026-09-01
**Method:** Every community below was checked against its official/community homepage or primary repository on 2026-09-01 via direct fetch. Each factual claim carries its source URL. Figures quoted from a source's own pages are labeled **self-reported** — they are what the source displays, not independent measurements. Anything that could not be confirmed from the cited source is written **not verified**.
**Status of gap statements:** All "what a practitioner does not get" statements and the positioning gaps at the end are **analysis**, not fact. They are judgments drawn from the cited surface descriptions, offered as positioning input only. They do not propose product features and must not be read as a commitment to build anything in `NON_GOALS.md`.

No statement in this report is a claim about Practice's own features or traction.

---

## 1. Open-source project communities

### 1.1 Hugging Face

Source: https://huggingface.co/forums (site navigation) and https://discuss.huggingface.co (forum home), as of 2026-09-01.

What it offers:

- Hugging Face's site navigation lists, under "Community": Blog, Posts, Daily Papers, Hardware, Learn, Discord, Forum (discuss.huggingface.co), and GitHub (https://github.com/huggingface). Source: https://huggingface.co/forums, as of 2026-09-01.
- The forum at https://discuss.huggingface.co is a Discourse instance with categories including Spaces, Beginners, Tokenizers, Show and Tell, Research, Datasets, Models, "Awesome paper", and Community Calls. Source: https://discuss.huggingface.co, as of 2026-09-01.
- First-page topics on the forum home carried activity dates from 2026-08-27 through 2026-09-01 at the time of fetch. Source: https://discuss.huggingface.co, as of 2026-09-01.
- Member counts, topic totals, and activity levels for the forum or Discord: not verified.

Formats: forum threads (Q&A, tutorials posted as "Show and Tell", research discussion), daily paper listings, Discord chat, an education portal ("Learn") linked from site navigation, and code/model repositories on GitHub. The dominant learning format is thread-based Q&A around Hugging Face's own platform (Spaces, quotas, model cards, datasets).

What a practitioner does not get there (analysis): knowledge is tied to the Hugging Face platform and its roadmap; forum threads answer "how do I make X work here" rather than distilling transferable methods; there is no visible maturity or evidence process by which a community answer becomes a reusable, tested method; thread knowledge is not versioned or promoted through recorded trials.

### 1.2 LangChain

Source: https://www.langchain.com/community, as of 2026-09-01.

What it offers:

- A community-run help forum (forum.langchain.com), a community Slack, an events calendar with meetups and workshops (lu.ma/langchain), and a "LangChain Academy" education site. Source: https://www.langchain.com/community, as of 2026-09-01.
- Structured volunteer programs: "Community Champions" (contributors to the open-source packages), "LangChain Experts" (volunteer question-answerers on the forum and Slack), and "Ambassadors" who host local meetups and create educational content. Source: https://www.langchain.com/community, as of 2026-09-01.
- The page states that over 3,500 contributors have built the open-source frameworks (self-reported on that page). Source: https://www.langchain.com/community, as of 2026-09-01.
- Independent member counts for forum/Slack: not verified.

Formats: Q&A forum threads, Slack discussion, vendor-run courses (Academy), YouTube how-tos, documentation, meetup talks, and contributor recognition programs. Learning is oriented around LangChain/LangGraph/LangSmith products.

What a practitioner does not get there (analysis): scope is one framework family plus its commercial platform; a method validated on this stack carries no portable, vendor-neutral record; community programs reward contribution to the product (PRs, docs) rather than tested, reusable practice knowledge that works across stacks; there is no model-agnostic governance under which shared methods outlive product changes.

### 1.3 LlamaIndex

Source: https://github.com/run-llama/llama_index (README and repository page), as of 2026-09-01.

What it offers:

- An open-source framework for building agentic applications, with the README listing community channels: Discord, Reddit (r/LlamaIndex), X, and LinkedIn; the repository also hosts GitHub Discussions and Issues/PRs. Source: https://github.com/run-llama/llama_index, as of 2026-09-01.
- The README describes a plugin ecosystem: a starter package plus `llama-index-core` with over 300 integration packages ("LlamaHub") covering different LLM, embedding, and vector-store providers (self-reported on that page). Source: https://github.com/run-llama/llama_index, as of 2026-09-01.
- The repository page displays approximately 52k stars and 8.1k forks at fetch time (displayed on the page). Source: https://github.com/run-llama/llama_index, as of 2026-09-01. Discord/Reddit membership sizes: not verified.

Formats: code-first learning — documentation, example notebooks in the repo, integration packages, GitHub issues/discussions for help, Discord chat, Reddit discussion. Learning happens by reading docs and examples and asking in chat channels.

What a practitioner does not get there (analysis): help and knowledge are organized around using the framework, not around reusable methods; a Discord answer is ephemeral and unreviewed; there is no mechanism that promotes a recurring pattern into a documented, tested Practice with recorded evidence; model/vendor neutrality exists at the integration level but the community's identity is the framework itself.

### 1.4 Ollama (local/self-hosted models)

Source: https://ollama.com, as of 2026-09-01.

What it offers:

- A tool for running open models locally and via cloud hosting, positioned for use with coding agents; the homepage lists model search, docs, download, and pricing, and states "Trusted by more than 9M developers" (self-reported on that page). Source: https://ollama.com, as of 2026-09-01.
- Community surfaces listed in the footer: GitHub (github.com/ollama/ollama), Discord (discord.com/invite/ollama), X, and meetups (lu.ma/ollama). Source: https://ollama.com, as of 2026-09-01.
- Discord and meetup participation levels: not verified.

Formats: documentation, a model search/discovery surface, GitHub issues, Discord chat, and in-person meetups under the Ollama brand. The community gathers around running and serving open models.

What a practitioner does not get there (analysis): the gathering point is a serving tool, so shared knowledge concentrates on setup, hardware, and model choice rather than on the surrounding discipline (evaluation, workflow design, verification); chat and issue threads are not curated into reusable methods; no recorded evidence trail connects a community tip to a tested practice.

---

## 2. Vendor developer communities

### 2.1 OpenAI Developer Community

Source: https://community.openai.com, as of 2026-09-01.

What it offers:

- A Discourse forum organized around OpenAI products: categories include Announcements, API, ChatGPT, ChatGPT Apps SDK, Open Models (gpt-oss), Codex, Prompting, Documentation, GPT builders, Forum feedback, and Community. Source: https://community.openai.com, as of 2026-09-01.
- Category topic counts are displayed on the forum home (e.g., the API category is the largest); exact current totals change constantly and are displayed on the cited page. Source: https://community.openai.com, as of 2026-09-01.
- Membership counts and activity rates: not verified.

Formats: forum threads for troubleshooting, prompting best practices, feature feedback, and project sharing; announcements of product updates.

What a practitioner does not get there (analysis): single-vendor scope by design; methods discussed are framed against one provider's models and tools; there is no neutral ground for comparing approaches across vendors, and no community process that elevates a thread into a portable, tested method.

---

## 3. Production-ML / MLOps communities

### 3.1 MLOps Community

Source: https://mlops.community, as of 2026-09-01.

What it offers:

- In-person meetups and conferences (mlops.community/meetups), virtual tech talks (home.mlops.community/public/events), a practitioner podcast, a weekly newsletter, and paid/corporate workshops via learn.mlops.community. Source: https://mlops.community, as of 2026-09-01.
- A jobs board (jobs.mlops.community) and a corporate partner/sponsorship program with named vendor sponsors displayed on the homepage. Source: https://mlops.community, as of 2026-09-01.
- The homepage displays a self-reported figure of "90,000+ developers" for the community. Source: https://mlops.community, as of 2026-09-01.
- Slack member counts and event attendance: not verified.

Formats: events (in-person and virtual), podcast episodes, newsletter issues, workshops/masterclasses, job listings. Content is talk- and story-shaped rather than artifact-shaped.

What a practitioner does not get there (analysis): learning arrives as one-off talks and newsletter items that are hard to reuse operationally; there is no public library of methods with stated inputs, steps, evaluation, and failure modes; sponsorship-supported programming is shaped around partner products; org-level transformation (the "Transform" rung) appears mainly as a topic of talks, not as a body of tested methods.

### 3.2 Weights & Biases learning ecosystem (tool-attached community)

Source: https://wandb.ai/site/community (redirects to the product homepage; resources listed there), as of 2026-09-01.

What it offers:

- A developer platform for experiment tracking, agent/LLM evaluation, and model management. Its resources navigation lists AI courses, a blog ("Fully Connected"), articles, a podcast, and events/webinars. Source: https://wandb.ai/site/community (resources section of the fetched page), as of 2026-09-01.
- A standalone "community" membership surface with member counts: not verified — the community URL serves the product homepage at fetch time.

Formats: vendor courses, tutorials, webinars, podcast, and product documentation. Learning is anchored to using the W&B platform.

What a practitioner does not get there (analysis): education is product-attached; the community dimension (if any, e.g., Slack/Discord) is not verifiable from the cited page; no vendor-neutral method repository with community-owned governance.

---

## 4. Practitioner newsletters and media communities

### 4.1 Latent Space

Source: https://www.latent.space (Substack landing page), as of 2026-09-01.

What it offers:

- A self-described "AI Engineer newsletter + Top technical AI podcast" covering agents, models, and infrastructure, with guest interviews (the landing page names guests including Simon Willison and Soumith Chintala). Source: https://www.latent.space, as of 2026-09-01.
- The landing page displays "Over 198,000 subscribers" (self-reported on that page). Source: https://www.latent.space, as of 2026-09-01.
- The page references an associated community, but the landing page itself does not display membership figures; community size: not verified.

Formats: newsletter essays, podcast interviews, conference-style events (the page's about-linked highlights are editorial). Primarily broadcast media with reader commentary.

What a practitioner does not get there (analysis): editorial insight does not come with a reusable artifact; readers consume analysis but have no path to contribute a method through recorded trial and review; the medium (newsletter/podcast) ages quickly and is not structured for operational reuse.

### 4.2 The Batch (DeepLearning.AI)

Source: https://www.deeplearning.ai/the-batch/, as of 2026-09-01.

What it offers:

- A weekly newsletter ("The Batch") with news, letters, research summaries, and career/business essays, published by DeepLearning.AI. Source: https://www.deeplearning.ai/the-batch/, as of 2026-09-01.
- DeepLearning.AI's broader site lists courses, a discussion forum (community.deeplearning.ai), events, ambassadors, and paid membership/business plans. Source: https://www.deeplearning.ai/the-batch/ (site navigation), as of 2026-09-01.
- Forum membership and activity levels: not verified.

Formats: weekly editorial issues, structured online courses, a course-support forum, events. Learning is top-down: authored curriculum and editorial analysis.

What a practitioner does not get there (analysis): a curated consumer of expert content is not the same as a contributor to a shared practice base; course content is fixed at authorship time, and the forum's purpose is course support rather than community-owned method development; vendor examples in curriculum change with the market and there is no model-agnostic governance of the material by the community itself.

---

## 5. In-person and cohort learning communities

### 5.1 AI Tinkerers

Source: https://aitinkerers.org, as of 2026-09-01.

What it offers:

- A self-described global, curated community for hands-on AI builders, organized as local city rooms with an application process; the homepage states "Bring working code, share what broke." Source: https://aitinkerers.org, as of 2026-09-01.
- The homepage displays figures of 126,425 members, 254 cities, and 90-day counts for events, speakers, and hackathons (all self-reported, displayed on that page). Source: https://aitinkerers.org, as of 2026-09-01.
- Programs listed: demo-driven meetups, global hackathons, a newsletter ("Post-Training"), a YouTube channel ("One-Shot"), a Paper Club livestream series, virtual events, a weekly demo roundup digest, a jobs board, and a talent-intro service. Source: https://aitinkerers.org, as of 2026-09-01.
- A stated house rule: "Demos over decks" — working demos, traces, and failure stories carry more weight than predictions. Source: https://aitinkerers.org, as of 2026-09-01.

Formats: in-person demo nights, hackathons, talk/demo writeups on city pages, newsletters, video series. The unit of sharing is a live demo and an accompanying talk page.

What a practitioner does not get there (analysis): demo culture rewards the working artifact shown in the room, but a demo is not a reproducible method; there is no visible process for turning a demonstrated technique into a documented, tested, reusable practice with recorded evidence; access is application-curated, and durable written method libraries are secondary to events.

### 5.2 DataTalks.Club

Source: https://datatalks.club, as of 2026-09-01.

What it offers:

- A free global online community for data professionals described on the site as covering data science, ML engineering, and AI practice; the landing page lists Slack, weekly events, a podcast, articles, a wiki, books, and a newsletter. Source: https://datatalks.club, as of 2026-09-01.
- Free cohort-style "Zoomcamp" courses (the landing page announces an "AI Dev Tools Zoomcamp 2026" starting 2026-08-31; other listed courses include ML, MLOps, and LLM Zoomcamps with certification per the linked articles). Source: https://datatalks.club, as of 2026-09-01.
- A sponsor-facing article linked from the landing page cites a reach of "130,000+ Data and AI Professionals" (self-reported in that article's title). Source: https://datatalks.club, as of 2026-09-01.
- Slack member count: not verified.

Formats: cohort courses with structured curricula and certificates, live events/Q&A, podcast, Slack community, wiki and books pages. Learning is course-shaped and event-shaped.

What a practitioner does not get there (analysis): cohort courses teach a fixed curriculum rather than hosting a living method library; community knowledge in Slack is ephemeral and uncurated; scope is the broad data/ML profession rather than a model-agnostic AI-practitioner method base with evidence trails.

---

## 6. Not verified

- **r/LocalLLaMA (Reddit)** — referenced widely as a large gathering space for local-model practitioners, but https://www.reddit.com/r/LocalLLaMA/ returned no readable content at fetch time (2026-09-01). Purpose, size, rules, and formats: not verified. Excluded from analysis above for that reason.
- Membership/activity figures for Discord servers (Hugging Face, LlamaIndex, Ollama, LangChain Slack, DataTalks.Club Slack): not verified for any community.

---

## 7. Cross-cutting observations (analysis)

Each of these is a judgment across the sources above, not a fact:

- **The gathering places are real but format-bound.** Practitioners already convene in six shapes: product forums (Hugging Face, OpenAI, LangChain), project repos (LlamaIndex, Ollama), event networks (MLOps Community, AI Tinkerers), media (Latent Space, The Batch), cohort courses (DataTalks.Club, DeepLearning.AI), and tool-attached education (W&B). Every format optimizes for Q&A, broadcast, events, or curriculum — none optimizes for a curated, evidence-backed method library.
- **Knowledge is ephemeral where practitioners are.** Slack threads, Discord channels, demo talks, and newsletter issues do not version, review, or accumulate. The durable artifacts that do exist (GitHub repos) are code, not method.
- **Scope is vertical everywhere.** Nearly every space is anchored to a product, vendor, or media brand. A practitioner using more than one stack joins several communities and reconciles them privately.
- **No visible evidence ladder.** None of the surveyed surfaces describes a process by which shared knowledge is promoted through recorded trials and human review to "tested" status. Quality signals, where they exist, are reputation programs (Champions, Experts, Ambassadors) tied to a specific product.

---

## 8. Positioning gaps for Practice (analysis)

Each item below is **analysis** — a positioning hypothesis grounded in the scan above, not a verified fact about any community and not a committed product feature. Practice's locked positioning is "The open community for AI practitioners" with the Learn → Use → Automate → Build → Transform ladder.

1. **The portable-method gap.** Adjacent spaces transfer knowledge inside a product, an event, or a media frame. No surveyed space positions itself as a vendor-neutral home where a method is written to survive tool churn. Practice's model-agnostic posture and Git-based artifacts map directly onto this hole. (Analysis.)
2. **The evidence ladder gap.** Community knowledge elsewhere is promoted by visibility (upvotes, program badges, stage time), not by recorded trial plus human review. Practice's Practice maturity model — proposed → tested via recorded trial and human review — is a differentiator none of the surveyed communities visibly offers. (Analysis.)
3. **The durability gap.** Practitioner conversations happen in formats that decay (chat, talks, newsletters). Practice's "durable source of truth in Git" — versioned, reviewable, reusable outside the relay — addresses the reuse-after-the-room problem that event- and chat-first communities leave open. (Analysis.)
4. **The ladder-coverage gap.** The surveyed spaces cluster on Learn (courses, docs, papers) and Build (frameworks, demos). The Automate rung (turning recurring work into reliable, reviewable workflows) and especially the Transform rung (redesigning teams and organizations) are served mostly as talk topics, not as tested, shared methods. A community organized outcome-first across the whole ladder occupies ground adjacent communities treat as content rather than capability. (Analysis.)
5. **The governance gap.** Most surveyed spaces are product communities whose moderation, roadmap influence, and recognition programs ultimately serve the vendor or media brand. Practice's locked posture — community-owned governance, human-owned moderation, model/platform-agnostic identity — is a distinct claim to stewardship that no surveyed space makes. (Analysis.)

---

## Scope guard

This report is positioning input only. It does not propose courses, certifications, paid memberships, leaderboards, tool directories, news aggregation, or any other item listed in `NON_GOALS.md`. Where a gap suggests future work, it is recorded in `handoffs/R3.md` under Deferred opportunities.

## Sources (all fetched 2026-09-01)

| Community | URL |
|---|---|
| Hugging Face site nav | https://huggingface.co/forums |
| Hugging Face forum | https://discuss.huggingface.co |
| LangChain community | https://www.langchain.com/community |
| LlamaIndex repository | https://github.com/run-llama/llama_index |
| Ollama homepage | https://ollama.com |
| OpenAI Developer Community | https://community.openai.com |
| MLOps Community | https://mlops.community |
| Weights & Biases | https://wandb.ai/site/community |
| Latent Space | https://www.latent.space |
| The Batch (DeepLearning.AI) | https://www.deeplearning.ai/the-batch/ |
| AI Tinkerers | https://aitinkerers.org |
| DataTalks.Club | https://datatalks.club |
| r/LocalLLaMA (blocked fetch) | https://www.reddit.com/r/LocalLLaMA/ |

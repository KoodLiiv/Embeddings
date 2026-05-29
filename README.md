# MGM Embeddings — Semantic SEO Analysis Proof of Concept

A proof-of-concept Python pipeline that uses vector embeddings to surface internal linking opportunities — the kind of semantic relationships that traditional keyword-based SEO tools miss.

Built after reading Mike King's article on relevance engineering, this project takes a Screaming Frog crawl, generates embeddings for every page via the Google Gemini API, and ranks pages by cosine similarity. Tested on a 47-page sample of mgmresorts.com to validate the approach end-to-end.

## The Problem

Traditional SEO tools rank pages by keyword overlap — same words, related content. Google doesn't. Google has been ranking by semantic meaning since BERT (2019), which means SEO tools and Google have drifted apart on how they understand content.

Vector embeddings close that gap. They convert page content into 768-dimensional vectors that represent meaning, not vocabulary. Pages with similar meanings produce similar vectors, even when they share few exact words. Measuring the distance between vectors gives an objective signal for internal linking, content clustering, and relevance scoring — the same kind of signal Google uses internally.

## Findings

Three findings from the all-pages analysis stood out as worth flagging:

**Cross-link opportunity worth shipping.** Sports Tourism and Meetings are mutual top neighbors at 0.511. Both pages serve the same B2B audience — event planners booking large group bookings at MGM properties. They are not currently linked. Adding internal links between them helps a high-value commercial audience navigate the site.

**Most isolated page.** The MGM Collection with Marriott Bonvoy partnership scored 0.106 against its top neighbor — the most semantically orphaned page in the dataset. For a commercially important loyalty partnership page, that's a real business risk. Both users and search engines have trouble reaching it through normal navigation.

**Potential cannibalization.** Pools and the Things To Do hub are mutual top matches at 0.509 — high enough to suggest the two pages may be competing for the same searches. Worth clarifying which page owns which intent, then using internal linking to establish hierarchy.

These are observations from the analysis, not recommendations to ship blind. The next step is bringing the team's context to confirm which findings are worth acting on.

## Methodology Note: Brand Baseline Removal

The first pass of the analysis surfaced false positives — pages scoring as highly similar when they shouldn't have. The cause was brand-level signal contaminating topic-level signal: every page on the site shares MGM's corporate framing, which artificially inflated similarity scores across the board.

Fix: added a centering step that calculates the average embedding across all pages, then subtracts it from each page before comparing. What's left is topic-specific signal with the brand baseline removed. All findings above use the centered analysis.

## How It Works

1. **Crawl** — Screaming Frog produces a CSV of every page on the site with titles, meta descriptions, and headings
2. **Filter** — keep only 200-OK, indexable pages with >100 words (47 pages from 299 total URLs)
3. **Embed** — send each page's text to the Gemini embedding API; receive a 768-dimensional vector representing the page's meaning
4. **Center** — subtract the site-wide average embedding to remove brand baseline noise
5. **Compare** — for any target page, compute cosine similarity against every other page; rank the results

## Files

### Core Pipeline
- `embed_all.py` — generates embeddings for all 47 pages and saves to `mgm_embeddings.json`
- `find_similar_centered.py` — finds semantically similar pages with brand baseline removed
- `all_pages_recommendations.py` — generates top 5 internal linking recommendations for every page

### Data
- `mgm_pages_to_embed.json` — input dataset (47 filtered pages from the Screaming Frog crawl)
- `mgm_embeddings.json` — output (pages with their 768-dimensional vectors attached)
- `mgm_internal_linking_recommendations.csv` — actionable linking suggestions for each page

### Visualization
- `dashboard.py` — interactive Marimo notebook visualizing the semantic network as a t-SNE graph

## Running It

Install dependencies:

```bash
pip install google-genai numpy marimo plotly scikit-learn
```

Set your Gemini API key:

```bash
export GEMINI_API_KEY="your-key-here"
```

Generate embeddings (one-time, ~1 minute):

```bash
python3 embed_all.py
```

Run the analysis:

```bash
python3 find_similar_centered.py       # Single-page similarity with brand signal removed
python3 all_pages_recommendations.py   # Generate CSV recommendations for all pages
marimo run dashboard.py                # Launch interactive network visualization
```

## What's NOT in This Version

This is a proof of concept. A production version would add:

- **Boilerplate stripping** — currently embeds page text including shared navigation and footer language; stripping to content-area-only would reduce brand contamination at the source
- **Full body content** — currently embeds title + meta + headings; embedding full body text would produce more topic-specific vectors
- **Persistent storage** — currently saves to JSON; Postgres + pgvector would scale to thousands of pages and enable production querying
- **Multi-page filtering in the dashboard** — currently shows all-to-all; faceted views would make large datasets even more digestible

These are deliberate scope choices for the POC, not unknowns. The goal of this version was to validate the approach end-to-end and identify the brand contamination issue — both done.

## Credits

Built after reading Mike King's [Vector Embeddings Is All You Need](https://ipullrank.com/vector-embeddings-is-all-you-need) on iPullRank, and Screaming Frog's [tutorial on using vector embeddings for redirect mapping](https://www.screamingfrog.co.uk/seo-spider/tutorials/how-to-use-vector-embeddings-for-redirect-mapping/).

---

*Built as a proof of concept while preparing for an interview process with Superformula. The methodology generalizes to any client, any site, any SEO use case where semantic relationships matter.*
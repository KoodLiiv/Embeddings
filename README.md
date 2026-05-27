# MGM Embeddings — Semantic SEO Analysis Proof of Concept

A proof-of-concept Python pipeline that uses vector embeddings to surface internal linking opportunities — the kind of semantic relationships that traditional keyword-based SEO tools miss. Built after reading Mike King's article on relevance engineering, this project takes a Screaming Frog crawl, generates embeddings for every page via the Google Gemini API, and ranks pages by cosine similarity. Tested on a 47-page sample of mgmresorts.com to validate the approach end-to-end, including a centering step to remove brand-level signal contamination.

## The Problem

Traditional SEO tools rank pages by keyword overlap — same words, related content. Google doesn't. Google has been ranking by semantic meaning since BERT (2019), which means SEO tools and Google have drifted apart on how they understand content.

Vector embeddings close that gap. They convert page content into 768-dimensional vectors that represent meaning, not vocabulary. Pages with similar meanings produce similar vectors, even when they share few exact words. Measuring the distance between vectors gives an objective signal for internal linking, content clustering, and relevance scoring — the same kind of signal Google uses internally.

## What I Found

Running the pipeline against a 47-page slice of mgmresorts.com, with the Spas page as the test query:

**Real recommendation:** The Spas page and the Pools page scored 0.853 on cosine similarity — high enough that they should be cross-linking each other. Same audience, same trip-planning intent. The relationship survived after centering, which confirms it's a genuine topic relationship rather than a brand artifact.

**Diagnosed limitation:** The first run surfaced BetMGM Sportsbooks at 0.816 against Spas — a false positive. The cause was brand-level signal contaminating the topic-level signal: every page on the site shares MGM's corporate framing, which artificially inflated similarity scores across the board.

**Fix:** Added a centering step — calculate the average embedding across all 47 pages (the brand baseline), subtract it from each page before comparing. After centering, BetMGM dropped from 0.816 to 0.139, while Spas-Pools held its position. Cleaner signal, more confidence in what's real.

## Scaled to All 47 Pages

Beyond the single-page analysis, I generated internal linking recommendations for every page — top 5 semantic neighbors per page, saved to `mgm_internal_linking_recommendations.csv`. Three findings stood out:

**Strongest cross-link opportunity:** Sports Tourism and Meetings are mutual top neighbors at 0.511 — clear B2B audience overlap, ship-it recommendation.

**Most isolated page:** The MGM Collection with Marriott Bonvoy partnership scored 0.106 against its top neighbor — the most semantically orphaned page in the dataset. For a commercially important loyalty partnership page, that's a serious flag worth investigating.

**Potential cannibalization:** Pools and the Things To Do hub are mutual top matches at 0.509 — high enough to suggest the two pages may be competing for the same queries. Either differentiate them, consolidate, or establish clear hierarchy through internal linking.

## How It Works

1. **Crawl** — Screaming Frog produces a CSV of every page on the site with titles, meta descriptions, and headings
2. **Filter** — keep only 200-OK, indexable pages with >100 words (47 pages from 299 total URLs)
3. **Embed** — send each page's text to the Gemini embedding API; receive a 768-dimensional vector representing the page's meaning
4. **Compare** — for any target page, compute cosine similarity against every other page; rank the results
5. **Center (optional)** — subtract the site-wide average embedding before comparison to remove brand baseline noise

## Files

### Core Pipeline
- `embed_all.py` — generates embeddings for all 47 pages and saves to `mgm_embeddings.json`
- `find_similar_centered.py` — finds semantically similar pages with brand baseline removed

### Data
- `mgm_pages_to_embed.json` — input dataset (47 filtered pages from the Screaming Frog crawl)
- `mgm_embeddings.json` — output (pages with their 768-dimensional vectors attached)

### Analysis & Recommendations
- `all_pages_recommendations.py` — generates top 5 internal linking recommendations for every page on the site
- `mgm_internal_linking_recommendations.csv` — CSV output with actionable linking suggestions for each page
- `dashboard.py` — interactive marimo notebook visualizing semantic network as t-SNE graph

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

Run similarity analysis:

```bash
python3 find_similar_centered.py  # Find similar pages with brand signal removed
python3 all_pages_recommendations.py  # Generate CSV recommendations for all pages
marimo run dashboard.py  # Launch interactive network visualization
```

## What's NOT in This Version

This is a proof of concept. A production version would add:

- **Boilerplate stripping** — currently embeds page text including shared navigation and footer language; stripping to content-area-only would reduce brand contamination at the source
- **Full body content** — currently embeds title + meta + headings; embedding full body text would produce more topic-specific vectors
- **Persistent storage** — currently saves to JSON; Postgres + pgvector would scale to thousands of pages and enable production querying
- **Multi-page similarity** — currently dashboard shows all-to-all; a filtered/faceted view would make large datasets even more digestible

These are deliberate scope choices for the POC, not unknowns. The goal of this version was to validate the approach end-to-end and identify the brand contamination issue — both done.

## Development Notes

**Removed scripts (for reference):**
- `test_embedding.py` — one-time API verification; functionality now included in `embed_all.py`
- `find_similar.py` — superseded by `find_similar_centered.py` (which removes brand noise and produces cleaner results)

## Credits

Built after reading Mike King's [Vector Embeddings Is All You Need](https://ipullrank.com/vector-embeddings-is-all-you-need) on iPullRank, and Screaming Frog's [tutorial on using vector embeddings for redirect mapping](https://www.screamingfrog.co.uk/seo-spider/tutorials/how-to-use-vector-embeddings-for-redirect-mapping/).

---

*Built as a proof of concept while preparing for an interview process with Superformula. The methodology generalizes to any client, any site, any SEO use case where semantic relationships matter.*
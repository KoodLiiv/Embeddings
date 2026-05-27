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

## How It Works

1. **Crawl** — Screaming Frog produces a CSV of every page on the site with titles, meta descriptions, and headings
2. **Filter** — keep only 200-OK, indexable pages with >100 words (47 pages from 299 total URLs)
3. **Embed** — send each page's text to the Gemini embedding API; receive a 768-dimensional vector representing the page's meaning
4. **Compare** — for any target page, compute cosine similarity against every other page; rank the results
5. **Center (optional)** — subtract the site-wide average embedding before comparison to remove brand baseline noise

## Files

- `embed_all.py` — generates embeddings for all 47 pages and saves to `mgm_embeddings.json`
- `find_similar.py` — finds semantically similar pages using standard cosine similarity
- `find_similar_centered.py` — same, but with brand baseline removed
- `test_embedding.py` — single-page test of the Gemini API integration
- `mgm_pages_to_embed.json` — input dataset (47 filtered pages from the Screaming Frog crawl)
- `mgm_embeddings.json` — output (pages with their 768-dimensional vectors attached)

## Running It

Install dependencies:

```bash
pip install google-genai numpy
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
python3 find_similar.py           # Standard
python3 find_similar_centered.py  # With brand baseline removed
```

## What's NOT in This Version

This is a proof of concept. A production version would add:

- **Boilerplate stripping** — currently embeds page text including shared navigation and footer language; stripping to content-area-only would reduce brand contamination at the source
- **Full body content** — currently embeds title + meta + headings; embedding full body text would produce more topic-specific vectors
- **Persistent storage** — currently saves to JSON; Postgres + pgvector would scale to thousands of pages and enable production querying
- **Multi-page output** — currently runs against one target page at a time; production would generate a full internal linking table for every page on the site
- **Visualization** — currently outputs to terminal; a clustering visualization would surface topic groups at a glance

These are deliberate scope choices for the POC, not unknowns. The goal of this version was to validate the approach end-to-end and identify the brand contamination issue — both done.

## Credits

Built after reading Mike King's [Vector Embeddings Is All You Need](https://ipullrank.com/vector-embeddings-is-all-you-need) on iPullRank, and Screaming Frog's [tutorial on using vector embeddings for redirect mapping](https://www.screamingfrog.co.uk/seo-spider/tutorials/how-to-use-vector-embeddings-for-redirect-mapping/).

---

*Built as a proof of concept while preparing for an interview process with Superformula. The methodology generalizes to any client, any site, any SEO use case where semantic relationships matter.*
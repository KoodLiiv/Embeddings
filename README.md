# MGM Embeddings

A semantic search system for MGM Resorts webpages using Google Gemini embeddings.

## What It Does

Converts MGM Resorts webpage content into vector embeddings (768-dimensional vectors) and finds semantically similar pages using cosine similarity.

## Files

- **embed_all.py** - Generate embeddings for all pages (requires GEMINI_API_KEY)
- **test_embedding.py** - Test the Gemini API integration
- **find_similar.py** - Find similar pages using standard cosine similarity
- **find_similar_centered.py** - Find similar pages after removing brand baseline signal
- **mgm_pages_to_embed.json** - Input: 47 MGM pages with content to embed
- **mgm_embeddings.json** - Output: Pages with their 768-dim embeddings

## Requirements

```bash
pip install google-genai numpy
```

Set your API key:
```bash
export GEMINI_API_KEY="your-key-here"
```

## Usage

1. **Generate embeddings** (one-time setup):
   ```bash
   python3 embed_all.py
   ```

2. **Find similar pages**:
   ```bash
   python3 find_similar.py          # Standard similarity
   python3 find_similar_centered.py # With brand signal removed
   ```

3. **Test API**:
   ```bash
   python3 test_embedding.py
   ```

## Data Format

Each page includes:
- `url` - Page URL
- `title` - Page title
- `meta_desc` - Meta description
- `h1`, `h2_1`, `h2_2` - Heading text
- `word_count` - Content length
- `text_to_embed` - Combined text for embedding
- `embedding` - 768-dimensional vector (output only)

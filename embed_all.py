import os
import json
import time
from google import genai
from google.genai import types

# Connect to Gemini
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Load our 47 pages
with open("mgm_pages_to_embed.json", "r") as f:
    pages = json.load(f)

print(f"Loaded {len(pages)} pages to embed")
print("Starting embeddings... this will take 1-2 minutes\n")

embedded_pages = []

for i, page in enumerate(pages, start=1):
    text = page["text_to_embed"]

    try:
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=768
            )
        )

        embedding = result.embeddings[0].values
        page["embedding"] = embedding
        embedded_pages.append(page)

        print(f"  [{i}/{len(pages)}] OK: {page['url'][:80]}")

        time.sleep(0.3)

    except Exception as e:
        print(f"  [{i}/{len(pages)}] FAILED: {page['url'][:60]} - {e}")
        continue

# Save the embeddings to a file
output_file = "mgm_embeddings.json"
with open(output_file, "w") as f:
    json.dump(embedded_pages, f)

print(f"\nDone. Saved {len(embedded_pages)} embeddings to {output_file}")
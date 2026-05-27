import json
import numpy as np

# Load our embedded pages
with open("mgm_embeddings.json", "r") as f:
    pages = json.load(f)

print(f"Loaded {len(pages)} embedded pages\n")

# Convert to numpy array
embeddings = np.array([p["embedding"] for p in pages])

# Step 1: Calculate the site-wide average embedding (the "brand baseline")
site_average = np.mean(embeddings, axis=0)
print(f"Calculated site-wide average embedding from {len(pages)} pages")
print(f"This represents the 'MGM brand baseline' shared across all pages\n")

# Step 2: Subtract the average from each page's embedding (centering)
centered = embeddings - site_average
print("Centered all embeddings - brand signal removed\n")

# Step 3: Normalize the centered vectors
norms = np.linalg.norm(centered, axis=1, keepdims=True)
normalized = centered / norms

# Pick our target page
target_url = "https://www.mgmresorts.com/en/things-to-do/spas.html"

target_index = None
for i, page in enumerate(pages):
    if page["url"] == target_url:
        target_index = i
        break

if target_index is None:
    print(f"Target page not found: {target_url}")
    exit()

print(f"Target page: {target_url}")
print(f"Title: {pages[target_index]['title']}\n")

# Calculate similarity
target_vector = normalized[target_index]
similarities = np.dot(normalized, target_vector)

results = []
for i, page in enumerate(pages):
    if i == target_index:
        continue
    results.append((similarities[i], page))

results.sort(key=lambda x: x[0], reverse=True)

print("=" * 80)
print("TOP 10 MOST SIMILAR PAGES (after brand centering):")
print("=" * 80)
for score, page in results[:10]:
    print(f"\n  Score: {score:.3f}")
    print(f"  URL:   {page['url']}")
    print(f"  Title: {page['title']}")

print("\n" + "=" * 80)
print("BOTTOM 5 LEAST SIMILAR PAGES:")
print("=" * 80)
for score, page in results[-5:]:
    print(f"\n  Score: {score:.3f}")
    print(f"  URL:   {page['url']}")
    print(f"  Title: {page['title']}")
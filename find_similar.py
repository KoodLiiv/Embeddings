import json
import numpy as np

# Load our embedded pages
with open("mgm_embeddings.json", "r") as f:
    pages = json.load(f)

print(f"Loaded {len(pages)} embedded pages\n")

# Convert all embeddings into a numpy array for fast math
# Each row is one page's 768-dimensional vector
embeddings = np.array([p["embedding"] for p in pages])

# Normalize the vectors (makes cosine similarity simpler)
# Don't worry about the math - this just makes the next step easy
norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
normalized = embeddings / norms

# Pick a target page to analyze
# Let's start with the Spas page
target_url = "https://www.mgmresorts.com/en/things-to-do/spas.html"

# Find the index of our target page in the list
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

# Calculate cosine similarity between target and every other page
# Because we normalized the vectors, this is just a dot product
target_vector = normalized[target_index]
similarities = np.dot(normalized, target_vector)

# Build a list of (similarity score, page) tuples
results = []
for i, page in enumerate(pages):
    if i == target_index:
        continue  # Skip the target itself (it would be 1.0)
    results.append((similarities[i], page))

# Sort from most similar to least similar
results.sort(key=lambda x: x[0], reverse=True)

# Show the top 10
print("=" * 80)
print("TOP 10 MOST SIMILAR PAGES (semantically):")
print("=" * 80)
for score, page in results[:10]:
    print(f"\n  Score: {score:.3f}")
    print(f"  URL:   {page['url']}")
    print(f"  Title: {page['title']}")

# Show the bottom 5 - the least related pages
print("\n" + "=" * 80)
print("BOTTOM 5 LEAST SIMILAR PAGES (just for contrast):")
print("=" * 80)
for score, page in results[-5:]:
    print(f"\n  Score: {score:.3f}")
    print(f"  URL:   {page['url']}")
    print(f"  Title: {page['title']}")
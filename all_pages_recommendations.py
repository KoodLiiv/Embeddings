import json
import numpy as np

# Load all 47 embedded pages
with open("mgm_embeddings.json", "r") as f:
    pages = json.load(f)

print(f"Loaded {len(pages)} embedded pages")

# Convert to numpy array
embeddings = np.array([p["embedding"] for p in pages])

# Center: subtract the brand baseline
site_average = np.mean(embeddings, axis=0)
centered = embeddings - site_average

# Normalize so cosine similarity is just a dot product
norms = np.linalg.norm(centered, axis=1, keepdims=True)
normalized = centered / norms

print("Embeddings centered and normalized — ready for analysis\n")

# For each page, find its top 5 most similar neighbors
all_recommendations = []

for i, source_page in enumerate(pages):
    # Get this page's vector
    source_vector = normalized[i]
    
    # Compare to every other page
    similarities = np.dot(normalized, source_vector)
    
    # Build (score, page) pairs, excluding the page itself
    candidates = []
    for j, candidate_page in enumerate(pages):
        if j == i:
            continue  # Skip the page itself (would always score 1.0)
        candidates.append((similarities[j], candidate_page))
    
    # Sort by score, highest first
    candidates.sort(key=lambda x: x[0], reverse=True)
    
    # Keep only the top 5
    top_5 = candidates[:5]
    
    # Save the result for this source page
    all_recommendations.append({
        "source_url": source_page["url"],
        "source_title": source_page["title"],
        "neighbors": top_5
    })

print(f"Generated recommendations for {len(all_recommendations)} pages\n")

# Show a quick preview — first 3 pages
print("=" * 80)
print("PREVIEW — first 3 pages:")
print("=" * 80)
for rec in all_recommendations[:3]:
    print(f"\n{rec['source_title']}")
    print(f"  {rec['source_url']}")
    print(f"  Top neighbors:")
    for score, neighbor in rec['neighbors']:
        print(f"    {score:.3f}  →  {neighbor['title'][:60]}")

import csv

# Save to CSV
output_file = "mgm_internal_linking_recommendations.csv"

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    
    # Header row
    writer.writerow([
        "Source URL",
        "Source Title",
        "Top 1 URL", "Top 1 Title", "Top 1 Score",
        "Top 2 URL", "Top 2 Title", "Top 2 Score",
        "Top 3 URL", "Top 3 Title", "Top 3 Score",
        "Top 4 URL", "Top 4 Title", "Top 4 Score",
        "Top 5 URL", "Top 5 Title", "Top 5 Score",
    ])
    
    # One row per source page
    for rec in all_recommendations:
        row = [rec["source_url"], rec["source_title"]]
        for score, neighbor in rec["neighbors"]:
            row.extend([neighbor["url"], neighbor["title"], f"{score:.3f}"])
        writer.writerow(row)

print(f"Saved {len(all_recommendations)} pages of recommendations to {output_file}")
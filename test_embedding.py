import os
from google import genai
from google.genai import types

# Get the API key from your environment variable
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# The text we want to embed - one MGM page's title + meta + headings
sample_text = "Spas Las Vegas | For the best in spa days in Las Vegas, look no further than MGM Resorts. Many of our resorts feature day and half-day spa options for guests & locals to use. Book online today. | Spa"

# Make the API call
result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=sample_text,
    config=types.EmbedContentConfig(
        task_type="RETRIEVAL_DOCUMENT",
        output_dimensionality=768
    )
)

# Get the embedding (the list of numbers)
embedding = result.embeddings[0].values

# Show us what came back
print(f"Number of dimensions: {len(embedding)}")
print(f"First 10 numbers: {embedding[:10]}")
print(f"Last 5 numbers: {embedding[-5:]}")
print(f"Type of each number: {type(embedding[0])}")
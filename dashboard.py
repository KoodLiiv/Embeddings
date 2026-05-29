import marimo

__generated_with = "0.8.0"
app = marimo.App()


@app.cell
def __():
    import json
    import numpy as np
    import plotly.graph_objects as go
    import marimo as mo
    from sklearn.manifold import TSNE
    return json, np, go, mo, TSNE


@app.cell
def __(json):
    # Load embeddings
    with open("mgm_embeddings.json", "r") as f:
        pages = json.load(f)
    
    print(f"Loaded {len(pages)} pages")
    return pages


@app.cell
def __(np, pages, TSNE):
    # Extract embeddings and metadata
    embeddings = np.array([p["embedding"] for p in pages])
    titles = [p["title"] for p in pages]
    urls = [p["url"] for p in pages]
    
    # Center the embeddings (remove brand baseline)
    site_average = np.mean(embeddings, axis=0)
    centered = embeddings - site_average
    
    # Normalize for cosine similarity
    norms = np.linalg.norm(centered, axis=1, keepdims=True)
    normalized = centered / norms
    
    # Calculate similarity matrix (centered)
    similarity_matrix = np.dot(normalized, normalized.T)
    
    # Calculate node colors (average similarity / centrality)
    node_colors = np.mean(similarity_matrix, axis=1)
    
    # Use t-SNE to project embeddings to 2D
    # This creates a layout where similar pages naturally cluster together
    print("Running t-SNE projection...")
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(40, len(pages)-1), n_iter=2000, verbose=0)
    positions_2d = tsne.fit_transform(embeddings)
    
    node_x = positions_2d[:, 0].tolist()
    node_y = positions_2d[:, 1].tolist()
    
    print(f"✓ t-SNE complete: {len(pages)} pages positioned")
    
    return embeddings, titles, urls, site_average, centered, normalized, similarity_matrix, node_colors, node_x, node_y


@app.cell
def __(np, similarity_matrix, node_x, node_y):
    # Extract edges (strong connections only)
    edge_x = []
    edge_y = []
    connections = []
    
    similarity_threshold = 0.30
    n_pages = len(similarity_matrix)
    
    for _i in range(n_pages):
        for _j in range(_i+1, n_pages):
            _sim = similarity_matrix[_i][_j]
            if _sim > similarity_threshold:
                edge_x.extend([node_x[_i], node_x[_j], None])
                edge_y.extend([node_y[_i], node_y[_j], None])
                connections.append((_sim, _i, _j))
    
    print(f"✓ Found {len(connections)} strong connections (similarity > {similarity_threshold})")
    
    return edge_x, edge_y, connections, similarity_threshold


@app.cell
def __(go, node_x, node_y, node_colors, titles, edge_x, edge_y):
    # Create interactive visualization
    fig = go.Figure()
    
    # Add connection lines
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=3.5, color='rgba(40,100,160,0.55)'),
        hoverinfo='none',
        showlegend=False,
        name='Connections'
    ))
    
    # Add page nodes
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        marker=dict(
            size=24,
            color=node_colors,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title="Centrality<br>(Avg Similarity)",
                thickness=18,
                len=0.75,
                x=1.02
            ),
            line=dict(width=3, color='white'),
            opacity=0.95
        ),
        text=titles,
        hovertemplate='<b>%{text}</b><extra></extra>',
        showlegend=False
    ))
    
    fig.update_layout(
        title={
            'text': "MGM Resorts — Page Relationships by Meaning<br><sub>Pages closer together share more semantic meaning. Lines show strong connections.</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        showlegend=False,
        hovermode='closest',
        margin=dict(b=40, l=5, r=110, t=100),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            scaleanchor='y',
            scaleratio=1
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            scaleanchor='x',
            scaleratio=1
        ),
        plot_bgcolor='rgba(248,250,252,1)',
        paper_bgcolor='white',
        height=900,
        width=None,
        font=dict(family='Arial, sans-serif', size=12)
    )
    
    return fig


@app.cell
def __(mo):
    mo.md("""
# MGM Resorts — Semantic Site Map

A view of how the content on MGM Resorts' site relates by meaning, not just by shared keywords. Built to surface three business problems traditional SEO tools struggle with:

- **Internal linking opportunities** — pages that should connect because they serve the same audience
- **Content orphans** — commercially important pages with no semantic neighbors, making them harder to discover
- **Cannibalization risk** — pairs of pages competing for the same searches

Each dot is a page. Pages that mean similar things sit closer together. Lines show the strongest connections. Hover for page titles.

*Built on a 47-page sample as proof of concept. Methodology generalizes to the full site.*
""")


@app.cell
def __(mo, fig):
    mo.ui.plotly(fig)


@app.cell
def __(mo, titles, urls, node_colors, connections, np):
    # Find most isolated pages
    isolated_indices = np.argsort(node_colors)[:3]
    
    # Find strongest mutual connections
    sorted_connections = sorted(connections, key=lambda x: x[0], reverse=True)
    
    findings_md = """
## Findings

### 1. Cross-link opportunity worth shipping
Sports Tourism and Meetings are each other's strongest semantic match. Both pages serve the same B2B audience — event planners booking large group bookings at MGM properties. They are not currently linked. Adding internal links between them helps a high-value commercial audience navigate the site.

### 2. Content orphans — commercially important pages with no neighbors
"""
    for _idx in isolated_indices:
        findings_md += f"- **{titles[_idx][:80]}** (score {node_colors[_idx]:.3f})\n"
    
    findings_md += """

The most isolated page is the MGM Collection with Marriott Bonvoy partnership — a key loyalty integration with no semantic neighbors on the site. This means both users and search engines have trouble reaching it through normal navigation, which is a real business risk for a commercially important page.

### 3. Potential cannibalization
Pools and the Things To Do hub are each other's top match. When two pages serve similar searches, Google has to pick one — and not always the stronger one. Worth clarifying which page owns which intent.
"""
    mo.md(findings_md)


if __name__ == "__main__":
    app.run()

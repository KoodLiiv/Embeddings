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
    
    similarity_threshold = 0.45
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
            'text': "🌐 MGM Semantic Network Dashboard<br><sub>t-SNE layout | Colors show centrality | Lines show semantic similarity >0.45</sub>",
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
def __(mo, fig):
    mo.md("""
    # 🌐 MGM Semantic Network Dashboard
    
    **Explore how 47 MGM pages relate semantically** based on their embedding vectors.
    
    ### How to read this:
    - **Node position**: Determined by t-SNE (similar content clusters together)
    - **Node color**: Centrality score (how similar to other pages on average)  
    - **Lines**: Strong semantic relationships (similarity > 0.45 after brand baseline removal)
    - **Hover**: See page titles
    
    **Key findings:**
    - Dark purple nodes = isolated pages worth investigating
    - Bright green nodes = central pages connected to many others
    - Dense clusters = topic groups (e.g., dining, accommodations, events)
    """)


@app.cell
def __(mo, fig):
    mo.ui.plotly(fig)


@app.cell
def __(mo, titles, node_colors, np):
    # Find most isolated pages
    isolated_indices = np.argsort(node_colors)[:5]
    
    isolated_md = "## 📍 Most Isolated Pages\n\n"
    isolated_md += "Pages with lowest average similarity (most unique/orphaned):\n\n"
    for _idx in isolated_indices:
        isolated_md += f"- **{titles[_idx][:70]}** — Centrality: {node_colors[_idx]:.3f}\n"
    
    mo.md(isolated_md)


@app.cell
def __(mo, titles, node_colors, np):
    # Find most central pages
    central_indices = np.argsort(node_colors)[-5:][::-1]
    
    central_md = "## 🎯 Most Central Pages\n\n"
    central_md += "Pages with highest average similarity (most semantically connected):\n\n"
    for _idx in central_indices:
        central_md += f"- **{titles[_idx][:70]}** — Centrality: {node_colors[_idx]:.3f}\n"
    
    mo.md(central_md)


@app.cell
def __(mo, titles, connections):
    # Show strongest relationships
    strongest_md = "## 🔗 Strongest Semantic Relationships\n\n"
    strongest_md += "Top 10 page pairs by similarity:\n\n"
    
    sorted_connections = sorted(connections, key=lambda x: x[0], reverse=True)
    
    for _sim, _i, _j in sorted_connections[:10]:
        strongest_md += f"- **{_sim:.3f}** → {titles[_i][:50]} ↔ {titles[_j][:50]}\n"
    
    mo.md(strongest_md)


if __name__ == "__main__":
    app.run()

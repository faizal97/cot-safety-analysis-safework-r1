import plotly.graph_objects as go
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
from typing import List
from .safety_analyzer import CoTResponse

def create_safety_timeline(analysis: CoTResponse) -> go.Figure:
    """
    Create a timeline showing safety scores across reasoning steps
    Red stars indicate 'Safety Aha Moments' from SafeWork-R1 paper
    """

    steps = list(range(len(analysis.safety_analyses)))
    scores = [a.safety_score for a in analysis.safety_analyses]
    peak_steps = analysis.safety_peaks

    fig = go.Figure()

    # Add safety score line
    fig.add_trace(go.Scatter(
        x=steps,
        y=scores,
        mode='lines+markers',
        name='Safety Score',
        line=dict(color='blue', width=3),
        marker=dict(size=10),
        hovertemplate="Step %{x}<br>Safety Score: %{y:.4f}<extra></extra>"
    ))

    # Highlight safety peaks (aha moments)
    if peak_steps:
        peak_scores = [scores[i] for i in peak_steps]
        fig.add_trace(go.Scatter(
            x=peak_steps,
            y=peak_scores,
            mode='markers',
            name="Safety Aha Moments",
            marker=dict(color='red', size=20, symbol='star'),
            hovertemplate="Safety peak!<br>Step %{x}<br>Score: %{y:.4f}<extra></extra>"
        ))

    fig.update_layout(
        title=f"Safety Analysis Timeline - {analysis.model_name}",
        xaxis_title="Reasoning Step",
        yaxis_title="Safety Score",
        hovermode="x unified",
        height=450,
        showlegend=False
    )

    return fig

def create_category_comparison(analyses: List[CoTResponse]) -> go.Figure:
    """Create comparison of safety categories across models"""

    if not analyses:
        return go.Figure()

    models = [a.model_name for a in analyses]
    categories = ['primary_safety', 'ethical_guidance', 'refusal_patterns', 'guidance_words']

    # Calculate average category scores for each model
    data = []
    for analysis in analyses:
        row = []
        for category in categories:
            avg_score = sum(sa.category_scores.get(category, 0) for sa in analysis.safety_analyses) / len(analysis.safety_analyses)
            row.append(avg_score)
        data.append(row)

    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=categories,
        y=models,
        colorscale='Reds',
        hoverongaps=False,
        colorbar=dict(title="Safety Score")
    ))

    fig.update_layout(
        title="Safety Category Scores by Model",
        height=400,
        xaxis_title="Safety Categories",
        yaxis_title="Models"
    )

    return fig

def create_peaks_comparison(analyses: List[CoTResponse]) -> go.Figure:
    """Compare the number of safety peaks across models"""

    models = [a.model_name for a in analyses]
    peak_counts = [len(a.safety_peaks) for a in analyses]
    avg_scores = [a.overall_safety_score for a in analyses]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=models,
        y=peak_counts,
        name="Safety Peaks",
        marker=dict(color='red'),
        yaxis='y'
    ))

    fig.add_trace(go.Scatter(
        x=models,
        y=[score * max(peak_counts) * 10 for score in avg_scores], # Scale for visibility
        mode='lines+markers',
        name="Avg Safety Score (scaled)",
        line=dict(color='blue'),
        yaxis='y2'
    ))

    fig.update_layout(
        title="Safety Peak vs Average Safety Score By Model",
        xaxis_title="Models",
        yaxis=dict(title="Number of Safety Peaks", side='left'),
        yaxis2=dict(title="Average Safety Score (scaled)", side='right', overlaying='y'),
        height=400
    )

    return fig

def create_keyword_wordcloud(analyses: List[CoTResponse]) -> plt.Figure:
    """Create a word cloud of safety keywords found"""

    all_keywords = []
    for analysis in analyses:
        for sa in analysis.safety_analyses:
            all_keywords.extend(sa.safety_keywords_found)

    if not all_keywords:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, 'No safety keywords found', ha='center', va='center', transform=ax.transAxes, fontsize=16)
        ax.axis('off')
        return fig

    keyword_counts = Counter(all_keywords)

    # Create word cloud
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        colormap='Reds',
        max_words=100,
        relative_scaling=0.5
    ).generate_from_frequencies(keyword_counts)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title("Safety Keywords from SafeWork-R1 Analysis", fontsize=16, pad=20)

    return fig
"""Chart components using Plotly."""

import plotly.graph_objects as go
import plotly.express as px
from typing import List, Optional, Tuple
from datetime import date, datetime
import streamlit as st

from config.constants import COLORS


def render_donut_chart(
    score: int,
    max_score: int,
    title: str = "",
    color: str = None,
    show_percentage: bool = True
) -> None:
    """
    Render a donut chart showing score as percentage of max.
    
    Args:
        score: Current score
        max_score: Maximum possible score
        title: Chart title
        color: Primary color for the filled portion
        show_percentage: Whether to show percentage in center
    """
    if color is None:
        color = COLORS["dark_teal"]
    
    remaining = max_score - score
    percentage = (score / max_score) * 100 if max_score > 0 else 0
    
    fig = go.Figure(data=[go.Pie(
        values=[score, remaining],
        hole=0.7,
        marker_colors=[color, COLORS["light_gray"]],
        textinfo='none',
        hoverinfo='skip',
        showlegend=False
    )])
    
    # Add center text
    center_text = f"{percentage:.0f}%" if show_percentage else f"{score}/{max_score}"
    
    fig.add_annotation(
        text=f"<b>{center_text}</b>",
        x=0.5, y=0.5,
        font_size=24,
        font_color=COLORS["charcoal"],
        showarrow=False
    )
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=COLORS["charcoal"]), x=0.5),
        margin=dict(t=50, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=250,
        width=250,
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_mood_line_chart(
    dates: List[date],
    mood_scores: List[int],
    title: str = "Mood Trends",
    show_markers: bool = True
) -> None:
    """
    Render a line chart showing mood over time.
    
    Args:
        dates: List of dates
        mood_scores: List of mood scores (1-10)
        title: Chart title
        show_markers: Whether to show data point markers
    """
    if not dates or not mood_scores:
        st.info("No mood data available yet. Start logging your mood!")
        return
    
    # Format dates for display
    date_labels = [d.strftime("%b %d") if isinstance(d, (date, datetime)) else str(d) for d in dates]
    
    fig = go.Figure()
    
    # Add the main line
    fig.add_trace(go.Scatter(
        x=date_labels,
        y=mood_scores,
        mode='lines+markers' if show_markers else 'lines',
        name='Mood',
        line=dict(
            color=COLORS["dark_teal"],
            width=3,
            shape='spline'
        ),
        marker=dict(
            size=10,
            color=COLORS["dark_teal"],
            line=dict(color=COLORS["white"], width=2)
        ),
        fill='tozeroy',
        fillcolor='rgba(0, 137, 123, 0.1)',
        hovertemplate='%{x}<br>Mood: %{y}<extra></extra>'
    ))
    
    # Add reference lines
    fig.add_hline(y=5, line_dash="dash", line_color=COLORS["accent_teal"], 
                  annotation_text="Average", annotation_position="right")
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color=COLORS["charcoal"])),
        xaxis=dict(
            title="Date",
            showgrid=False,
            tickfont=dict(color=COLORS["charcoal"]),
        ),
        yaxis=dict(
            title="Mood Score",
            range=[0, 11],
            tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            tickfont=dict(color=COLORS["charcoal"]),
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, b=40, l=40, r=20),
        height=350,
        hovermode='x unified',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_sentiment_pie_chart(
    sentiment_counts: dict,
    title: str = "Sentiment Distribution"
) -> None:
    """
    Render a pie chart showing sentiment distribution.
    
    Args:
        sentiment_counts: Dict with sentiment labels as keys and counts as values
        title: Chart title
    """
    if not sentiment_counts or sum(sentiment_counts.values()) == 0:
        st.info("No sentiment data available yet.")
        return
    
    colors = {
        "POSITIVE": COLORS["success_green"],
        "NEGATIVE": COLORS["error_red"],
        "NEUTRAL": COLORS["accent_teal"],
        "positive": COLORS["success_green"],
        "negative": COLORS["error_red"],
        "neutral": COLORS["accent_teal"],
    }
    
    labels = list(sentiment_counts.keys())
    values = list(sentiment_counts.values())
    chart_colors = [colors.get(label.upper(), COLORS["accent_teal"]) for label in labels]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=chart_colors,
        textinfo='percent+label',
        textfont=dict(size=12),
        hovertemplate='%{label}: %{value} entries<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=COLORS["charcoal"]), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, b=20, l=20, r=20),
        height=300,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_sleep_bar_chart(
    dates: List[date],
    sleep_hours: List[float],
    title: str = "Sleep Patterns"
) -> None:
    """
    Render a bar chart showing sleep hours over time.
    
    Args:
        dates: List of dates
        sleep_hours: List of sleep hours
        title: Chart title
    """
    if not dates or not sleep_hours:
        st.info("No sleep data available yet.")
        return
    
    date_labels = [d.strftime("%b %d") if isinstance(d, (date, datetime)) else str(d) for d in dates]
    
    # Color bars based on sleep quality
    colors = []
    for hours in sleep_hours:
        if hours < 6:
            colors.append(COLORS["error_red"])
        elif hours < 7:
            colors.append(COLORS["warning_orange"])
        elif hours <= 9:
            colors.append(COLORS["success_green"])
        else:
            colors.append(COLORS["warning_orange"])
    
    fig = go.Figure(data=[go.Bar(
        x=date_labels,
        y=sleep_hours,
        marker_color=colors,
        hovertemplate='%{x}<br>Sleep: %{y:.1f} hours<extra></extra>'
    )])
    
    # Add recommended sleep range
    fig.add_hrect(y0=7, y1=9, line_width=0, fillcolor=COLORS["success_green"], 
                  opacity=0.1, annotation_text="Recommended", annotation_position="right")
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=COLORS["charcoal"])),
        xaxis=dict(title="Date", tickfont=dict(color=COLORS["charcoal"])),
        yaxis=dict(title="Hours", range=[0, 12], tickfont=dict(color=COLORS["charcoal"])),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, b=40, l=40, r=20),
        height=300,
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_burnout_gauge(
    risk_score: float,
    title: str = "Burnout Risk"
) -> None:
    """
    Render a gauge chart showing burnout risk level.
    
    Args:
        risk_score: Risk score (0-100)
        title: Chart title
    """
    # Determine color based on score
    if risk_score <= 30:
        bar_color = COLORS["success_green"]
    elif risk_score <= 60:
        bar_color = COLORS["warning_orange"]
    else:
        bar_color = COLORS["error_red"]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16, 'color': COLORS["charcoal"]}},
        number={'font': {'size': 40, 'color': COLORS["charcoal"]}, 'suffix': '%'},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': COLORS["charcoal"]},
            'bar': {'color': bar_color, 'thickness': 0.75},
            'bgcolor': COLORS["light_gray"],
            'borderwidth': 0,
            'steps': [
                {'range': [0, 30], 'color': 'rgba(102, 187, 106, 0.2)'},
                {'range': [30, 60], 'color': 'rgba(255, 167, 38, 0.2)'},
                {'range': [60, 100], 'color': 'rgba(239, 83, 80, 0.2)'}
            ],
            'threshold': {
                'line': {'color': COLORS["charcoal"], 'width': 2},
                'thickness': 0.75,
                'value': risk_score
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': COLORS["charcoal"]},
        margin=dict(t=50, b=20, l=30, r=30),
        height=250
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

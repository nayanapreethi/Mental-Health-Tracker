"""Glassmorphism card components."""

import streamlit as st
from typing import Optional


def render_glass_card(content: str, title: Optional[str] = None, subtitle: Optional[str] = None) -> None:
    """
    Render content inside a glassmorphism card.
    
    Args:
        content: HTML content to display inside the card
        title: Optional card title
        subtitle: Optional card subtitle
    """
    title_html = f'<div class="glass-card-title">{title}</div>' if title else ""
    subtitle_html = f'<div class="glass-card-subtitle">{subtitle}</div>' if subtitle else ""
    
    html = f"""
    <div class="glass-card">
        {title_html}
        {subtitle_html}
        {content}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_auth_card(content: str, title: str = "MindfulMe", subtitle: str = "") -> None:
    """
    Render centered authentication card.
    
    Args:
        content: HTML content for the card
        title: Card title (default: MindfulMe)
        subtitle: Card subtitle
    """
    html = f"""
    <div class="auth-container">
        <div class="auth-card">
            <div class="brand-logo">{title}</div>
            <div class="auth-subtitle">{subtitle}</div>
            {content}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_recommendation_card(title: str, text: str, severity_class: str = "") -> None:
    """
    Render a recommendation card with optional severity styling.
    
    Args:
        title: Card title
        text: Recommendation text
        severity_class: CSS class for severity (severity-minimal, severity-mild, etc.)
    """
    html = f"""
    <div class="recommendation-card">
        <div class="recommendation-title">{title}</div>
        <div class="recommendation-text">{text}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_severity_badge(level: str, color: str) -> None:
    """
    Render a severity level badge.
    
    Args:
        level: Severity level text (e.g., "Mild", "Moderate")
        color: Badge color
    """
    html = f"""
    <span class="severity-badge" style="background: {color}20; color: {color};">
        {level}
    </span>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_burnout_indicator(level: str, message: str, color: str) -> None:
    """
    Render burnout risk indicator.
    
    Args:
        level: Risk level (low, medium, high)
        message: Display message
        color: Indicator color
    """
    icon = "✓" if level == "low" else ("⚠" if level == "medium" else "⚡")
    
    html = f"""
    <div class="burnout-indicator burnout-{level}">
        <span style="font-size: 1.5rem;">{icon}</span>
        <div>
            <div style="font-weight: 600; color: {color};">{level.upper()} RISK</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">{message}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_mood_display(score: int, label: str) -> None:
    """
    Render a large mood score display.
    
    Args:
        score: Mood score (1-10)
        label: Mood label description
    """
    # Color gradient from red (1) to green (10)
    if score <= 3:
        color = "#EF5350"  # Red
    elif score <= 5:
        color = "#FFA726"  # Orange
    elif score <= 7:
        color = "#80CBC4"  # Teal
    else:
        color = "#66BB6A"  # Green
    
    html = f"""
    <div class="glass-card" style="text-align: center;">
        <div class="mood-score" style="color: {color};">{score}</div>
        <div class="mood-score-label">{label}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_journal_entry(date_str: str, text: str, sentiment: Optional[str] = None) -> None:
    """
    Render a journal entry card.
    
    Args:
        date_str: Formatted date string
        text: Journal entry text
        sentiment: Optional sentiment label
    """
    sentiment_badge = ""
    if sentiment:
        sentiment_colors = {
            "POSITIVE": "#66BB6A",
            "NEGATIVE": "#EF5350",
            "NEUTRAL": "#80CBC4"
        }
        color = sentiment_colors.get(sentiment.upper(), "#80CBC4")
        sentiment_badge = f'<span class="severity-badge" style="background: {color}20; color: {color};">{sentiment}</span>'
    
    html = f"""
    <div class="journal-entry">
        <div class="journal-date">{date_str} {sentiment_badge}</div>
        <div class="journal-text">{text[:200]}{'...' if len(text) > 200 else ''}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_stat_card(title: str, value: str, subtitle: str = "", icon: str = "") -> None:
    """
    Render a statistics card.
    
    Args:
        title: Stat title
        value: Main value to display
        subtitle: Optional subtitle
        icon: Optional emoji icon
    """
    html = f"""
    <div class="glass-card" style="text-align: center; padding: 1.5rem;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-size: 2rem; font-weight: 700; color: #00897B;">{value}</div>
        <div style="font-weight: 600; color: #263238;">{title}</div>
        <div style="font-size: 0.85rem; opacity: 0.7;">{subtitle}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

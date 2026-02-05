"""Dashboard page with mood tracking, analytics, and journal functionality."""

import streamlit as st
from datetime import datetime, date
from services.analytics_service import get_user_analytics, calculate_burnout_risk, get_weekly_report
from services.ai_service import analyze_sentiment, generate_journal_insights
from services.voice_service import analyze_voice_tension, get_tension_interpretation
from components.cards import glass_card
from components.charts import create_mood_chart, create_donut_chart
from components.voice_recorder import render_voice_recorder
from database.connection import get_session
from database.models import DailyLog
from config.constants import MOOD_SCALE, COLORS


def render():
    """Render the main dashboard page."""
    st.markdown("## 🧠 MindfulMe Dashboard")

    # Get user analytics
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("User not authenticated")
        return

    analytics = get_user_analytics(user_id)

    # Main dashboard layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # Mood tracking section
        render_mood_tracking(user_id, analytics)

        # Journal entry section
        render_journal_section(user_id)

    with col2:
        # Analytics sidebar
        render_analytics_sidebar(analytics, user_id)

        # Voice recorder
        render_voice_section(user_id)


def render_mood_tracking(user_id: int, analytics: dict):
    """Render mood tracking section."""
    with glass_card("Today's Mood & Analytics"):
        # Current mood display
        current_mood = analytics.get('current_mood', 5)

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown(f"""
                <div style="text-align: center; padding: 2rem;">
                    <div class="mood-score">{current_mood}/10</div>
                    <div class="mood-score-label">
                        {MOOD_SCALE.get(current_mood, 'Unknown')}
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # Mood slider for today
        today = date.today()
        mood_value = st.slider(
            "How are you feeling today?",
            min_value=1,
            max_value=10,
            value=int(current_mood),
            key="today_mood"
        )

        if st.button("Update Mood", key="update_mood"):
            save_mood_entry(user_id, today, mood_value)
            st.success("Mood updated!")
            st.rerun()

        # Weekly mood chart
        if analytics.get('mood_trend'):
            st.markdown("### Mood Trend (Last 30 Days)")
            mood_data = analytics['mood_trend']
            create_mood_chart(mood_data)


def render_journal_section(user_id: int):
    """Render journal entry section."""
    with glass_card("Daily Journal"):
        # Journal input
        journal_text = st.text_area(
            "What's on your mind today?",
            height=150,
            placeholder="Write about your thoughts, feelings, or experiences...",
            key="journal_text"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Save Journal Entry", key="save_journal"):
                if journal_text.strip():
                    save_journal_entry(user_id, journal_text)
                    st.success("Journal entry saved!")

                    # Show AI insights
                    insights = generate_journal_insights(journal_text)
                    display_journal_insights(insights)
                else:
                    st.warning("Please write something in your journal.")

        with col2:
            if st.button("View Past Entries", key="view_entries"):
                st.session_state.show_entries = not st.session_state.get('show_entries', False)
                st.rerun()

        # Show past entries if requested
        if st.session_state.get('show_entries', False):
            display_recent_entries(user_id)


def render_analytics_sidebar(analytics: dict, user_id: int):
    """Render analytics sidebar."""
    # Burnout indicator
    burnout_score = calculate_burnout_risk(user_id)

    with glass_card("Burnout Risk Indicator"):
        if burnout_score <= 30:
            st.success(f"Low Risk ({burnout_score:.1f})")
            st.progress(burnout_score / 100)
        elif burnout_score <= 60:
            st.warning(f"Moderate Risk ({burnout_score:.1f})")
            st.progress(burnout_score / 100)
        else:
            st.error(f"High Risk ({burnout_score:.1f})")
            st.progress(burnout_score / 100)

    # Weekly summary
    with glass_card("Weekly Summary"):
        weekly_avg = analytics.get('weekly_mood_avg', 0)
        total_journals = analytics.get('total_journals', 0)

        st.metric("Average Mood", f"{weekly_avg:.1f}/10")
        st.metric("Journal Entries", total_journals)

        # Sentiment distribution
        sentiment_dist = analytics.get('sentiment_distribution', {})
        if sentiment_dist:
            st.markdown("**Sentiment Analysis:**")
            for sentiment, count in sentiment_dist.items():
                st.write(f"{sentiment}: {count} entries")

    # Weekly report
    with glass_card("Weekly Report"):
        report = get_weekly_report(user_id)

        st.markdown(f"**{report['mood_summary']['level']}**")
        st.write(report['mood_summary']['message'])

        if report['achievements']:
            st.markdown("**Achievements:**")
            for achievement in report['achievements']:
                st.write(f"✓ {achievement}")

        if report['recommendations']:
            st.markdown("**Recommendations:**")
            for rec in report['recommendations']:
                st.write(f"• {rec}")


def render_voice_section(user_id: int):
    """Render voice recording section."""
    with glass_card("Voice Analysis"):
        st.markdown("Record your voice to analyze stress levels:")

        # Voice recorder component
        audio_data = render_voice_recorder()

        if audio_data:
            # Analyze the recorded audio
            with st.spinner("Analyzing voice..."):
                analysis = analyze_voice_tension(audio_data)

                if analysis['analysis_successful']:
                    tension_score = analysis['tension_score']
                    interpretation = get_tension_interpretation(tension_score)

                    st.markdown(f"**Tension Level: {interpretation['label']}**")
                    st.write(interpretation['message'])

                    # Save voice analysis
                    save_voice_analysis(user_id, tension_score, analysis)

                    # Progress bar
                    st.progress(tension_score / 100)

                    # Recommendations
                    from services.voice_service import generate_voice_recommendations
                    recommendations = generate_voice_recommendations(tension_score)

                    if recommendations:
                        st.markdown("**Recommendations:**")
                        for rec in recommendations:
                            st.write(f"• {rec}")
                else:
                    st.error(f"Analysis failed: {analysis.get('error', 'Unknown error')}")


def save_mood_entry(user_id: int, entry_date: date, mood_score: int):
    """Save mood entry to database."""
    with get_session() as session:
        # Check if entry already exists for today
        existing = session.query(DailyLog).filter(
            DailyLog.user_id == user_id,
            DailyLog.log_date == entry_date
        ).first()

        if existing:
            existing.mood_score = mood_score
        else:
            new_entry = DailyLog(
                user_id=user_id,
                log_date=entry_date,
                mood_score=mood_score
            )
            session.add(new_entry)


def save_journal_entry(user_id: int, journal_text: str):
    """Save journal entry with AI analysis."""
    # Analyze sentiment and emotion
    sentiment, confidence = analyze_sentiment(journal_text)
    emotion = generate_journal_insights(journal_text)['emotion']

    today = date.today()

    with get_session() as session:
        # Check if entry already exists for today
        existing = session.query(DailyLog).filter(
            DailyLog.user_id == user_id,
            DailyLog.log_date == today
        ).first()

        if existing:
            existing.journal_text = journal_text
            existing.ai_sentiment = sentiment
            existing.ai_emotion = emotion
        else:
            new_entry = DailyLog(
                user_id=user_id,
                log_date=today,
                journal_text=journal_text,
                ai_sentiment=sentiment,
                ai_emotion=emotion
            )
            session.add(new_entry)


def save_voice_analysis(user_id: int, tension_score: float, analysis: dict):
    """Save voice analysis results."""
    today = date.today()

    with get_session() as session:
        existing = session.query(DailyLog).filter(
            DailyLog.user_id == user_id,
            DailyLog.log_date == today
        ).first()

        if existing:
            existing.vocal_tension = tension_score


def display_journal_insights(insights: dict):
    """Display AI-generated insights from journal entry."""
    with st.expander("AI Insights", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            sentiment = insights.get('sentiment', 'NEUTRAL')
            confidence = insights.get('sentiment_confidence', 0.0)

            if sentiment == 'POSITIVE':
                st.success(f"Positive sentiment ({confidence:.1%} confidence)")
            elif sentiment == 'NEGATIVE':
                st.error(f"Negative sentiment ({confidence:.1%} confidence)")
            else:
                st.info(f"Neutral sentiment ({confidence:.1%} confidence)")

            st.write(f"**Emotion:** {insights.get('emotion', 'neutral').title()}")

        with col2:
            word_count = insights.get('word_count', 0)
            st.metric("Word Count", word_count)

            themes = insights.get('themes', [])
            if themes:
                st.write(f"**Themes:** {', '.join(themes)}")

        # Cognitive distortions
        distortions = insights.get('cognitive_distortions', [])
        if distortions:
            st.warning("**Cognitive Distortions Detected:**")
            for dist in distortions:
                st.write(f"• {dist['description']}")

        # Recommendations
        recommendations = insights.get('recommendations', [])
        if recommendations:
            st.info("**Suggestions:**")
            for rec in recommendations:
                st.write(f"• {rec}")


def display_recent_entries(user_id: int, limit: int = 5):
    """Display recent journal entries."""
    with get_session() as session:
        entries = session.query(DailyLog).filter(
            DailyLog.user_id == user_id,
            DailyLog.journal_text.isnot(None)
        ).order_by(DailyLog.log_date.desc()).limit(limit).all()

    if not entries:
        st.info("No journal entries found.")
        return

    for entry in entries:
        with st.expander(f"{entry.log_date.strftime('%B %d, %Y')} - Mood: {entry.mood_score}/10"):
            st.write(entry.journal_text)

            if entry.ai_sentiment:
                sentiment_color = {
                    'POSITIVE': 'green',
                    'NEGATIVE': 'red',
                    'NEUTRAL': 'blue'
                }.get(entry.ai_sentiment, 'blue')

                st.markdown(f"**Sentiment:** <span style='color:{sentiment_color}'>{entry.ai_sentiment}</span>", unsafe_allow_html=True)

            if entry.ai_emotion:
                st.write(f"**Emotion:** {entry.ai_emotion.title()}")

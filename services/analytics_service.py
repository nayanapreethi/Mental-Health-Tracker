"""Analytics service for dashboard data aggregation and calculations."""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func

from database.connection import get_session
from database.models import DailyLog, UserProfile, HealthBaseline
from config.constants import BURNOUT_THRESHOLDS


def get_user_analytics(user_id: int) -> Dict:
    """
    Get comprehensive analytics for a user.
    
    Returns:
        Dict containing various analytics metrics
    """
    analytics = {
        'current_mood': 5,  # Default
        'weekly_mood_avg': 0.0,
        'total_journals': 0,
        'mood_trend': [],
        'sentiment_distribution': {},
        'burnout_score': 0.0,
        'sleep_avg': 0.0,
        'assessment_completed': False
    }

    with get_session() as session:
        # Get current mood (today's log)
        today = datetime.now().date()
        today_log = session.query(DailyLog).filter(
            DailyLog.user_id == user_id,
            DailyLog.log_date == today
        ).first()

        if today_log:
            analytics['current_mood'] = today_log.mood_score

        # Get weekly mood average
        seven_days_ago = datetime.now() - timedelta(days=7)
        weekly_logs = session.query(DailyLog).filter(
            DailyLog.user_id == user_id,
            DailyLog.log_date >= seven_days_ago.date()
        ).all()

        if weekly_logs:
            analytics['weekly_mood_avg'] = sum(log.mood_score for log in weekly_logs) / len(weekly_logs)
            analytics['total_journals'] = len([log for log in weekly_logs if log.journal_text])

        # Get mood trend data
        thirty_days_ago = datetime.now() - timedelta(days=30)
        monthly_logs = session.query(DailyLog).filter(
            DailyLog.user_id == user_id,
            DailyLog.log_date >= thirty_days_ago.date()
        ).order_by(DailyLog.log_date).all()

        analytics['mood_trend'] = [
            {'date': log.log_date.isoformat(), 'mood': log.mood_score}
            for log in monthly_logs
        ]

        # Sentiment distribution
        sentiment_counts = {}
        for log in monthly_logs:
            if log.ai_sentiment:
                sentiment_counts[log.ai_sentiment] = sentiment_counts.get(log.ai_sentiment, 0) + 1

        analytics['sentiment_distribution'] = sentiment_counts

        # Average sleep hours
        sleep_logs = [log for log in monthly_logs if log.sleep_hours]
        if sleep_logs:
            analytics['sleep_avg'] = sum(log.sleep_hours for log in sleep_logs) / len(sleep_logs)

        # Check if assessment completed
        baseline = session.query(HealthBaseline).filter(
            HealthBaseline.user_id == user_id
        ).first()
        analytics['assessment_completed'] = baseline is not None

    return analytics


def calculate_burnout_risk(user_id: int) -> float:
    """
    Calculate burnout risk score based on recent data.
    
    Returns:
        Burnout score (0-100)
    """
    score = 0.0

    with get_session() as session:
        # Get last 7 days of data
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_logs = session.query(DailyLog).filter(
            DailyLog.user_id == user_id,
            DailyLog.log_date >= seven_days_ago.date()
        ).all()

        if not recent_logs:
            return 0.0

        # Factors contributing to burnout:
        # 1. Low mood scores (weight: 40%)
        mood_scores = [log.mood_score for log in recent_logs]
        avg_mood = sum(mood_scores) / len(mood_scores)
        mood_factor = max(0, (6 - avg_mood) / 5) * 40  # Lower mood = higher risk

        # 2. Low sleep quality/hours (weight: 30%)
        sleep_factor = 0
        sleep_logs = [log for log in recent_logs if log.sleep_hours]
        if sleep_logs:
            avg_sleep = sum(log.sleep_hours for log in sleep_logs) / len(sleep_logs)
            sleep_factor = max(0, (8 - avg_sleep) / 8) * 30  # Less than 8 hours = higher risk

        # 3. Negative sentiment in journals (weight: 20%)
        negative_count = sum(1 for log in recent_logs if log.ai_sentiment == 'NEGATIVE')
        sentiment_factor = (negative_count / len(recent_logs)) * 20

        # 4. High vocal tension (weight: 10%)
        tension_logs = [log for log in recent_logs if log.vocal_tension]
        if tension_logs:
            avg_tension = sum(log.vocal_tension for log in tension_logs) / len(tension_logs)
            tension_factor = (avg_tension / 100) * 10

        score = mood_factor + sleep_factor + sentiment_factor + tension_factor

    return min(100, score)


def get_mood_patterns(user_id: int) -> Dict:
    """
    Analyze mood patterns over time.
    
    Returns:
        Dict with pattern analysis
    """
    patterns = {
        'best_day': None,
        'worst_day': None,
        'most_improved_period': None,
        'consistency_score': 0.0,
        'trends': []
    }

    with get_session() as session:
        # Get all logs for analysis
        logs = session.query(DailyLog).filter(
            DailyLog.user_id == user_id
        ).order_by(DailyLog.log_date).all()

        if len(logs) < 7:
            return patterns

        # Find best and worst days
        mood_scores = [(log.log_date, log.mood_score) for log in logs]
        best_day = max(mood_scores, key=lambda x: x[1])
        worst_day = min(mood_scores, key=lambda x: x[1])

        patterns['best_day'] = {
            'date': best_day[0].isoformat(),
            'mood': best_day[1]
        }
        patterns['worst_day'] = {
            'date': worst_day[0].isoformat(),
            'mood': worst_day[1]
        }

        # Calculate consistency (lower variance = higher consistency)
        scores = [log.mood_score for log in logs]
        if len(scores) > 1:
            mean_score = sum(scores) / len(scores)
            variance = sum((x - mean_score) ** 2 for x in scores) / len(scores)
            patterns['consistency_score'] = max(0, 10 - variance)  # Scale to 0-10

        # Simple trend analysis (last 14 days vs previous 14 days)
        if len(logs) >= 28:
            recent_14 = logs[-14:]
            previous_14 = logs[-28:-14]

            recent_avg = sum(log.mood_score for log in recent_14) / len(recent_14)
            previous_avg = sum(log.mood_score for log in previous_14) / len(previous_14)

            improvement = recent_avg - previous_avg
            patterns['trends'].append({
                'period': 'Last 2 weeks',
                'change': improvement,
                'direction': 'improving' if improvement > 0 else 'declining'
            })

    return patterns


def get_weekly_report(user_id: int) -> Dict:
    """
    Generate a weekly mental health report.
    
    Returns:
        Dict with weekly insights
    """
    report = {
        'period': 'Last 7 days',
        'mood_summary': {},
        'journal_insights': {},
        'recommendations': [],
        'achievements': []
    }

    analytics = get_user_analytics(user_id)

    # Mood summary
    weekly_avg = analytics['weekly_mood_avg']
    if weekly_avg >= 8:
        report['mood_summary'] = {
            'level': 'Excellent',
            'message': 'You\'ve been feeling great this week!'
        }
    elif weekly_avg >= 6:
        report['mood_summary'] = {
            'level': 'Good',
            'message': 'You\'ve maintained a positive mood this week.'
        }
    elif weekly_avg >= 4:
        report['mood_summary'] = {
            'level': 'Fair',
            'message': 'There\'s room for improvement, but you\'re doing okay.'
        }
    else:
        report['mood_summary'] = {
            'level': 'Concerning',
            'message': 'Consider reaching out for additional support.'
        }

    # Journal insights
    total_journals = analytics['total_journals']
    if total_journals >= 5:
        report['achievements'].append('Consistent journaling habit')
    elif total_journals >= 3:
        report['achievements'].append('Regular reflection practice')

    # Recommendations based on data
    burnout_score = calculate_burnout_risk(user_id)
    if burnout_score > BURNOUT_THRESHOLDS['medium']['max_score']:
        report['recommendations'].append('Consider taking a break and practicing self-care')
    elif burnout_score > BURNOUT_THRESHOLDS['low']['max_score']:
        report['recommendations'].append('Monitor your stress levels and ensure adequate rest')

    if weekly_avg < 5:
        report['recommendations'].append('Try incorporating daily mindfulness or exercise')

    return report

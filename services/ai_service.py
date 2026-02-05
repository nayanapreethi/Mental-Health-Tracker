"""AI service for sentiment analysis and text processing using DistilBERT."""

import streamlit as st
from typing import Dict, Optional, Tuple
import re

# Lazy loading of AI models
@st.cache_resource
def load_sentiment_model():
    """Load the sentiment analysis model (cached for performance)."""
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch

        # Use DistilBERT for faster inference
        model_name = "distilbert-base-uncased-finetuned-sst-2-english"

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)

        return tokenizer, model
    except ImportError:
        st.error("Transformers library not installed. Please install with: pip install transformers torch")
        return None, None
    except Exception as e:
        st.error(f"Error loading AI model: {str(e)}")
        return None, None


def analyze_sentiment(text: str) -> Tuple[str, float]:
    """
    Analyze sentiment of text using DistilBERT.

    Args:
        text: Input text to analyze

    Returns:
        Tuple of (sentiment_label, confidence_score)
    """
    if not text or not text.strip():
        return "NEUTRAL", 0.5

    tokenizer, model = load_sentiment_model()

    if not tokenizer or not model:
        return "NEUTRAL", 0.5

    try:
        # Preprocess text
        text = text.strip()
        if len(text) > 512:  # Truncate if too long
            text = text[:512]

        # Tokenize and predict
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        outputs = model(**inputs)

        # Get probabilities
        import torch
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        confidence, predicted_class = torch.max(probabilities, dim=-1)

        # Map to sentiment labels
        labels = ["NEGATIVE", "POSITIVE"]
        sentiment = labels[predicted_class.item()]
        confidence_score = confidence.item()

        return sentiment, confidence_score

    except Exception as e:
        st.warning(f"Sentiment analysis failed: {str(e)}")
        return "NEUTRAL", 0.5


def analyze_emotion(text: str) -> str:
    """
    Analyze emotion in text using keyword-based approach.
    This is a simplified emotion detection for demo purposes.

    Args:
        text: Input text to analyze

    Returns:
        Emotion label
    """
    if not text:
        return "neutral"

    text_lower = text.lower()

    # Emotion keywords
    emotions = {
        "joy": ["happy", "joy", "excited", "great", "wonderful", "amazing", "love", "fantastic"],
        "sadness": ["sad", "depressed", "unhappy", "miserable", "down", "blue", "heartbroken"],
        "anger": ["angry", "mad", "furious", "irritated", "annoyed", "frustrated", "hate"],
        "fear": ["scared", "afraid", "anxious", "worried", "nervous", "terrified", "panic"],
        "surprise": ["surprised", "shocked", "amazed", "astonished", "unexpected"],
        "disgust": ["disgusted", "gross", "repulsed", "sick", "hate", "awful"]
    }

    # Count emotion keywords
    emotion_scores = {}
    for emotion, keywords in emotions.items():
        count = sum(1 for keyword in keywords if keyword in text_lower)
        if count > 0:
            emotion_scores[emotion] = count

    if emotion_scores:
        return max(emotion_scores, key=emotion_scores.get)

    return "neutral"


def detect_cognitive_distortions(text: str) -> List[Dict]:
    """
    Detect cognitive distortions in text.

    Args:
        text: Input text to analyze

    Returns:
        List of detected distortions with explanations
    """
    from config.constants import COGNITIVE_DISTORTIONS

    detected = []
    text_lower = text.lower()

    for distortion_name, distortion_data in COGNITIVE_DISTORTIONS.items():
        patterns = distortion_data["patterns"]
        description = distortion_data["description"]

        # Check if any pattern matches
        for pattern in patterns:
            if re.search(r'\b' + re.escape(pattern) + r'\b', text_lower):
                detected.append({
                    "type": distortion_name,
                    "description": description,
                    "matched_pattern": pattern
                })
                break  # Only add once per distortion type

    return detected


def generate_journal_insights(text: str) -> Dict:
    """
    Generate insights from journal entry.

    Args:
        text: Journal text

    Returns:
        Dict with various insights
    """
    insights = {
        "sentiment": "NEUTRAL",
        "sentiment_confidence": 0.0,
        "emotion": "neutral",
        "cognitive_distortions": [],
        "word_count": 0,
        "themes": [],
        "recommendations": []
    }

    if not text or not text.strip():
        return insights

    # Basic text analysis
    insights["word_count"] = len(text.split())

    # Sentiment analysis
    sentiment, confidence = analyze_sentiment(text)
    insights["sentiment"] = sentiment
    insights["sentiment_confidence"] = confidence

    # Emotion analysis
    insights["emotion"] = analyze_emotion(text)

    # Cognitive distortions
    insights["cognitive_distortions"] = detect_cognitive_distortions(text)

    # Simple theme detection
    text_lower = text.lower()
    themes = []

    if any(word in text_lower for word in ["work", "job", "career", "boss", "colleague"]):
        themes.append("work-related")
    if any(word in text_lower for word in ["family", "parent", "child", "spouse", "relationship"]):
        themes.append("family/relationships")
    if any(word in text_lower for word in ["health", "sick", "pain", "doctor", "medicine"]):
        themes.append("health concerns")
    if any(word in text_lower for word in ["stress", "anxious", "worried", "overwhelmed"]):
        themes.append("stress/anxiety")
    if any(word in text_lower for word in ["sleep", "tired", "exhausted", "rest"]):
        themes.append("sleep/fatigue")

    insights["themes"] = themes

    # Generate recommendations based on analysis
    recommendations = []

    if sentiment == "NEGATIVE" and confidence > 0.7:
        recommendations.append("Consider practicing mindfulness or deep breathing exercises")
        if "stress" in themes:
            recommendations.append("Try progressive muscle relaxation before bed")

    if insights["emotion"] == "anger":
        recommendations.append("Consider journaling about what specifically triggered this anger")

    if insights["cognitive_distortions"]:
        recommendations.append("Notice any 'all-or-nothing' thinking patterns and challenge them")

    if "sleep" in themes and sentiment == "NEGATIVE":
        recommendations.append("Establish a consistent bedtime routine")

    insights["recommendations"] = recommendations

    return insights


def summarize_journal_entries(entries: List[str]) -> str:
    """
    Generate a summary of multiple journal entries.

    Args:
        entries: List of journal texts

    Returns:
        Summary string
    """
    if not entries:
        return "No entries to summarize."

    total_entries = len(entries)
    sentiments = []
    emotions = []
    themes = []

    for entry in entries:
        insights = generate_journal_insights(entry)
        sentiments.append(insights["sentiment"])
        emotions.append(insights["emotion"])
        themes.extend(insights["themes"])

    # Analyze patterns
    positive_count = sentiments.count("POSITIVE")
    negative_count = sentiments.count("NEGATIVE")
    neutral_count = sentiments.count("NEUTRAL")

    # Most common emotion
    emotion_counts = {}
    for emotion in emotions:
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    common_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else "neutral"

    # Most common themes
    theme_counts = {}
    for theme in themes:
        theme_counts[theme] = theme_counts.get(theme, 0) + 1
    common_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:3]

    # Generate summary
    summary_parts = [f"Summary of {total_entries} journal entries:"]

    if positive_count > negative_count:
        summary_parts.append("Overall positive sentiment")
    elif negative_count > positive_count:
        summary_parts.append("Overall negative sentiment")
    else:
        summary_parts.append("Mixed sentiment")

    summary_parts.append(f"Common emotional tone: {common_emotion}")

    if common_themes:
        theme_str = ", ".join([theme for theme, _ in common_themes])
        summary_parts.append(f"Frequent themes: {theme_str}")

    return ". ".join(summary_parts)

"""Application constants including colors, questionnaire data, and scales."""

# Color palette (Mindify theme)
COLORS = {
    "soft_teal": "#B2DFDB",
    "white": "#FFFFFF",
    "charcoal": "#263238",
    "light_gray": "#F5F5F5",
    "accent_teal": "#80CBC4",
    "dark_teal": "#00897B",
    "error_red": "#EF5350",
    "warning_orange": "#FFA726",
    "success_green": "#66BB6A",
}

# Mood scale (1-10)
MOOD_SCALE = {
    1: "Very Low",
    2: "Low",
    3: "Somewhat Low",
    4: "Below Average",
    5: "Average",
    6: "Above Average",
    7: "Good",
    8: "Very Good",
    9: "Excellent",
    10: "Outstanding",
}

# Sleep quality scale (1-5)
SLEEP_QUALITY_SCALE = {
    1: "Very Poor",
    2: "Poor",
    3: "Fair",
    4: "Good",
    5: "Excellent",
}

# PHQ-9 Questions (Patient Health Questionnaire-9)
PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless",
    "Trouble falling or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself - or that you are a failure or have let yourself or your family down",
    "Trouble concentrating on things, such as reading the newspaper or watching television",
    "Moving or speaking so slowly that other people could have noticed, or the opposite - being so fidgety or restless that you have been moving around a lot more than usual",
    "Thoughts that you would be better off dead, or of hurting yourself in some way",
]

# PHQ-9 Response options
PHQ9_OPTIONS = {
    0: "Not at all",
    1: "Several days",
    2: "More than half the days",
    3: "Nearly every day",
}

# PHQ-9 Severity levels
PHQ9_SEVERITY = {
    (0, 4): {"level": "Minimal", "color": COLORS["success_green"], "recommendation": "Continue maintaining your mental wellness routine."},
    (5, 9): {"level": "Mild", "color": COLORS["accent_teal"], "recommendation": "Consider daily mindfulness exercises and monitor your mood."},
    (10, 14): {"level": "Moderate", "color": COLORS["warning_orange"], "recommendation": "Professional consultation recommended. Practice stress-reduction techniques."},
    (15, 19): {"level": "Moderately Severe", "color": COLORS["warning_orange"], "recommendation": "Strongly consider speaking with a mental health professional."},
    (20, 27): {"level": "Severe", "color": COLORS["error_red"], "recommendation": "Please seek professional help. Contact a mental health provider."},
}

# GAD-7 Questions (Generalized Anxiety Disorder-7)
GAD7_QUESTIONS = [
    "Feeling nervous, anxious, or on edge",
    "Not being able to stop or control worrying",
    "Worrying too much about different things",
    "Trouble relaxing",
    "Being so restless that it's hard to sit still",
    "Becoming easily annoyed or irritable",
    "Feeling afraid as if something awful might happen",
]

# GAD-7 Response options (same as PHQ-9)
GAD7_OPTIONS = PHQ9_OPTIONS

# GAD-7 Severity levels
GAD7_SEVERITY = {
    (0, 4): {"level": "Minimal", "color": COLORS["success_green"], "recommendation": "Your anxiety levels are within normal range. Keep up healthy habits."},
    (5, 9): {"level": "Mild", "color": COLORS["accent_teal"], "recommendation": "Practice breathing exercises and consider journaling your thoughts."},
    (10, 14): {"level": "Moderate", "color": COLORS["warning_orange"], "recommendation": "Consider speaking with a counselor. Implement daily relaxation techniques."},
    (15, 21): {"level": "Severe", "color": COLORS["error_red"], "recommendation": "Professional support is recommended. Please consult a mental health provider."},
}

# Health goals options
HEALTH_GOALS = [
    "Reduce anxiety",
    "Manage depression symptoms",
    "Improve sleep quality",
    "Build emotional resilience",
    "Practice mindfulness",
    "Track mood patterns",
    "Develop coping strategies",
    "Maintain work-life balance",
]

# Profession categories
PROFESSION_CATEGORIES = [
    "Student",
    "Healthcare Professional",
    "Technology/IT",
    "Education",
    "Business/Finance",
    "Creative/Arts",
    "Service Industry",
    "Self-employed",
    "Retired",
    "Other",
]

# Burnout risk thresholds
BURNOUT_THRESHOLDS = {
    "low": {"max_score": 30, "color": COLORS["success_green"], "message": "Low burnout risk"},
    "medium": {"max_score": 60, "color": COLORS["warning_orange"], "message": "Moderate burnout risk - consider taking breaks"},
    "high": {"max_score": 100, "color": COLORS["error_red"], "message": "High burnout risk - prioritize self-care"},
}

# Voice analysis thresholds
VOICE_TENSION_THRESHOLDS = {
    "relaxed": {"max": 30, "label": "Relaxed"},
    "normal": {"max": 50, "label": "Normal"},
    "mild_stress": {"max": 70, "label": "Mild Stress"},
    "high_stress": {"max": 100, "label": "High Stress"},
}

# Sentiment labels
SENTIMENT_LABELS = {
    "POSITIVE": {"color": COLORS["success_green"], "icon": "smile"},
    "NEGATIVE": {"color": COLORS["error_red"], "icon": "frown"},
    "NEUTRAL": {"color": COLORS["accent_teal"], "icon": "meh"},
}

# Cognitive distortion patterns
COGNITIVE_DISTORTIONS = {
    "catastrophizing": {
        "patterns": ["worst", "terrible", "disaster", "ruined", "end of the world", "never recover"],
        "description": "Expecting the worst possible outcome",
    },
    "black_and_white": {
        "patterns": ["always", "never", "everyone", "no one", "everything", "nothing"],
        "description": "All-or-nothing thinking",
    },
    "mind_reading": {
        "patterns": ["they think", "they must think", "everyone thinks", "they probably think"],
        "description": "Assuming you know what others are thinking",
    },
    "should_statements": {
        "patterns": ["should have", "must have", "ought to", "have to"],
        "description": "Using 'should' statements to criticize yourself or others",
    },
    "overgeneralization": {
        "patterns": ["this always happens", "i never", "every time", "nothing ever"],
        "description": "Drawing broad conclusions from a single event",
    },
}

# MindfulMe Implementation Plan

## Overview
Build a Streamlit-based mental health tracking app with glassmorphism UI, local AI inference (DistilBERT/Librosa), browser voice recording, and SQLite database.

## User Choices
- **Database**: SQLite for dev (PostgreSQL-compatible schema)
- **AI Models**: Lazy loading with `@st.cache_resource`
- **Voice Input**: Browser recording via MediaRecorder API
- **UI Theme**: Custom CSS overlay (Soft Teal #B2DFDB, White #FFFFFF, Charcoal #263238)

---

## Project Structure

```
Mental Health Tracker/
├── app.py                         # Main router with CSS injection
├── requirements.txt
├── .env.example
│
├── config/
│   ├── __init__.py
│   ├── settings.py                # Environment config loader
│   └── constants.py               # Colors, scales, questionnaire data
│
├── database/
│   ├── __init__.py
│   ├── models.py                  # SQLAlchemy ORM (User, Profile, Logs, Baseline)
│   ├── connection.py              # Session factory
│   └── init_db.py                 # Schema creation
│
├── services/
│   ├── __init__.py
│   ├── auth_service.py            # bcrypt login/signup
│   ├── ai_service.py              # @st.cache_resource DistilBERT loading
│   ├── voice_service.py           # Librosa pitch/jitter analysis
│   ├── questionnaire_service.py   # PHQ-9/GAD-7 scoring
│   └── analytics_service.py       # Dashboard aggregation, burnout forecast
│
├── pages/
│   ├── __init__.py
│   ├── auth.py                    # Login/Signup glassmorphism cards
│   ├── onboarding.py              # Multi-step profile wizard
│   ├── clinical_assessment.py     # PHQ-9/GAD-7 with donut charts
│   └── dashboard.py               # Mood chart, journals, burnout indicator
│
├── components/
│   ├── __init__.py
│   ├── charts.py                  # Plotly donut/line charts
│   ├── cards.py                   # Glass card wrapper
│   ├── forms.py                   # Reusable inputs
│   └── voice_recorder.py          # HTML/JS MediaRecorder component
│
├── static/
│   ├── styles.css                 # Glassmorphism theme
│   └── recorder.js                # Audio capture logic
│
└── utils/
    ├── __init__.py
    ├── validators.py              # Email, password validation
    └── session_manager.py         # Session state helpers
```

---

## Implementation Order

### Phase 1: Foundation
1. `requirements.txt` - Dependencies
2. `config/settings.py` - Environment loader
3. `database/models.py` - All 4 SQLAlchemy models
4. `database/connection.py` - Session factory
5. `database/init_db.py` - Schema creation
6. `services/auth_service.py` - bcrypt hashing
7. `utils/session_manager.py` - Session state utilities
8. `static/styles.css` - Glassmorphism CSS
9. `components/cards.py` - Glass card component
10. `pages/auth.py` - Login/Signup page
11. `app.py` - Router entry point

### Phase 2: User Profiling
12. `components/forms.py` - Form helpers
13. `pages/onboarding.py` - Multi-step wizard

### Phase 3: Clinical Assessment
14. `config/constants.py` - PHQ-9/GAD-7 questions
15. `services/questionnaire_service.py` - Scoring logic
16. `components/charts.py` - Donut/line charts
17. `pages/clinical_assessment.py` - Assessment page

### Phase 4: AI Services
18. `services/ai_service.py` - DistilBERT sentiment
19. `services/voice_service.py` - Librosa analysis

### Phase 5: Voice Recording
20. `static/recorder.js` - MediaRecorder JS
21. `components/voice_recorder.py` - Streamlit component

### Phase 6: Dashboard
22. `services/analytics_service.py` - Data aggregation
23. `pages/dashboard.py` - Main dashboard

### Phase 7: Polish
24. Add sidebar navigation to `app.py`
25. `utils/validators.py` - Input validation

---

## Database Schema

```sql
-- users
id, username (unique), email (unique), hashed_password, created_at

-- user_profiles  
id, user_id (FK unique), age, profession, sleep_hours, sleep_quality, health_goals

-- health_baseline
id, user_id (FK unique), phq9_score, gad7_score, phq9_severity, gad7_severity, last_test_date

-- daily_logs
id, user_id (FK), log_date, mood_score, journal_text, ai_sentiment, ai_emotion, vocal_tension, sleep_hours, created_at
UNIQUE(user_id, log_date)
```

---

## Key Patterns

### CSS Injection (app.py)
```python
with open('static/styles.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
```

### Lazy AI Loading (ai_service.py)
```python
@st.cache_resource
def load_sentiment_model():
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
    model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
    return tokenizer, model
```

### Browser Voice Recording
- Inject MediaRecorder JS via `st.components.v1.html()`
- Capture audio as base64 blob
- Decode in Python, save temp file, process with Librosa

---

## Verification Plan

1. **Run app**: `streamlit run app.py`
2. **Test auth flow**: Sign up, logout, login
3. **Complete onboarding**: Fill all steps, verify DB insert
4. **Take assessment**: PHQ-9 + GAD-7, check donut charts render
5. **Dashboard**: Submit text journal, verify sentiment analysis
6. **Voice recording**: Record audio, verify stress analysis (Chrome/Firefox)
7. **Mood chart**: Add multiple logs, verify 7-day chart
8. **Burnout indicator**: Check calculation based on recent data

---

## Dependencies (requirements.txt)

```
streamlit>=1.31.0
sqlalchemy>=2.0.0
bcrypt>=4.1.0
transformers>=4.36.0
torch>=2.0.0
librosa>=0.10.0
plotly>=5.18.0
python-dotenv>=1.0.0
numpy>=1.24.0
scipy>=1.11.0
soundfile>=0.12.0
```

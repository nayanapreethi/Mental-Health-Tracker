"""Voice analysis service using Librosa for vocal tension detection."""

import streamlit as st
import numpy as np
from typing import Dict, Optional, Tuple
import io

# Lazy loading of voice analysis libraries
@st.cache_resource
def load_voice_libraries():
    """Load voice analysis libraries (cached for performance)."""
    try:
        import librosa
        import scipy.signal
        return librosa, scipy.signal
    except ImportError:
        st.error("Librosa or scipy not installed. Please install with: pip install librosa scipy")
        return None, None


def analyze_voice_tension(audio_data: bytes, sample_rate: int = 44100) -> Dict:
    """
    Analyze vocal tension from audio data.

    Args:
        audio_data: Raw audio bytes
        sample_rate: Audio sample rate

    Returns:
        Dict with tension analysis results
    """
    librosa, scipy = load_voice_libraries()

    if not librosa or not scipy:
        return {
            "tension_score": 50.0,  # Default neutral
            "pitch_variability": 0.0,
            "jitter": 0.0,
            "shimmer": 0.0,
            "analysis_successful": False,
            "error": "Voice analysis libraries not available"
        }

    try:
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.float32)

        # Ensure audio is not empty
        if len(audio_array) == 0:
            return {
                "tension_score": 50.0,
                "pitch_variability": 0.0,
                "jitter": 0.0,
                "shimmer": 0.0,
                "analysis_successful": False,
                "error": "Empty audio data"
            }

        # Extract features
        features = extract_voice_features(audio_array, sample_rate, librosa, scipy)

        # Calculate tension score (0-100)
        tension_score = calculate_tension_score(features)

        return {
            "tension_score": tension_score,
            "pitch_variability": features.get("pitch_variability", 0.0),
            "jitter": features.get("jitter", 0.0),
            "shimmer": features.get("shimmer", 0.0),
            "analysis_successful": True,
            "error": None
        }

    except Exception as e:
        st.warning(f"Voice analysis failed: {str(e)}")
        return {
            "tension_score": 50.0,
            "pitch_variability": 0.0,
            "jitter": 0.0,
            "shimmer": 0.0,
            "analysis_successful": False,
            "error": str(e)
        }


def extract_voice_features(audio: np.ndarray, sr: int, librosa, scipy) -> Dict:
    """
    Extract voice features for tension analysis.

    Args:
        audio: Audio signal
        sr: Sample rate
        librosa: Librosa library
        scipy: Scipy library

    Returns:
        Dict of extracted features
    """
    features = {}

    try:
        # Extract fundamental frequency (pitch)
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio,
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7'),
            sr=sr,
            frame_length=2048,
            hop_length=512
        )

        # Filter out unvoiced frames
        f0_voiced = f0[voiced_flag]

        if len(f0_voiced) > 10:  # Need minimum frames for analysis
            # Pitch variability (coefficient of variation)
            pitch_mean = np.mean(f0_voiced)
            pitch_std = np.std(f0_voiced)
            features["pitch_variability"] = (pitch_std / pitch_mean) * 100 if pitch_mean > 0 else 0

            # Jitter (pitch perturbation)
            # Calculate differences between consecutive pitch values
            pitch_diffs = np.abs(np.diff(f0_voiced))
            features["jitter"] = np.mean(pitch_diffs) / pitch_mean if pitch_mean > 0 else 0

        # Extract amplitude envelope
        amplitude = np.abs(audio)

        # Shimmer (amplitude perturbation)
        if len(amplitude) > 1000:
            # Calculate amplitude differences
            amp_diffs = np.abs(np.diff(amplitude))
            features["shimmer"] = np.mean(amp_diffs) / np.mean(amplitude) if np.mean(amplitude) > 0 else 0

        # Spectral features
        # Calculate spectral centroid (brightness of voice)
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
        features["spectral_centroid"] = np.mean(spectral_centroid)

        # Zero-crossing rate (voice quality indicator)
        zcr = librosa.feature.zero_crossing_rate(audio)
        features["zero_crossing_rate"] = np.mean(zcr)

        # RMS energy
        rms = librosa.feature.rms(y=audio)
        features["rms_energy"] = np.mean(rms)

    except Exception as e:
        # If feature extraction fails, return default values
        features = {
            "pitch_variability": 0.0,
            "jitter": 0.0,
            "shimmer": 0.0,
            "spectral_centroid": 0.0,
            "zero_crossing_rate": 0.0,
            "rms_energy": 0.0
        }

    return features


def calculate_tension_score(features: Dict) -> float:
    """
    Calculate vocal tension score from extracted features.

    Args:
        features: Dict of voice features

    Returns:
        Tension score (0-100)
    """
    score = 50.0  # Start at neutral

    # Pitch variability (higher = more tense)
    pitch_var = features.get("pitch_variability", 0.0)
    if pitch_var > 20:  # High variability indicates tension
        score += min(20, (pitch_var - 20) / 2)
    elif pitch_var < 5:  # Very low variability might indicate monotone/stress
        score += 10

    # Jitter (higher = more tense)
    jitter = features.get("jitter", 0.0)
    if jitter > 0.01:
        score += min(15, jitter * 1000)

    # Shimmer (higher = more tense)
    shimmer = features.get("shimmer", 0.0)
    if shimmer > 0.1:
        score += min(10, shimmer * 50)

    # Spectral centroid (higher frequency = more tense)
    centroid = features.get("spectral_centroid", 0.0)
    if centroid > 3000:  # High frequency content
        score += min(10, (centroid - 3000) / 500)

    # Zero crossing rate (higher = more tense/strained voice)
    zcr = features.get("zero_crossing_rate", 0.0)
    if zcr > 0.15:
        score += min(5, (zcr - 0.15) * 100)

    # RMS energy (very low or very high might indicate tension)
    rms = features.get("rms_energy", 0.0)
    if rms < 0.05:  # Very quiet voice
        score += 10
    elif rms > 0.3:  # Very loud/shouty voice
        score += 15

    # Ensure score is within 0-100 range
    return max(0.0, min(100.0, score))


def get_tension_interpretation(tension_score: float) -> Dict:
    """
    Interpret the tension score.

    Args:
        tension_score: Tension score (0-100)

    Returns:
        Dict with interpretation
    """
    from config.constants import VOICE_TENSION_THRESHOLDS

    if tension_score <= VOICE_TENSION_THRESHOLDS["relaxed"]["max"]:
        level = "relaxed"
        message = "Your voice sounds relaxed and calm."
        color = "#66BB6A"
    elif tension_score <= VOICE_TENSION_THRESHOLDS["normal"]["max"]:
        level = "normal"
        message = "Your voice sounds normal with moderate tension."
        color = "#80CBC4"
    elif tension_score <= VOICE_TENSION_THRESHOLDS["mild_stress"]["max"]:
        level = "mild_stress"
        message = "Your voice shows signs of mild stress. Consider relaxation techniques."
        color = "#FFA726"
    else:
        level = "high_stress"
        message = "Your voice indicates high stress levels. Please consider professional support."
        color = "#EF5350"

    return {
        "level": level,
        "label": VOICE_TENSION_THRESHOLDS[level]["label"],
        "message": message,
        "color": color
    }


def process_audio_file(file_path: str) -> Dict:
    """
    Process an audio file for tension analysis.

    Args:
        file_path: Path to audio file

    Returns:
        Dict with analysis results
    """
    librosa, _ = load_voice_libraries()

    if not librosa:
        return {
            "tension_score": 50.0,
            "analysis_successful": False,
            "error": "Voice analysis libraries not available"
        }

    try:
        # Load audio file
        audio, sr = librosa.load(file_path, sr=None)

        # Convert to bytes-like object for analysis
        audio_bytes = audio.tobytes()

        # Analyze
        return analyze_voice_tension(audio_bytes, sr)

    except Exception as e:
        return {
            "tension_score": 50.0,
            "analysis_successful": False,
            "error": f"Failed to process audio file: {str(e)}"
        }


def generate_voice_recommendations(tension_score: float) -> List[str]:
    """
    Generate recommendations based on voice tension analysis.

    Args:
        tension_score: Tension score (0-100)

    Returns:
        List of recommendations
    """
    recommendations = []

    if tension_score > 70:
        recommendations.extend([
            "Practice deep breathing exercises before speaking",
            "Consider vocal warm-up exercises",
            "Take breaks during stressful conversations",
            "Stay hydrated to maintain vocal health"
        ])
    elif tension_score > 50:
        recommendations.extend([
            "Try relaxation techniques like progressive muscle relaxation",
            "Practice mindfulness meditation",
            "Ensure adequate rest and sleep"
        ])
    elif tension_score < 30:
        recommendations.extend([
            "Your voice sounds relaxed - keep up the good work!",
            "Continue practicing stress management techniques"
        ])

    return recommendations

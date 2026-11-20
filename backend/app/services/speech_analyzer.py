import re
from typing import Dict, Any, Optional

FILLER_PATTERNS = [
    r'\bum\b',
    r'\buh\b',
    r'\ber\b',
    r'\bah\b',
    r'\blike\b',
    r'\bbasically\b',
    r'\bactually\b',
    r'\byou know\b',
    r'\bi mean\b',
    r'\bkind of\b',
    r'\bsort of\b'
]

def analyze_speech_transcript(
    transcript: str,
    duration_seconds: Optional[float] = None
) -> Dict[str, Any]:
    """
    Performs speech and communication analysis on the candidate's answer transcript.
    Computes filler word density, pace (WPM), and cautious communication indicators.
    """
    clean_text = transcript.strip().lower()
    words = re.findall(r'\b[a-zA-Z0-9_\'-]+\b', clean_text)
    total_words = len(words)

    filler_breakdown: Dict[str, int] = {}
    total_fillers = 0

    for pattern in FILLER_PATTERNS:
        matches = re.findall(pattern, clean_text)
        count = len(matches)
        if count > 0:
            key = pattern.replace(r'\b', '')
            filler_breakdown[key] = count
            total_fillers += count

    filler_freq_pct = round((total_fillers / total_words * 100), 1) if total_words > 0 else 0.0

    # Words per minute calculation: only calculate if duration was recorded from audio
    wpm: Optional[float] = None
    if duration_seconds and duration_seconds > 0 and total_words > 0:
        wpm = round((total_words / (duration_seconds / 60.0)), 1)

    # Communication indicators (cautious qualitative indicators)
    clarity_score = 9.0
    if filler_freq_pct > 8.0:
        clarity_score -= 2.5
    elif filler_freq_pct > 4.0:
        clarity_score -= 1.0

    conciseness_score = 8.5
    if total_words > 180:
        conciseness_score -= 1.5
    elif total_words < 20:
        conciseness_score -= 2.0

    structure_score = 8.0
    if any(k in clean_text for k in ["first", "second", "specifically", "for example", "in summary", "because", "furthermore"]):
        structure_score += 1.2
    structure_score = min(structure_score, 10.0)

    # Vocabulary diversity (unique word ratio)
    unique_words = len(set(words))
    vocab_ratio = round(unique_words / total_words, 2) if total_words > 0 else 1.0
    vocab_score = min(round(vocab_ratio * 10, 1), 9.5)

    if wpm is not None:
        pacing_assessment = "Optimal" if 110 <= wpm <= 160 else ("Brisk" if wpm > 160 else "Measured")
    else:
        pacing_assessment = "N/A (Text Response)"

    if filler_freq_pct < 4.0:
        observations = "Clear and articulate delivery with minimal verbal hesitations."
    else:
        observations = f"Observed occasional verbal fillers ({filler_freq_pct}% of words). Pausing deliberately between thoughts can enhance executive presence."

    if wpm is not None and (wpm > 175 or wpm < 95):
        observations += f" Spoken pace was {wpm} WPM ({pacing_assessment})."

    communication_indicators = {
        "clarity_indicator": round(clarity_score, 1),
        "conciseness_indicator": round(conciseness_score, 1),
        "structure_indicator": round(structure_score, 1),
        "vocabulary_indicator": round(vocab_score, 1),
        "pacing_assessment": pacing_assessment,
        "observations": observations
    }

    return {
        "filler_words_count": total_fillers,
        "filler_breakdown": filler_breakdown,
        "filler_frequency_pct": filler_freq_pct,
        "words_count": total_words,
        "speech_pace_wpm": wpm,
        "communication_indicators": communication_indicators
    }

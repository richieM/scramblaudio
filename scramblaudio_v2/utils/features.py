"""
Feature extraction utilities for MIR (Music Information Retrieval)

Extracts timbral and rhythmic features from audio samples.
Requires librosa for full functionality.
"""

import numpy as np
from typing import Dict, Any


def extract_features(audio: np.ndarray, sr: int) -> Dict[str, Any]:
    """
    Extract comprehensive MIR features from audio

    Args:
        audio: Audio signal as numpy array
        sr: Sample rate in Hz

    Returns:
        Dict of features including:
        - brightness: Spectral centroid (timbral brightness)
        - noisiness: Spectral flatness (how noise-like vs tonal)
        - energy: RMS energy
        - zcr: Zero-crossing rate (roughness indicator)
        - duration: Length in seconds
        - mfcc: First 13 MFCCs (timbral texture)
    """
    features = {}

    # Basic features (always available)
    features['duration'] = len(audio) / sr
    features['energy'] = float(np.sqrt(np.mean(audio**2)))

    # Zero-crossing rate (simple, no dependencies)
    zcr = np.sum(np.abs(np.diff(np.sign(audio)))) / (2 * len(audio))
    features['zcr'] = float(zcr)

    # Try to use librosa for advanced features
    try:
        import librosa

        # Spectral centroid (brightness)
        centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
        features['brightness'] = float(np.mean(centroid))

        # Spectral flatness (noisiness)
        flatness = librosa.feature.spectral_flatness(y=audio)
        features['noisiness'] = float(np.mean(flatness))

        # Spectral bandwidth
        bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)
        features['bandwidth'] = float(np.mean(bandwidth))

        # Spectral rolloff
        rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
        features['rolloff'] = float(np.mean(rolloff))

        # MFCCs (timbral texture)
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        features['mfcc'] = [float(np.mean(m)) for m in mfcc]

        # Onset strength (rhythmic character)
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
        features['onset_strength'] = float(np.mean(onset_env))

        # Tempo estimation (if long enough)
        if len(audio) / sr > 1.0:
            tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
            features['tempo'] = float(tempo)

    except ImportError:
        # Fallback to basic spectral features without librosa
        features['brightness'] = _estimate_brightness_simple(audio, sr)
        features['noisiness'] = _estimate_noisiness_simple(audio)
        features['bandwidth'] = 0.0
        features['rolloff'] = 0.0
        features['mfcc'] = [0.0] * 13
        features['onset_strength'] = 0.0

    return features


def _estimate_brightness_simple(audio: np.ndarray, sr: int) -> float:
    """
    Simple brightness estimation using FFT

    Higher frequencies weighted more heavily.
    """
    # Compute FFT
    fft = np.fft.rfft(audio)
    magnitude = np.abs(fft)
    freqs = np.fft.rfftfreq(len(audio), 1/sr)

    # Compute weighted average frequency
    if np.sum(magnitude) > 0:
        centroid = np.sum(freqs * magnitude) / np.sum(magnitude)
        return float(centroid)

    return 0.0


def _estimate_noisiness_simple(audio: np.ndarray) -> float:
    """
    Simple noisiness estimation

    Based on distribution of FFT magnitudes.
    More uniform = more noise-like = higher value.
    """
    # Compute FFT
    fft = np.fft.rfft(audio)
    magnitude = np.abs(fft)

    if len(magnitude) == 0:
        return 0.0

    # Spectral flatness = geometric mean / arithmetic mean
    # More uniform spectrum (noise) = closer to 1
    geometric_mean = np.exp(np.mean(np.log(magnitude + 1e-10)))
    arithmetic_mean = np.mean(magnitude)

    if arithmetic_mean > 0:
        flatness = geometric_mean / arithmetic_mean
        return float(flatness)

    return 0.0


def normalize_features(features_list: list) -> list:
    """
    Normalize a list of feature dicts to 0-1 range

    Args:
        features_list: List of feature dicts from extract_features

    Returns:
        List of normalized feature dicts
    """
    if not features_list:
        return []

    # Find min/max for each feature
    feature_keys = features_list[0].keys()
    ranges = {}

    for key in feature_keys:
        values = []
        for features in features_list:
            val = features.get(key, 0)
            if isinstance(val, list):
                values.extend(val)
            else:
                values.append(val)

        ranges[key] = {
            'min': min(values),
            'max': max(values)
        }

    # Normalize
    normalized = []
    for features in features_list:
        norm_features = {}

        for key, val in features.items():
            min_val = ranges[key]['min']
            max_val = ranges[key]['max']
            range_val = max_val - min_val

            if range_val > 0:
                if isinstance(val, list):
                    norm_features[key] = [
                        (v - min_val) / range_val for v in val
                    ]
                else:
                    norm_features[key] = (val - min_val) / range_val
            else:
                norm_features[key] = val

        normalized.append(norm_features)

    return normalized


def compare_features(features1: Dict, features2: Dict,
                    weights: Dict[str, float] = None) -> float:
    """
    Compute similarity between two feature dicts

    Args:
        features1: First feature dict
        features2: Second feature dict
        weights: Optional weights for different features

    Returns:
        Similarity score (0 = identical, higher = more different)
    """
    weights = weights or {}
    distance = 0.0
    num_features = 0

    # Compare common features
    common_keys = set(features1.keys()) & set(features2.keys())

    for key in common_keys:
        val1 = features1[key]
        val2 = features2[key]

        weight = weights.get(key, 1.0)

        # Handle both scalar and list features
        if isinstance(val1, list) and isinstance(val2, list):
            # Euclidean distance for vectors
            diff = np.array(val1) - np.array(val2)
            distance += weight * np.linalg.norm(diff)
        else:
            # Absolute difference for scalars
            distance += weight * abs(val1 - val2)

        num_features += 1

    # Average distance
    if num_features > 0:
        return distance / num_features

    return 0.0


if __name__ == "__main__":
    # Example usage
    print("Feature extraction utilities")
    print("\nGenerating test signal...")

    # Generate a test signal
    sr = 44100
    duration = 1.0
    freq = 440.0  # A4

    t = np.linspace(0, duration, int(sr * duration))
    audio = np.sin(2 * np.pi * freq * t)

    # Extract features
    print("\nExtracting features...")
    features = extract_features(audio, sr)

    print("\nExtracted features:")
    for key, val in features.items():
        if isinstance(val, list):
            print(f"  {key}: {val[:3]}... ({len(val)} values)")
        else:
            print(f"  {key}: {val:.4f}")

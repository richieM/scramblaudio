"""
Sample Bank module - Load and organize audio samples with MIR features
"""

import os
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import pickle


class Sample:
    """Represents a single audio sample with metadata and features"""

    def __init__(self, path: str, audio: np.ndarray, sr: int, features: Dict = None):
        self.path = path
        self.audio = audio
        self.sr = sr
        self.features = features or {}
        self.name = Path(path).stem

    def __repr__(self):
        return f"Sample('{self.name}', {len(self.audio)} samples, {self.sr}Hz)"


class SampleBank:
    """
    Manages a collection of audio samples with MIR features

    Features are computed on load and cached for performance.
    Samples can be queried by category, feature similarity, etc.
    """

    def __init__(self, cache_path: Optional[str] = None):
        self.samples: Dict[str, List[Sample]] = {}
        self.cache_path = cache_path

    def load_directory(self, directory: str, category: str = "default",
                      extract_features: bool = True):
        """
        Load all .wav files from a directory

        Args:
            directory: Path to directory containing .wav files
            category: Category label for these samples (e.g., 'kick', 'snare')
            extract_features: Whether to compute MIR features
        """
        directory_path = Path(directory)

        if not directory_path.exists():
            print(f"Warning: Directory {directory} does not exist")
            return

        if category not in self.samples:
            self.samples[category] = []

        wav_files = list(directory_path.glob("*.wav"))

        for wav_path in wav_files:
            try:
                # Import here to make librosa optional for now
                try:
                    import librosa
                    audio, sr = librosa.load(str(wav_path), sr=None, mono=True)
                except ImportError:
                    print("Warning: librosa not installed. Loading with scipy instead.")
                    from scipy.io import wavfile
                    sr, audio = wavfile.read(str(wav_path))
                    # Convert to float and normalize
                    audio = audio.astype(np.float32)
                    if audio.max() > 1.0:
                        audio = audio / np.iinfo(np.int16).max

                features = {}
                if extract_features:
                    try:
                        from ..utils.features import extract_features as extract_fn
                        features = extract_fn(audio, sr)
                    except ImportError as e:
                        print(f"Warning: Could not import feature extraction: {e}")
                    except Exception as e:
                        print(f"Warning: Feature extraction failed: {e}")

                sample = Sample(str(wav_path), audio, sr, features)
                self.samples[category].append(sample)

            except Exception as e:
                print(f"Error loading {wav_path}: {e}")

        print(f"Loaded {len(wav_files)} samples into category '{category}'")

    def load_directories(self, dir_map: Dict[str, str], extract_features: bool = True):
        """
        Load multiple directories with category mapping

        Args:
            dir_map: Dict mapping category names to directory paths
                     e.g., {'kick': './samples/kicks/', 'snare': './samples/snares/'}
        """
        for category, directory in dir_map.items():
            self.load_directory(directory, category, extract_features)

    def get_samples(self, category: str) -> List[Sample]:
        """Get all samples in a category"""
        return self.samples.get(category, [])

    def get_random_sample(self, category: str) -> Optional[Sample]:
        """Get a random sample from a category"""
        samples = self.get_samples(category)
        if not samples:
            return None
        return np.random.choice(samples)

    def get_all_categories(self) -> List[str]:
        """Get list of all categories"""
        return list(self.samples.keys())

    def save_cache(self, path: Optional[str] = None):
        """Save sample bank to cache file"""
        cache_path = path or self.cache_path
        if cache_path:
            with open(cache_path, 'wb') as f:
                pickle.dump(self.samples, f)
            print(f"Saved sample bank cache to {cache_path}")

    @classmethod
    def load_cache(cls, path: str) -> 'SampleBank':
        """Load sample bank from cache file"""
        bank = cls(cache_path=path)
        with open(path, 'rb') as f:
            bank.samples = pickle.load(f)
        print(f"Loaded sample bank from cache: {path}")
        return bank

    def __repr__(self):
        total_samples = sum(len(samples) for samples in self.samples.values())
        categories = ', '.join(self.samples.keys())
        return f"SampleBank({total_samples} samples, categories: {categories})"

"""
Renderer module - Assemble and output audio

Takes rhythm patterns, samples, and arrangement info and renders
final audio output (stems or mixed down).
"""

import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from .sample_bank import Sample
from .arrangement import Arrangement
from .semantic_space import SemanticSpace

try:
    from .effects import EffectsChain
    EFFECTS_AVAILABLE = True
except ImportError:
    EFFECTS_AVAILABLE = False


class Renderer:
    """
    Renders audio from rhythm patterns and samples

    Handles timing, sample placement, mixing, and file output.
    """

    def __init__(self, sample_rate: int = 44100):
        """
        Initialize renderer

        Args:
            sample_rate: Output sample rate in Hz
        """
        self.sample_rate = sample_rate
        self._resample_cache = {}  # Cache resampled audio

    def render_pattern(self, pattern: List[int], samples: List[Sample],
                      onset_times: List[float],
                      duration: float,
                      semantic_path: Optional['SemanticPath'] = None,
                      time_offset: float = 0.0) -> np.ndarray:
        """
        Render a single pattern with given samples

        Args:
            pattern: Rhythm pattern (list of 0s and 1s)
            samples: Pool of samples to choose from
            onset_times: Time in seconds for each step
            duration: Total duration in seconds
            semantic_path: Optional SemanticPath for automated sample selection
            time_offset: Offset for semantic path timing

        Returns:
            Audio buffer as numpy array
        """
        # Create output buffer
        num_samples = int(duration * self.sample_rate)
        output = np.zeros(num_samples, dtype=np.float32)

        if not samples:
            return output

        # Place samples at onset times
        for i, (hit, onset_time) in enumerate(zip(pattern, onset_times)):
            if hit == 1:
                # Choose a sample
                if semantic_path is not None:
                    # Use semantic path for sample selection
                    sample = semantic_path.get_sample_at_time(time_offset + onset_time)
                    if sample is None:
                        sample = np.random.choice(samples)
                else:
                    # Random selection (original behavior)
                    sample = np.random.choice(samples)

                # Resample if needed
                audio = self._resample_if_needed(sample)

                # Calculate placement
                start_idx = int(onset_time * self.sample_rate)
                end_idx = min(start_idx + len(audio), num_samples)
                audio_len = end_idx - start_idx

                if audio_len > 0:
                    # Mix sample into output
                    output[start_idx:end_idx] += audio[:audio_len]

        return output

    def render_track(self, patterns: Dict[int, List[int]],
                    samples_by_section: Dict[int, List[Sample]],
                    onset_times_by_section: Dict[int, List[float]],
                    section_durations: List[float],
                    semantic_paths: Optional[Dict[int, 'SemanticPath']] = None) -> np.ndarray:
        """
        Render a complete track across multiple sections

        Args:
            patterns: Dict mapping section index to rhythm pattern
            samples_by_section: Dict mapping section index to sample pool
            onset_times_by_section: Dict mapping section index to onset times
            section_durations: Duration of each section in seconds
            semantic_paths: Optional dict mapping section index to SemanticPath

        Returns:
            Complete audio track
        """
        # Calculate total duration
        total_duration = sum(section_durations)
        num_samples = int(total_duration * self.sample_rate)
        output = np.zeros(num_samples, dtype=np.float32)

        # Render each section and place in timeline
        current_time = 0.0

        for section_idx, duration in enumerate(section_durations):
            if section_idx not in patterns:
                current_time += duration
                continue

            # Get semantic path for this section
            semantic_path = semantic_paths.get(section_idx) if semantic_paths else None

            # Render this section
            section_audio = self.render_pattern(
                patterns[section_idx],
                samples_by_section.get(section_idx, []),
                onset_times_by_section.get(section_idx, []),
                duration,
                semantic_path=semantic_path,
                time_offset=0.0  # Reset time for each section
            )

            # Place in output buffer
            start_idx = int(current_time * self.sample_rate)
            end_idx = start_idx + len(section_audio)

            if end_idx <= num_samples:
                output[start_idx:end_idx] += section_audio
            else:
                # Truncate if needed
                available = num_samples - start_idx
                output[start_idx:] += section_audio[:available]

            current_time += duration

        return output

    def render_arrangement(self, arrangement: Arrangement,
                          track_data: Dict[str, Dict]) -> Dict[str, np.ndarray]:
        """
        Render complete arrangement with multiple tracks

        Args:
            arrangement: Arrangement object defining song structure
            track_data: Dict mapping track names to rendering data
                       Each track should have patterns, samples, onset_times
                       per section

        Returns:
            Dict mapping track names to rendered audio arrays
        """
        timeline = arrangement.get_timeline()
        section_durations = [entry['duration'] for entry in timeline]

        rendered_tracks = {}

        for track_name, data in track_data.items():
            patterns = data.get('patterns', {})
            samples = data.get('samples', {})
            onset_times = data.get('onset_times', {})

            track_audio = self.render_track(
                patterns,
                samples,
                onset_times,
                section_durations
            )

            rendered_tracks[track_name] = track_audio

        return rendered_tracks

    def mix_tracks(self, tracks: Dict[str, np.ndarray],
                  levels: Optional[Dict[str, float]] = None,
                  normalize: bool = True) -> np.ndarray:
        """
        Mix multiple tracks together

        Args:
            tracks: Dict mapping track names to audio arrays
            levels: Optional dict of level multipliers per track
            normalize: Whether to normalize output to prevent clipping

        Returns:
            Mixed audio
        """
        if not tracks:
            return np.array([])

        levels = levels or {}

        # Find max length
        max_len = max(len(audio) for audio in tracks.values())

        # Mix tracks
        mixed = np.zeros(max_len, dtype=np.float32)

        for track_name, audio in tracks.items():
            level = levels.get(track_name, 1.0)
            mixed[:len(audio)] += audio * level

        # Normalize if requested
        if normalize and np.max(np.abs(mixed)) > 0:
            mixed = mixed / np.max(np.abs(mixed)) * 0.95

        return mixed

    def apply_effects(self, audio: np.ndarray,
                     effects_chain: Union['EffectsChain', None]) -> np.ndarray:
        """
        Apply effects chain to audio

        Args:
            audio: Input audio array
            effects_chain: EffectsChain object or None

        Returns:
            Processed audio
        """
        if effects_chain is None or not EFFECTS_AVAILABLE:
            return audio

        return effects_chain.process(audio)

    def apply_track_effects(self, tracks: Dict[str, np.ndarray],
                           effects_chains: Dict[str, 'EffectsChain']) -> Dict[str, np.ndarray]:
        """
        Apply effects to multiple tracks

        Args:
            tracks: Dict mapping track names to audio arrays
            effects_chains: Dict mapping track names to EffectsChain objects

        Returns:
            Dict of processed tracks
        """
        if not EFFECTS_AVAILABLE:
            print("Warning: Effects not available, returning unprocessed tracks")
            return tracks

        processed_tracks = {}

        for track_name, audio in tracks.items():
            if track_name in effects_chains:
                processed_tracks[track_name] = self.apply_effects(
                    audio,
                    effects_chains[track_name]
                )
            else:
                processed_tracks[track_name] = audio

        return processed_tracks

    def write_wav(self, audio: np.ndarray, filepath: str):
        """
        Write audio to WAV file

        Args:
            audio: Audio array
            filepath: Output file path
        """
        try:
            import scipy.io.wavfile as wavfile
        except ImportError:
            raise ImportError("scipy required for WAV output. Install with: pip install scipy")

        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        # Convert to int16
        audio_int16 = (audio * 32767).astype(np.int16)

        wavfile.write(filepath, self.sample_rate, audio_int16)
        print(f"Wrote audio to {filepath}")

    def write_stems(self, tracks: Dict[str, np.ndarray],
                   output_dir: str, prefix: str = "stem"):
        """
        Write individual track stems to separate files

        Args:
            tracks: Dict mapping track names to audio arrays
            output_dir: Output directory path
            prefix: Filename prefix for stems
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for track_name, audio in tracks.items():
            filename = f"{prefix}_{track_name}.wav"
            filepath = output_path / filename
            self.write_wav(audio, str(filepath))

        print(f"Wrote {len(tracks)} stems to {output_dir}")

    def _resample_if_needed(self, sample: Sample) -> np.ndarray:
        """
        Resample audio if sample rate doesn't match renderer's
        Uses caching to avoid resampling the same sample multiple times.

        Args:
            sample: Sample object

        Returns:
            Resampled audio array
        """
        if sample.sr == self.sample_rate:
            return sample.audio

        # Check cache first
        cache_key = (sample.path, self.sample_rate)
        if cache_key in self._resample_cache:
            return self._resample_cache[cache_key]

        # Need to resample
        ratio = self.sample_rate / sample.sr
        new_length = int(len(sample.audio) * ratio)

        # Use librosa for fast resampling if available
        try:
            import librosa
            resampled = librosa.resample(sample.audio, orig_sr=sample.sr, target_sr=self.sample_rate)
        except ImportError:
            # Fallback: simple linear interpolation (fast but lower quality)
            old_indices = np.linspace(0, len(sample.audio) - 1, len(sample.audio))
            new_indices = np.linspace(0, len(sample.audio) - 1, new_length)
            resampled = np.interp(new_indices, old_indices, sample.audio)

        # Cache it
        self._resample_cache[cache_key] = resampled
        return resampled

    def apply_envelope(self, audio: np.ndarray, attack: float = 0.01,
                      release: float = 0.05) -> np.ndarray:
        """
        Apply simple attack/release envelope to audio

        Args:
            audio: Input audio
            attack: Attack time in seconds
            release: Release time in seconds

        Returns:
            Audio with envelope applied
        """
        envelope = np.ones_like(audio)

        attack_samples = int(attack * self.sample_rate)
        release_samples = int(release * self.sample_rate)

        # Attack
        if attack_samples > 0 and attack_samples < len(audio):
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

        # Release
        if release_samples > 0 and release_samples < len(audio):
            envelope[-release_samples:] = np.linspace(1, 0, release_samples)

        return audio * envelope


if __name__ == "__main__":
    # Example usage (requires actual samples)
    print("Renderer module - use in combination with other modules")
    print("See example.py for complete usage")

"""
Audio Effects module - Wrapper for Pedalboard effects

Provides easy-to-use audio effects for the scramblaudio v2 engine.
Built on Spotify's Pedalboard library for high-quality DSP.
"""

import numpy as np
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

try:
    from pedalboard import (
        Pedalboard,
        Reverb,
        Delay,
        Distortion,
        Chorus,
        Phaser,
        Compressor,
        Gain,
        HighpassFilter,
        LowpassFilter,
        Limiter,
        NoiseGate,
    )
    PEDALBOARD_AVAILABLE = True
except ImportError:
    PEDALBOARD_AVAILABLE = False
    print("Warning: Pedalboard not installed. Effects will not be available.")


@dataclass
class EffectConfig:
    """Configuration for an audio effect"""
    name: str
    params: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    wet_dry_mix: float = 1.0  # 0.0 = fully dry, 1.0 = fully wet

    def __repr__(self):
        status = "ON" if self.enabled else "OFF"
        return f"{self.name} ({status}, mix={self.wet_dry_mix:.2f})"


class EffectsChain:
    """
    A chain of audio effects that can be applied to audio

    Effects are applied in order. Supports wet/dry mixing and
    enable/disable per effect.
    """

    def __init__(self, sample_rate: int = 44100):
        """
        Initialize effects chain

        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.effects: List[EffectConfig] = []

    def add_reverb(self, room_size: float = 0.5, damping: float = 0.5,
                  wet_level: float = 0.33, dry_level: float = 0.4,
                  width: float = 1.0, freeze_mode: float = 0.0,
                  wet_dry_mix: float = 1.0) -> 'EffectsChain':
        """
        Add reverb effect

        Args:
            room_size: Room size (0.0-1.0)
            damping: Damping of high frequencies (0.0-1.0)
            wet_level: Wet signal level (0.0-1.0)
            dry_level: Dry signal level (0.0-1.0)
            width: Stereo width (0.0-1.0)
            freeze_mode: Freeze mode (0.0 or 1.0)
            wet_dry_mix: Overall wet/dry mix (0.0-1.0)

        Returns:
            Self for chaining
        """
        self.effects.append(EffectConfig(
            name='reverb',
            params={
                'room_size': room_size,
                'damping': damping,
                'wet_level': wet_level,
                'dry_level': dry_level,
                'width': width,
                'freeze_mode': freeze_mode
            },
            wet_dry_mix=wet_dry_mix
        ))
        return self

    def add_delay(self, delay_seconds: float = 0.5, feedback: float = 0.0,
                 mix: float = 0.5, wet_dry_mix: float = 1.0) -> 'EffectsChain':
        """
        Add delay effect

        Args:
            delay_seconds: Delay time in seconds
            feedback: Feedback amount (0.0-1.0)
            mix: Wet/dry mix (0.0-1.0)
            wet_dry_mix: Overall wet/dry mix

        Returns:
            Self for chaining
        """
        self.effects.append(EffectConfig(
            name='delay',
            params={
                'delay_seconds': delay_seconds,
                'feedback': feedback,
                'mix': mix
            },
            wet_dry_mix=wet_dry_mix
        ))
        return self

    def add_distortion(self, drive_db: float = 25.0,
                      wet_dry_mix: float = 1.0) -> 'EffectsChain':
        """
        Add distortion effect

        Args:
            drive_db: Drive amount in dB
            wet_dry_mix: Overall wet/dry mix

        Returns:
            Self for chaining
        """
        self.effects.append(EffectConfig(
            name='distortion',
            params={'drive_db': drive_db},
            wet_dry_mix=wet_dry_mix
        ))
        return self

    def add_chorus(self, rate_hz: float = 1.0, depth: float = 0.25,
                  centre_delay_ms: float = 7.0, feedback: float = 0.0,
                  mix: float = 0.5, wet_dry_mix: float = 1.0) -> 'EffectsChain':
        """
        Add chorus effect

        Args:
            rate_hz: LFO rate in Hz
            depth: LFO depth (0.0-1.0)
            centre_delay_ms: Center delay in milliseconds
            feedback: Feedback amount (0.0-1.0)
            mix: Wet/dry mix (0.0-1.0)
            wet_dry_mix: Overall wet/dry mix

        Returns:
            Self for chaining
        """
        self.effects.append(EffectConfig(
            name='chorus',
            params={
                'rate_hz': rate_hz,
                'depth': depth,
                'centre_delay_ms': centre_delay_ms,
                'feedback': feedback,
                'mix': mix
            },
            wet_dry_mix=wet_dry_mix
        ))
        return self

    def add_phaser(self, rate_hz: float = 1.0, depth: float = 0.5,
                  centre_frequency_hz: float = 1300.0, feedback: float = 0.0,
                  mix: float = 0.5, wet_dry_mix: float = 1.0) -> 'EffectsChain':
        """
        Add phaser effect

        Args:
            rate_hz: LFO rate in Hz
            depth: LFO depth (0.0-1.0)
            centre_frequency_hz: Center frequency in Hz
            feedback: Feedback amount (0.0-1.0)
            mix: Wet/dry mix (0.0-1.0)
            wet_dry_mix: Overall wet/dry mix

        Returns:
            Self for chaining
        """
        self.effects.append(EffectConfig(
            name='phaser',
            params={
                'rate_hz': rate_hz,
                'depth': depth,
                'centre_frequency_hz': centre_frequency_hz,
                'feedback': feedback,
                'mix': mix
            },
            wet_dry_mix=wet_dry_mix
        ))
        return self

    def add_compressor(self, threshold_db: float = 0.0, ratio: float = 2.0,
                      attack_ms: float = 1.0, release_ms: float = 100.0,
                      wet_dry_mix: float = 1.0) -> 'EffectsChain':
        """
        Add compressor effect

        Args:
            threshold_db: Threshold in dB
            ratio: Compression ratio
            attack_ms: Attack time in milliseconds
            release_ms: Release time in milliseconds
            wet_dry_mix: Overall wet/dry mix

        Returns:
            Self for chaining
        """
        self.effects.append(EffectConfig(
            name='compressor',
            params={
                'threshold_db': threshold_db,
                'ratio': ratio,
                'attack_ms': attack_ms,
                'release_ms': release_ms
            },
            wet_dry_mix=wet_dry_mix
        ))
        return self

    def add_highpass_filter(self, cutoff_frequency_hz: float = 100.0,
                           wet_dry_mix: float = 1.0) -> 'EffectsChain':
        """
        Add high-pass filter

        Args:
            cutoff_frequency_hz: Cutoff frequency in Hz
            wet_dry_mix: Overall wet/dry mix

        Returns:
            Self for chaining
        """
        self.effects.append(EffectConfig(
            name='highpass',
            params={'cutoff_frequency_hz': cutoff_frequency_hz},
            wet_dry_mix=wet_dry_mix
        ))
        return self

    def add_lowpass_filter(self, cutoff_frequency_hz: float = 5000.0,
                          wet_dry_mix: float = 1.0) -> 'EffectsChain':
        """
        Add low-pass filter

        Args:
            cutoff_frequency_hz: Cutoff frequency in Hz
            wet_dry_mix: Overall wet/dry mix

        Returns:
            Self for chaining
        """
        self.effects.append(EffectConfig(
            name='lowpass',
            params={'cutoff_frequency_hz': cutoff_frequency_hz},
            wet_dry_mix=wet_dry_mix
        ))
        return self

    def add_gain(self, gain_db: float = 0.0,
                wet_dry_mix: float = 1.0) -> 'EffectsChain':
        """
        Add gain effect

        Args:
            gain_db: Gain in dB
            wet_dry_mix: Overall wet/dry mix

        Returns:
            Self for chaining
        """
        self.effects.append(EffectConfig(
            name='gain',
            params={'gain_db': gain_db},
            wet_dry_mix=wet_dry_mix
        ))
        return self

    def add_limiter(self, threshold_db: float = -10.0, release_ms: float = 100.0,
                   wet_dry_mix: float = 1.0) -> 'EffectsChain':
        """
        Add limiter effect

        Args:
            threshold_db: Threshold in dB
            release_ms: Release time in milliseconds
            wet_dry_mix: Overall wet/dry mix

        Returns:
            Self for chaining
        """
        self.effects.append(EffectConfig(
            name='limiter',
            params={
                'threshold_db': threshold_db,
                'release_ms': release_ms
            },
            wet_dry_mix=wet_dry_mix
        ))
        return self

    def add_noise_gate(self, threshold_db: float = -100.0, ratio: float = 10.0,
                      attack_ms: float = 1.0, release_ms: float = 100.0,
                      wet_dry_mix: float = 1.0) -> 'EffectsChain':
        """
        Add noise gate effect

        Args:
            threshold_db: Threshold in dB
            ratio: Gate ratio
            attack_ms: Attack time in milliseconds
            release_ms: Release time in milliseconds
            wet_dry_mix: Overall wet/dry mix

        Returns:
            Self for chaining
        """
        self.effects.append(EffectConfig(
            name='noise_gate',
            params={
                'threshold_db': threshold_db,
                'ratio': ratio,
                'attack_ms': attack_ms,
                'release_ms': release_ms
            },
            wet_dry_mix=wet_dry_mix
        ))
        return self

    def _create_effect_instance(self, effect_config: EffectConfig):
        """Create a Pedalboard effect instance from config"""
        if not PEDALBOARD_AVAILABLE:
            return None

        name = effect_config.name
        params = effect_config.params

        if name == 'reverb':
            return Reverb(**params)
        elif name == 'delay':
            return Delay(**params)
        elif name == 'distortion':
            return Distortion(**params)
        elif name == 'chorus':
            return Chorus(**params)
        elif name == 'phaser':
            return Phaser(**params)
        elif name == 'compressor':
            return Compressor(**params)
        elif name == 'highpass':
            return HighpassFilter(**params)
        elif name == 'lowpass':
            return LowpassFilter(**params)
        elif name == 'gain':
            return Gain(**params)
        elif name == 'limiter':
            return Limiter(**params)
        elif name == 'noise_gate':
            return NoiseGate(**params)
        else:
            print(f"Warning: Unknown effect type: {name}")
            return None

    def process(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply effects chain to audio

        Args:
            audio: Input audio (mono or stereo)

        Returns:
            Processed audio
        """
        if not PEDALBOARD_AVAILABLE:
            print("Warning: Pedalboard not available, returning unprocessed audio")
            return audio

        if len(self.effects) == 0:
            return audio

        # Ensure audio is float32 and 2D (channels, samples)
        if audio.ndim == 1:
            audio = audio.reshape(1, -1)

        processed = audio.copy()

        # Apply each effect
        for effect_config in self.effects:
            if not effect_config.enabled:
                continue

            effect = self._create_effect_instance(effect_config)
            if effect is None:
                continue

            # Create pedalboard with single effect
            board = Pedalboard([effect])

            # Process audio
            wet = board(processed, self.sample_rate)

            # Apply wet/dry mix
            mix = effect_config.wet_dry_mix
            processed = (1.0 - mix) * processed + mix * wet

        return processed.squeeze()  # Remove channel dimension if mono

    def clear(self):
        """Remove all effects from the chain"""
        self.effects = []

    def disable_effect(self, index: int):
        """Disable an effect by index"""
        if 0 <= index < len(self.effects):
            self.effects[index].enabled = False

    def enable_effect(self, index: int):
        """Enable an effect by index"""
        if 0 <= index < len(self.effects):
            self.effects[index].enabled = True

    def set_wet_dry_mix(self, index: int, mix: float):
        """Set wet/dry mix for an effect"""
        if 0 <= index < len(self.effects):
            self.effects[index].wet_dry_mix = np.clip(mix, 0.0, 1.0)

    def __repr__(self):
        if not self.effects:
            return "EffectsChain(empty)"
        return f"EffectsChain({len(self.effects)} effects: {', '.join(e.name for e in self.effects)})"

    def __len__(self):
        return len(self.effects)


# Preset effect chains
def create_ambient_chain(sample_rate: int = 44100) -> EffectsChain:
    """Create an ambient/atmospheric effects chain"""
    chain = EffectsChain(sample_rate)
    chain.add_reverb(room_size=0.9, damping=0.5, wet_level=0.5, wet_dry_mix=0.7)
    chain.add_delay(delay_seconds=0.375, feedback=0.4, mix=0.3, wet_dry_mix=0.5)
    chain.add_chorus(rate_hz=0.5, depth=0.3, mix=0.2, wet_dry_mix=0.3)
    return chain


def create_distorted_chain(sample_rate: int = 44100) -> EffectsChain:
    """Create a distorted/aggressive effects chain"""
    chain = EffectsChain(sample_rate)
    chain.add_distortion(drive_db=30.0, wet_dry_mix=0.8)
    chain.add_compressor(threshold_db=-20.0, ratio=4.0, attack_ms=1.0, release_ms=50.0)
    chain.add_lowpass_filter(cutoff_frequency_hz=3000.0, wet_dry_mix=0.5)
    return chain


def create_lo_fi_chain(sample_rate: int = 44100) -> EffectsChain:
    """Create a lo-fi/vintage effects chain"""
    chain = EffectsChain(sample_rate)
    chain.add_lowpass_filter(cutoff_frequency_hz=4000.0)
    chain.add_distortion(drive_db=15.0, wet_dry_mix=0.3)
    chain.add_chorus(rate_hz=0.3, depth=0.4, mix=0.2, wet_dry_mix=0.4)
    chain.add_reverb(room_size=0.3, damping=0.7, wet_level=0.2, wet_dry_mix=0.3)
    return chain


def create_clean_chain(sample_rate: int = 44100) -> EffectsChain:
    """Create a clean/polished effects chain"""
    chain = EffectsChain(sample_rate)
    chain.add_compressor(threshold_db=-15.0, ratio=3.0, attack_ms=5.0, release_ms=100.0)
    chain.add_reverb(room_size=0.2, damping=0.5, wet_level=0.15, wet_dry_mix=0.4)
    chain.add_limiter(threshold_db=-1.0, release_ms=100.0)
    return chain


if __name__ == "__main__":
    # Example usage
    print("Effects module loaded")
    print(f"Pedalboard available: {PEDALBOARD_AVAILABLE}\n")

    if PEDALBOARD_AVAILABLE:
        # Create a chain
        chain = EffectsChain()
        chain.add_reverb(room_size=0.8)
        chain.add_delay(delay_seconds=0.5, feedback=0.3)
        chain.add_distortion(drive_db=20.0)

        print(f"Created chain: {chain}\n")

        # List effects
        print("Effects in chain:")
        for i, effect in enumerate(chain.effects):
            print(f"  {i}. {effect}")

        # Test presets
        print("\nPreset chains:")
        print(f"Ambient: {create_ambient_chain()}")
        print(f"Distorted: {create_distorted_chain()}")
        print(f"Lo-fi: {create_lo_fi_chain()}")
        print(f"Clean: {create_clean_chain()}")

"""
Semantic Automation module - Automate sample selection through semantic space over time

Provides classes for defining paths through semantic space and automating
sample selection during rendering.
"""

import numpy as np
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from .sample_bank import Sample
from .semantic_space import SemanticSpace


@dataclass
class SemanticPathPoint:
    """A point in a semantic path"""
    time: float  # Time in seconds or beats
    sample: Optional[Sample] = None
    feature_target: Optional[Dict[str, float]] = None


class SemanticPath:
    """
    Defines a path through semantic space over time

    Can be used to automate sample selection during rendering,
    creating evolving timbral characteristics.
    """

    def __init__(self, space: SemanticSpace, duration: float = 0.0):
        """
        Initialize a semantic path

        Args:
            space: SemanticSpace to navigate
            duration: Total duration of the path
        """
        self.space = space
        self.duration = duration
        self.points: List[SemanticPathPoint] = []

    def add_point(self, time: float, sample: Optional[Sample] = None,
                 feature_target: Optional[Dict[str, float]] = None):
        """
        Add a control point to the path

        Args:
            time: Time position
            sample: Specific sample at this point (or None)
            feature_target: Target feature values at this point
        """
        point = SemanticPathPoint(time, sample, feature_target)
        self.points.append(point)
        # Keep sorted by time
        self.points.sort(key=lambda p: p.time)

    def get_sample_at_time(self, time: float) -> Optional[Sample]:
        """
        Get the appropriate sample at a given time

        Interpolates between path points.

        Args:
            time: Time position to query

        Returns:
            Sample at that time
        """
        if not self.points:
            return None

        # Find surrounding points
        before = None
        after = None

        for point in self.points:
            if point.time <= time:
                before = point
            if point.time >= time and after is None:
                after = point

        # If we're exactly on a point with a sample, return it
        if before and before.time == time and before.sample:
            return before.sample

        # Interpolate between points
        if before and after and before != after:
            # Calculate interpolation factor
            alpha = (time - before.time) / (after.time - before.time)

            # If both have samples, interpolate path
            if before.sample and after.sample:
                path = self.space.interpolate_path(before.sample, after.sample, steps=10)
                idx = int(alpha * (len(path) - 1))
                return path[idx]

            # If one has a sample, use it
            if before.sample:
                return before.sample
            if after.sample:
                return after.sample

        # Fallback: use nearest point
        if before:
            return before.sample
        if after:
            return after.sample

        return None

    @staticmethod
    def linear_sweep(space: SemanticSpace, start_sample: Sample,
                    end_sample: Sample, duration: float,
                    num_steps: int = 10) -> 'SemanticPath':
        """
        Create a linear sweep between two samples

        Args:
            space: SemanticSpace to use
            start_sample: Starting sample
            end_sample: Ending sample
            duration: Duration of sweep
            num_steps: Number of intermediate steps

        Returns:
            SemanticPath from start to end
        """
        path = SemanticPath(space, duration)

        # Get interpolated samples
        samples = space.interpolate_path(start_sample, end_sample, num_steps)

        # Add points at regular intervals
        for i, sample in enumerate(samples):
            time = (i / (len(samples) - 1)) * duration
            path.add_point(time, sample=sample)

        return path

    @staticmethod
    def gradient_sweep(space: SemanticSpace, start_sample: Sample,
                      feature_name: str, amount: float,
                      duration: float, num_steps: int = 10) -> 'SemanticPath':
        """
        Create a sweep along a specific feature dimension

        Args:
            space: SemanticSpace to use
            start_sample: Starting sample
            feature_name: Feature to sweep ('brightness', 'energy', etc.)
            amount: How much to change the feature
            duration: Duration of sweep
            num_steps: Number of steps

        Returns:
            SemanticPath along the feature gradient
        """
        path = SemanticPath(space, duration)

        current_sample = start_sample
        step_amount = amount / num_steps

        for i in range(num_steps):
            time = (i / (num_steps - 1)) * duration if num_steps > 1 else 0
            path.add_point(time, sample=current_sample)

            # Move to next sample
            next_sample = space.navigate_gradient(current_sample, feature_name, step_amount)
            if next_sample:
                current_sample = next_sample

        return path

    @staticmethod
    def orbit_path(space: SemanticSpace, center_sample: Sample,
                  radius: float, duration: float,
                  revolutions: float = 1.0) -> 'SemanticPath':
        """
        Create an orbital path around a sample

        Args:
            space: SemanticSpace to use
            center_sample: Center of orbit
            radius: Orbit radius
            duration: Duration of path
            revolutions: Number of times to orbit

        Returns:
            SemanticPath orbiting the center
        """
        path = SemanticPath(space, duration)

        # Calculate number of steps (more steps for more revolutions)
        num_steps = max(8, int(revolutions * 16))
        orbit_samples = space.orbit_sample(center_sample, radius, num_steps)

        # Extend samples to cover multiple revolutions
        if revolutions > 1.0:
            full_samples = orbit_samples * int(np.ceil(revolutions))
        else:
            full_samples = orbit_samples

        # Add points
        for i, sample in enumerate(full_samples[:int(revolutions * len(orbit_samples))]):
            time = (i / len(full_samples)) * duration
            path.add_point(time, sample=sample)

        return path

    @staticmethod
    def random_walk_path(space: SemanticSpace, start_sample: Sample,
                        duration: float, step_size: float = 0.5,
                        num_steps: int = 20) -> 'SemanticPath':
        """
        Create a random walk path

        Args:
            space: SemanticSpace to use
            start_sample: Starting sample
            duration: Duration of path
            step_size: Size of random steps
            num_steps: Number of steps

        Returns:
            SemanticPath with random walk
        """
        path = SemanticPath(space, duration)

        # Generate random walk
        walk_samples = space.random_walk(start_sample, num_steps, step_size)

        # Add points
        for i, sample in enumerate(walk_samples):
            time = (i / (len(walk_samples) - 1)) * duration if len(walk_samples) > 1 else 0
            path.add_point(time, sample=sample)

        return path


class SemanticAutomation:
    """
    Manages automated sample selection using semantic paths

    Can be integrated with arrangement sections to define
    evolving timbral characteristics.
    """

    def __init__(self):
        """Initialize automation manager"""
        self.paths: Dict[str, SemanticPath] = {}
        self.active = True

    def add_path(self, name: str, path: SemanticPath):
        """
        Add a named semantic path

        Args:
            name: Identifier for the path (e.g., 'kick_evolution')
            path: SemanticPath object
        """
        self.paths[name] = path

    def get_sample(self, path_name: str, time: float) -> Optional[Sample]:
        """
        Get sample from a path at a specific time

        Args:
            path_name: Name of the path
            time: Time to query

        Returns:
            Sample at that time, or None
        """
        if not self.active or path_name not in self.paths:
            return None

        return self.paths[path_name].get_sample_at_time(time)

    def get_samples_for_pattern(self, path_name: str,
                               onset_times: List[float]) -> List[Sample]:
        """
        Get samples for each onset in a rhythm pattern

        Args:
            path_name: Name of the path
            onset_times: List of onset times

        Returns:
            List of samples, one for each onset
        """
        samples = []
        for time in onset_times:
            sample = self.get_sample(path_name, time)
            if sample:
                samples.append(sample)

        return samples


# LFO and modulation sources for dynamic automation
class LFO:
    """Low Frequency Oscillator for modulating parameters"""

    def __init__(self, rate_hz: float = 1.0, shape: str = 'sine',
                 depth: float = 1.0, phase: float = 0.0):
        """
        Initialize LFO

        Args:
            rate_hz: Frequency in Hz
            shape: Waveform shape ('sine', 'triangle', 'square', 'saw')
            depth: Modulation depth (0-1)
            phase: Initial phase (0-1)
        """
        self.rate_hz = rate_hz
        self.shape = shape
        self.depth = depth
        self.phase = phase

    def value_at_time(self, time: float) -> float:
        """
        Get LFO value at a specific time

        Args:
            time: Time in seconds

        Returns:
            LFO value in range [-depth, +depth]
        """
        # Calculate phase at this time
        phase = (time * self.rate_hz + self.phase) % 1.0

        # Generate waveform
        if self.shape == 'sine':
            value = np.sin(2 * np.pi * phase)
        elif self.shape == 'triangle':
            value = 2 * abs(2 * (phase - 0.5)) - 1
        elif self.shape == 'square':
            value = 1.0 if phase < 0.5 else -1.0
        elif self.shape == 'saw':
            value = 2 * phase - 1
        else:
            value = 0.0

        return value * self.depth

    def modulate_feature(self, base_value: float, time: float,
                        scale: float = 1.0) -> float:
        """
        Modulate a feature value with the LFO

        Args:
            base_value: Base feature value
            time: Current time
            scale: Scaling factor for modulation

        Returns:
            Modulated value
        """
        mod = self.value_at_time(time)
        return base_value + mod * scale


class PerlinNoiseModulator:
    """Perlin noise for smooth, organic modulation"""

    def __init__(self, scale: float = 1.0, octaves: int = 1):
        """
        Initialize Perlin noise modulator

        Args:
            scale: Noise scale (affects frequency)
            octaves: Number of noise octaves (more = more detail)
        """
        self.scale = scale
        self.octaves = octaves
        self._permutation = np.random.permutation(256)

    def value_at_time(self, time: float) -> float:
        """
        Get noise value at time

        Args:
            time: Time in seconds

        Returns:
            Noise value in range [-1, 1]
        """
        # Simple 1D Perlin noise approximation
        x = time * self.scale

        # Multiple octaves
        value = 0.0
        amplitude = 1.0
        frequency = 1.0

        for _ in range(self.octaves):
            # Get integer and fractional parts
            xi = int(x * frequency) % 256
            xf = (x * frequency) % 1.0

            # Smoothstep interpolation
            u = xf * xf * (3.0 - 2.0 * xf)

            # Get noise values
            a = self._permutation[xi]
            b = self._permutation[(xi + 1) % 256]

            # Interpolate
            value += (a * (1 - u) + b * u) * amplitude / 128.0 - amplitude

            amplitude *= 0.5
            frequency *= 2.0

        return np.clip(value, -1.0, 1.0)

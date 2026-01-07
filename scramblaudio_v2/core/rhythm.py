"""
Rhythm generation module - Euclidean and polymeter patterns

Based on Bjorklund's algorithm for generating rhythms that distribute
hits as evenly as possible across a given number of steps.
"""

import numpy as np
from typing import List, Tuple


def euclidean_rhythm(hits: int, steps: int, rotation: int = 0) -> List[int]:
    """
    Generate a Euclidean rhythm pattern using Bjorklund's algorithm

    Distributes 'hits' as evenly as possible across 'steps'.
    Examples:
        euclidean_rhythm(3, 8) = [1,0,0,1,0,0,1,0]  # Standard rock beat
        euclidean_rhythm(5, 8) = [1,0,1,1,0,1,1,0]  # Cuban tresillo
        euclidean_rhythm(5, 13) = [1,0,0,1,0,1,0,1,0,1,0,0,0]  # Odd meter

    Args:
        hits: Number of 1s (hits) to distribute
        steps: Total length of pattern
        rotation: Rotate the pattern by this many steps

    Returns:
        List of 0s and 1s representing the rhythm pattern
    """
    if hits >= steps:
        return [1] * steps

    if hits == 0:
        return [0] * steps

    # Bjorklund's algorithm
    pattern = []
    counts = []
    remainders = []

    divisor = steps - hits
    remainders.append(hits)

    level = 0
    while True:
        counts.append(divisor // remainders[level])
        remainders.append(divisor % remainders[level])
        divisor = remainders[level]
        level += 1

        if remainders[level] <= 1:
            break

    counts.append(divisor)

    def build(level):
        if level == -1:
            pattern.append(0)
        elif level == -2:
            pattern.append(1)
        else:
            for _ in range(counts[level]):
                build(level - 1)
            if remainders[level] != 0:
                build(level - 2)

    build(level)

    # Rotate pattern
    if rotation != 0:
        rotation = rotation % len(pattern)
        pattern = pattern[rotation:] + pattern[:rotation]

    return pattern


def polymeter_rhythm(meters: List[Tuple[int, int]], bars: int = 1) -> dict:
    """
    Generate multiple rhythms with different meter patterns running simultaneously

    This creates polyrhythmic/polymetric patterns where different voices
    cycle at different rates.

    Args:
        meters: List of (hits, steps) tuples for each voice
                e.g., [(3, 8), (5, 13), (7, 16)]
        bars: Number of bars to generate

    Returns:
        Dict mapping voice index to rhythm pattern
        e.g., {0: [1,0,0,1,0,0,1,0, ...], 1: [1,0,0,1,0,1,0,1,0,1,0,0,0, ...]}
    """
    patterns = {}

    # Find LCM of all step counts to determine full cycle length
    step_counts = [steps for _, steps in meters]
    lcm = np.lcm.reduce(step_counts)
    total_steps = lcm * bars

    for i, (hits, steps) in enumerate(meters):
        base_pattern = euclidean_rhythm(hits, steps)

        # Repeat pattern to fill total_steps
        num_repeats = total_steps // len(base_pattern)
        remainder = total_steps % len(base_pattern)

        patterns[i] = base_pattern * num_repeats + base_pattern[:remainder]

    return patterns


def pattern_to_onset_times(pattern: List[int], bpm: float = 120.0,
                           subdivision: int = 16) -> List[float]:
    """
    Convert a rhythm pattern to onset times in seconds

    Args:
        pattern: List of 0s and 1s
        bpm: Beats per minute
        subdivision: What rhythmic subdivision the pattern represents
                    (e.g., 16 = sixteenth notes)

    Returns:
        List of onset times in seconds where pattern has 1s
    """
    # Time per step in seconds
    beat_duration = 60.0 / bpm
    step_duration = beat_duration * (4.0 / subdivision)

    onset_times = []
    for i, hit in enumerate(pattern):
        if hit == 1:
            onset_times.append(i * step_duration)

    return onset_times


def visualize_pattern(pattern: List[int], label: str = "") -> str:
    """
    Create a visual representation of a rhythm pattern

    Args:
        pattern: List of 0s and 1s
        label: Optional label for the pattern

    Returns:
        String representation (e.g., "x . . x . . x .")
    """
    symbols = ['.' if x == 0 else 'x' for x in pattern]
    viz = ' '.join(symbols)

    if label:
        return f"{label:12s} | {viz}"
    return viz


def visualize_polymeter(patterns: dict, labels: dict = None) -> str:
    """
    Visualize multiple rhythms aligned

    Args:
        patterns: Dict of rhythm patterns (from polymeter_rhythm)
        labels: Optional dict mapping indices to labels

    Returns:
        Multi-line string showing all patterns aligned
    """
    lines = []
    max_len = max(len(p) for p in patterns.values())

    for i, pattern in sorted(patterns.items()):
        label = labels.get(i, f"Voice {i}") if labels else f"Voice {i}"
        # Pad pattern to max length for alignment
        padded = pattern + [0] * (max_len - len(pattern))
        lines.append(visualize_pattern(padded, label))

    return '\n'.join(lines)


if __name__ == "__main__":
    # Example usage
    print("=== Euclidean Rhythm Examples ===\n")

    print("Standard 4/4 kick (3 hits in 8 steps):")
    print(visualize_pattern(euclidean_rhythm(3, 8)))
    print()

    print("Cuban tresillo (5 hits in 8 steps):")
    print(visualize_pattern(euclidean_rhythm(5, 8)))
    print()

    print("Odd meter (5 hits in 13 steps):")
    print(visualize_pattern(euclidean_rhythm(5, 13)))
    print()

    print("\n=== Polymeter Example ===\n")
    meters = [
        (3, 8),   # Kick
        (5, 13),  # Snare
        (7, 16),  # Hi-hat
    ]

    patterns = polymeter_rhythm(meters, bars=1)
    labels = {0: "Kick", 1: "Snare", 2: "Hi-hat"}
    print(visualize_polymeter(patterns, labels))

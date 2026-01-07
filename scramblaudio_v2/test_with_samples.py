#!/usr/bin/env python3
"""
Test scramblaudio v2 engine with real samples
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import scramblaudio_v2 as a package
sys.path.insert(0, str(Path(__file__).parent.parent))

from scramblaudio_v2.core.sample_bank import SampleBank
from scramblaudio_v2.core.rhythm import euclidean_rhythm, polymeter_rhythm, pattern_to_onset_times, visualize_polymeter
from scramblaudio_v2.core.semantic_space import SemanticSpace
from scramblaudio_v2.core.arrangement import Section, Arrangement, create_simple_arrangement
from scramblaudio_v2.core.renderer import Renderer

def test_sample_loading():
    """Test loading samples from the samples directory"""
    print("=" * 60)
    print("TEST 1: Loading Samples")
    print("=" * 60)

    bank = SampleBank()

    # Load samples from organized directories
    # Paths are relative to scramblaudio root (parent of scramblaudio_v2)
    sample_dirs = {
        'kick': '../samples/kicks/',
        'snare': '../samples/snares/',
        'hihat': '../samples/hihats/',
        'perc': '../samples/perc/',
        'crash': '../samples/crashes/',
    }

    bank.load_directories(sample_dirs, extract_features=True)
    print(f"\n{bank}\n")

    # Show categories
    for category in bank.get_all_categories():
        samples = bank.get_samples(category)
        print(f"{category:10s}: {len(samples):3d} samples")

    return bank


def test_semantic_space(bank):
    """Test semantic space with real samples"""
    print("\n" + "=" * 60)
    print("TEST 2: Semantic Space Navigation")
    print("=" * 60)

    # Create semantic space for kicks
    kick_samples = bank.get_samples('kick')
    if kick_samples:
        # Debug: check if samples have features
        print(f"\nDEBUG: First kick sample has {len(kick_samples[0].features)} features")
        print(f"DEBUG: Features: {list(kick_samples[0].features.keys())[:5]}")

        space = SemanticSpace(kick_samples)
        print(f"\n{space}")

        # Show feature summary
        summary = space.get_feature_summary()
        print("\nKick feature ranges:")
        for feature, stats in summary.items():
            if feature != 'mfcc':  # Skip MFCC for brevity
                print(f"  {feature:20s}: {stats['min']:7.2f} - {stats['max']:7.2f} (mean: {stats['mean']:7.2f})")

        # Find similar samples
        print(f"\nSamples similar to {kick_samples[0].name}:")
        similar = space.find_similar(kick_samples[0], n=3)
        for sample in similar:
            print(f"  - {sample.name}")
    else:
        print("No kick samples loaded")


def test_rhythm_generation():
    """Test rhythm generation"""
    print("\n" + "=" * 60)
    print("TEST 3: Rhythm Generation")
    print("=" * 60)

    # Create polymeter
    meters = [
        (3, 8),   # Kick
        (5, 13),  # Snare
        (7, 16),  # Hi-hat
    ]

    patterns = polymeter_rhythm(meters, bars=1)
    labels = {0: "Kick", 1: "Snare", 2: "Hi-hat"}

    print("\nPolymetric rhythm pattern:")
    print(visualize_polymeter(patterns, labels))


def test_simple_beat_generation(bank):
    """Generate a simple beat and render to audio"""
    print("\n" + "=" * 60)
    print("TEST 4: Generate and Render Beat")
    print("=" * 60)

    # Create simple arrangement
    arr = create_simple_arrangement([
        ('intro', 2, ['kick']),
        ('main', 4, ['kick', 'snare', 'hihat']),
    ], bpm=120)

    print(arr.visualize())

    # Generate rhythms
    kick_pattern = euclidean_rhythm(3, 8)
    snare_pattern = euclidean_rhythm(5, 13)
    hihat_pattern = euclidean_rhythm(7, 16)

    print("\nRhythm patterns:")
    from core.rhythm import visualize_pattern
    print(visualize_pattern(kick_pattern, "Kick"))
    print(visualize_pattern(snare_pattern, "Snare"))
    print(visualize_pattern(hihat_pattern, "Hi-hat"))

    # Create renderer
    renderer = Renderer(sample_rate=44100)

    # Build track data for rendering
    timeline = arr.get_timeline()

    # For simplicity, render just the kick drum for now
    kick_samples = bank.get_samples('kick')

    if kick_samples:
        print("\nRendering kick track...")

        # Convert pattern to onset times
        bpm = 120
        onset_times = pattern_to_onset_times(kick_pattern, bpm=bpm)

        # Render intro section (2 bars = 4 seconds at 120 BPM)
        intro_duration = timeline[0]['duration']
        intro_audio = renderer.render_pattern(
            pattern=kick_pattern * 2,  # Repeat pattern for 2 bars
            samples=kick_samples,
            onset_times=onset_times * 2,
            duration=intro_duration
        )

        # Render main section (4 bars = 8 seconds)
        main_duration = timeline[1]['duration']
        main_audio = renderer.render_pattern(
            pattern=kick_pattern * 4,  # Repeat for 4 bars
            samples=kick_samples,
            onset_times=onset_times * 4,
            duration=main_duration
        )

        # Write output
        import numpy as np
        full_audio = np.concatenate([intro_audio, main_audio])

        output_dir = Path("../output")
        output_dir.mkdir(exist_ok=True)

        renderer.write_wav(full_audio, str(output_dir / "test_beat_kick.wav"))
        print(f"✓ Rendered kick track: {len(full_audio)/44100:.2f} seconds")

    else:
        print("No kick samples available for rendering")


def test_cache_samples(bank):
    """Test sample caching"""
    print("\n" + "=" * 60)
    print("TEST 5: Sample Caching")
    print("=" * 60)

    cache_path = "../samples/sample_cache.pkl"
    bank.save_cache(cache_path)

    # Load from cache
    bank2 = SampleBank.load_cache(cache_path)
    print(f"Loaded from cache: {bank2}")


def main():
    print("\n" + "=" * 60)
    print("SCRAMBLAUDIO V2 - REAL SAMPLE TESTS")
    print("=" * 60 + "\n")

    try:
        # Load samples
        bank = test_sample_loading()

        # Test semantic space
        test_semantic_space(bank)

        # Test rhythm generation
        test_rhythm_generation()

        # Generate a beat
        test_simple_beat_generation(bank)

        # Test caching
        test_cache_samples(bank)

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETE!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

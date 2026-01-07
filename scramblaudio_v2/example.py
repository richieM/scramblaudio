"""
Example usage of scramblaudio v2 engine

Demonstrates:
- Loading samples with MIR features
- Creating euclidean/polymeter rhythms
- Building song arrangements
- Navigating semantic space
- Rendering audio output
"""

import numpy as np
from pathlib import Path

from core.sample_bank import SampleBank
from core.rhythm import euclidean_rhythm, polymeter_rhythm, pattern_to_onset_times, visualize_polymeter
from core.semantic_space import SemanticSpace
from core.arrangement import Section, Arrangement, create_simple_arrangement
from core.renderer import Renderer


def example_1_basic_rhythm():
    """Example 1: Generate and visualize euclidean rhythms"""
    print("=" * 60)
    print("EXAMPLE 1: Basic Euclidean Rhythms")
    print("=" * 60)

    from core.rhythm import visualize_pattern

    rhythms = [
        (3, 8, "Kick (standard rock)"),
        (5, 8, "Cuban tresillo"),
        (5, 13, "Odd meter pattern"),
        (7, 16, "Dense hi-hat"),
    ]

    for hits, steps, label in rhythms:
        pattern = euclidean_rhythm(hits, steps)
        print(visualize_pattern(pattern, label))

    print()


def example_2_polymeter():
    """Example 2: Create polyrhythmic patterns"""
    print("=" * 60)
    print("EXAMPLE 2: Polymeter/Polyrhythm")
    print("=" * 60)

    meters = [
        (3, 8),   # Kick
        (5, 13),  # Snare
        (7, 16),  # Hi-hat
    ]

    patterns = polymeter_rhythm(meters, bars=1)
    labels = {0: "Kick", 1: "Snare", 2: "Hi-hat"}

    print(visualize_polymeter(patterns, labels))
    print()


def example_3_arrangement():
    """Example 3: Create song arrangement"""
    print("=" * 60)
    print("EXAMPLE 3: Song Arrangement")
    print("=" * 60)

    # Simple arrangement
    arr = create_simple_arrangement([
        ('intro', 4, ['kick']),
        ('verse_a', 8, ['kick', 'snare', 'hihat']),
        ('chorus', 8, 'all'),
        ('verse_b', 8, ['kick', 'snare', 'hihat']),
        ('chorus', 8, 'all'),
        ('outro', 4, ['perc'])
    ], bpm=140)

    print(arr.visualize())
    print()


def example_4_complex_arrangement():
    """Example 4: Complex arrangement with polymeter and different time signatures"""
    print("=" * 60)
    print("EXAMPLE 4: Complex Arrangement with Polymeter")
    print("=" * 60)

    sections = [
        Section('intro', bars=4, bpm=120, time_signature=(4, 4),
               instruments=['kick'],
               metadata={'vibe': 'minimal'}),

        Section('verse', bars=8, bpm=120, time_signature=(7, 8),
               instruments=['kick', 'snare', 'hihat'],
               rhythm_params={
                   'kick': {'hits': 3, 'steps': 7},
                   'snare': {'hits': 5, 'steps': 13},
                   'hihat': {'hits': 7, 'steps': 16}
               },
               metadata={'vibe': 'polymetric chaos'}),

        Section('chorus', bars=8, bpm=140, time_signature=(4, 4),
               instruments='all',
               semantic_params={
                   'bass': {'brightness': 0.3, 'noisiness': 0.2},
                   'lead': {'brightness': 0.8, 'noisiness': 0.5}
               },
               metadata={'vibe': 'bright and dense'}),

        Section('breakdown', bars=4, bpm=90, time_signature=(5, 8),
               instruments=['perc', 'bass'],
               metadata={'vibe': 'sparse and weird'}),
    ]

    arr = Arrangement(sections)
    print(arr.visualize())
    print()


def example_5_sample_bank():
    """Example 5: Load samples and extract features"""
    print("=" * 60)
    print("EXAMPLE 5: Sample Bank with MIR Features")
    print("=" * 60)

    # Create sample bank
    bank = SampleBank()

    # Check if sample directories exist
    sample_dirs = {
        'kicks': '../wavs',  # Adjust to your sample paths
    }

    existing_dirs = {}
    for category, path in sample_dirs.items():
        if Path(path).exists():
            existing_dirs[category] = path

    if existing_dirs:
        print(f"Loading samples from: {existing_dirs}")
        bank.load_directories(existing_dirs, extract_features=True)
        print(f"\n{bank}\n")

        # Show features of first sample
        for category in bank.get_all_categories():
            samples = bank.get_samples(category)
            if samples:
                print(f"\nFeatures of first {category} sample:")
                for key, val in samples[0].features.items():
                    if isinstance(val, list):
                        print(f"  {key}: {val[:3]}... ({len(val)} values)")
                    else:
                        print(f"  {key}: {val:.4f}")
                break
    else:
        print("No sample directories found. Skipping sample loading.")
        print("Update the sample_dirs paths to point to your .wav files.")

    print()


def example_6_semantic_space():
    """Example 6: Navigate semantic space"""
    print("=" * 60)
    print("EXAMPLE 6: Semantic Space Navigation")
    print("=" * 60)

    # This example requires actual samples with features
    # For now, we'll create dummy samples

    from core.sample_bank import Sample

    # Create dummy samples with fake features
    dummy_samples = []
    for i in range(10):
        audio = np.random.randn(44100)  # 1 second of noise
        features = {
            'brightness': np.random.random(),
            'noisiness': np.random.random(),
            'energy': np.random.random(),
        }
        sample = Sample(f"sample_{i}.wav", audio, 44100, features)
        dummy_samples.append(sample)

    # Create semantic space
    space = SemanticSpace(dummy_samples)
    print(f"{space}\n")

    # Show feature summary
    summary = space.get_feature_summary()
    print("Feature ranges:")
    for feature, stats in summary.items():
        print(f"  {feature}: {stats['min']:.3f} - {stats['max']:.3f} "
              f"(mean: {stats['mean']:.3f})")

    # Find similar samples
    print(f"\nSamples similar to {dummy_samples[0].name}:")
    similar = space.find_similar(dummy_samples[0], n=3)
    for sample in similar:
        print(f"  - {sample.name}")

    # Find in region
    print("\nSamples with high brightness and low noisiness:")
    region_samples = space.find_in_region(
        {'brightness': 0.8, 'noisiness': 0.2},
        radius=0.5,
        n=3
    )
    for sample in region_samples:
        print(f"  - {sample.name}")

    print()


def example_7_complete_workflow():
    """Example 7: Complete workflow (requires samples)"""
    print("=" * 60)
    print("EXAMPLE 7: Complete Workflow")
    print("=" * 60)
    print("This example shows the complete workflow:")
    print("1. Load samples")
    print("2. Create arrangement")
    print("3. Generate rhythms")
    print("4. Render audio")
    print("\nNote: Requires actual sample files to run")
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("SCRAMBLAUDIO V2 - EXAMPLES")
    print("=" * 60 + "\n")

    examples = [
        example_1_basic_rhythm,
        example_2_polymeter,
        example_3_arrangement,
        example_4_complex_arrangement,
        example_5_sample_bank,
        example_6_semantic_space,
        example_7_complete_workflow,
    ]

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"Error in {example_func.__name__}: {e}\n")

    print("=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

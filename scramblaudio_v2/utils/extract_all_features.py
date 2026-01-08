#!/usr/bin/env python3
"""
Extract Features from All Downloaded Samples

Processes all samples from multi-source download and extracts MIR features.
Creates unified sample bank with semantic spaces.
"""

import sys
from pathlib import Path
import pickle
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scramblaudio_v2.core.sample_bank import SampleBank
from scramblaudio_v2.core.semantic_space import SemanticSpace


def extract_features_from_directory(base_dir: str, output_cache: str):
    """
    Extract features from all samples in directory tree

    Args:
        base_dir: Root directory containing samples
        output_cache: Where to save cache file
    """
    print("="*80)
    print("FEATURE EXTRACTION - Multi-Source Sample Library")
    print("="*80)

    base_path = Path(base_dir)

    if not base_path.exists():
        print(f"⚠️  Directory not found: {base_dir}")
        return

    # Find all subdirectories (categories)
    categories = {}
    for subdir in base_path.iterdir():
        if subdir.is_dir():
            # Count audio files
            audio_files = list(subdir.glob("*.wav")) + list(subdir.glob("*.ogg")) + list(subdir.glob("*.mp3"))
            if audio_files:
                categories[subdir.name] = str(subdir)

    print(f"\nFound {len(categories)} categories:")
    total_estimate = 0
    for cat, path in list(categories.items())[:20]:
        count = len(list(Path(path).glob("*.wav"))) + len(list(Path(path).glob("*.ogg")))
        print(f"   • {cat}: ~{count} samples")
        total_estimate += count

    if len(categories) > 20:
        print(f"   • ... and {len(categories) - 20} more categories")

    print(f"\nEstimated total: ~{total_estimate} samples")
    print(f"\nThis will take approximately {total_estimate * 0.5 / 60:.1f} minutes...")

    # Create sample bank
    print("\n📦 Loading samples and extracting features...")
    bank = SampleBank()

    start_time = time.time()
    last_update = start_time

    # Load each category
    for i, (cat_name, cat_path) in enumerate(categories.items(), 1):
        print(f"\n[{i}/{len(categories)}] Processing: {cat_name}")

        try:
            bank.load_directory(cat_path, cat_name, extract_features=True)

            # Progress update
            elapsed = time.time() - start_time
            avg_time_per_cat = elapsed / i
            remaining_cats = len(categories) - i
            eta_seconds = avg_time_per_cat * remaining_cats
            eta_minutes = eta_seconds / 60

            print(f"   ✓ {cat_name}: {len(bank.get_samples(cat_name))} samples")
            print(f"   Total so far: {len(bank.samples)} samples")
            print(f"   ETA: {eta_minutes:.1f} minutes")

        except Exception as e:
            print(f"   ✗ Error processing {cat_name}: {e}")
            continue

    total_time = time.time() - start_time

    print("\n" + "="*80)
    print("EXTRACTION COMPLETE")
    print("="*80)
    print(f"Total samples: {len(bank.samples)}")
    print(f"Categories: {len(bank.categories)}")
    print(f"Time: {total_time / 60:.1f} minutes")

    # Save cache
    print(f"\n💾 Saving cache to {output_cache}...")
    bank.save_cache(output_cache)
    print("✓ Cache saved")

    # Build semantic spaces
    print("\n🧠 Building semantic spaces per category...")

    spaces = {}
    for cat_name in bank.categories.keys():
        samples = bank.get_samples(cat_name)
        if len(samples) >= 10:  # Need at least 10 for meaningful space
            space = SemanticSpace(samples)
            spaces[cat_name] = space
            print(f"   • {cat_name}: {space}")

    # Save spaces
    spaces_cache = Path(output_cache).parent / "semantic_spaces.pkl"
    print(f"\n💾 Saving semantic spaces to {spaces_cache}...")
    with open(spaces_cache, 'wb') as f:
        pickle.dump(spaces, f)
    print("✓ Semantic spaces saved")

    print("\n" + "🎉"*40)
    print("ALL DONE!")
    print("🎉"*40)
    print(f"\nCache files:")
    print(f"   • Sample bank: {output_cache}")
    print(f"   • Semantic spaces: {spaces_cache}")
    print(f"\nTotal samples: {len(bank.samples)}")
    print(f"Total categories: {len(bank.categories)}")
    print(f"\nReady for semantic navigation! 🚀\n")


if __name__ == "__main__":
    import sys

    base_dir = sys.argv[1] if len(sys.argv) > 1 else "../samples/world_sounds"
    output_cache = sys.argv[2] if len(sys.argv) > 2 else "../samples/world_sounds_cache.pkl"

    extract_features_from_directory(base_dir, output_cache)

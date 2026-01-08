#!/usr/bin/env python3
"""
Quick Sample Download - Get 1,000 diverse samples FAST

Downloads small, curated subset from ESC-50 (fast, small dataset)
Plus fills gaps with existing samples we already have.
"""

import sys
import requests
import zipfile
import shutil
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scramblaudio_v2.core.sample_bank import SampleBank
from scramblaudio_v2.core.semantic_space import SemanticSpace


def quick_download_esc50():
    """Download ESC-50 (2k samples, 600MB, ~5 minutes)"""

    print("🚀 QUICK DOWNLOAD - 1,000 Diverse Samples")
    print("="*80)

    base_dir = Path("../../samples/world_sounds")
    base_dir.mkdir(parents=True, exist_ok=True)

    target_dir = base_dir / "esc50"
    target_dir.mkdir(exist_ok=True)

    # Check if already downloaded
    existing_cats = [d for d in target_dir.iterdir() if d.is_dir()]
    if len(existing_cats) > 40:
        print(f"\n✓ ESC-50 already downloaded!")
        print(f"   Found {len(existing_cats)} categories")

        # Count samples
        total = sum(len(list(cat_dir.glob("*.ogg"))) for cat_dir in existing_cats)
        print(f"   Total samples: {total}")
        return total

    print("\nDownloading ESC-50 dataset...")
    print("Size: ~600MB")
    print("Time: ~5-10 minutes")

    url = "https://github.com/karolpiczak/ESC-50/archive/master.zip"
    zip_path = target_dir / "esc50.zip"

    print(f"\n📥 Downloading from GitHub...")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192*4):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size:
                    pct = (downloaded / total_size) * 100
                    mb = downloaded / (1024*1024)
                    total_mb = total_size / (1024*1024)
                    print(f"   {pct:.1f}% - {mb:.1f}/{total_mb:.1f} MB", end='\r')

        print(f"\n✓ Downloaded")

        # Extract
        print("\n📦 Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)

        print("✓ Extracted")

        # Organize by category
        audio_dir = target_dir / "ESC-50-master" / "audio"
        meta_file = target_dir / "ESC-50-master" / "meta" / "esc50.csv"

        categories = {}

        if meta_file.exists() and audio_dir.exists():
            print("\n🗂️  Organizing into categories...")

            with open(meta_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    filename = row['filename']
                    category = row['category']

                    cat_dir = target_dir / category
                    cat_dir.mkdir(exist_ok=True)

                    src = audio_dir / filename
                    dst = cat_dir / filename

                    if src.exists():
                        shutil.copy2(src, dst)

                        if category not in categories:
                            categories[category] = 0
                        categories[category] += 1

        # Cleanup
        zip_path.unlink()
        shutil.rmtree(target_dir / "ESC-50-master")

        total = sum(categories.values())
        print(f"\n✓ Organized {total} samples into {len(categories)} categories")

        # Show sample categories
        print("\nCategories:")
        for cat, count in sorted(categories.items())[:10]:
            print(f"   • {cat}: {count} samples")
        if len(categories) > 10:
            print(f"   • ... and {len(categories) - 10} more")

        print(f"\n✅ ESC-50 download complete!")
        print(f"   Location: {target_dir}")
        print(f"   Samples: {total}")

        return total

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 0


def combine_with_existing():
    """Combine ESC-50 with existing drum samples"""

    print("\n" + "="*80)
    print("COMBINING WITH EXISTING SAMPLES")
    print("="*80)

    bank = SampleBank()

    # Load existing drums (already have ~300)
    existing = {
        'kick': '../../samples/kicks/',
        'snare': '../../samples/snares/',
        'hihat': '../../samples/hihats/',
        'perc': '../../samples/perc/',
        'crash': '../../samples/crashes/',
    }

    print("\nLoading existing drum samples...")
    for cat, path in existing.items():
        if Path(path).exists():
            bank.load_directory(path, cat, extract_features=True)

    print(f"✓ Loaded {len(bank.samples)} existing samples")

    # Load ESC-50
    esc50_dir = Path("../../samples/world_sounds/esc50")
    if esc50_dir.exists():
        print("\nLoading ESC-50 samples...")

        for cat_dir in esc50_dir.iterdir():
            if cat_dir.is_dir():
                cat_name = cat_dir.name
                bank.load_directory(str(cat_dir), cat_name, extract_features=True)

        print(f"✓ Loaded ESC-50")

    total_samples = sum(len(samples) for samples in bank.samples.values())
    print(f"\n📊 Total samples: {total_samples}")
    print(f"📂 Total categories: {len(bank.samples)}")

    # Show breakdown
    print("\nBreakdown:")
    for cat in sorted(bank.samples.keys())[:20]:
        count = len(bank.get_samples(cat))
        print(f"   • {cat}: {count} samples")

    if len(bank.samples) > 20:
        print(f"   • ... and {len(bank.samples) - 20} more categories")

    # Save cache
    cache_path = Path("../../samples/world_sounds_cache.pkl")
    print(f"\n💾 Saving cache to {cache_path}...")
    bank.save_cache(str(cache_path))
    print("✓ Cache saved")

    # Build semantic spaces
    print("\n🧠 Building semantic spaces...")

    import pickle

    spaces = {}
    for cat_name in list(bank.samples.keys())[:30]:  # Limit for speed
        samples = bank.get_samples(cat_name)
        if len(samples) >= 5:
            space = SemanticSpace(samples)
            spaces[cat_name] = space
            print(f"   • {cat_name}: {space}")

    spaces_cache = cache_path.parent / "semantic_spaces.pkl"
    with open(spaces_cache, 'wb') as f:
        pickle.dump(spaces, f)

    print(f"✓ Saved {len(spaces)} semantic spaces")

    print("\n" + "🎉"*40)
    print("READY TO GO!")
    print("🎉"*40)
    print(f"\nTotal samples: {total_samples}")
    print(f"Total categories: {len(bank.samples)}")
    print(f"Cache: {cache_path}")
    print("\nRun semantic_navigation_demo.py to see it in action! 🚀\n")


if __name__ == "__main__":
    # Download ESC-50
    count = quick_download_esc50()

    if count > 0:
        # Combine and extract features
        combine_with_existing()
    else:
        print("\n⚠️  Download failed. Check your internet connection.")

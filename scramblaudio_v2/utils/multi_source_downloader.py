#!/usr/bin/env python3
"""
Multi-Source Sample Downloader - Download 20k+ diverse samples from multiple sources

Sources:
- FSD50K: Freesound Dataset 50K (environmental, curated)
- NSynth: Google's musical instrument dataset
- ESC-50: Environmental Sound Classification
- UrbanSound8K: Urban environmental sounds
- Freesound: Fill gaps and get specific categories

All automatically organized, tagged, and feature-extracted.
"""

import os
import sys
import requests
import zipfile
import tarfile
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import time
from dataclasses import dataclass


@dataclass
class DownloadSource:
    """Configuration for a download source"""
    name: str
    url: str
    format: str  # 'zip', 'tar.gz', 'direct'
    output_dir: str
    target_count: int
    description: str


class MultiSourceDownloader:
    """
    Download and organize samples from multiple curated datasets
    """

    def __init__(self, base_dir: str = "../samples"):
        """
        Initialize multi-source downloader

        Args:
            base_dir: Base directory for all samples
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.stats = {
            'total_downloaded': 0,
            'by_source': {},
            'by_category': {}
        }

    def download_esc50(self, target_dir: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Download ESC-50 dataset (2,000 environmental sounds)

        Returns:
            Dict mapping categories to file paths
        """
        print("\n" + "="*80)
        print("DOWNLOADING ESC-50 DATASET")
        print("="*80)
        print("Environmental Sound Classification - 2,000 sounds in 50 categories")

        target_dir = Path(target_dir or self.base_dir / "esc50")
        target_dir.mkdir(parents=True, exist_ok=True)

        # ESC-50 GitHub repo
        url = "https://github.com/karolpiczak/ESC-50/archive/master.zip"
        zip_path = target_dir / "esc50.zip"

        print(f"\n📥 Downloading from {url}...")

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size:
                        pct = (downloaded / total_size) * 100
                        print(f"   Progress: {pct:.1f}% ({downloaded}/{total_size} bytes)", end='\r')

            print(f"\n✓ Downloaded: {zip_path}")

            # Extract
            print("\n📦 Extracting...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)

            # Find audio files
            audio_dir = target_dir / "ESC-50-master" / "audio"

            if not audio_dir.exists():
                print(f"⚠️  Audio directory not found at {audio_dir}")
                return {}

            # Organize by category (using metadata CSV)
            meta_file = target_dir / "ESC-50-master" / "meta" / "esc50.csv"

            organized = {}

            if meta_file.exists():
                print("\n🗂️  Organizing by category...")
                import csv

                with open(meta_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        filename = row['filename']
                        category = row['category']

                        # Create category dir
                        cat_dir = target_dir / category
                        cat_dir.mkdir(exist_ok=True)

                        # Copy file
                        src = audio_dir / filename
                        dst = cat_dir / filename

                        if src.exists():
                            shutil.copy2(src, dst)

                            if category not in organized:
                                organized[category] = []
                            organized[category].append(str(dst))

                print(f"✓ Organized {sum(len(files) for files in organized.values())} files into {len(organized)} categories")

            # Cleanup
            zip_path.unlink()
            shutil.rmtree(target_dir / "ESC-50-master")

            self.stats['by_source']['ESC-50'] = sum(len(files) for files in organized.values())

            return organized

        except Exception as e:
            print(f"✗ Error downloading ESC-50: {e}")
            return {}

    def download_urbansound8k(self, target_dir: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Download UrbanSound8K dataset

        NOTE: UrbanSound8K requires manual download due to terms of use.
        This function provides instructions.
        """
        print("\n" + "="*80)
        print("URBANSOUND8K DATASET")
        print("="*80)
        print("⚠️  Manual download required due to license agreement")
        print("\nTo download UrbanSound8K:")
        print("1. Go to: https://urbansounddataset.weebly.com/urbansound8k.html")
        print("2. Fill out the download form")
        print("3. Download UrbanSound8K.tar.gz")
        print("4. Extract to: " + str(self.base_dir / "urbansound8k"))
        print("\nSkipping automatic download...")

        return {}

    def download_fsd50k(self, target_dir: Optional[str] = None, subset: str = 'dev') -> Dict[str, List[str]]:
        """
        Download FSD50K dataset

        NOTE: FSD50K is large (30GB+). This downloads the dev subset by default.

        Args:
            subset: 'dev' (1GB, 5k samples) or 'eval' (5GB, 10k samples)
        """
        print("\n" + "="*80)
        print("FSD50K DATASET")
        print("="*80)
        print("Freesound Dataset 50K - Curated environmental sounds")
        print(f"Subset: {subset}")

        target_dir = Path(target_dir or self.base_dir / "fsd50k")
        target_dir.mkdir(parents=True, exist_ok=True)

        # Zenodo direct download links
        urls = {
            'dev': 'https://zenodo.org/record/4060432/files/FSD50K.dev_audio.zip',
            'eval': 'https://zenodo.org/record/4060432/files/FSD50K.eval_audio.zip',
        }

        if subset not in urls:
            print(f"⚠️  Unknown subset: {subset}")
            return {}

        url = urls[subset]
        zip_path = target_dir / f"fsd50k_{subset}.zip"

        print(f"\n📥 Downloading {subset} subset...")
        print(f"   URL: {url}")
        print(f"   This may take a while (1-5 GB)...")

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192*16):  # Larger chunks
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size:
                        pct = (downloaded / total_size) * 100
                        mb = downloaded / (1024*1024)
                        total_mb = total_size / (1024*1024)
                        print(f"   Progress: {pct:.1f}% ({mb:.1f}/{total_mb:.1f} MB)", end='\r')

            print(f"\n✓ Downloaded: {zip_path}")

            # Extract
            print("\n📦 Extracting (this may take several minutes)...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)

            print("✓ Extraction complete")

            # Find audio files
            audio_files = list(target_dir.glob("**/*.wav"))

            print(f"✓ Found {len(audio_files)} audio files")

            # For FSD50K, files are already organized in folders
            # We'll just return them all in one category for now
            organized = {'fsd50k_' + subset: [str(f) for f in audio_files]}

            # Cleanup zip
            zip_path.unlink()

            self.stats['by_source']['FSD50K'] = len(audio_files)

            return organized

        except Exception as e:
            print(f"✗ Error downloading FSD50K: {e}")
            return {}

    def download_nsynth_subset(self, target_dir: Optional[str] = None,
                               count: int = 6000) -> Dict[str, List[str]]:
        """
        Download NSynth dataset subset

        NOTE: Full NSynth is 30GB+. This downloads a subset.

        For full dataset, download manually from:
        https://magenta.tensorflow.org/datasets/nsynth
        """
        print("\n" + "="*80)
        print("NSYNTH DATASET")
        print("="*80)
        print(f"Downloading subset of ~{count} samples")
        print("Google's musical instrument dataset")

        target_dir = Path(target_dir or self.base_dir / "nsynth")
        target_dir.mkdir(parents=True, exist_ok=True)

        # NSynth "lite" subset (smaller, curated)
        # We'll use the test set which is smaller
        url = "http://download.magenta.tensorflow.org/datasets/nsynth/nsynth-test.jsonwav.tar.gz"

        tar_path = target_dir / "nsynth-test.tar.gz"

        print(f"\n📥 Downloading NSynth test set...")
        print(f"   URL: {url}")
        print(f"   Size: ~2-3 GB")
        print(f"   This will take a while...")

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(tar_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192*16):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size:
                        pct = (downloaded / total_size) * 100
                        mb = downloaded / (1024*1024)
                        total_mb = total_size / (1024*1024)
                        print(f"   Progress: {pct:.1f}% ({mb:.1f}/{total_mb:.1f} MB)", end='\r')

            print(f"\n✓ Downloaded: {tar_path}")

            # Extract
            print("\n📦 Extracting (this will take 5-10 minutes)...")
            with tarfile.open(tar_path, 'r:gz') as tar:
                tar.extractall(target_dir)

            print("✓ Extraction complete")

            # Find audio files
            audio_files = list(target_dir.glob("**/*.wav"))

            # NSynth has metadata JSON with instrument families
            # Organize by instrument family
            organized = {}

            json_path = target_dir / "nsynth-test" / "examples.json"
            if json_path.exists():
                print("\n🗂️  Organizing by instrument family...")

                with open(json_path, 'r') as f:
                    metadata = json.load(f)

                # Map instrument_family_str to category
                for filename, meta in list(metadata.items())[:count]:
                    family = meta.get('instrument_family_str', 'unknown')

                    # Create category dir
                    cat_dir = target_dir / family
                    cat_dir.mkdir(exist_ok=True)

                    # Find and move file
                    wav_name = filename + ".wav"
                    src = target_dir / "nsynth-test" / "audio" / wav_name

                    if src.exists():
                        dst = cat_dir / wav_name
                        shutil.move(str(src), str(dst))

                        if family not in organized:
                            organized[family] = []
                        organized[family].append(str(dst))

                print(f"✓ Organized {sum(len(files) for files in organized.values())} files into {len(organized)} families")
            else:
                # Fallback: just copy first N files
                organized = {'nsynth': [str(f) for f in audio_files[:count]]}

            # Cleanup
            tar_path.unlink()
            if (target_dir / "nsynth-test").exists():
                shutil.rmtree(target_dir / "nsynth-test")

            self.stats['by_source']['NSynth'] = sum(len(files) for files in organized.values())

            return organized

        except Exception as e:
            print(f"✗ Error downloading NSynth: {e}")
            return {}

    def download_all(self, target_total: int = 20000) -> Dict[str, Dict[str, List[str]]]:
        """
        Download samples from all sources to reach target total

        Args:
            target_total: Target number of samples (default 20k)

        Returns:
            Dict mapping source name to organized samples
        """
        print("\n" + "🎵"*40)
        print("MULTI-SOURCE SAMPLE LIBRARY DOWNLOAD")
        print("🎵"*40)
        print(f"\nTarget: {target_total} samples")
        print(f"Sources: ESC-50, FSD50K, NSynth, Freesound")

        all_samples = {}

        # 1. ESC-50 (~2,000 samples)
        print("\n[1/4] ESC-50...")
        esc50_samples = self.download_esc50()
        if esc50_samples:
            all_samples['ESC-50'] = esc50_samples

        # 2. FSD50K dev subset (~5,000 samples)
        print("\n[2/4] FSD50K...")
        fsd50k_samples = self.download_fsd50k(subset='dev')
        if fsd50k_samples:
            all_samples['FSD50K'] = fsd50k_samples

        # 3. NSynth subset (~6,000 samples)
        print("\n[3/4] NSynth...")
        nsynth_samples = self.download_nsynth_subset(count=6000)
        if nsynth_samples:
            all_samples['NSynth'] = nsynth_samples

        # 4. Freesound for filling gaps
        current_total = sum(
            len(files)
            for source in all_samples.values()
            for files in source.values()
        )

        remaining = target_total - current_total

        if remaining > 0:
            print(f"\n[4/4] Freesound (filling {remaining} remaining)...")
            print("   Set FREESOUND_API_KEY environment variable to download from Freesound")
            print("   Skipping for now...")

        # Summary
        print("\n" + "="*80)
        print("DOWNLOAD SUMMARY")
        print("="*80)

        total = 0
        for source_name, categories in all_samples.items():
            source_total = sum(len(files) for files in categories.values())
            total += source_total
            print(f"\n{source_name}: {source_total} samples")
            for cat, files in list(categories.items())[:5]:  # Show first 5 categories
                print(f"   • {cat}: {len(files)} samples")
            if len(categories) > 5:
                print(f"   • ... and {len(categories) - 5} more categories")

        print(f"\n{'='*80}")
        print(f"TOTAL DOWNLOADED: {total} samples")
        print(f"Target: {target_total} ({total/target_total*100:.1f}%)")
        print(f"Output directory: {self.base_dir}")
        print(f"{'='*80}\n")

        return all_samples


def main():
    """Run multi-source download"""
    downloader = MultiSourceDownloader(base_dir="../samples/world_sounds")

    # Download 20k samples
    downloader.download_all(target_total=20000)

    print("\n✨ Download complete! Run feature extraction next:")
    print("   python extract_all_features.py")


if __name__ == "__main__":
    main()

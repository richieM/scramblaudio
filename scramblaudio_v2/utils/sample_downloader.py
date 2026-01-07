#!/usr/bin/env python3
"""
Sample Downloader - Download samples from Freesound.org

Uses Freesound API to download diverse, high-quality audio samples.
Automatically organizes, tags, and extracts features.

To use this, you need a Freesound API key:
1. Register at https://freesound.org/
2. Get API key from https://freesound.org/apiv2/apply/
3. Set environment variable: export FREESOUND_API_KEY="your_key"
"""

import os
import json
import time
import requests
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
import hashlib


@dataclass
class SampleMetadata:
    """Metadata for a downloaded sample"""
    id: int
    name: str
    tags: List[str]
    duration: float
    filesize: int
    samplerate: int
    channels: int
    bitdepth: int
    license: str
    username: str
    description: str
    local_path: Optional[str] = None


class FreesoundDownloader:
    """
    Download and manage samples from Freesound.org

    Handles API requests, file downloads, organization, and metadata.
    """

    BASE_URL = "https://freesound.org/apiv2"

    def __init__(self, api_key: Optional[str] = None, output_dir: str = "../samples/freesound"):
        """
        Initialize downloader

        Args:
            api_key: Freesound API key (or None to read from env)
            output_dir: Where to save downloaded samples
        """
        self.api_key = api_key or os.environ.get('FREESOUND_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Freesound API key required. "
                "Get one at https://freesound.org/apiv2/apply/ and set FREESOUND_API_KEY env var"
            )

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.metadata_file = self.output_dir / "metadata.json"
        self.downloaded_ids: Set[int] = set()
        self._load_metadata()

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 10 requests per second max

    def _load_metadata(self):
        """Load existing metadata from disk"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
                self.downloaded_ids = set(data.get('downloaded_ids', []))
        else:
            self.downloaded_ids = set()

    def _save_metadata(self):
        """Save metadata to disk"""
        data = {
            'downloaded_ids': list(self.downloaded_ids),
            'total_samples': len(self.downloaded_ids),
        }
        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def _api_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Make API request to Freesound

        Args:
            endpoint: API endpoint (e.g., '/search/text/')
            params: Query parameters

        Returns:
            JSON response as dict
        """
        self._rate_limit()

        url = f"{self.BASE_URL}{endpoint}"
        headers = {"Authorization": f"Token {self.api_key}"}
        params = params or {}

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        return response.json()

    def search(self, query: str, filter_params: Optional[str] = None,
              max_results: int = 100, duration_range: tuple = (0.1, 10.0)) -> List[Dict]:
        """
        Search for samples

        Args:
            query: Search query (tags, keywords)
            filter_params: Additional filter string (e.g., "tag:oneshot duration:[0 TO 5]")
            max_results: Maximum number of results
            duration_range: (min, max) duration in seconds

        Returns:
            List of sample info dicts
        """
        results = []
        page = 1
        page_size = 150  # Max per page

        # Build filter
        filters = []
        if filter_params:
            filters.append(filter_params)

        # Duration filter
        filters.append(f"duration:[{duration_range[0]} TO {duration_range[1]}]")

        # Only want audio files (not packs)
        filters.append("type:wav OR type:ogg OR type:mp3")

        filter_str = " ".join(filters)

        while len(results) < max_results:
            params = {
                'query': query,
                'filter': filter_str,
                'page': page,
                'page_size': min(page_size, max_results - len(results)),
                'fields': 'id,name,tags,duration,filesize,type,channels,samplerate,bitdepth,license,username,description,previews,download',
            }

            try:
                response = self._api_request('/search/text/', params)
                sounds = response.get('results', [])

                if not sounds:
                    break

                results.extend(sounds)
                page += 1

                print(f"   Found {len(results)} samples so far...")

                # Check if we've reached the end
                if len(sounds) < page_size:
                    break

            except Exception as e:
                print(f"   Error during search: {e}")
                break

        return results[:max_results]

    def download_sample(self, sample_info: Dict, category: str = "uncategorized") -> Optional[str]:
        """
        Download a single sample

        Args:
            sample_info: Sample info from search results
            category: Category folder to save in

        Returns:
            Local file path or None if failed
        """
        sample_id = sample_info['id']

        # Skip if already downloaded
        if sample_id in self.downloaded_ids:
            return None

        try:
            # Get full sample info including download URL
            full_info = self._api_request(f'/sounds/{sample_id}/')

            # Prefer high-quality preview over full download (requires OAuth)
            # We'll use the HQ preview which is good enough for most uses
            preview_url = full_info['previews']['preview-hq-ogg']

            # Download file
            self._rate_limit()
            response = requests.get(preview_url, stream=True)
            response.raise_for_status()

            # Create category directory
            category_dir = self.output_dir / category
            category_dir.mkdir(exist_ok=True)

            # Sanitize filename
            safe_name = "".join(c for c in sample_info['name'] if c.isalnum() or c in (' ', '-', '_'))
            safe_name = safe_name[:100]  # Limit length

            # Save with ID to avoid collisions
            filename = f"{sample_id}_{safe_name}.ogg"
            filepath = category_dir / filename

            # Write file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Save metadata
            metadata = SampleMetadata(
                id=sample_id,
                name=sample_info['name'],
                tags=sample_info.get('tags', []),
                duration=sample_info['duration'],
                filesize=sample_info.get('filesize', 0),
                samplerate=sample_info.get('samplerate', 44100),
                channels=sample_info.get('channels', 1),
                bitdepth=sample_info.get('bitdepth', 16),
                license=sample_info.get('license', 'unknown'),
                username=sample_info.get('username', 'unknown'),
                description=sample_info.get('description', ''),
                local_path=str(filepath)
            )

            # Save individual metadata file
            metadata_path = filepath.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata.__dict__, f, indent=2)

            # Mark as downloaded
            self.downloaded_ids.add(sample_id)
            self._save_metadata()

            return str(filepath)

        except Exception as e:
            print(f"   Error downloading sample {sample_id}: {e}")
            return None

    def download_category(self, category: str, query: str, count: int = 100,
                         duration_range: tuple = (0.1, 10.0)) -> List[str]:
        """
        Download samples for a specific category

        Args:
            category: Category name (e.g., 'kick', 'percussion')
            query: Search query for this category
            count: Number of samples to download
            duration_range: (min, max) duration in seconds

        Returns:
            List of downloaded file paths
        """
        print(f"\n📥 Downloading {count} samples for category: {category}")
        print(f"   Query: {query}")

        # Search
        results = self.search(query, max_results=count * 2, duration_range=duration_range)  # Get extra in case some fail

        print(f"   Found {len(results)} candidates")

        # Download
        downloaded = []
        for i, sample_info in enumerate(results):
            if len(downloaded) >= count:
                break

            print(f"   Downloading {i+1}/{count}: {sample_info['name'][:50]}...", end=' ')

            filepath = self.download_sample(sample_info, category)
            if filepath:
                downloaded.append(filepath)
                print("✓")
            else:
                print("(skipped)")

            # Be nice to the API
            time.sleep(0.1)

        print(f"   ✓ Downloaded {len(downloaded)} samples for {category}")
        return downloaded

    def download_diverse_library(self, target_count: int = 10000) -> Dict[str, List[str]]:
        """
        Download a diverse library of samples across many categories

        Args:
            target_count: Total number of samples to download

        Returns:
            Dict mapping categories to file paths
        """
        # Define categories with search queries and counts
        # Balanced to represent "sounds of the world"
        categories = {
            # Drums & Percussion (20%)
            'kick': ('kick drum oneshot', 200, (0.1, 2.0)),
            'snare': ('snare drum oneshot', 200, (0.1, 2.0)),
            'hihat': ('hihat closed open oneshot', 200, (0.05, 1.0)),
            'cymbal': ('cymbal crash ride oneshot', 200, (0.2, 5.0)),
            'tom': ('tom drum oneshot', 100, (0.1, 2.0)),
            'percussion': ('percussion shaker conga bongo oneshot', 300, (0.1, 3.0)),
            'clap': ('clap handclap oneshot', 100, (0.05, 1.0)),

            # Tonal/Musical (15%)
            'bass': ('bass note oneshot synth', 200, (0.1, 3.0)),
            'synth': ('synth note oneshot', 300, (0.1, 3.0)),
            'keys': ('piano keyboard note oneshot', 200, (0.1, 3.0)),
            'guitar': ('guitar note oneshot pluck', 100, (0.1, 3.0)),
            'string': ('string violin cello note oneshot', 100, (0.2, 3.0)),
            'brass': ('brass trumpet horn note oneshot', 100, (0.2, 3.0)),

            # Effects & Atmosphere (15%)
            'riser': ('riser sweep up oneshot', 150, (0.5, 5.0)),
            'impact': ('impact hit boom oneshot', 150, (0.1, 3.0)),
            'noise': ('noise white pink texture oneshot', 150, (0.1, 5.0)),
            'fx': ('fx sound effect whoosh zap oneshot', 300, (0.1, 5.0)),
            'drone': ('drone ambient pad oneshot', 150, (1.0, 10.0)),

            # Nature & Environment (20%)
            'bird': ('bird chirp tweet oneshot', 300, (0.1, 5.0)),
            'animal': ('animal sound oneshot', 200, (0.1, 5.0)),
            'water': ('water splash drop rain oneshot', 300, (0.1, 5.0)),
            'wind': ('wind air breeze oneshot', 200, (0.2, 5.0)),
            'wood': ('wood hit knock tap oneshot', 200, (0.1, 2.0)),
            'metal': ('metal hit clang oneshot', 200, (0.1, 3.0)),
            'glass': ('glass break clink oneshot', 100, (0.1, 3.0)),
            'stone': ('stone rock hit oneshot', 100, (0.1, 3.0)),

            # Urban & Mechanical (15%)
            'door': ('door slam close open oneshot', 150, (0.1, 3.0)),
            'machine': ('machine mechanical motor oneshot', 200, (0.1, 5.0)),
            'beep': ('beep bleep electronic oneshot', 150, (0.05, 2.0)),
            'click': ('click switch button oneshot', 200, (0.05, 1.0)),
            'vehicle': ('car engine vehicle oneshot', 150, (0.2, 5.0)),
            'tool': ('tool drill hammer saw oneshot', 150, (0.1, 3.0)),

            # Human & Voice (10%)
            'vocal': ('vocal voice human oneshot', 300, (0.1, 5.0)),
            'breath': ('breath inhale exhale oneshot', 100, (0.1, 3.0)),
            'footstep': ('footstep walk step oneshot', 200, (0.1, 1.0)),

            # Miscellaneous (5%)
            'weird': ('strange unusual weird glitch oneshot', 300, (0.1, 5.0)),
            'toy': ('toy plastic squeak oneshot', 100, (0.1, 3.0)),
            'food': ('food eating cooking oneshot', 100, (0.1, 3.0)),
        }

        # Calculate samples per category to reach target
        total_base = sum(count for _, (_, count, _) in categories.items())
        scale = target_count / total_base

        print(f"\n{'='*60}")
        print(f"DOWNLOADING DIVERSE SAMPLE LIBRARY")
        print(f"{'='*60}")
        print(f"Target: {target_count} samples across {len(categories)} categories")
        print(f"Scale factor: {scale:.2f}")

        downloaded = {}
        total_downloaded = 0

        for category, (query, count, duration_range) in categories.items():
            adjusted_count = max(10, int(count * scale))  # At least 10 per category

            try:
                files = self.download_category(category, query, adjusted_count, duration_range)
                downloaded[category] = files
                total_downloaded += len(files)
            except Exception as e:
                print(f"   ✗ Failed to download {category}: {e}")
                downloaded[category] = []

            # Progress
            print(f"\n   Progress: {total_downloaded} / {target_count} samples ({total_downloaded/target_count*100:.1f}%)")

        print(f"\n{'='*60}")
        print(f"DOWNLOAD COMPLETE!")
        print(f"{'='*60}")
        print(f"Total downloaded: {total_downloaded} samples")
        print(f"Categories: {len([c for c, files in downloaded.items() if files])} / {len(categories)}")
        print(f"Output directory: {self.output_dir}")

        return downloaded


def main():
    """Example usage"""
    import sys

    if not os.environ.get('FREESOUND_API_KEY'):
        print("ERROR: FREESOUND_API_KEY environment variable not set")
        print("\nTo get an API key:")
        print("1. Register at https://freesound.org/")
        print("2. Get API key from https://freesound.org/apiv2/apply/")
        print("3. Run: export FREESOUND_API_KEY='your_key_here'")
        sys.exit(1)

    downloader = FreesoundDownloader()

    # Download diverse library
    target = 10000 if len(sys.argv) < 2 else int(sys.argv[1])
    downloader.download_diverse_library(target_count=target)


if __name__ == "__main__":
    main()

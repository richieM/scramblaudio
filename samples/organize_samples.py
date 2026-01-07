#!/usr/bin/env python3
"""
Organize downloaded drum samples into category folders
"""

import os
import shutil
from pathlib import Path

def organize_samples():
    """Organize samples from temp_drum_samples into category folders"""

    source_dir = Path("temp_drum_samples")

    # Define categories and their matching patterns
    categories = {
        'kicks': ['Kick-', 'kick-', 'KICK-', '-KD'],
        'snares': ['SNARE-', 'SNR-', 'Snare-', 'snare-', '-SD', 'EQ-SD'],
        'hihats': ['HHats-', 'HH-', 'hihat-', 'HIHAT-', 'Hats-', '-PDL', 'Shack-'],
        'perc': ['FLAM', 'RIMSHOT', 'SSTICK', 'BELL-', 'Tom-', 'TOM-', 'Rim-', 'Drag-', 'TFlams'],
        'crashes': ['Crash-', 'CRASH-', 'Splash-', 'crash-', 'Ride-', 'Rbell-', 'chk-', 'Chk-'],
    }

    # Create crash directory if needed
    Path("crashes").mkdir(exist_ok=True)

    # Find all WAV files
    wav_files = list(source_dir.glob("**/*.wav"))
    print(f"Found {len(wav_files)} WAV files")

    stats = {cat: 0 for cat in categories.keys()}
    stats['other'] = 0

    for wav_file in wav_files:
        filename = wav_file.name
        categorized = False

        # Check each category
        for category, patterns in categories.items():
            for pattern in patterns:
                if pattern in filename:
                    # Copy to category folder
                    dest = Path(category) / filename
                    shutil.copy2(wav_file, dest)
                    stats[category] += 1
                    categorized = True
                    break
            if categorized:
                break

        if not categorized:
            stats['other'] += 1
            # print(f"Uncategorized: {filename}")

    # Print stats
    print("\n=== Organization Complete ===")
    for category, count in stats.items():
        print(f"{category:12s}: {count:3d} samples")

    total = sum(stats.values())
    print(f"{'TOTAL':12s}: {total:3d} samples")

if __name__ == "__main__":
    organize_samples()

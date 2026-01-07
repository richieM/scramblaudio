#!/usr/bin/env python3
"""
Test effects integration with scramblaudio v2

Generates a complete beat with effects applied
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scramblaudio_v2.core.sample_bank import SampleBank
from scramblaudio_v2.core.rhythm import euclidean_rhythm, pattern_to_onset_times
from scramblaudio_v2.core.arrangement import Section, Arrangement
from scramblaudio_v2.core.renderer import Renderer
from scramblaudio_v2.core.effects import (
    EffectsChain,
    create_ambient_chain,
    create_distorted_chain,
    create_lo_fi_chain,
    create_clean_chain
)


def main():
    print("=" * 60)
    print("SCRAMBLAUDIO V2 - EFFECTS TEST")
    print("=" * 60)

    # Load samples
    print("\n1. Loading samples...")
    bank = SampleBank()
    bank.load_directories({
        'kick': '../samples/kicks/',
        'snare': '../samples/snares/',
        'hihat': '../samples/hihats/',
    }, extract_features=False)  # Skip features for speed

    print(f"   Loaded {bank}")

    # Create arrangement with effects per section
    print("\n2. Creating arrangement...")
    sections = [
        Section('intro', bars=2, bpm=140,
               instruments=['kick'],
               effects_params={'kick': 'clean'}),

        Section('verse', bars=4, bpm=140,
               instruments=['kick', 'snare', 'hihat'],
               effects_params={
                   'kick': 'clean',
                   'snare': 'distorted',
                   'hihat': 'lo_fi'
               }),

        Section('chorus', bars=4, bpm=140,
               instruments=['kick', 'snare', 'hihat'],
               effects_params={
                   'kick': 'clean',
                   'snare': 'ambient',
                   'hihat': 'ambient'
               }),
    ]

    arr = Arrangement(sections)
    print(arr.visualize())

    # Generate rhythms
    print("\n3. Generating rhythms...")
    kick_pattern = euclidean_rhythm(3, 8)
    snare_pattern = euclidean_rhythm(5, 13)
    hihat_pattern = euclidean_rhythm(7, 16)

    from scramblaudio_v2.core.rhythm import visualize_pattern
    print("   " + visualize_pattern(kick_pattern, "Kick"))
    print("   " + visualize_pattern(snare_pattern, "Snare"))
    print("   " + visualize_pattern(hihat_pattern, "Hi-hat"))

    # Render tracks
    print("\n4. Rendering tracks (dry)...")
    renderer = Renderer(sample_rate=44100)
    timeline = arr.get_timeline()

    # Simple rendering - just repeat patterns for each section
    tracks = {}

    for track_name, pattern in [('kick', kick_pattern), ('snare', snare_pattern), ('hihat', hihat_pattern)]:
        samples = bank.get_samples(track_name)
        if not samples:
            print(f"   Warning: No {track_name} samples")
            continue

        onset_times = pattern_to_onset_times(pattern, bpm=140)

        # Render each section
        section_audio = []
        for entry in timeline:
            duration = entry['duration']

            # Repeat pattern to fill duration
            num_repeats = int(duration * 140 / 60 / (len(pattern) / 8)) + 1

            audio = renderer.render_pattern(
                pattern * num_repeats,
                samples,
                onset_times * num_repeats,
                duration
            )
            section_audio.append(audio)

        # Concatenate sections
        import numpy as np
        tracks[track_name] = np.concatenate(section_audio)

    print(f"   Rendered {len(tracks)} tracks")

    # Create effects chains
    print("\n5. Creating effects chains...")
    effects_presets = {
        'clean': create_clean_chain(),
        'ambient': create_ambient_chain(),
        'distorted': create_distorted_chain(),
        'lo_fi': create_lo_fi_chain(),
    }

    for name, chain in effects_presets.items():
        print(f"   {name:12s}: {chain}")

    # Apply effects to tracks
    print("\n6. Applying effects...")
    effects_chains = {
        'kick': effects_presets['clean'],
        'snare': effects_presets['distorted'],
        'hihat': effects_presets['lo_fi'],
    }

    processed_tracks = renderer.apply_track_effects(tracks, effects_chains)
    print(f"   Processed {len(processed_tracks)} tracks")

    # Mix down
    print("\n7. Mixing tracks...")
    mixed = renderer.mix_tracks(processed_tracks, normalize=True)
    print(f"   Mixed: {len(mixed)/44100:.2f} seconds")

    # Write outputs
    print("\n8. Writing outputs...")
    output_dir = Path("../output")
    output_dir.mkdir(exist_ok=True)

    # Write individual stems
    renderer.write_stems(processed_tracks, str(output_dir / "stems_fx"))

    # Write mix
    renderer.write_wav(mixed, str(output_dir / "mix_with_effects.wav"))

    print("\n" + "=" * 60)
    print("EFFECTS TEST COMPLETE!")
    print("=" * 60)
    print(f"\nOutputs:")
    print(f"  - Stems (with FX): {output_dir / 'stems_fx'}/*.wav")
    print(f"  - Mix (with FX):   {output_dir / 'mix_with_effects.wav'}")


if __name__ == "__main__":
    main()

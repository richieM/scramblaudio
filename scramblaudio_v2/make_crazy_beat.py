#!/usr/bin/env python3
"""
CRAZY BEAT GENERATOR - Scramblaudio v2

Generates chaotic beats with:
- Polymeters (multiple time signatures at once)
- Odd time signatures (7/8, 13/16, etc.)
- Heavy effects processing
- Multiple layers
- Sample variation using semantic space
"""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from scramblaudio_v2.core.sample_bank import SampleBank
from scramblaudio_v2.core.rhythm import euclidean_rhythm, polymeter_rhythm, pattern_to_onset_times, visualize_polymeter
from scramblaudio_v2.core.semantic_space import SemanticSpace
from scramblaudio_v2.core.arrangement import Section, Arrangement
from scramblaudio_v2.core.renderer import Renderer
from scramblaudio_v2.core.effects import EffectsChain, create_ambient_chain, create_distorted_chain, create_lo_fi_chain


def create_polyrhythmic_madness():
    """Create a completely polyrhythmic beat with multiple odd meters"""

    print("🎵" * 30)
    print("SCRAMBLAUDIO V2 - CRAZY BEAT GENERATOR")
    print("🎵" * 30)

    # Load ALL the samples
    print("\n📦 Loading sample arsenal...")
    bank = SampleBank()
    bank.load_directories({
        'kick': '../samples/kicks/',
        'snare': '../samples/snares/',
        'hihat': '../samples/hihats/',
        'perc': '../samples/perc/',
        'crash': '../samples/crashes/',
    }, extract_features=True)

    print(f"   Loaded {bank}")

    # Create semantic spaces for smart sample selection
    print("\n🧠 Building semantic spaces...")
    kick_space = SemanticSpace(bank.get_samples('kick'))
    snare_space = SemanticSpace(bank.get_samples('snare'))

    # Define CRAZY polymeter patterns
    print("\n🥁 Generating polyrhythmic chaos...")

    # Section 1: Polymeter Madness
    meters_intro = [
        (3, 7),   # Kick - 3 hits in 7 steps
        (5, 11),  # Snare - 5 hits in 11 steps
        (7, 13),  # Hi-hat - 7 hits in 13 steps
    ]

    # Section 2: Even Crazier
    meters_verse = [
        (5, 13),  # Kick
        (7, 16),  # Snare
        (11, 23), # Hi-hat - VERY odd
        (3, 8),   # Percussion
    ]

    # Section 3: Absolute Chaos
    meters_chaos = [
        (8, 17),  # Kick
        (13, 21), # Snare
        (5, 9),   # Hi-hat
        (7, 15),  # Perc 1
        (4, 11),  # Perc 2
    ]

    # Generate patterns
    intro_patterns = polymeter_rhythm(meters_intro, bars=2)
    verse_patterns = polymeter_rhythm(meters_verse, bars=2)
    chaos_patterns = polymeter_rhythm(meters_chaos, bars=2)

    # Visualize one section
    print("\n   Verse polymeter (first 100 steps):")
    labels = {0: "Kick", 1: "Snare", 2: "Hi-hat", 3: "Perc"}
    # Truncate for display
    truncated = {k: v[:100] for k, v in verse_patterns.items()}
    print(visualize_polymeter(truncated, labels))

    # Create arrangement with EXTREME effects
    print("\n🎼 Building arrangement...")

    sections = [
        Section('intro', bars=2, bpm=180, time_signature=(7, 8),
               instruments=['kick', 'snare', 'hihat'],
               effects_params={
                   'kick': 'clean',
                   'snare': 'lo_fi',
                   'hihat': 'ambient'
               }),

        Section('verse', bars=4, bpm=180, time_signature=(13, 16),
               instruments=['kick', 'snare', 'hihat', 'perc'],
               effects_params={
                   'kick': 'distorted',
                   'snare': 'distorted',
                   'hihat': 'lo_fi',
                   'perc': 'ambient'
               }),

        Section('breakdown', bars=2, bpm=90, time_signature=(5, 8),
               instruments=['perc', 'crash'],
               effects_params={
                   'perc': 'ambient',
                   'crash': 'ambient'
               }),

        Section('chaos', bars=4, bpm=220, time_signature=(17, 16),
               instruments=['kick', 'snare', 'hihat', 'perc'],
               effects_params={
                   'kick': 'distorted',
                   'snare': 'distorted',
                   'hihat': 'distorted',
                   'perc': 'distorted'
               }),
    ]

    arr = Arrangement(sections)
    print(arr.visualize())

    # Render each track with varying samples
    print("\n🔊 Rendering chaotic audio...")
    renderer = Renderer(sample_rate=44100)
    timeline = arr.get_timeline()

    tracks = {}

    # INTRO - use intro patterns
    def render_crazy_track(track_name, section_patterns_list, bpms, category_name=None):
        """Render a track with different patterns per section"""
        if category_name is None:
            category_name = track_name

        samples = bank.get_samples(category_name)
        if not samples:
            print(f"   ⚠️  No {category_name} samples")
            return None

        # Create semantic space for this category
        if len(samples) > 1:
            space = SemanticSpace(samples)
        else:
            space = None

        section_audios = []

        for section_idx, (patterns_dict, bpm) in enumerate(zip(section_patterns_list, bpms)):
            # Get pattern for this track
            if track_name == 'kick':
                pattern = patterns_dict.get(0, [])
            elif track_name == 'snare':
                pattern = patterns_dict.get(1, [])
            elif track_name == 'hihat':
                pattern = patterns_dict.get(2, [])
            elif track_name == 'perc':
                pattern = patterns_dict.get(3, [])
            elif track_name == 'crash':
                # Generate simple pattern for crash
                pattern = euclidean_rhythm(2, 8)
            else:
                pattern = []

            if not pattern:
                # Empty section for this track
                duration = timeline[section_idx]['duration']
                section_audios.append(np.zeros(int(duration * 44100)))
                continue

            # Select samples - vary them using semantic space
            if space and len(samples) > 3:
                # Pick 3-5 different samples from different regions
                seed_sample = samples[0]
                selected_samples = space.find_similar(seed_sample, n=3, exclude_self=False)
                # Add a random one for variation
                selected_samples.append(np.random.choice(samples))
            else:
                selected_samples = samples

            # Convert pattern to onset times
            onset_times = pattern_to_onset_times(pattern, bpm=bpm, subdivision=16)

            # Render
            duration = timeline[section_idx]['duration']
            audio = renderer.render_pattern(pattern, selected_samples, onset_times, duration)
            section_audios.append(audio)

        return np.concatenate(section_audios)

    # Define which patterns to use for each section
    all_section_patterns = [
        intro_patterns,   # Section 0: intro
        verse_patterns,   # Section 1: verse
        {},              # Section 2: breakdown (will use simple patterns)
        chaos_patterns   # Section 3: chaos
    ]

    bpms = [180, 180, 90, 220]

    # Render all tracks
    print("   Rendering: kick...")
    tracks['kick'] = render_crazy_track('kick', all_section_patterns, bpms)

    print("   Rendering: snare...")
    tracks['snare'] = render_crazy_track('snare', all_section_patterns, bpms)

    print("   Rendering: hihat...")
    tracks['hihat'] = render_crazy_track('hihat', all_section_patterns, bpms)

    print("   Rendering: perc...")
    # For perc, use pattern index 3
    tracks['perc'] = render_crazy_track('perc', all_section_patterns, bpms)

    print("   Rendering: crash...")
    tracks['crash'] = render_crazy_track('crash', all_section_patterns, bpms)

    # Remove None tracks
    tracks = {k: v for k, v in tracks.items() if v is not None}

    print(f"   ✓ Rendered {len(tracks)} tracks")

    # Apply HEAVY effects
    print("\n🎛️  Applying extreme effects...")

    # Create custom heavy chains
    distorted_heavy = EffectsChain()
    distorted_heavy.add_distortion(drive_db=40.0, wet_dry_mix=0.9)
    distorted_heavy.add_compressor(threshold_db=-25.0, ratio=8.0, attack_ms=0.5, release_ms=50.0)
    distorted_heavy.add_lowpass_filter(cutoff_frequency_hz=2000.0, wet_dry_mix=0.7)
    distorted_heavy.add_reverb(room_size=0.8, damping=0.3, wet_level=0.4, wet_dry_mix=0.5)

    ambient_heavy = EffectsChain()
    ambient_heavy.add_reverb(room_size=0.95, damping=0.4, wet_level=0.6, wet_dry_mix=0.8)
    ambient_heavy.add_delay(delay_seconds=0.5, feedback=0.6, mix=0.5, wet_dry_mix=0.7)
    ambient_heavy.add_chorus(rate_hz=0.3, depth=0.5, mix=0.4, wet_dry_mix=0.6)
    ambient_heavy.add_phaser(rate_hz=0.4, depth=0.7, mix=0.5, wet_dry_mix=0.5)

    lo_fi_heavy = EffectsChain()
    lo_fi_heavy.add_lowpass_filter(cutoff_frequency_hz=3000.0, wet_dry_mix=0.8)
    lo_fi_heavy.add_distortion(drive_db=25.0, wet_dry_mix=0.6)
    lo_fi_heavy.add_chorus(rate_hz=0.2, depth=0.6, mix=0.4, wet_dry_mix=0.7)
    lo_fi_heavy.add_reverb(room_size=0.4, damping=0.8, wet_level=0.3, wet_dry_mix=0.5)

    effects_map = {
        'kick': distorted_heavy,
        'snare': distorted_heavy,
        'hihat': lo_fi_heavy,
        'perc': ambient_heavy,
        'crash': ambient_heavy,
    }

    # Apply effects
    processed_tracks = renderer.apply_track_effects(tracks, effects_map)
    print(f"   ✓ Processed {len(processed_tracks)} tracks with heavy effects")

    # Mix with dynamic levels
    print("\n🎚️  Mixing down...")
    levels = {
        'kick': 1.2,   # Boost kick
        'snare': 1.0,
        'hihat': 0.7,  # Quieter hihats
        'perc': 0.8,
        'crash': 0.6,  # Quieter crashes
    }

    mixed = renderer.mix_tracks(processed_tracks, levels=levels, normalize=True)
    print(f"   ✓ Mixed: {len(mixed)/44100:.2f} seconds of chaos")

    # Output
    print("\n💾 Writing outputs...")
    output_dir = Path("../output")
    output_dir.mkdir(exist_ok=True)

    # Write stems
    renderer.write_stems(processed_tracks, str(output_dir / "crazy_stems"))

    # Write mix
    renderer.write_wav(mixed, str(output_dir / "crazy_beat.wav"))

    print("\n" + "🎉" * 30)
    print("CRAZY BEAT COMPLETE!")
    print("🎉" * 30)
    print(f"\n📁 Outputs:")
    print(f"   • Crazy mix:  {output_dir / 'crazy_beat.wav'}")
    print(f"   • Stems:      {output_dir / 'crazy_stems'}/*.wav")
    print(f"\n🎵 Duration: {len(mixed)/44100:.1f}s")
    print(f"🥁 Tracks: {len(processed_tracks)}")
    print(f"⚡ BPM range: 90-220")
    print(f"🎼 Time signatures: 7/8, 13/16, 5/8, 17/16")
    print(f"🎛️  Effects: HEAVY distortion, reverb, delay, chorus, phaser, compression")
    print("\n🔊 Turn it up and enjoy the chaos! 🔊\n")


if __name__ == "__main__":
    create_polyrhythmic_madness()

#!/usr/bin/env python3
"""
SEMANTIC NAVIGATION DEMO - Scramblaudio v2

Demonstrates navigating through semantic audio space with sweeps,
orbits, random walks, and feature gradients.

Like the Google AI Drum Machine but for all kinds of sounds!
"""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from scramblaudio_v2.core.sample_bank import SampleBank
from scramblaudio_v2.core.rhythm import euclidean_rhythm, pattern_to_onset_times
from scramblaudio_v2.core.semantic_space import SemanticSpace
from scramblaudio_v2.core.semantic_automation import SemanticPath, LFO
from scramblaudio_v2.core.arrangement import Section, Arrangement
from scramblaudio_v2.core.renderer import Renderer
from scramblaudio_v2.core.effects import create_clean_chain, create_ambient_chain
from scramblaudio_v2.utils.visualize_space import SpaceVisualizer


def create_semantic_journey():
    """Create a beat that travels through semantic space"""

    print("🎵" * 30)
    print("SEMANTIC NAVIGATION DEMO")
    print("🎵" * 30)

    # Load samples
    print("\n📦 Loading samples...")

    # Try to load from cache first (use world_sounds if available)
    cache_file = '../samples/world_sounds_cache.pkl'
    if not Path(cache_file).exists():
        cache_file = '../samples/sample_cache.pkl'

    if Path(cache_file).exists():
        print(f"   Loading from cache: {cache_file}")
        bank = SampleBank.load_cache(cache_file)
    else:
        # Load from directories
        bank = SampleBank()
        bank.load_directories({
            'kick': '../samples/kicks/',
            'snare': '../samples/snares/',
            'hihat': '../samples/hihats/',
            'perc': '../samples/perc/',
        }, extract_features=True)

        # Save cache for next time
        bank.save_cache(cache_file)

    print(f"   Loaded {bank}")

    # Create semantic spaces
    print("\n🧠 Building semantic spaces...")
    kick_samples = bank.get_samples('kick')
    snare_samples = bank.get_samples('snare')
    hihat_samples = bank.get_samples('hihat')

    if not kick_samples or not snare_samples:
        print("   ⚠️  Not enough samples. Please run test_with_samples.py first.")
        return

    kick_space = SemanticSpace(kick_samples)
    snare_space = SemanticSpace(snare_samples)
    hihat_space = SemanticSpace(hihat_samples)

    print(f"   Kick space: {kick_space}")
    print(f"   Snare space: {snare_space}")
    print(f"   Hihat space: {hihat_space}")

    # Visualize spaces
    print("\n📊 Visualizing kick semantic space...")
    print("   Computing 2D projection...")
    kick_space.compute_2d_projection(method='tsne')

    visualizer = SpaceVisualizer(width=80, height=30)
    viz = visualizer.visualize(kick_space)
    print(viz)

    # Create semantic paths for each track
    print("\n🗺️  Creating semantic paths...")

    # KICK: Linear sweep from dark to bright
    kick_start = kick_samples[0]
    kick_end = kick_samples[-1]
    kick_path_intro = SemanticPath.linear_sweep(
        kick_space, kick_start, kick_end, duration=8.0, num_steps=16
    )
    print("   ✓ Kick intro: Linear sweep")

    # KICK: Gradient sweep along brightness
    kick_path_verse = SemanticPath.gradient_sweep(
        kick_space, kick_samples[len(kick_samples)//2],
        'brightness', amount=2.0, duration=16.0, num_steps=20
    )
    print("   ✓ Kick verse: Brightness gradient")

    # SNARE: Orbit around a center sample
    snare_center = snare_samples[len(snare_samples)//2]
    snare_path = SemanticPath.orbit_path(
        snare_space, snare_center, radius=1.5, duration=16.0, revolutions=2.0
    )
    print("   ✓ Snare: Orbiting center sample")

    # Visualize the kick sweep path
    if len(kick_samples) >= 10:
        print("\n📍 Visualizing kick sweep path...")
        kick_path_samples = [kick_start] + kick_space.interpolate_path(kick_start, kick_end, 10) + [kick_end]
        viz_path = visualizer.visualize_path(kick_space, kick_path_samples)
        print(viz_path)

    # HIHAT: Random walk
    if hihat_samples:
        hihat_path = SemanticPath.random_walk_path(
            hihat_space, hihat_samples[0], duration=16.0, step_size=0.5, num_steps=30
        )
        print("   ✓ Hihat: Random walk")
    else:
        hihat_path = None

    # Generate rhythms
    print("\n🥁 Generating rhythms...")
    kick_pattern = euclidean_rhythm(4, 16)  # 4 kicks in 16 steps
    snare_pattern = euclidean_rhythm(3, 16)  # 3 snares
    hihat_pattern = euclidean_rhythm(11, 16)  # 11 hihats

    # Create arrangement
    print("\n🎼 Building arrangement...")
    sections = [
        Section('intro', bars=2, bpm=120, time_signature=(4, 4),
               instruments=['kick', 'hihat']),
        Section('verse', bars=4, bpm=120, time_signature=(4, 4),
               instruments=['kick', 'snare', 'hihat']),
    ]

    arr = Arrangement(sections)
    print(arr.visualize())

    # Render with semantic paths
    print("\n🔊 Rendering with semantic navigation...")
    renderer = Renderer(sample_rate=44100)
    timeline = arr.get_timeline()

    # Calculate onset times
    onset_times = pattern_to_onset_times(kick_pattern, bpm=120, subdivision=16)

    # INTRO (0-8 seconds) - Kick linear sweep
    print("   Rendering intro with kick sweep...")
    intro_duration = timeline[0]['duration']
    kick_intro_audio = renderer.render_pattern(
        kick_pattern, kick_samples, onset_times, intro_duration,
        semantic_path=kick_path_intro
    )

    hihat_intro_audio = renderer.render_pattern(
        hihat_pattern, hihat_samples,
        pattern_to_onset_times(hihat_pattern, bpm=120, subdivision=16),
        intro_duration,
        semantic_path=hihat_path if hihat_path else None
    )

    # VERSE (8-24 seconds) - Kick gradient, snare orbit
    print("   Rendering verse with kick gradient and snare orbit...")
    verse_duration = timeline[1]['duration']

    kick_verse_audio = renderer.render_pattern(
        kick_pattern, kick_samples, onset_times, verse_duration,
        semantic_path=kick_path_verse
    )

    snare_verse_audio = renderer.render_pattern(
        snare_pattern, snare_samples,
        pattern_to_onset_times(snare_pattern, bpm=120, subdivision=16),
        verse_duration,
        semantic_path=snare_path
    )

    hihat_verse_audio = renderer.render_pattern(
        hihat_pattern, hihat_samples,
        pattern_to_onset_times(hihat_pattern, bpm=120, subdivision=16),
        verse_duration,
        semantic_path=hihat_path if hihat_path else None
    )

    # Concatenate sections
    print("   Combining sections...")
    kick_audio = np.concatenate([kick_intro_audio, kick_verse_audio])
    snare_audio = np.concatenate([
        np.zeros(len(kick_intro_audio)),  # Silent in intro
        snare_verse_audio
    ])
    hihat_audio = np.concatenate([hihat_intro_audio, hihat_verse_audio])

    # Apply effects
    print("\n🎛️  Applying effects...")
    clean_fx = create_clean_chain()
    ambient_fx = create_ambient_chain()

    tracks = {
        'kick': kick_audio,
        'snare': snare_audio,
        'hihat': hihat_audio
    }

    effects = {
        'kick': clean_fx,
        'snare': clean_fx,
        'hihat': ambient_fx
    }

    processed_tracks = renderer.apply_track_effects(tracks, effects)

    # Mix
    print("\n🎚️  Mixing...")
    mixed = renderer.mix_tracks(processed_tracks, levels={
        'kick': 1.2,
        'snare': 1.0,
        'hihat': 0.6
    }, normalize=True)

    # Output
    print("\n💾 Writing output...")
    output_dir = Path("../output")
    output_dir.mkdir(exist_ok=True)

    renderer.write_wav(mixed, str(output_dir / "semantic_journey.wav"))
    renderer.write_stems(processed_tracks, str(output_dir / "semantic_stems"))

    # Summary
    print("\n" + "🎉" * 30)
    print("SEMANTIC NAVIGATION DEMO COMPLETE!")
    print("🎉" * 30)
    print(f"\n📁 Output:")
    print(f"   • Mix: {output_dir / 'semantic_journey.wav'}")
    print(f"   • Stems: {output_dir / 'semantic_stems'}/*.wav")
    print(f"\n🗺️  Navigation paths used:")
    print(f"   • Kick intro: Linear sweep (dark → bright)")
    print(f"   • Kick verse: Brightness gradient (+2.0 std)")
    print(f"   • Snare: Orbit (radius=1.5, 2 revolutions)")
    print(f"   • Hihat: Random walk (step_size=0.5)")
    print(f"\n⏱️  Duration: {len(mixed)/44100:.1f}s")
    print("\n🔊 Listen to hear samples evolving through semantic space! 🔊\n")


if __name__ == "__main__":
    create_semantic_journey()

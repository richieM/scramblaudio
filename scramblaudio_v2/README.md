# Scramblaudio v2

**Algorithmic beat generation engine for creating non-4/4 music**

Scramblaudio v2 is a modular Python system for generating complex rhythmic music using:
- **Euclidean rhythms** - mathematically distributed hit patterns
- **Polymeter/polyrhythm** - multiple time signatures running simultaneously
- **Semantic audio space** - MIR features for intelligent sample selection
- **Song structure** - verse/chorus/etc with different instruments per section

## Features

### Core Capabilities

- 🥁 **Euclidean Rhythm Generator** - Create evenly-distributed rhythmic patterns
- 🎵 **Polymeter Engine** - Multiple rhythms with different cycle lengths
- 🎼 **Arrangement System** - Build complete song structures with sections
- 🔊 **Sample Bank** - Load and organize samples with automatic feature extraction
- 🌈 **Semantic Space** - Navigate samples by timbral similarity
- 🎚️ **Audio Renderer** - Mix tracks and export stems

### Design Philosophy

- **Offline processing** - No real-time constraints, focus on quality
- **Deterministic** - Same parameters = same output
- **Modular** - Use only what you need
- **Extensible** - Easy to add new features

## Installation

```bash
# Required
pip install numpy scipy

# Recommended for full MIR features
pip install librosa

# Optional for development
pip install essentia-tensorflow  # Advanced audio analysis
```

## Quick Start

```python
from scramblaudio_v2.core import *

# Generate a euclidean rhythm
pattern = euclidean_rhythm(hits=5, steps=13)
# Result: [1,0,0,1,0,1,0,1,0,1,0,0,0]

# Create polymeter (multiple rhythms simultaneously)
meters = [
    (3, 8),   # Kick: 3 hits in 8 steps
    (5, 13),  # Snare: 5 hits in 13 steps
    (7, 16),  # Hi-hat: 7 hits in 16 steps
]
patterns = polymeter_rhythm(meters, bars=1)

# Build song arrangement
arr = create_simple_arrangement([
    ('intro', 4, ['kick']),
    ('verse', 8, ['kick', 'snare', 'hihat']),
    ('chorus', 8, 'all'),
], bpm=140)

print(arr.visualize())
```

## Architecture

```
scramblaudio_v2/
├── core/
│   ├── sample_bank.py      # Load samples, compute MIR features
│   ├── rhythm.py            # Euclidean + polymeter generators
│   ├── semantic_space.py    # Feature-based sample navigation
│   ├── arrangement.py       # Song structure (intro/verse/chorus)
│   └── renderer.py          # Assemble audio + write files
├── utils/
│   └── features.py          # MIR feature extraction
├── interface/
│   └── (future: CLI, GUI, etc.)
└── example.py               # Usage examples
```

## Usage Examples

### 1. Euclidean Rhythms

```python
from scramblaudio_v2.core.rhythm import euclidean_rhythm, visualize_pattern

# Standard rock beat (3 hits in 8 steps)
pattern = euclidean_rhythm(3, 8)
print(visualize_pattern(pattern, "Kick"))
# Output: x . . x . . x .

# Cuban tresillo (5 hits in 8 steps)
pattern = euclidean_rhythm(5, 8)
print(visualize_pattern(pattern, "Snare"))
# Output: x . x x . x x .

# Odd meter (5 hits in 13 steps)
pattern = euclidean_rhythm(5, 13)
print(visualize_pattern(pattern, "Perc"))
# Output: x . . x . x . x . x . . .
```

### 2. Polymeter/Polyrhythm

```python
from scramblaudio_v2.core.rhythm import polymeter_rhythm, visualize_polymeter

meters = [
    (3, 8),   # Kick
    (5, 13),  # Snare
    (7, 16),  # Hi-hat
]

patterns = polymeter_rhythm(meters, bars=2)
labels = {0: "Kick", 1: "Snare", 2: "Hi-hat"}

print(visualize_polymeter(patterns, labels))
# Shows all three rhythms aligned
```

### 3. Song Arrangement

```python
from scramblaudio_v2.core.arrangement import Section, Arrangement

sections = [
    Section('intro', bars=4, bpm=120,
           instruments=['kick']),

    Section('verse', bars=8, bpm=120, time_signature=(7, 8),
           instruments=['kick', 'snare', 'hihat'],
           rhythm_params={
               'kick': {'hits': 3, 'steps': 7},
               'snare': {'hits': 5, 'steps': 13},
           }),

    Section('chorus', bars=8, bpm=140,
           instruments='all',
           semantic_params={
               'bass': {'brightness': 0.3},
               'lead': {'brightness': 0.8},
           })
]

arr = Arrangement(sections)
print(arr.visualize())
```

### 4. Sample Bank with MIR Features

```python
from scramblaudio_v2.core.sample_bank import SampleBank

# Load samples and extract features
bank = SampleBank()
bank.load_directories({
    'kicks': './samples/kicks/',
    'snares': './samples/snares/',
    'hihats': './samples/hihats/',
})

# Get random sample from category
kick = bank.get_random_sample('kicks')
print(kick.features)
# {'brightness': 1234.5, 'noisiness': 0.23, 'energy': 0.85, ...}

# Save for faster loading next time
bank.save_cache('my_samples.pkl')

# Load from cache
bank = SampleBank.load_cache('my_samples.pkl')
```

### 5. Semantic Space Navigation

```python
from scramblaudio_v2.core.semantic_space import SemanticSpace

# Create semantic space from samples
samples = bank.get_samples('kicks')
space = SemanticSpace(samples)

# Find similar samples
similar = space.find_similar(samples[0], n=5)

# Find samples in a region of feature space
bright_samples = space.find_in_region(
    center_features={'brightness': 0.8, 'noisiness': 0.3},
    radius=0.5,
    n=10
)

# Get random sample weighted by preferences
sample = space.get_random_weighted({
    'brightness': 0.7,  # Prefer brighter sounds
    'energy': 0.9,      # High energy
})

# Create smooth path between two samples
path = space.interpolate_path(samples[0], samples[-1], steps=8)
```

### 6. Audio Rendering

```python
from scramblaudio_v2.core.renderer import Renderer

renderer = Renderer(sample_rate=44100)

# Render a pattern with samples
pattern = euclidean_rhythm(5, 13)
onset_times = pattern_to_onset_times(pattern, bpm=140)
samples = bank.get_samples('kicks')

audio = renderer.render_pattern(
    pattern=pattern,
    samples=samples,
    onset_times=onset_times,
    duration=4.0
)

# Write to file
renderer.write_wav(audio, 'output/kick_track.wav')

# Render multiple tracks and mix
tracks = {
    'kick': kick_audio,
    'snare': snare_audio,
    'hihat': hihat_audio,
}

mixed = renderer.mix_tracks(tracks, normalize=True)
renderer.write_wav(mixed, 'output/mix.wav')

# Or write stems separately
renderer.write_stems(tracks, 'output/stems/')
```

## Complete Workflow Example

```python
from scramblaudio_v2.core import *

# 1. Load samples
bank = SampleBank()
bank.load_directories({
    'kick': './samples/kicks/',
    'snare': './samples/snares/',
})

# 2. Create arrangement
arr = create_simple_arrangement([
    ('intro', 4, ['kick']),
    ('verse', 8, ['kick', 'snare']),
], bpm=140)

# 3. Generate rhythms for each section
kick_pattern = euclidean_rhythm(3, 8)
snare_pattern = euclidean_rhythm(5, 13)

# 4. Create semantic spaces
kick_space = SemanticSpace(bank.get_samples('kick'))
snare_space = SemanticSpace(bank.get_samples('snare'))

# 5. Render audio
renderer = Renderer()

# ... (build track_data with patterns and samples per section)

tracks = renderer.render_arrangement(arr, track_data)
mixed = renderer.mix_tracks(tracks)
renderer.write_wav(mixed, 'output/my_track.wav')
```

## MIR Features

The feature extraction module computes:

- **brightness**: Spectral centroid (timbral brightness)
- **noisiness**: Spectral flatness (noise-like vs tonal)
- **energy**: RMS energy
- **zcr**: Zero-crossing rate (roughness)
- **bandwidth**: Spectral bandwidth
- **rolloff**: Spectral rolloff point
- **mfcc**: 13 MFCCs (timbral texture)
- **onset_strength**: Rhythmic character
- **tempo**: Estimated tempo (if long enough)

## Roadmap

### v2.0 (Current)
- ✅ Core engine
- ✅ Euclidean rhythms
- ✅ Polymeter support
- ✅ Song arrangement
- ✅ MIR features
- ✅ Semantic space navigation
- ✅ Audio rendering

### v2.1 (Next)
- [ ] CLI interface
- [ ] MIDI export
- [ ] Integration with original transformations (Reverse, Syncopate, etc.)
- [ ] More sophisticated sample selection algorithms
- [ ] Groove templates

### v2.2 (Future)
- [ ] OSC/MIDI input for semi-real-time control
- [ ] Web-based GUI
- [ ] Pattern evolution using scramblaudio transformations
- [ ] Machine learning for rhythm generation
- [ ] Ableton Live integration

## Design Decisions

### Why Offline?
Real-time audio is complex and introduces constraints. By focusing on offline generation, we can:
- Use pure Python (no C extensions needed)
- Do heavy MIR analysis
- Iterate on parameters easily
- Generate high-quality output

### Why Deterministic?
Same inputs → same outputs makes the tool:
- Reproducible
- Debuggable
- Suitable for composition workflows
- Easy to version control parameters

### Why Modular?
- Use only what you need
- Easy to understand each piece
- Simple to extend or replace components
- Good for learning algorithmic composition

## Contributing

The project is designed to be extended:

1. **New rhythm generators** - Add to `rhythm.py`
2. **New transformations** - Port from original scramblaudio
3. **New features** - Extend `features.py`
4. **New navigation modes** - Extend `semantic_space.py`
5. **Interfaces** - Add to `interface/`

## License

MIT

## Credits

- Original scramblaudio concept and transformations
- Euclidean rhythm algorithm by Bjorklund
- Statistical feedback (wchoose/statchoose) by Larry Polansky / David Kant
- MIR features via librosa

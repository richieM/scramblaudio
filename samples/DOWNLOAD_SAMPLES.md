# Downloading Samples from Freesound

This guide explains how to download 10,000+ diverse audio samples using the Freesound API.

## Setup

### 1. Get a Freesound API Key

1. Register at [Freesound.org](https://freesound.org/)
2. Get your API key from [https://freesound.org/apiv2/apply/](https://freesound.org/apiv2/apply/)
3. Set the environment variable:

```bash
export FREESOUND_API_KEY="your_api_key_here"
```

### 2. Install Dependencies

```bash
cd /Users/mendelbot/Code/scramblaudio
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Download Full Diverse Library (10k samples)

```bash
cd scramblaudio_v2/utils
python sample_downloader.py 10000
```

This will download ~10,000 samples across 40+ categories including:

**Drums & Percussion (20%)**
- Kicks, snares, hi-hats, cymbals, toms, percussion, claps

**Tonal/Musical (15%)**
- Bass, synth, keys, guitar, strings, brass

**Effects & Atmosphere (15%)**
- Risers, impacts, noise, FX, drones

**Nature & Environment (20%)**
- Birds, animals, water, wind, wood, metal, glass, stone

**Urban & Mechanical (15%)**
- Doors, machines, beeps, clicks, vehicles, tools

**Human & Voice (10%)**
- Vocals, breath, footsteps

**Miscellaneous (5%)**
- Weird sounds, toys, food

### Download Specific Amount

```bash
python sample_downloader.py 5000   # Download 5k samples
python sample_downloader.py 1000   # Download 1k samples
```

### Download Specific Category Only

```python
from sample_downloader import FreesoundDownloader

downloader = FreesoundDownloader()

# Download 100 kick samples
downloader.download_category('kick', 'kick drum oneshot', count=100, duration_range=(0.1, 2.0))

# Download 200 bird sounds
downloader.download_category('bird', 'bird chirp tweet oneshot', count=200, duration_range=(0.1, 5.0))
```

## Output Structure

Samples are organized as:

```
samples/freesound/
├── metadata.json                 # Overall metadata
├── kick/
│   ├── 12345_kick_01.ogg
│   ├── 12345_kick_01.json       # Individual metadata
│   └── ...
├── snare/
│   └── ...
├── bird/
│   └── ...
└── ...
```

## File Formats

- Downloaded as **OGG** format (high-quality preview)
- Can be converted to WAV if needed
- Librosa and soundfile handle OGG natively

## Feature Extraction

After downloading, extract MIR features:

```python
from scramblaudio_v2.core import SampleBank

bank = SampleBank()
bank.load_directories({
    'kick': '../samples/freesound/kick/',
    'snare': '../samples/freesound/snare/',
    'bird': '../samples/freesound/bird/',
    # ... add all categories
}, extract_features=True)

# This will cache features as .pkl files for fast loading
bank.save_cache('../samples/freesound/sample_cache.pkl')
```

## Rate Limiting

The downloader automatically rate-limits to 10 requests/second to be respectful to Freesound's API.

Downloading 10k samples will take approximately 20-30 minutes depending on file sizes and network speed.

## License Information

Each sample includes metadata with license info. Most Freesound samples are Creative Commons licensed. Always check `license` field in the metadata JSON files.

## Tips

- Download overnight for large batches
- Check `metadata.json` to see what's already downloaded
- Restart if interrupted - it won't re-download existing samples
- Prefer shorter samples (< 5s) for one-shots
- Longer samples work for drones and atmosphere

## Converting to WAV (Optional)

If you need WAV files:

```bash
for file in samples/freesound/*/*.ogg; do
    ffmpeg -i "$file" "${file%.ogg}.wav"
done
```

Or use librosa/soundfile in Python (they read OGG natively).

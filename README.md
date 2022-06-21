# scramblaudio
Audio remixer

## Diff files and what they do
- scramblaudio.py
  So I think this is the original guy, which I wrote like in 2016-7 as a response to the scramblaudio midi stuff that I was doing at WACM.

  Input: some pre-recorded .wav file

  Process: applies semi-random (see statchoose / wchoose) to the audio to scramble it, including reverse, syncopate, rotate, scrambleChunks, with diff probabilities applied to choosing each of those. Runs over x steps, then outputs .wav. It's destructive, so f(x) -> x+1 etc...

  Output: wav file


- euroVibes.py:
  Sept/Oct 2021, done for cachedMedia open call. Pretty sure that it's just reading in the inputAudio, using librosa to calculate offsets, and then randomly choosing audio and a random sampleLength and then glueing it all together. Not very logical. I also think that there was a version where I was steadily decreasing the sampleLength so that it got increasingly glitchier. Possibly not as interesting as I thought.

  I eventually used this to generate some audio and then arrange it all together in Ableton for my piece.

  Output: .wav file

- crazyMidi.py:

  Prototype for writing midi to a file. It's currently using rhythm2Pitch as a function for deciding timing.
  Parameters look smth like:
  `MyMIDI.addNote(track, channel, 60, time, duration, volume)`

  Good schematic for understanding how to write midi to file and tracks etc

- r2p.py

  Same as crazyMidi.py

- infinityPool.py

- watMidi.py

- timeHorizons.py

  some Greek stuff...

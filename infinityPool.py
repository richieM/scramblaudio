'''
Okay I'm starting to feel a bit overwhelmed with scramblaudio dreams
so I wanna scope things down

A nice goal for this little swatch is

To time-align samples based on some tempo / MIDI file.
I could even be playing random stuff, I just wanna play samples
on a beat.

So, to do that, I need:
- A collection or list of samples
- Some analysis of those samples, which could just be a library or list of which samples I have and a time of the first onset or whatever, that would be fine
- Some MIDI timing, along with tracks and stuff maybe? Like a track for snare, a track for bass, and a track for words or whatever
- A runner, which "renders" the MIDI with the samples and writes to disk

See what code I already have that helps me do this
'''

import librosa
from midiutil import MIDIFile

from pathlib import Path
import copy
import numpy as np
import os
import pickle
import random
import soundfile as sf
from scipy import signal
import string
from math import exp
from collections import defaultdict

WAV_DIR = "./wavs/nonverbalVocalization/"
SAMPLE_RATE = 44100
allOfEm = defaultdict(dict)
hopLength = 512
OUTPUT_PATH = "./outputAudio/infinityPool/"

def readInFilesAndGetOnsets(WAV_DIR):
    ### Read through directory to pick all wavs

    for root, dirs, files in os.walk(WAV_DIR):
        path = root.split(os.sep)
        print((len(path) - 1) * '---', os.path.basename(root))
        for currFile in files:
            ##print(len(path) * '---', currFile)
            if currFile.endswith(".wav"):
                fullPath = "%s/%s" % (root, currFile)

                audioType = fullPath.split('/')[3]

                y, sr = librosa.load(fullPath)

                newFileName = currFile.replace(" ", "_")
                currData = {"rawAudio": y,
                            "sr": sr,
                            "onsets": librosa.onset.onset_detect(y=y, sr=sr, hop_length=hopLength)
                            }

                allOfEm[audioType][newFileName] = currData

                print("%s imported!" % currFile)

    return allOfEm

def createAudioFromSamples(allOfEm, startingAudioLengthSeconds=0.1, howManyLoopies=100):
    """
    Exp 1:
    - Grab random onset (remember to multipy by hop_length, right?)
    - grab a certain width
    - Optional: window it
    - Optional: randomly perform a transformation (maybe)
    - Glue it back together
    - Write to a track
    """
    ##import pdb; pdb.set_trace()
    origAudioSampleWidth = int(startingAudioLengthSeconds * SAMPLE_RATE)
    someNoise = np.array(0)

    for i in range(howManyLoopies):
        if i % 10 == 9:
            print("%d -- %d samples" % (i, len(someNoise)))
        #audioSampleWidth = int(origAudioSampleWidth * (howManyLoopies - i) / howManyLoopies)
        audioSampleWidth = origAudioSampleWidth

        # Choose a random file
        currSpecificAudio = random.choice(list(allOfEm.keys()))
        howManyChunks = len(allOfEm[currSpecificAudio]['onsets'])
        currSignal = allOfEm[currSpecificAudio]['rawAudio']

        randomNum = random.randrange(0, howManyChunks)
        currOnsetStartPoint = allOfEm[currSpecificAudio]['onsets'][randomNum] * hopLength

        #currAudioSampleWidth = int(audioSampleWidth * random.random())
        currAudioSampleWidth = audioSampleWidth

        begPoint = currOnsetStartPoint - int(currAudioSampleWidth/2)
        begPoint = begPoint if begPoint > 0 else 0

        endPoint = currOnsetStartPoint + int(currAudioSampleWidth/2)
        endPoint = len(currSignal) if endPoint > len(currSignal) else endPoint

        newAudioChunk = currSignal[int(begPoint): int(endPoint)]
        currWindow = signal.windows.hamming(len(newAudioChunk))
        newAudioChunkWindowApplied = np.multiply(newAudioChunk, currWindow)
        someNoise = np.append(someNoise, newAudioChunkWindowApplied)

    randomFileName = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))

    sf.write(OUTPUT_PATH + randomFileName + ".wav", someNoise, SAMPLE_RATE)
    print("%s written!" % randomFileName)

    return someNoise

def createMIDI():
    '''
    So, I guess this generates some MIDI data?
    Depending on what the instrument type (or whatever) is, there
    doesnt even need to be pitch info, it can just be an on and off, right? And that is a signal for the sample to be written

    Would be cool to create a DSL for specifying midi patterns, and then I can just write an engine to convert that to a MIDIFile

    What might that look like?
    {"Track1" : {}}
    '''
    degrees  = [60, 62, 64, 65, 67, 69, 71, 72]  # MIDI note number
    track    = 0
    channel  = 0
    time     = 0    # In beats
    duration = 1    # In beats
    tempo    = 60   # In BPM
    volume   = 100  # 0-127, as per the MIDI standard

    MyMIDI = MIDIFile(2)  # One track, defaults to format 1 (tempo track is created
                           # automatically)
    MyMIDI.addTempo(track, time, tempo)

    for i, pitch in enumerate(degrees):
        MyMIDI.addNote(track, channel, pitch, time + i, duration, volume)

    track = 1
    degrees.reverse()

    MyMIDI.addTempo(track, time, tempo)

    for i, pitch in enumerate(degrees):
        MyMIDI.addNote(track, channel, pitch, time + i, duration, volume)

    with open("major-scale.mid", "wb") as output_file:
         MyMIDI.writeFile(output_file)

def createAudioR2P(allOfEm, audioType):
    rp2Fxn = lambda x : 1/exp(0.13*x)
    someNoise = np.array(0)
    startTime = 0

    for i in range(400):
        # Pick a random sample
        currSpecificAudio = allOfEm[audioType][random.choice(list(allOfEm[audioType].keys()))]

        # How long this sample will play
        currSampleDurationInSamples = rp2Fxn(startTime) * currSpecificAudio['sr']

        # Get first onset
        # TODO -- experiment -- first onset vs random onset?
        # firstOnsetHopWindow = currSpecificAudio['onsets'][0]
        randomOnsetHopWindow = random.choice(currSpecificAudio['onsets'])

        # Get that audio dawgio
        begPoint = hopLength*randomOnsetHopWindow
        endPoint = begPoint + currSampleDurationInSamples
        endPoint = len(currSpecificAudio['rawAudio']) if endPoint > len(currSpecificAudio['rawAudio']) else endPoint
        datAudio = currSpecificAudio['rawAudio'][int(begPoint):int(endPoint)]
        print("%d -- %f samples" % (i, (endPoint - begPoint)))

        someNoise = np.append(someNoise, datAudio)

        startTime += rp2Fxn(startTime)

    randomFileName = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))

    sf.write(OUTPUT_PATH + randomFileName + ".wav", someNoise, SAMPLE_RATE)
    print("%s written!" % randomFileName)

    return someNoise

if __name__ == "__main__":
    from pathlib import Path

    #savedPicklePath = "./audioPickles/nonverbalVocalization.p"
    savedPicklePath = "./audioPickles/nonverbalVocalizationByType.p"

    pastAudioPickle = Path(savedPicklePath)
    if pastAudioPickle.is_file():
        print("Pickle exists -- read in audio")
        with open(savedPicklePath, "rb") as handle:
            allDemAudio = pickle.load(handle)
    else:
        print("No pickle -- reading in and saving audio")
        allDemAudio = readInFilesAndGetOnsets(WAV_DIR)
        import pdb; pdb.set_trace()
        with open(savedPicklePath, "wb") as handle:
            pickle.dump(allDemAudio, handle, protocol=pickle.HIGHEST_PROTOCOL)

    '''
    x = createAudioFromSamples(allDemAudio, startingAudioLengthSeconds=0.2, howManyLoopies=100)
    '''
    #scramblaudio(x)

    x = createAudioR2P(allDemAudio, audioType='yawning')

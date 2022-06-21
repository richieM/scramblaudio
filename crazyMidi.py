from midiutil import MIDIFile
from math import exp
import random
import string

def createMIDI():
    '''
    So, I guess this generates some MIDI data?
    Depending on what the instrument type (or whatever) is, there
    doesnt even need to be pitch info, it can just be an on and off, right? And that is a signal for the sample to be written

    Would be cool to create a DSL for specifying midi patterns, and then I can just write an engine to convert that to a MIDIFile
    ** Check out TidalCycles stuff and how they do it....

    What might that look like?
    {"Track1" : {}}
    '''

    rp2Fxn = lambda x : 1/exp(1.5*x)

    track    = 0
    pitch    = 60
    channel  = 0
    time     = 0    # In beats
    # duration = 1    # In beats
    tempo    = 120   # In BPM
    volume   = 100  # 0-127, as per the MIDI standard

    MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                           # automatically)
    MyMIDI.addTempo(track, time, tempo)

    import pdb; pdb.set_trace()

    for i in range(100):
        duration = rp2Fxn(time)
        MyMIDI.addNote(track, channel, 60, time, duration, volume)
        time += duration

    import pdb; pdb.set_trace()

    '''
    offset = time

    for i in reversed(range(100)):
        duration = rp2Fxn(time)
        MyMIDI.addNote(track, channel, 60, time + offset, duration, volume)
        time += duration
    '''

    with open("r2p_v2.mid", "wb") as output_file:
         MyMIDI.writeFile(output_file)

def createGlitchyMIDI():
    '''
    Glitchy version
    '''

    track    = 0
    pitch    = 60
    channel  = 0
    time     = 0    # In beats
    # duration = 1    # In beats
    tempo    = 120   # In BPM
    volume   = 100  # 0-127, as per the MIDI standard

    MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                           # automatically)
    MyMIDI.addTempo(track, time, tempo)

    howManyBeats = 32
    maxNumSubdivisions = 11
    probabilityNoteHits = 0.7
    howManyDiffSamples = 4

    for i in range(howManyBeats):
        numBeatsInMeasure = int(random.random() * (maxNumSubdivisions+1))
        for numBeat in range(numBeatsInMeasure):
            stepDuration = 1. / numBeatsInMeasure
            if random.random() < probabilityNoteHits:
                currPitch = pitch + int(random.random()*howManyDiffSamples)
                MyMIDI.addNote(track, channel, currPitch, time, stepDuration, volume)

            time += stepDuration

    randomFileName = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6)) + ".mid"

    with open("crazyMidiOutputs/" + randomFileName, "wb") as output_file:
         MyMIDI.writeFile(output_file)

def timeSignatureOverlap():
    track    = 0
    pitch    = 60
    channel  = 0
    time     = 0    # In beats
    # duration = 1    # In beats
    tempo    = 120   # In BPM
    volume   = 100  # 0-127, as per the MIDI standard

    MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                           # automatically)
    MyMIDI.addTempo(track, time, tempo)

    howManyBeats = 16
    howManyDiffSamples = 4
    currPitch = 60

    for i in range(howManyBeats):
        time = i
        for count, numSubdivisions in enumerate([3,4,5,7]):
            stepDuration = 1. / numSubdivisions
            for howMany in range(numSubdivisions):
                MyMIDI.addNote(track, channel, currPitch+count, time, stepDuration, volume)
                time += stepDuration

    randomFileName = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6)) + ".mid"

    with open("crazyMidiOutputs/overlap_" + randomFileName, "wb") as output_file:
         MyMIDI.writeFile(output_file)


if __name__ == "__main__":
    #createMIDI()
    #createGlitchyMIDI()
    timeSignatureOverlap()

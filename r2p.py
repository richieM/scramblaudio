from midiutil import MIDIFile
from math import exp

def createMIDI():
    '''
    So, I guess this generates some MIDI data?
    Depending on what the instrument type (or whatever) is, there
    doesnt even need to be pitch info, it can just be an on and off, right? And that is a signal for the sample to be written

    Would be cool to create a DSL for specifying midi patterns, and then I can just write an engine to convert that to a MIDIFile

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

    for i in range(100):
        duration = rp2Fxn(time)
        MyMIDI.addNote(track, channel, 60, time, duration, volume)
        time += duration

    '''
    offset = time

    for i in reversed(range(100)):
        duration = rp2Fxn(time)
        MyMIDI.addNote(track, channel, 60, time + offset, duration, volume)
        time += duration
    '''

    with open("r2p_v2.mid", "wb") as output_file:
         MyMIDI.writeFile(output_file)

if __name__ == "__main__":
    createMIDI()

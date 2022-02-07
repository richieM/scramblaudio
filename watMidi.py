from midiutil import MIDIFile

"""
Broader questions include:
- For each movement, how much do I want to be defining on the pattern?
- Multiple instruments per movement?!
- What about fancy moves and stuff, do I just uh... make those probabilities?

I fear none of this has a soul to it...yet
"""

class Song:
    '''
    Song class, maybe made up of other shit
    '''
    def __init__(self, movements=[], bpm=120):
        self.movements = movements
        self.bpm = bpm

    def addMovement(self, movement):
        self.movements.append(movement)

    def print(self):
        print("Num movements: %d" % len(self.movements))
        for m in self.movements:
            m.print()

    def render(self):
        someNoise = np.array(0)
        for m in self.movements:
            currMovementAudio = m.render(self.bpm)
            someNoise = np.append(someNoise, currMovementAudio)

        return someNoise

class Movement:
    '''
    Movement of a song, like intro / verse / chorus / bridge

    TODO questions -- where do I apply a time signature and stuff, maybe in movement?
    '''
    def __init__(self, numMeasures, beatsPerMeasure=4, name="", pattern=""):
        self.numMeasures = numMeasures
        self.beatsPerMeasure = beatsPerMeasure
        self.name = name
        self.pattern = pattern

    def print(self):
        print("name: %s  numMeasures: %d  beatsPerMeasure: %d  pattern: %s" % (self.name, self.numMeasures, self.beatsPerMeasure, self.pattern))

    def render(self, bpm):
        '''
        Sooo, this actually makes audio?
        Questions include:
        - Which samples to use?
        - Do I do any fancy transformations on that audio so it's not boring AF?
        '''
        audio = np.array(0)
        oneBeatInMillis = 60 * 1000 / bpm

        for currMeasure in range(self.numMeasures):
            for i, currChar enumerate(self.pattern):
                if currChar == "x":
                    pass
                elif currChar == "_"":
                    pass
                else:
                    pass



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
    tempo    = 120   # In BPM
    volume   = 100  # 0-127, as per the MIDI standard

    MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
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

def createSongOne():
    mySong = Song()
    mySong.addMovement(Movement(numMeasures=2, beatsPerMeasure=3, name="intro", pattern="x_x"))
    mySong.addMovement(Movement(numMeasures=4, beatsPerMeasure=3, name="verse1", pattern="__x"))
    mySong.addMovement(Movement(numMeasures=4, beatsPerMeasure=4, name="chorus", pattern="_x_x"))
    mySong.addMovement(Movement(numMeasures=4, beatsPerMeasure=3, name="verse2", pattern="__x"))
    mySong.addMovement(Movement(numMeasures=4, beatsPerMeasure=4, name="chorus", pattern="_x_x"))
    mySong.addMovement(Movement(numMeasures=2, beatsPerMeasure=4, name="outtro", pattern="x_x"))
    mySong.print()

    songAudio = mySong.render()

if __name__ == "__main__":
    #createMIDI()
    createSongOne()

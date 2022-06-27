## TODO where's the prettyMIDI code?

p1 = "{2{3] 3}"
p2 = "{3{2{7} 3{5}} 5 2{4 4{3}}}"
p3 = "{4 3{6}}"
p4 = "{1 1 3{7}}"

"""
import pretty_midi
# Create a PrettyMIDI object
cello_c_chord = pretty_midi.PrettyMIDI()
# Create an Instrument instance for a cello instrument
cello_program = pretty_midi.instrument_name_to_program('Cello')
cello = pretty_midi.Instrument(program=cello_program)
# Iterate over note names, which will be converted to note number later
for note_name in ['C5', 'E5', 'G5']:
    # Retrieve the MIDI note number for this note name
    note_number = pretty_midi.note_name_to_number(note_name)
    # Create a Note instance, starting at 0s and ending at .5s
    note = pretty_midi.Note(
        velocity=100, pitch=note_number, start=0, end=.5)
    # Add it to our cello instrument
    cello.notes.append(note)
# Add the cello instrument to the PrettyMIDI object
cello_c_chord.instruments.append(cello)
# Write out the MIDI data
cello_c_chord.write('cello-C-chord.mid')
"""

patterns = [p1, p2, p3, p4]
defaultPitch = 60

import pretty_midi as pm

def recurseGrammar(pattern, currRecursiveDepth, instr, startTime, endTime, deeper=False):
    """
    Recursively parse shit!
    """
    if deeper:
        woah = "notToday"
        """
        #pattern = [1, 1, 3]
        pattern = [1, 3, 2, 2] # sum 8
        0-0.125 note,
        one var is how much space
        one is arpeggiator pattern and how many times to hit
        deeperPattern = [1, 3[5], 2, 4[7]]

        DSL as json or xml?
        noo
        """
    # deeperPattern = [1, 3[5], 2, 4[7]]

    currStartTime = startTime
    chunkTime = (endTime-startTime)/sum(pattern)

    if currRecursiveDepth > 1:
        # Return a single note at startTime
        for event in pattern:
            currEndTime = currStartTime + chunkTime*event

            # recursion!
            recurseGrammar(pattern=pattern, currRecursiveDepth=currRecursiveDepth-1, startTime=currStartTime, endTime=currEndTime, instr=instr)

            currStartTime = currEndTime
    else:
        # Apply pattern over length
        for event in pattern:
            currEndTime = currStartTime + chunkTime*event
            currNote = pm.Note(velocity=100, pitch=defaultPitch, start=currStartTime, end=currEndTime)
            instr.notes.append(currNote)
            currStartTime = currEndTime

    print("wowio recurse %d!" % currRecursiveDepth)

def somethingClever(pattern, recursiveDepth, unitLengthSecs):
    # TODO need to sort this pattern crapola
    # Takes in some stuff, maybe a pattern or schema
    myMusic = pm.PrettyMIDI()
    # Create an Instrument instance for a cello instrument
    myMusicProgram = pm.instrument_name_to_program('cello')
    instr1 = pm.Instrument(program=myMusicProgram)

    recurseGrammar(pattern=pattern, currRecursiveDepth=recursiveDepth, startTime=0, endTime=unitLengthSecs, instr=instr1)
    # deeperPatternGrammar(pattern=deeperPattern, currRecursiveDepth=recursiveDepth, startTime=0, endTime=unitLengthMillis, instr=instr1, deep=True)

    myMusic.instruments.append(instr1)

    myMusic.write("woahnow.mid")

    # import pdb; pdb.set_trace()
    return myMusic

    print("wuoh somethingClever()")

def patternLangSomethingClever(patterns):
    myMusic = pm.PrettyMIDI()

    for currPattern in patterns:
        # Create an Instrument instance for a cello instrument
        myMusicProgram = pm.instrument_name_to_program('cello')
        currInstr = pm.Instrument(program=myMusicProgram,name=currPattern['sampleLabel'])

        for i in range(currPattern['numRepeats']):
            currStartTime = currPattern['start'] + i*currPattern['unitLengthSecs']
            currEndTime = currPattern['start'] + (i+1)*currPattern['unitLengthSecs']
            recurseGrammar(pattern=currPattern['pattern'], currRecursiveDepth=currPattern['recurse'], startTime=currStartTime , endTime=currEndTime, instr=currInstr)

        myMusic.instruments.append(currInstr)

    myMusic.write("woahnow.mid")
    print("Wrote+returned midi in patternLangSomethingClever")
    # import pdb; pdb.set_trace()
    return myMusic

def badBoyMIDI(pattern, recursiveDepth, songLengthSecs):
    myMusicMIDI = somethingClever(pattern, recursiveDepth, unitLengthSecs=songLengthSecs)
    return myMusicMIDI
    return " u go gadang __ZN4TSNE31computeSquaredEuclideanDistanceEPdiiS0_"

def badBoyMIDIPatternLang(patterns):
    myMusicMIDI = patternLangSomethingClever(patterns)
    return myMusicMIDI
    return " u go gadang __ZN4TSNE31computeSquaredEuclideanDistanceEPdiiS0_"

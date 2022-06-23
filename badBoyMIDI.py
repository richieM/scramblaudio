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

def parseIntoNotes(pattern, currRecursiveDepth, instr, startTime, endTime):
    """
    Recursively parse shit!
    """
    currStartTime = startTime
    chunkTime = (endTime-startTime)/sum(pattern)

    if currRecursiveDepth > 1:
        # Return a single note at startTime
        for event in pattern:
            currEndTime = currStartTime + chunkTime*event

            parseIntoNotes(pattern=pattern, currRecursiveDepth=currRecursiveDepth-1, startTime=currStartTime, endTime=currEndTime, instr=instr)

            currStartTime = currEndTime
    else:
        # Apply pattern over length
        for event in pattern:
            currEndTime = currStartTime + chunkTime*event
            currNote = pm.Note(velocity=100, pitch=defaultPitch, start=currStartTime, end=currEndTime)
            instr.notes.append(currNote)
            currStartTime = currEndTime

    # TODO no return because it's pass by value?

    print("wowio")

def somethingClever(unitLengthMillis):
    # Takes in some stuff, maybe a pattern or schema
    """
    No way around it, this has to involve some kind of grammar or pattern pyparsing
    There could be rhythm parsing and also measure parsing and also song parsing

    A = pattern
    B = pattern
    B = pattern


    Grammar
    """
    myMusic = pm.PrettyMIDI()
    # Create an Instrument instance for a cello instrument
    myMusicProgram = pm.instrument_name_to_program('Cello')
    instr1 = pm.Instrument(program=myMusicProgram)

    #pattern = [1, 1, 3]
    pattern = [1, 3, 2, 2]

    recursiveDepth = 4
    parseIntoNotes(pattern=pattern, currRecursiveDepth=recursiveDepth, startTime=0, endTime=unitLengthMillis, instr=instr1)

    myMusic.instruments.append(instr1)

    myMusic.write("woahnow.mid")

    import pdb; pdb.set_trace()

    print("wuoh")

def badBoyMIDI():
    somethingClever(unitLengthMillis=4.000)
    return " u go gadang __ZN4TSNE31computeSquaredEuclideanDistanceEPdiiS0_"

## TODO where's the prettyMIDI code?
"""
     p1 = "{2{3] 3}"
     p2 = "{3{2{7} 3{5}} 5 2{4 4{3}}}"
     p3 = "{4 3{6}}"
     p4 = "{1 1 3{7}}"
"""
import pretty_midi as pm

def parseIntoNotes(pattern, currRecursiveDepth, instr, startTime, endTime):
    if currRecursiveDepth > 0:
        pass
    else:
        # Return a single note at startTime
        pass
    import pdb; pdb.set_trace()
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

    notes = parseIntoNotes(pattern = [1, 1, 3])
    recursiveDepth = 2

    theSum = sum(pattern)
    print("sum: %d" % theSum)



    import pdb; pdb.set_trace()

def badBoyMIDI():
    somethingClever()
    return " u go gadang __ZN4TSNE31computeSquaredEuclideanDistanceEPdiiS0_"

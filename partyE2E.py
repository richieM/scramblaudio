import pretty_midi as pm
import pyparsing as pp

def getPatterns():
     p1 = "{2{3] 3}"
     p2 = "{3{2{7} 3{5}} 5 2{4 4{3}}}"
     p3 = "{4 3{6}}"
     p4 = "{1 1 3{7}}"

     return [p1,p2,p3]

def parseIntoNotes(pattern, instr, startTime, endTime):
    import pdb; pdb.set_trace()
    print("wowio")

def poo():
    #TODO how to parse this:
    masterBPM = 140
    patterns = getPatterns()

    instruments = []

    for i in range(len(patterns)):
        instruments.append(pm.Instrument(i, name=str(i)))

    #Verse1

    startTime = 0
    coreIncrement = 10

    numTimes = 4
    for i in range(numTimes):
       endTime = startTime + coreIncrement*masterBPM

       for i in range(len(patterns)):
           parseIntoNotes(patterns[i], instruments[i], startTime, endTime)

       startTime=endTime

    import pdb; pdb.set_trace()

    print("waluigi")

#from samplesToFingerprints import samplesToFingerprints
from readInSamples import readInSamples
from badBoyMIDI import badBoyMIDI
def thursPee():
    #WAV_DIR = "./wavs/cached_media/sample_bank/arps/" #TODO
    WAV_DIR = "/Users/mendelbot/Projects/scramblaudio/wavs/nonverbalVocalization"
    samples = readInSamples(WAV_DIR)

    import pdb; pdb.set_trace()

    ## Optional: retrieve or generate patterns
    ## generate MIDI based on patterns...
    badBoyMIDI()

    print("]]]]]],,,........;;;;;;\\\\\\||||||")

if __name__ == "__main__":
    thursPee()

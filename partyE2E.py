"""
Tasks to do:
    ADSR so it doesnt clip
    not picking random clips - more intelligent audio analysis
    multiple instrs - how do i overlap audio with multiple instrs?
        might be simple if i just add over that period += in numpy or smth?

    more interesting midi stuff, with maybe a pattern and a length of meaures defined or something, along with start bar in music, and sampleRules. that could be my "Score"?
    start=0, pattern=[1,1,2], recurse=1, numRepeats, moaning
    start=0, pattern=[1,2,2], recurse=2, numRepeats=8, lipSmacking, mirFilter=???
    start=0, pattern=[1,1,2], duration=4measures, moaning
    start=0, pattern=[1,1,2], duration=4measures, moaning
    start=12, pattern=[1,1,3], duration=4measures, moaning

    midi pattern evolution, using scramblaudio...
"""

"""
dict_keys(['Rides', 'Crashes', 'Closed Hihat', 'Open Hihat', 'Percussion', 'Claps', 'Snares', '808s', 'Kicks', 'MagicalChords', 'sneezing', 'screaming', 'moaning', 'crying', 'yawning', 'tongue-clicking', 'laughing', 'lip-popping', 'throat-clearing', 'lip-smacking', 'nose-blowing', 'coughing', 'sighing', 'teeth-grinding', 'teeth-chattering', 'panting'])

TODO: what are the units for:
start
unitLengthSecs (bpm formulas)
"""



song1 = [
    #VERSE1 LOL
    {'start':0,
    'pattern': [1,1,3],
    'unitLengthSecs': 2.0,
    'recurse': 2,
    'numRepeats': 4,
    'sampleLabel':'Kicks'
    },
    {'start':0,
    'pattern': [1,2,1],
    'unitLengthSecs': 2.0,
    'recurse': 2,
    'numRepeats': 4,
    'sampleLabel':'Snares'
    },
    {'start':0,
    'pattern': [1,1,1],
    'unitLengthSecs': 2.0,
    'recurse': 2,
    'numRepeats': 4,
    'sampleLabel':'Closed Hihat'
    },
    {'start':0,
    'pattern': [5,1,1],
    'unitLengthSecs': 2.0,
    'recurse': 2,
    'numRepeats': 4,
    'sampleLabel':'MagicalChords'
    },

    # CHORUS
    {'start':8,
    'pattern': [1,3,1],
    'unitLengthSecs': 2.0,
    'recurse': 2,
    'numRepeats': 4,
    'sampleLabel':'Kicks'
    },
    {'start':8,
    'pattern': [1,2,1],
    'unitLengthSecs': 2.0,
    'recurse': 2,
    'numRepeats': 4,
    'sampleLabel':'Snares'
    },
    {'start':8,
    'pattern': [1,1,1],
    'unitLengthSecs': 2.0,
    'recurse': 2,
    'numRepeats': 4,
    'sampleLabel':'moaning'
    },
    {'start':8,
    'pattern': [1,3,1,1,1],
    'unitLengthSecs': 2.0,
    'recurse': 2,
    'numRepeats': 4,
    'sampleLabel':'MagicalChords'
    },

    # CHORUS
    {'start':16,
    'pattern': [3,1,1],
    'unitLengthSecs': 2.0,
    'recurse': 2,
    'numRepeats': 4,
    'sampleLabel':'Kicks'
    },
    {'start':16,
    'pattern': [2,1,1],
    'unitLengthSecs': 2.0,
    'recurse': 1,
    'numRepeats': 4,
    'sampleLabel':'Snares'
    },
    {'start':16,
    'pattern': [1,1,1],
    'unitLengthSecs': 2.0,
    'recurse': 1,
    'numRepeats': 4,
    'sampleLabel':'laughing'
    },
    {'start':16,
    'pattern': [1,3,1,1,1],
    'unitLengthSecs': 2.0,
    'recurse': 1,
    'numRepeats': 4,
    'sampleLabel':'MagicalChords'
    },

    # CHORUS
    {'start':24,
    'pattern': [3,1,1],
    'unitLengthSecs': 3.0,
    'recurse': 1,
    'numRepeats': 8,
    'sampleLabel':'Kicks'
    },
    {'start':24,
    'pattern': [2,1,1],
    'unitLengthSecs': 2.0,
    'recurse': 1,
    'numRepeats': 12,
    'sampleLabel':'Snares'
    },
    {'start':24,
    'pattern': [1,3,1],
    'unitLengthSecs': 1.0,
    'recurse': 1,
    'numRepeats': 24,
    'sampleLabel':'laughing'
    },
    {'start':24,
    'pattern': [1,3,1,1,1],
    'unitLengthSecs': 6.0,
    'recurse': 1,
    'numRepeats': 4,
    'sampleLabel':'Open Hihat'
    },
    {'start':24,
    'pattern': [1,3,7,1,1],
    'unitLengthSecs': 6.0,
    'recurse': 1,
    'numRepeats': 4,
    'sampleLabel':'yawning'
    },
    {'start':24,
    'pattern': [1,3,12,1,1,1,1,1,1],
    'unitLengthSecs': 6.0,
    'recurse': 1,
    'numRepeats': 4,
    'sampleLabel':'panting'
    },

    # HRM
    {'start':36,
    'pattern': [3,1,1],
    'unitLengthSecs': 1.0,
    'recurse': 2,
    'numRepeats': 4,
    'sampleLabel':'Kicks'
    },
    {'start':40,
    'pattern': [1,3,12,1,1,1,1,1,1],
    'unitLengthSecs': 3.0,
    'recurse': 1,
    'numRepeats': 6,
    'sampleLabel':'crying'
    },
    {'start':40,
    'pattern': [3,1,1,1,1],
    'unitLengthSecs': 2.0,
    'recurse': 1,
    'numRepeats': 10,
    'sampleLabel':'moaning'
    },
]

BPM = 340

song2 = [
    #VERSE1 LOL
    {'start':0,
    'pattern': [1,1,3], #5
    'unitLengthSecs': 60*5/BPM,
    'recurse': 1,
    'numRepeats': 4,
    'sampleLabel':'Kicks'
    },
    {'start':0,
    'pattern': [1,2,1], #4
    'unitLengthSecs': 60*4/BPM,
    'recurse': 1,
    'numRepeats': 5,
    'sampleLabel':'Snares'
    },
    {'start':0,
    'pattern': [2,1], #3
    'unitLengthSecs': 60*3/BPM,
    'recurse': 1,
    'numRepeats': 7,
    'sampleLabel':'Closed Hihat'
    },
    {'start':0,
    'pattern': [5,1,1], #7
    'unitLengthSecs': 60*7/BPM,
    'recurse': 1,
    'numRepeats': 3,
    'sampleLabel':'MagicalChords'
    },

    #VERSE1 LOL
    {'start':60*20/BPM,
    'pattern': [1,1,3], #5
    'unitLengthSecs': 60*5/BPM,
    'recurse': 2,
    'numRepeats': 8,
    'sampleLabel':'Kicks'
    },
    {'start':60*20/BPM,
    'pattern': [1,2,1], #4
    'unitLengthSecs': 60*4/BPM,
    'recurse': 2,
    'numRepeats': 10,
    'sampleLabel':'Snares'
    },
    {'start':60*20/BPM,
    'pattern': [2,1], #3
    'unitLengthSecs': 60*2/BPM,
    'recurse': 1,
    'numRepeats': 40,
    'sampleLabel':'moaning'
    },
    {'start':60*20/BPM,
    'pattern': [1,3,1], #3
    'unitLengthSecs': 60*2/BPM,
    'recurse': 1,
    'numRepeats': 40,
    'sampleLabel':'yawning'
    },
    {'start':60*20/BPM,
    'pattern': [1,2,2,1,1], #7
    'unitLengthSecs': 60*7/BPM,
    'recurse': 1,
    'numRepeats': 6,
    'sampleLabel':'MagicalChords'
    },

    {'start':30,
    'pattern': [1,1,3], #5
    'unitLengthSecs': 60*5/BPM,
    'recurse': 1,
    'numRepeats': 12,
    'sampleLabel':'Kicks'
    },
    {'start':30,
    'pattern': [1,2,1], #4
    'unitLengthSecs': 60*4/BPM,
    'recurse': 1,
    'numRepeats': 15,
    'sampleLabel':'Snares'
    },
    {'start':30,
    'pattern': [2,1], #3
    'unitLengthSecs': 60*3/BPM,
    'recurse': 1,
    'numRepeats': 20,
    'sampleLabel':'Closed Hihat'
    },
    {'start':30,
    'pattern': [5,1,1], #7
    'unitLengthSecs': 60*7/BPM,
    'recurse': 1,
    'numRepeats': 9,
    'sampleLabel':'MagicalChords'
    },
]

# start
#pm.instr.notes
# transformations (pattern or probs)
song3 = [
    ## FIRST
    {'start':0,
    'pattern': [1,2,1], #4
    'recurse': 1,
    'numRepeats': 32,
    'sampleLabel':'Kicks'
    },
    {'start':0,
    'pattern': [2,2,1,1,1], #7
    'unitLengthSecs': 60*7/BPM,
    'recurse': 1,
    'numRepeats': 32,
    'sampleLabel':'Snares'
    },
    {'start':0,
    'pattern': [1,1,2,1], #5
    'unitLengthSecs': 60*5/BPM,
    'recurse': 1,
    'numRepeats': 32,
    'sampleLabel':'Closed Hihat'
    },
    {'start':0,
    'pattern': [1,2,1,1,2], #7
    'unitLengthSecs': 60*4/BPM, #7-plet?
    'recurse': 1,
    'numRepeats': 32,
    'sampleLabel':'Percussion'
    },
    {'start':0,
    'pattern': [2,2,3], #7
    'unitLengthSecs': 60*4/BPM,
    'recurse': 2,
    'numRepeats': 32,
    'sampleLabel':'lip-smacking'
    },


    {'start':24,
    'pattern': [1,3], #7
    'unitLengthSecs': 60*4/BPM,
    'recurse': 1,
    'numRepeats': 32,
    'sampleLabel':'MagicalChords'
    },

    {'start':24,
    'pattern': [1,2,1], #4
    'unitLengthSecs': 60*4/BPM,
    'recurse': 1,
    'numRepeats': 32,
    'sampleLabel':'Kicks'
    },
    {'start':20,
    'pattern': [1,2,1,2,1], #7
    'unitLengthSecs': 60*7/BPM,
    'recurse': 1,
    'numRepeats': 32,
    'sampleLabel':'Snares'
    },
    {'start':24,
    'pattern': [1,3,1,1], #5
    'unitLengthSecs': 60*5/BPM,
    'recurse': 1,
    'numRepeats': 32,
    'sampleLabel':'Closed Hihat'
    },
    {'start':24,
    'pattern': [1,2,1,1,2], #7
    'unitLengthSecs': 60*4/BPM, #7-plet?
    'recurse': 2,
    'numRepeats': 32,
    'sampleLabel':'Percussion'
    },
    {'start':36,
    'pattern': [2,2,3], #7
    'unitLengthSecs': 60*4/BPM,
    'recurse': 1,
    'numRepeats': 32,
    'sampleLabel':'lip-smacking'
    },
    {'start':36,
    'pattern': [1,3], #7
    'unitLengthSecs': 60*4/BPM,
    'recurse': 1,
    'numRepeats': 32,
    'sampleLabel':'MagicalChords'
    },
]


import pretty_midi as pm
import pyparsing as pp
import pickle

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
from badBoyMIDI import badBoyMIDIPatternLang
from renderMIDItoAudio import renderMIDItoAudio
def thursPee(song):
    n_fft = 1024
    hop_length = int(n_fft/4)
    PICKLE_PATH = 'samplePickles/27_June.p'

    """
    #WAV_DIR = "./wavs/cached_media/sample_bank/arps/" #TODO
    #WAV_DIR = "/Users/mendelbot/Projects/scramblaudio/wavs/nonverbalVocalization/moaning"
    PICKLE_PATH = 'samplePickles/27_June.p'

    WAV_DIRS = ["/Users/mendelbot/Projects/scramblaudio/wavs/oneShots",
    "/Users/mendelbot/Projects/scramblaudio/wavs/MagicalChords",
    "/Users/mendelbot/Projects/scramblaudio/wavs/nonverbalVocalization/"]

    import pdb; pdb.set_trace()

    samples = readInSamples(WAV_DIRS, n_fft=n_fft, hop_length=hop_length)

    output = open(PICKLE_PATH, 'wb')
    pickle.dump(samples, output)

    import pdb; pdb.set_trace()
    """
    # Pre-loaded and analyzed samples...
    samples = pickle.load(open(PICKLE_PATH, "rb"))

    ## Optional: retrieve or generate patterns
    ## generate MIDI based on patterns...

    #midiOutput = badBoyMIDI(pattern = [1, 1, 3], recursiveDepth=4, songLengthSecs=30)
    midiOutputPatternSyntax = badBoyMIDIPatternLang(song)

    #audio = renderMIDItoAudio(samples, midiOutput, hop_length)
    audio = renderMIDItoAudio(samples, midiOutputPatternSyntax, hop_length)


    print("]]]]]],,,........;;;;;;\\\\\\||||||")



if __name__ == "__main__":
    thursPee(song3)

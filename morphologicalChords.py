import json
import random
import math

# I know its tempting to think about non-diatonic theory and shit
# but be patient with it...

# I need a todo board

def getDemScales():
    # from https://github.com/danigb/music-scale/blob/master/dict/scales.json thanks mate
    return {"lydian": "1 2 3 4# 5 6 7",
            "major": "1 2 3 4 5 6 7",
            "mixolydian": "1 2 3 4 5 6 7b",
            "dorian": "1 2 3b 4 5 6 7b",
            "aeolian": "1 2 3b 4 5 6b 7b",
            "phrygian": "1 2b 3b 4 5 6b 7b",
            "locrian": "1 2b 3b 4 5b 6b 7b",
            "melodic minor": "1 2 3b 4 5 6 7",
            "melodic minor second mode": "1 2b 3b 4 5 6 7b",
            "lydian augmented": "1 2 3 4# 5A 6 7",
            "lydian dominant": "1 2 3 4# 5 6 7b",
            "melodic minor fifth mode": "1 2 3 4 5 6b 7b",
            "locrian #2": "1 2 3b 4 5b 6b 7b",
            "locrian major": "1 2 3 4 5b 6b 7b",
            "altered": "1 2b 3b 3 5b 6b 7b",
            "major pentatonic": "1 2 3 5 6",
            "lydian pentatonic": "1 3 4# 5 7",
            "mixolydian pentatonic": "1 3 4 5 7b",
            "locrian pentatonic": "1 3b 4 5b 7b",
            "minor pentatonic": "1 3b 4 5 7b",
            "minor six pentatonic": "1 3b 4 5 6",
            "minor hexatonic": "1 2 3b 4 5 7",
            "flat three pentatonic": "1 2 3b 5 6",
            "flat six pentatonic": "1 2 3 5 6b",
            "major flat two pentatonic": "1 2b 3 5 6",
            "whole tone pentatonic": "1 3 5b 6b 7b",
            "ionian pentatonic": "1 3 4 5 7",
            "lydian #5 pentatonic": "1 3 4# 5A 7",
            "lydian dominant pentatonic": "1 3 4# 5 7b",
            "minor #7 pentatonic": "1 3b 4 5 7",
            "super locrian pentatonic": "1 3b 4d 5b 7b",
            "in-sen": "1 2b 4 5 7b",
            "iwato": "1 2b 4 5b 7b",
            "hirajoshi": "1 2 3b 5 6b",
            "kumoijoshi": "1 2b 4 5 6b",
            "pelog": "1 2b 3b 5 6b",
            "vietnamese 1": "1 3b 4 5 6b",
            "vietnamese 2": "1 3b 4 5 7b",
            "prometheus": "1 2 3 4# 6 7b",
            "prometheus neopolitan": "1 2b 3 4# 6 7b",
            "ritusen": "1 2 4 5 6",
            "scriabin": "1 2b 3 5 6",
            "piongio": "1 2 4 5 6 7b",
            "major blues": "1 2 3b 3 5 6",
            "minor blues": "1 3b 4 5b 5 7b",
            "composite blues": "1 2 3b 3 4 5b 5 6 7b",
            "augmented": "1 2A 3 5 5A 7",
            "augmented heptatonic": "1 2A 3 4 5 5A 7",
            "dorian #4": "1 2 3b 4# 5 6 7b",
            "lydian diminished": "1 2 3b 4# 5 6 7",
            "whole tone": "1 2 3 4# 5A 7b",
            "leading whole tone": "1 2 3 4# 5A 7b 7",
            "harmonic minor": "1 2 3b 4 5 6b 7",
            "lydian minor": "1 2 3 4# 5 6b 7b",
            "neopolitan": "1 2b 3b 4 5 6b 7",
            "neopolitan minor": "1 2b 3b 4 5 6b 7b",
            "neopolitan major": "1 2b 3b 4 5 6 7",
            "neopolitan major pentatonic": "1 3 4 5b 7b",
            "romanian minor": "1 2 3b 5b 5 6 7b",
            "double harmonic lydian": "1 2b 3 4# 5 6b 7",
            "diminished": "1 2 3b 4 5b 6b 6 7",
            "harmonic major": "1 2 3 4 5 6b 7",
            "double harmonic major": "1 2b 3 4 5 6b 7",
            "egyptian": "1 2 4 5 7b",
            "hungarian minor": "1 2 3b 4# 5 6b 7",
            "hungarian major": "1 2A 3 4# 5 6 7b",
            "oriental": "1 2b 3 4 5b 6 7b",
            "spanish": "1 2b 3 4 5 6b 7b",
            "spanish heptatonic": "1 2b 3b 3 4 5 6b 7b",
            "flamenco": "1 2b 3b 3 4# 5 7b",
            "balinese": "1 2b 3b 4 5 6b 7",
            "todi raga": "1 2b 3b 4# 5 6b 7",
            "malkos raga": "1 3b 4 6b 7b",
            "kafi raga": "1 3b 3 4 5 6 7b 7",
            "purvi raga": "1 2b 3 4 4# 5 6b 7",
            "persian": "1 2b 3 4 5b 6b 7",
            "bebop": "1 2 3 4 5 6 7b 7",
            "bebop dominant": "1 2 3 4 5 6 7b 7",
            "bebop minor": "1 2 3b 3 4 5 6 7b",
            "bebop major": "1 2 3 4 5 5A 6 7",
            "bebop locrian": "1 2b 3b 4 5b 5 6b 7b",
            "minor bebop": "1 2 3b 4 5 6b 7b 7",
            "mystery #1": "1 2b 3 5b 6b 7b",
            "enigmatic": "1 2b 3 5b 6b 7b 7",
            "minor six diminished": "1 2 3b 4 5 6b 6 7",
            "ionian augmented": "1 2 3 4 5A 6 7",
            "lydian #9": "1 2b 3 4# 5 6 7",
            "ichikosucho": "1 2 3 4 5b 5 6 7",
            "six tone symmetric": "1 2b 3 4 5A 6"
            }

def basicDiatonicTheory(halfStep):
    # OKAY THIS IS THE IMPORTANT Parameters
    """
    okay WITH THIS PART ITS PRETTY coolBC
    U CAN JUST CHOODE WHICH SCALE U WANNA bridge
    NO MORE WORK FOR DADDY-O SIT BACK AND ENJOY THE RIDE.

    TEMPO ALSO IS COOL
    """
    chordDict = {"maj": {0, 4, 7},
                "min": {0, 3, 7},
                "maj7": {0, 4, 7, 10},
                "min7": {0, 3, 7, 10},
                "maj9":  {0, 4, 7, 10},
                "min9":  {0, 3, 7, 10},
                "dim":  {0, 3, 6}
                }

    scales = getDemScales()

    import pdb; pdb.set_trace()
    print("waluigi")



def morphChords(startingChrodmod):
    halfStep = startingChrodmod

    basicDiatonicTheory(halfStep)

    import pdb;pdb.set_trace(); print("waluigi")




# from NOW ON EACH FILE IS A SONG
# lol no thats not how it workds
if __name__ == "__main__":
    #createMIDI()
    #createGlitchyMIDI()
    #timeSignatureOverlap()

    startingChrodmod = "Good luck captain"

    morphChords(startingChrodmod)

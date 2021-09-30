## https://stackoverflow.com/questions/66310721/how-to-install-librosa-on-m1-mac

##########&^ ##########&^ ##########&^ ##########&^ ##########&^ ##########&^
##########&^  DOC STUFF   ##########&^ ##########&^ ##########&^ ##########&^
##########&^ ##########&^ ##########&^ ##########&^ ##########&^ ##########&^

'''
Future TODOs
- iterate over all sample files, so traverse directories before read if __name__ == '__main__':
- apply window function to audio
- maybe do a simple overlap on the adding? oo would be cool
'''

# Beat tracking example
print("Import librosa")
import librosa
print("Librosa imported")

import numpy as np
import os
import random
import soundfile as sf
from scipy import signal
import string

WAV_DIR = "./wavs/cached_media/sample_bank/" #TODO
SAMPLE_RATE = 44100
allOfEm = {}
hopLength = 512

def readInFilesAndGetOnsets(WAV_DIR):
    ### Read through directory to pick all waves



    for root, dirs, files in os.walk(WAV_DIR):
        path = root.split(os.sep)
        print((len(path) - 1) * '---', os.path.basename(root))
        for currFile in files:
            ##print(len(path) * '---', currFile)
            if currFile.endswith(".wav"):
                fullPath = "%s/%s" % (root, currFile)
                y, sr = librosa.load(fullPath)
                newFileName = currFile.replace(" ", "_")
                allOfEm[newFileName] = {"rawAudio": y}
                allOfEm[newFileName]['onsets'] = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hopLength)
                print("%s imported!" % currFile)


        return allOfEm

def doThatFirstThing(allOfEm):
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
    startingAudioLengthSeconds = 0.1
    origAudioSampleWidth = int(startingAudioLengthSeconds * SAMPLE_RATE)

    someNoise = np.array(0)
    howManyLoopies = 1500

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

        currAudioSampleWidth = int(audioSampleWidth * random.random())
        #currAudioSampleWidth = audioSampleWidth

        begPoint = currOnsetStartPoint - int(currAudioSampleWidth/2)
        begPoint = begPoint if begPoint > 0 else 0

        endPoint = currOnsetStartPoint + int(currAudioSampleWidth/2)
        endPoint = len(currSignal) if endPoint > len(currSignal) else endPoint

        newAudioChunk = currSignal[int(begPoint): int(endPoint)]
        currWindow = signal.windows.hamming(len(newAudioChunk))
        newAudioChunkWindowApplied = np.multiply(newAudioChunk, currWindow)
        someNoise = np.append(someNoise, newAudioChunkWindowApplied)

    OUTPUT_PATH = "./outputAudio/"
    randomFileName = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))

    sf.write(OUTPUT_PATH + randomFileName + ".wav", someNoise, SAMPLE_RATE)
    print("%s written!" % randomFileName)

def doAnotherThang(allOfEm)

if __name__ == "__main__":
    allDemAudio = readInFilesAndGetOnsets(WAV_DIR)
    #doThatFirstThing(allDemAudio)
    doAnotherThang(allDemAudio)

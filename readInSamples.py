import numpy as np
import os
import librosa

import samplesToFingerprints

n_fft = 1024
hop_length = n_fft/4

def readInSamples(WAV_DIR,):
    """
    Input: WAV_DIR which it recursively searches for files and onsetzzz

    Output: dict of dict {"rawAudio", "onsets"}
    """
    ## Import audio files
    allOfEm = {}
    OUTPUT_PATH = "./outputAudio/"

    ### Read through directory to pick all waves
    # from euroVibes
    # TODO make libraryy
    for root, dirs, files in os.walk(WAV_DIR):
        path = root.split(os.sep)
        print((len(path) - 1) * '---', os.path.basename(root))
        for currFile in files:
            ##print(len(path) * '---', currFile)
            if currFile.endswith(".wav"):
                newFileName = currFile.replace(" ", "_")
                fullPath = "%s/%s" % (root, currFile)

                y, sr = librosa.load(fullPath)

                # TODO add some data
                currDict = {"rawAudio": y}
                currDict['onsets'] = librosa.onset.onset_detect(y=y, sr=sr, hop_length=int(hop_length)) # why this int hack? cuz otherwise its a float and fails ;(
                currDict['label'] = path[-1]

                ## Feature analysis
                ## TODO make sure` I'm keeping hop_length consistent across diff modules
                currDict["stft"] = samplesToFingerprints.sampleToSTFT(y)
                n_mfcc = 32
                currDict["mfcc"] = samplesToFingerprints.sampleToMFCC(y=y, sr=sr, n_mfcc=n_mfcc)

                origMFCC = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)

                allOfEm[newFileName] = currDict

                print("%s imported!" % currFile)
                print("len: %d --  sr: %d" % (len(y), sr))

                print("stft-shape")
                print(currDict["stft"].shape)
                print()

                print("mfcc-shape")
                print(currDict["mfcc"].shape)
                print("origShape")
                print(origMFCC.shape)
                print("math: %f" % (len(y) / sr * currDict["mfcc"].shape[1] ))
                # TODO what controls length of mfcc

                print()
                print()


    return allOfEm

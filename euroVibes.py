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
import librosa

from pathlib import Path
import copy
import numpy as np
import os
import pickle
import random
import soundfile as sf
from scipy import signal
import string

WAV_DIR = "./wavs/cached_media/sample_bank/arps/" #TODO
SAMPLE_RATE = 44100
allOfEm = {}
hopLength = 512
OUTPUT_PATH = "./outputAudio/"

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

def wchoose(weights):
    '''
    returns index of choice from a weighted distribution
    '''
    break_points = np.cumsum(weights).tolist()
    index = random.random()*break_points[-1]
    return sum([bp<=index for bp in break_points])

def statchoose(weights, counts, alpha=1, dropdown=0):
    '''
    statistical feedback, returns index of choice and new weights
    '''
    growth = lambda count: count**float(alpha)                                      # exponential growth function
    reset = lambda count: float(dropdown)                                           # reset to dropdown when chosen
    probs = [w*growth(c) if c != 0 else w*reset(c) for w,c in zip(weights,counts)]  # compute probabilites
    probs = [p/sum(probs) for p in probs]                                           # and normalize them
    index = wchoose(probs)                                                          # choose
    counts = [c+1 if i != index else 0 for i,c in enumerate(counts)]                # update counts
    return index, counts, probs

def Reverse(x):
    """
    Reverses a segment of audio.

    Args:
        x: 1D array

    Returns:
        a copy of X, reversaflippydipped
    """

    arr = copy.copy(x)

    length = len(arr)
    for i in range(int(length/2)):
        temp = arr[i]
        arr[i] = arr[length-i-1]
        arr[length-i-1] = temp
    return arr

def Rotate(x, numRotations):
    """
    Rotate audio by a number of onset times.

    Args:
        x: input signal
        SAMPLE_RATE: sampling freq
        numRotations: desired num of rotations

    Returns:
        y: new rotated signal
    """

    onsetTimes = librosa.onset.onset_detect(y=y, sr=SAMPLE_RATE, hop_length=hopLength)

    ##print( "Onset Times: %d" % len(onsetTimes))

    if len(onsetTimes) == 0:
        return x

    onsetTimeCutOff = len(onsetTimes) - numRotations
    if onsetTimeCutOff < 0:
        onsetTimeCutOff = len(onsetTimes) - 1

    ##print( len(onsetTimes))
    cutTime = onsetTimes[onsetTimeCutOff]
    cutSample = int(cutTime * SAMPLE_RATE)
    # import pdb; pdb.set_trace()
    y = np.append(x[cutSample:], x[:cutSample])

    return y

def ScrambleChunks(x):
    """
    Just take all the onset points and scramble the fuck out of it.
    Alternately, how about a probability in here to uh reverse and syncopate some of the chunks?

    Args:
        x: input signal
        SAMPLE_RATE: sampling freq

    Returns:
        y: new rotated signal
    """
    import pdb; pdb.set_trace()
    onsetTimes = librosa.onset.onset_detect(y=x, sr=SAMPLE_RATE, hop_length=hopLength)

    #print( "Onset Times: %d" % len(onsetTimes))

    if len(onsetTimes) == 0:
        print( "no onset times ;(")
        import pdb; pdb.set_trace()
        return x

    arrayIndices = set(range(len(onsetTimes)))
    y = np.empty([1,1])

    while arrayIndices:
        currChunk = random.sample(arrayIndices,1)[0]
        arrayIndices.remove(currChunk)

        startTime = onsetTimes[currChunk] * SAMPLE_RATE
        if currChunk == (len(onsetTimes) - 1):
            endTime = len(x) - 1
        else:
            endTime = onsetTimes[currChunk+1] * SAMPLE_RATE

        #print(len(x))
        currAudio = _Window(x[startTime:endTime])

        if (len(currAudio) < .13 * SAMPLE_RATE) and (len(currAudio) > .01 * SAMPLE_RATE) and (random.random() < .15):
            numRepeats = int(random.random() * 7)
            for _ in range(numRepeats):
                y = np.append(y, currAudio)
        else:
            if random.random() < .3:
                currAudio = Reverse(currAudio)

            y = np.append(y, currAudio)

    return y

def Syncopate(x, numSyncopations):
    """
    Syncopate a signal by just windowing.

    Args:
        x: the chunk of audio to syncopate
        SAMPLE_RATE: sampling freq
        numSyncopations: number of chunks to syncopate

    Returns:
        y: new syncopated signal

    TODO: This is maybe clipping if the length of x is too small....
    so if x is smaller than a certain value, just return x
    """

    if len(x) > (SAMPLE_RATE * .05):
        chunkLength = (int) (len(x) / numSyncopations)
        y = np.empty([1,1])
        chunkStart = 0
        for _unused in range(numSyncopations):
            newChunk = _Window(x[chunkStart:chunkStart+chunkLength])
            y = np.append(y, newChunk) #there will be a random 0 at the beginnign from the np.empty ;(
        return y
    else:
        return x

def _Window(x):
    """
    TODO: Make cooler windows -- exponential, etc. Linear is smelly
    Window the signal by fading in and out at ends.

    Questions:
        - what type of windowing? linear? exponential?
        - should the ramp time be constant or a function of the chunk length?

    Args:
        x: signal to be windowed

    Returns:
        y: windowed signal, yo.
    """
    # TODO _Window is broken on smth, so bypass
    return x


    RAMP_FACTOR = .02
    rampLength = _GetLinearRamp(x, RAMP_FACTOR)

    try:
        ramp = np.arange(0,1,1./rampLength)
    except Exception as e:
        print("EXCEPTION!")
        import pdb; pdb.set_trace()
        print("wowee")
    y = np.copy(x)

    for i in range(rampLength):
        y[i] = y[i] * ramp[i]
        y[len(x) - i - 1] = y[len(x) - i - 1] * ramp[i]

    return y

def _GetLinearRamp(x, RAMP_FACTOR):
    return (int) (len(x) * RAMP_FACTOR)

def _GetExponentialRamp(x, RAMP_FACTOR):
    # TODO
    pass

def Reverb(x):
    #TODO
    pass

def createAudioFromSamples(allOfEm, startingAudioLengthSeconds=0.1, howManyLoopies=100):
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
    origAudioSampleWidth = int(startingAudioLengthSeconds * SAMPLE_RATE)
    someNoise = np.array(0)

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

    randomFileName = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))

    sf.write(OUTPUT_PATH + randomFileName + ".wav", someNoise, SAMPLE_RATE)
    print("%s written!" % randomFileName)

    return someNoise

def scramblaudio(x):

    HOW_MANY_TRANS = 10
    SAMPLE_RATE = 44100

    numRuns = 20
    numTracks = 1
    tracks = [np.array(0) for i in range(numTracks)]

    # Statistical feedback setup
    alpha_statFeedback = 5
    weights = [1, # 0 Reverse
               0, # 1 Rotate
               0, # 2 Syncopate 4
               0, # 3 Syncopate 7
               3, # 4 ScrambleChunks
               0] # 5 Syncopate 17


    numXforms = len(weights)

    eventChoices = [[] for i in range(numTracks)] # empty list for each elem
    counts = [[1]*numXforms for i in range(numTracks)]

    for n in range(numTracks): # for each track
        for i in range(numRuns): # for each run
            choice, counts[n], unused_probs = statchoose(weights, counts[n], alpha=alpha_statFeedback)
            eventChoices[n].append(choice)
    # End statfeedback setup


    seedRhythms = [copy.copy(x) for i in range(numTracks)]
    transAudio = []
    for track, choices, seed, i in zip(tracks, eventChoices, seedRhythms, range(numTracks)):
        print( "Calculating Track %d" % (i+1))
        for choice in choices:
            if choice == 0:
                # Reverse(x)
                print( "Reverse")
                transAudio = Reverse(seed)
            elif choice == 1:
                # Rotate(x, SAMPLE_RATE, numRotations)
                print( "Rotate")
                numRotations = 2
                transAudio = Rotate(seed, numRotations)
            elif choice == 2:
                # Syncopate(x, 4)
                print( "Syncopate 4")
                transAudio = Syncopate(seed, 4)
            elif choice == 3:
                # Syncopate(x, 7)
                print( "Syncopate 7")
                transAudio = Syncopate(seed, 7)
            elif choice == 4:
                # Scramble it up! via chunks
                print( "ScrambleChunks")
                ##import pdb; pdb.set_trace()
                transAudio = ScrambleChunks(seed)
            elif choice == 5:
                # Scramble it up! via chunks
                print( "Syncopate 17")
                transAudio = Syncopate(seed, 17)

            print("Seed -- %d \t TransAudio -- %d" % (len(seed), len(transAudio)))

            tracks[i] = np.append(tracks[i], transAudio)
            seed = np.array(transAudio)

            print("Added %d -- total is %d" % ( len(transAudio), len(tracks[i])))
            print()

    # TODO ugly hack, doesn't work with numTracks, and SO SLOW
    print( "All done! meowmeow <3")
    scramblaudio = [sum(x) for x in zip(tracks[0])]

    print( "converted to weird summed array")

    trackName = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

    print( "writing file! %s" % trackName)
    sf.write(OUTPUT_PATH + trackName + ".wav", scramblaudio, SAMPLE_RATE)

    return scramblaudio

if __name__ == "__main__":
    from pathlib import Path

    savedPicklePath = "./audioPickles/cached_arp.p"

    pastAudioPickle = Path(savedPicklePath)
    if pastAudioPickle.is_file():
        print("Pickle exists -- read in audio")
        with open(savedPicklePath, "rb") as handle:
            allDemAudio = pickle.load(handle)
    else:
        print("No pickle -- reading in and saving audio")
        allDemAudio = readInFilesAndGetOnsets(WAV_DIR)
        with open(savedPicklePath, "wb") as handle:
            pickle.dump(allDemAudio, handle, protocol=pickle.HIGHEST_PROTOCOL)

    x = createAudioFromSamples(allDemAudio, startingAudioLengthSeconds=0.2, howManyLoopies=100)
    scramblaudio(x)

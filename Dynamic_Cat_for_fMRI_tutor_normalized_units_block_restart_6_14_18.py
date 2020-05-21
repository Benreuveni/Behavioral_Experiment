from __future__ import division #so that 1/3=0.333 instead of 1/3=0
__author__ = "Ben Reuveni - ben.reuveni@gmail.com"
import os, sys, random, datetime, time, psychopy #handy system and path functions
from psychopy import visual, core, data, event, logging, gui
import numpy as np  # whole numpy lib is available, prepend 'np.'
from PINNACLE_5_18 import *


#This next bit will pop up a dialogue window where we can control a few things as well as specify participant #
expName = 'None'
expInfo = {'Participant': "", 'Block': 1} # can be expanded based on input needs
dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if dlg.OK == False:
    core.quit() #user pressed cancel
expInfo['date'] = datetime.datetime.now().strftime("%d-%m-%y\nTime: %H:%M:%S")#add a simple timestamp

# All times are in seconds.
trialClock = core.Clock()
block_clock = core.Clock()
total_block_time = 479.6 # 2.2 TR * 218 slices
total_blocks = 6
time_before_first_trial = 0
stimTimeout = 1.5
responseTimeout = 1
tooSlowTime = 0.5
feedbackTimeout = 0.5
jitter_time = 1

block_trial_start = [0, 79, 159, 239, 319, 399]
if int(expInfo["Block"]) == 1:
    block = 1
    stimCount = 0
else:
    block = int(expInfo["Block"]) - 1
    stimCount = block_trial_start[block]

#print "stimCount is: %s" %(stimCount)

stimSpeed = 0.0158


line_break = -.5
jitter = 0
instructions = 1
intervention = 0
YPos = 1
XPos = 0
block_clock_trial_time = 0
block_clock_jitter_trial_time = 0
time_to_start_trial = 1

easy_stims, hard_stims, a_stims_shown, b_stims_shown = 0, 0, 0, 0
sfs, oris, labels = [], [], []
disconfirming_stim = [0,0,0]
easy_thresh = 0.2
hard_thresh = 0.2
sample_decision = 'absolute'
stim_select_tries = 5
num_of_easy_stims = 1
num_of_hard_stims = 5
num_of_a_stims = 5
num_of_b_stims = 5
optimizer_time_buffer = 1.1

#label = None


soundFeedback = 0 # controls whether or not sound will be played along with the feedback
interventionBlock = 2 #after which block should we show the intervention?
timeBeforeBreak = 8
timeBeforeEnd = total_blocks * timeBeforeBreak
result = [9,10]
plotting = 0

par = [np.mean([0.95, 1.5]), np.mean([0.4, 0.85]), np.mean([0.001, 0.1]), np.mean([0.1, 0.4]), np.mean([0.3, 1]), np.mean([0.001, 0.1])]
trial_num_on_break = [80, 160, 240, 320, 400, 480, 560, 640, 720, 800, 880, 960]

# this is where we specify which keys are allowed. Make this whatever you like!
#allowedKeys = ("d", "k")
#keyMap = {"d":1, "k":2, 'NA':'NA', None:None} # this is a dictionary. Just like a normal dictionary, the first item is what you input, the second item is its definition

allowedKeys = ("1", "2", "3", "4")
keyMap = {"1":1, "2":1, "3":2, "4":2, 'NA':'NA', None:None}

actualkeyMap = {"1":1, "2":2, "3":3, "4":4, 'NA':'NA', None:None}


allKeys = []
jitter_text = ""
run = True
trial_terminated = 0
jitter_stim_count = 0
show_trial_num = 1
#TR = 0
#TR_array = []
#TR_time = []
#TR_trial_array = []

#Initialize pre-experiment stuff including loading the input file, creating the output file.

#Sets up a datafile
if not os.path.isdir('data'):
    os.makedirs('data') #if this fails (e.g. permissions) we will get error
filename='data' + os.path.sep + '%s' %(expInfo['Participant']) # this sets up the pathname for the output file using the participant number
#logging.console.setLevel(logging.WARNING)#this outputs to the screen, not a file
participant_num = (int(expInfo["Participant"]) % 5) + 1

#print(participant_num)

# if int(expInfo["Participant"]) == 999:
#     # for testing
#     input = np.loadtxt(os.path.dirname(__file__) + '/Bait_Switch/All_Stims_Trans_Shuffle_Jitter_test.txt')
# else:
    #input = np.loadtxt(os.path.dirname(__file__)+'/Bait_Switch/All_Stims_Trans_Shuffle_Jitter_'+str(participant_num)+'.txt')
rbx_input = np.loadtxt('./Bait_Switch/split/rbx_input_' + str(participant_num) + '.txt')
rby_input = np.loadtxt('./Bait_Switch/split/rby_input_' + str(participant_num) + '.txt')
jitter_input = np.loadtxt('./Bait_Switch/split/jitter_input_' + str(participant_num) + '.txt')

j = np.concatenate((rbx_input, rby_input), 0)
jn = normalize_space(j)
normed_rbx_input = jn[:len(rbx_input),]
normed_rby_input = jn[len(rbx_input):,]

#opens a datafile with the following name
dataFile = open(filename + '_Falling_Cat_Bait_n_Switch_no_jitter_task_fMRI_PINNACLE_actual_TARPON.txt', 'a') #it's best not to use spaces in the filename.
#scanner_TR_signal = open(filename + "_scanner_TR_timings.txt", "a")


if not os.path.isdir('pinn_files'):
    os.makedirs('pinn_files')
if not os.path.isdir('./pinn_files/subj_' + str(expInfo['Participant'])):
    os.makedirs('./pinn_files/subj_' + str(expInfo['Participant']))

pinn_data = open('./pinn_files/subj_' + str(expInfo['Participant']) + '/pinn_data_' + str(expInfo['Participant']) + '.txt', 'a')
pinn_data.close()

#pinn_data.write('%f %f %i %i\n' % (0.1, 0.3, 1, 1))
#pinn_data.write('%f %f %i %i\n' % (0.1, 0.3, 1, 1))


#pinn_data = open('pinn_data_' + str(participant_num) + '.txt', 'a')
#sets up the output file "header" with some useful information about trial design, start time, etc.
if stimCount < 2:
    #print "writing header"
    dataFile.write(
        'Participant #' +str(expInfo['Participant'])
        + '\nNo Jitter Task'
        + '\nParticipant input file number: ' + str(participant_num)
        + '\nStimulus Timeout: ' +str(stimTimeout)
        + 's\nFeedback Timeout: ' +str(feedbackTimeout)
        + 's\nToo Slow Timeout: ' + str(tooSlowTime)
        + '\n'
        + '\nBlocks Before Intervention: ' + str(interventionBlock)
        + '\nBlock Length: ' + str(timeBeforeBreak)
        + ' mins\nTotal Time: ' + str(timeBeforeEnd)+' mins\n')

#    scanner_TR_signal.write(
#        'Participant #' +str(expInfo['Participant'])
#        + '\n\n' \
#        + 'trial TR block_time block\n'
#    )
#    scanner_TR_signal.close()

# Objects

win = visual.Window(size=(1920, 1080), fullscr=True, screen=1, allowGUI=False, monitor=u'testMonitor',
                    allowStencil=False, color=[0,0,0], colorSpace=u'rgb', units='norm')

#actualStim = visual.GratingStim(win=win, mask="circle", size=None,
#                                pos=[0,0], sf=15, ori=1) #[0.2, (0.2 * 1.778)]

tarpon_stim_scalar =  1.20 #1.30
tarpon_text_scalar =  1.20 #1.30


actualStim = visual.ImageStim(
    win=win, name='actual_stim', image='./Bait_Switch/split/Stims/0.499007_36.374394.png', mask=None, ori=0,
    pos=[0, 0], size=[(0.125) * tarpon_stim_scalar, (0.125 * 1.778) * tarpon_stim_scalar], color=[1,1,1], colorSpace=u'rgb',
    opacity=1, texRes=128, interpolate=False, depth=-2.0)

textStim = visual.TextStim(
    win=win, ori=0, name='text', text='+', font='Arial',
    units='norm', pos=[0, 0], height= (0.07) * tarpon_text_scalar, wrapWidth=None,
    color="white", colorSpace='rgb', opacity=1, depth=0.0)

imageStim = visual.ImageStim(
    win=win, name='general_image', image='Correct.png', mask=None, ori=0,
    pos=[0, 0], size=[0.18, 0.18 * 1.778], color=[1,1,1], colorSpace=u'rgb',
    opacity=1, texRes=128, interpolate=False, depth=-2.0)

line = visual.Line(win, start=(-1.0, line_break), end=(1.0, line_break),
    ori = 0, name = 'line', opacity = 1, depth = 0.0)

d_label = visual.TextStim(
    win=win, ori=0, name='D', text="Left", font='Arial',
    pos=[-0.2, -0.65], height=(0.12) * tarpon_text_scalar, wrapWidth=None,
    color='white', opacity=1, depth=0.0)

k_label = visual.TextStim(
    win=win, ori=0, name='K', text="Right", font='Arial',
    pos=[0.2, -0.65], height=(0.12) * tarpon_text_scalar, wrapWidth=None,
    color='white', opacity=1, depth=0.0)

trial_num = visual.TextStim(
    win=win, ori=0, name='trial_num', text=str(stimCount), font='Arial',
    pos=[0.5, -0.7], height=0.05, wrapWidth=None,
    color='white', opacity=1, depth=0.0)

lever = visual.Line(win, start=(0.0, -.055), end=(0, -.24),
    ori = 0, name = 'line', opacity = 1, depth = 0.0, lineWidth= 1)


# Functions

def doUserInteraction(stim, expectedKeys, timeout, soundFile):
    global paused, jitter, stimCount, XPos, actualStim, instructions, \
        block_clock, block_clock_trial_time, block_clock_jitter_trial_time, \
        time_to_start_trial, trial_terminated, intervention, lever#, scanner_TR_signal, \
        #TR, TR_array, TR_time, TR_trial_array #, label

    event.clearEvents(eventType=None) #ensure no key carryover
    # check to see what "type" of stim is being shown.
    stim_type_str = stim.name

    if stim_type_str == "actual_stim":
        stim_type = 'sine'
    elif stim_type_str == "text":
        stim_type = 'text'
    elif stim_type_str == "general_image":
        stim_type = 'image'


    if timeout == None or timeout == 0:
        timeout = sys.maxint
    startTime = trialClock.getTime()
    endTime = startTime + timeout

    # draws the d --------- k line
    if instructions == 0:
        line.setAutoDraw(True)  # draw a line
        d_label.setAutoDraw(True)
        k_label.setAutoDraw(True)
        lever.setAutoDraw(True)
        if show_trial_num == 1:
            trial_num.text = str(stimCount + 1)
            trial_num.setAutoDraw(True)

    key_pressed = 0
    response = {
        "keys": [],
        "firstKey": None,
        "lastKey": None,
        "startTime": startTime,
        "endTime": endTime,
        "duration": 0,
        "timedOut": False,
        }

    if soundFile != None:
        soundFile.play()

    while(True):

        if instructions == 0 and block_clock.getTime() >= (time_to_start_trial - 0.100) or block_clock.getTime() >= (total_block_time - 0.100):
            trial_terminated = 1
            lever.end = (0, -.24)

            if key_pressed == 1 and instructions == 0:
                stimCount += 1
                stim.setAutoDraw(False)
                win.flip()
                event.clearEvents(eventType=None)
                return response

            elif key_pressed == 0 and instructions == 0:
                response["timedOut"] = True
                response["firstKey"] = 'NA'
                stim.setAutoDraw(False)
                win.flip()
                event.clearEvents(eventType=None)
                stimCount += 1
                return response

        stim.setAutoDraw(True) #continuously draws the stimulus to the buffer
        win.flip()

        # if it's a sinewave, it should animate by subtracting "stimSpeed" from the Y position.
        # the sinewave should also "slide" on a lever based on what key was pressed, then fall straight down

        start_side_movement = 0.09
        resume_vertical_movement = -0.24


        if stim_type == 'sine':
            if stim.pos[1] >= start_side_movement:
                stim.pos -= (XPos, stimSpeed)
            elif stim.pos[1] <= start_side_movement and stim.pos[1] >= resume_vertical_movement:
                if keyMap[response["firstKey"]] == 1:
                    stim.pos -= ((stimSpeed / 1.778), stimSpeed)
                elif keyMap[response["firstKey"]] == 2:
                    stim.pos -= ((-(stimSpeed / 1.778)), stimSpeed)
                elif keyMap[response["firstKey"]] == None:
                    stim.pos -= (XPos, stimSpeed)
            elif stim.pos[1] <= resume_vertical_movement:
                stim.pos -= (0, stimSpeed)
            #if stim.pos[1]

        keys = []

        if expectedKeys != None:
            if len(expectedKeys) != 0:
                keys = event.getKeys(expectedKeys)
            else:
                keys = event.getKeys()

        if trialClock.getTime() - startTime >= 0.5:
            if random.random > 0.8:
                if label == 1:
                    keys.append('d')
                else:
                    keys.append('k')
            else:
                if label == 1:
                    keys.append('k')
                else:
                    keys.append('d')

        if key_pressed == 0 and len(keys) > 0:
            key_pressed = 1
            response["keys"] = keys
            response["firstKey"] = keys[0]
            response["lastKey"] = keys[len(keys)-1]
            response["duration"] = trialClock.getTime() - startTime
            if jitter == 0: # now that a trial is always a specific length (either stimTimeOut or jitter_time, we need to store RT when a button is pressed.
                block_clock_trial_time = block_clock.getTime()
            else:
                block_clock_jitter_trial_time = block_clock.getTime()
            if instructions == 0:
                if keyMap[response["firstKey"]] == 1:
                    #actualStim.pos -= (10.0, 0)
                    lever.end = (-0.1, -.24)
                    win.flip()

                elif keyMap[response["firstKey"]] == 2:
                    #actualStim.pos += (10.0, 0)
                    lever.end = (0.1, -.24)
                    win.flip()

            if instructions == 1:
                if intervention == 1:
                    intervention = 0
                instructions = 0
                block_clock.reset()
                time_to_start_trial = int(jitter_input[stimCount])
                break


        elif trialClock.getTime() > endTime: # If the response time window has run out
            if key_pressed == 1:
                lever.end = (0, -.24)
                #stimCount += 1
                break
            elif key_pressed == 0:
                if instructions == 1:
                    if intervention == 1:
                        intervention = 0
                    instructions = 0
                    block_clock.reset()
                    time_to_start_trial = int(jitter_input[stimCount])
                    break
                else:
                    ##print "no key was pressed " + str(endTime)
                    response["timedOut"] = True
                    response["firstKey"] = 'NA'
                    #stimCount += 1
                    break

#        if event.getKeys(['5']): # This is a "pause" button for the experiment
#            TR_time.append(block_clock.getTime())
#            TR += 1
#            TR_array.append(TR)
#            TR_trial_array.append(stimCount)
            #print stimCount, TR, block_clock.getTime(), block
#            scanner_TR_signal = open(filename + "_scanner_TR_timings.txt", "a")
#            scanner_TR_signal.write('%i %i %f %i\n' %(stimCount, TR, TR_time, block))
#            scanner_TR_signal.close()

        #check for quit (the [Esc] key)
        if event.getKeys(["escape"]):
            dataFile.close()
#            for t in range(len(TR_time)):
#                scanner_TR_signal = open(filename + "_scanner_TR_timings.txt", "a")
#                scanner_TR_signal.write('%i %i %f\n' %(TR_trial_array[t], TR_array[t], TR_time[t]))
#                scanner_TR_signal.close()
            core.quit() #quits the entire experiment - will dump you to the desktop or whatever.

    stim.setAutoDraw(False) # stop drawing the stimulus to the buffer
    win.flip() # expose the now blank buffer to the screen
    #response["duration"] = trialClock.getTime() - startTime # keeps track of how long since the stim was drawn to the screen
    event.clearEvents(eventType=None) # clear the key buffer.
    return response # ends the function and returns the object "response". Without this return - we would not be able to access any of this data.

def stimUntilAnyKey(stim):
    return doUserInteraction(stim, allKeys, None, None)

def doStimulus(expectedKeys, timeout):
    global textStim, actualStim, XPos, YPos, jitter_text

    ##print "in doStim"

    textStim = textStim
    actualStim = actualStim

    if jitter == 1:
        ##print "showing text"
        return doUserInteraction(textStim, expectedKeys, timeout, None)

    elif jitter == 0:
        ##print "showing image"
        actualStim.pos = (XPos, YPos)
        return doUserInteraction(actualStim, expectedKeys, timeout, None)

def doFixate(duration):
# calls doUserInteraction with fixate stim, no keys
    textStim.color = 'White'
    textStim.text = ''
    return doUserInteraction(textStim, None, duration, None)

def showCorrect(duration, soundFeedback):
    # calls doUserInteraction  with "correct" stim
    imageStim.setImage("Correct.png")
    imageStim.setPos([0, -0.68])
    imageStim.setSize([0.18, 0.18 * 1.778])

    if soundFeedback == 1:
        return doUserInteraction(imageStim, None, duration, correctSound)
    else:
        return doUserInteraction(imageStim, None, duration, None)

def showIncorrect(duration, soundFeedback):
    # calls doUserInteraction with "incorrect" stim, no AllowedKeys, duration
    imageStim.setImage("Incorrect.png")
    imageStim.setPos([0, -0.68])
    imageStim.setSize([0.18, 0.18 * 1.778])
    if soundFeedback == 1:
        return doUserInteraction(imageStim, None, duration, incorrectSound)
    else:
        return doUserInteraction(imageStim, None, duration, None)

def doTooSlow(allowedKeys):
# calls doUserInteraction with the "too slow" stim, allowedKeys and no timeout
    textStim.color = 'White'
    textStim.pos = (0, 0.4)
    #textStim.height = 0.05
    textStim.text = '                          Too Slow!\n\nPlease make your selection faster next time'
    return doUserInteraction(textStim, None, tooSlowTime, None)

def doBlank(duration):
# calls doUserInteraction with blank stim
    textStim.text = ''
    return doUserInteraction(textStim, None, duration, None)

def doPause():
    global textStim, intervention, block, block_clock#, TR, TR_array
    #print "taking a break. Block #: " + str(block) +". Break started at: " + str(block_clock.getTime())
    #TR = 0
    textStim.color = 'White'
    if intervention == 1:
        textStim.setText("It seems like you're not doing as well as you were in the first block. Evidence suggests that people tend to do best in these "
                         "circumstances when they 'go with their gut' or even guess. Try that out as best you can.\n\nPlease let us know when you're ready to continue.")
    elif intervention == 0 and block < 6:
        textStim.text = "Please feel free to take a break.\n\nPlease let us know when you're ready to continue."
    elif intervention == 0 and block == 6:
        textStim.text = "This is the final run. Please note that you will no longer receive feedback for your choices.\n\nPlease let us know when you're ready to continue."
    return doUserInteraction(textStim, ("5"), None, None)

def doFeedback(response, label, show):
        ###print 'true feedback'
        if response == label:
            feedback = 1
            ##print "Correct"
            if show == 1:
                showCorrect(feedbackTimeout, soundFeedback)
        elif response == 'NA':
            feedback = 'NA'
        elif response != label:
            feedback = 0
            ##print "Incorrect"
            if show == 1:
                showIncorrect(feedbackTimeout, soundFeedback)
        return feedback

def stim_selection_dist_diff_old(stimCount, ps, db, prev_x, prev_y):
    global normed_rbx_input, normed_rby_input, easy_stims, hard_stims, a_stims_shown, b_stims_shown, disconfirming_stim, \
    rbx_input, rby_input, stim_select_tries, num_of_easy_stims, num_of_hard_stims, num_of_a_stims, num_of_b_stims, \
    optimizer_time_buffer

    ii_dom_rbx_or_rby = 0
    stim_location_threshold = 0.05
    norm_sf = prev_x
    norm_ori = prev_y
    disconfirming_stim[2] = 0

    while True:  # Check to see that no new stims are needed.

        # disconfirming_stim is an array. index[0] is whether it disconfirms or not.
        # index[1] is which distribution the stim is from (2 is RBX, 3 is RBY)
        # index[2] is how many times it has tried to find a stim.
        disconfirming_stim[0], disconfirming_stim[1] = 0, 0

        if a_stims_shown == num_of_a_stims:
            a_stims_shown = 0
        if b_stims_shown == num_of_b_stims:
            b_stims_shown = 0
        if easy_stims == num_of_easy_stims:
            easy_stims = 0
        if hard_stims == num_of_hard_stims:
            hard_stims = 0

        #print(str(len(normed_rbx_input)) + ' rbx stims left. ' +  str(len(normed_rby_input)) + ' rby stims left.')
        random_stim = random.randint(0, min(len(normed_rbx_input) - 1, len(normed_rby_input) - 1))

        if stimCount <= 81:
            #print("trial < 81")
            disconfirming_stim[1] = 2
            disconfirming_stim[2] = stim_select_tries + 1

        if disconfirming_stim[2] >= stim_select_tries:
            if stimCount > 81:
                disconfirming_stim[1] = random.randint(2,3)
            #print("max attempts exceeded. Picking a stim")
            #print(disconfirming_stim)
            if disconfirming_stim[1] == 2:
                #print("picking RBX")
                norm_sf = normed_rbx_input[random_stim][0]
                norm_ori = normed_rbx_input[random_stim][1]
                label = normed_rbx_input[random_stim][2]
                sf = rbx_input[random_stim, 0]
                ori = rbx_input[random_stim, 1]
                normed_rbx_input = np.delete(normed_rbx_input, random_stim, 0)
                rbx_input = np.delete(rbx_input, random_stim, 0)
                disconfirming_stim = [1, 2, 0]
                if label == 1:
                    a_stims_shown += 1
                elif label == 2:
                    b_stims_shown += 1
                break
            elif disconfirming_stim[1] == 3:
                #print("picking RBY")
                norm_sf = normed_rby_input[random_stim][0]
                norm_ori = normed_rby_input[random_stim][1]
                label = normed_rby_input[random_stim][2]
                sf = rby_input[random_stim, 0]
                ori = rby_input[random_stim, 1]
                normed_rby_input = np.delete(normed_rby_input, random_stim, 0)
                rby_input = np.delete(rby_input, random_stim, 0)
                disconfirming_stim = [1, 2, 0]
                if label == 1:
                    a_stims_shown += 1
                elif label == 2:
                    b_stims_shown += 1
                break

        elif stimCount > 81:
            ps_min = ps.index(min(ps)) + 1  # so that the index is either '1' '2' or '3'
            #print('PS values: ' + str(ps))

            if ps_min == 1:  # if we think they are using II, sample from the whole space

                while not math.hypot(norm_sf - prev_x, norm_ori - prev_y) > stim_location_threshold:
                    random_stim = random.randint(0, min(len(normed_rbx_input) - 1, len(normed_rby_input) - 1))
                    #print(random_stim)
                    #print('Dist was: ' + str(math.hypot(norm_sf - prev_x, norm_ori - prev_y)) + '. Not far enough from last stim, picking again')

                    if ii_dom_rbx_or_rby == 0:
                        ii_dom_rbx_or_rby = random.randint(2,3)

                    if ii_dom_rbx_or_rby == 2: #if II, pick
                        #print('II is most confident, picking RBX')
                        norm_sf = normed_rbx_input[random_stim][0]
                        norm_ori = normed_rbx_input[random_stim][1]
                        label = normed_rbx_input[random_stim][2]
                        disconfirming_stim[1] = 2

                    elif ii_dom_rbx_or_rby == 3:
                        #print('II is most confident, picking RBY')
                        norm_sf = normed_rby_input[random_stim][0]
                        norm_ori = normed_rby_input[random_stim][1]
                        label = normed_rby_input[random_stim][2]
                        disconfirming_stim[1] = 3

                #print('Far enough. Dist was: ' + str(math.hypot(norm_sf - prev_x, norm_ori - prev_y)) + ' from last stim')
                b = db[0]
                E_x = norm_ori - b
                ii_left_or_right = (norm_sf - E_x)
                dist_to_E = (abs(ii_left_or_right))
                dist = (dist_to_E * 0.7071067811865475)
                disconfirming_stim[0] = 1

            elif ps_min == 2:  # if we think they are using RB_X, sample from RB_Y
                #print('RBX is most confident')
                while disconfirming_stim[0] == 0 and disconfirming_stim[2] < stim_select_tries:
                    #while not math.hypot(norm_sf - prev_x, norm_ori - prev_y) > stim_location_threshold:
                    random_stim = random.randint(0, min(len(normed_rbx_input) - 1, len(normed_rby_input) - 1))
                    #print(random_stim)
                    norm_sf = normed_rby_input[random_stim][0]
                    norm_ori = normed_rby_input[random_stim][1]
                    label = normed_rby_input[random_stim][2]
                    # normed_rby_input = np.delete(normed_rby_input, random_stim, 0)

                    x1 = db[1]
                    y1 = 20

                    x2 = db[1]
                    y2 = 80
                    dist = abs(((y2 - y1) * norm_sf) - ((x2 - x1) * norm_ori) + (x2 * y1) - (y2 * x1)) / math.sqrt(
                        ((y2 - y1) ** 2) + ((x2 - x1) ** 2))

                    rbx_left_or_right = ((norm_sf - x1) * (y2 - y1) - (norm_ori - y1) * (x2 - x1))

                    #print(rbx_left_or_right, label)

                    if math.hypot(norm_sf - prev_x, norm_ori - prev_y) > stim_location_threshold:
                        #print(
                         #   'Far enough. Dist was: ' + str(
                         #       math.hypot(norm_sf - prev_x, norm_ori - prev_y)) + ' from last stim')
                        if (rbx_left_or_right < 0 and label in [2, 3]) or (rbx_left_or_right > 0 and label in [1, 4]):
                            #print('disconfirms')
                            disconfirming_stim[0] = 1
                            disconfirming_stim[1] = 3
                        else:
                            #print("doesn't disconfirm")
                            disconfirming_stim[2] += 1
                            #print(disconfirming_stim)
                    else:
                        disconfirming_stim[2] += 1
                        #print('Dist was: ' + str(math.hypot(norm_sf - prev_x,
                        #                                    norm_ori - prev_y)) + '. Not far enough from last stim, picking again')
                        #print(disconfirming_stim)

            elif ps_min == 3:  # if we think they are using RB_Y, sample from RB_X
                #print('RBY is most confident')
                while disconfirming_stim[0] == 0 and disconfirming_stim[2] < stim_select_tries:
                    random_stim = random.randint(0, min(len(normed_rbx_input) - 1, len(normed_rby_input) - 1))
                    #print(random_stim)
                    norm_sf = normed_rbx_input[random_stim][0]
                    norm_ori = normed_rbx_input[random_stim][1]
                    label = normed_rbx_input[random_stim][2]
                    # normed_rbx_input = np.delete(normed_rbx_input, random_stim, 0)

                    x1 = 20
                    y1 = db[2]

                    x2 = 80
                    y2 = db[2]

                    dist = abs(((y2 - y1) * norm_sf) - ((x2 - x1) * norm_ori) + (x2 * y1) - (y2 * x1)) / math.sqrt(
                        ((y2 - y1) ** 2) + ((x2 - x1) ** 2))

                    rby_left_or_right = ((norm_sf - x1) * (y2 - y1) - (norm_ori - y1) * (x2 - x1))

                    #print(rby_left_or_right, label)

                    if math.hypot(norm_sf - prev_x, norm_ori - prev_y) > stim_location_threshold:
                        #print(
                        #    'Far enough. Dist was: ' + str(
                        #        math.hypot(norm_sf - prev_x, norm_ori - prev_y)) + ' from last stim')
                        if (rby_left_or_right < 0 and label in [2, 3]) or (rby_left_or_right > 0 and label in [1, 4]):
                            #print('disconfirms')
                            disconfirming_stim[0] = 1
                            disconfirming_stim[1] = 2

                        else:
                            #print("doesn't disconfirm")
                            disconfirming_stim[2] += 1
                            #print(disconfirming_stim)
                    else:
                        disconfirming_stim[2] += 1
                        #print('Dist was: ' + str(math.hypot(norm_sf - prev_x,
                        #                                    norm_ori - prev_y)) + '. Not far enough from last stim, picking again')
                        #print(disconfirming_stim)

            if disconfirming_stim[0] == 1:
                if label == 4:
                    label -= 3
                if label == 3:
                    label -= 1
                #print label
                #print(easy_stims, hard_stims, a_stims_shown, b_stims_shown)
                #print(disconfirming_stim)

                if dist >= easy_thresh and easy_stims <= num_of_easy_stims:
                    #print('dist is > easy_thresh and easy_stims <= num_of_easy_stims')
                    if label == 1 and a_stims_shown <= num_of_a_stims:
                        #print "Dist was: " + str(dist) + " this is an easy A " + str(norm_sf) + ", " + str(norm_ori)
                        easy_stims += 1
                        a_stims_shown += 1
                        if disconfirming_stim[1] == 2:
                            sf = rbx_input[random_stim, 0]
                            ori = rbx_input[random_stim, 1]
                            normed_rbx_input = np.delete(normed_rbx_input, random_stim, 0)
                            rbx_input = np.delete(rbx_input, random_stim, 0)
                        elif disconfirming_stim[1] == 3:
                            sf = rby_input[random_stim, 0]
                            ori = rby_input[random_stim, 1]
                            normed_rby_input = np.delete(normed_rby_input, random_stim, 0)
                            rby_input = np.delete(rby_input, random_stim, 0)
                        break

                    elif label == 2 and b_stims_shown <= num_of_b_stims:
                        #print "Dist was: " + str(dist) + " this is an easy B " + str(norm_sf) + ", " + str(norm_ori)
                        easy_stims += 1
                        b_stims_shown += 1
                        if disconfirming_stim[1] == 2:
                            sf = rbx_input[random_stim, 0]
                            ori = rbx_input[random_stim, 1]
                            normed_rbx_input = np.delete(normed_rbx_input, random_stim, 0)
                            rbx_input = np.delete(rbx_input, random_stim, 0)
                        elif disconfirming_stim[1] == 3:
                            sf = rby_input[random_stim, 0]
                            ori = rby_input[random_stim, 1]
                            normed_rby_input = np.delete(normed_rby_input, random_stim, 0)
                            rby_input = np.delete(rby_input, random_stim, 0)
                        break

                    else:
                        #print "Not a valid stim. Dist was: " + str(dist) + " from the bound. Trying again."
                        #print('label: ' + str(label) + ' a_stims_shown: ' + str(a_stims_shown) + ' b_stims_shown: ' + str(b_stims_shown))
                        disconfirming_stim[2] += 1


                elif dist < hard_thresh and hard_stims <= num_of_hard_stims:
                    #print('dist is < hard_thresh and hard_stims <= num_of_hard_stims')
                    if label == 1 and a_stims_shown <= num_of_a_stims:
                        #print "Dist was: " + str(dist) + " this is a hard A " + str(norm_sf) + ", " + str(norm_ori)
                        hard_stims += 1
                        a_stims_shown += 1
                        if disconfirming_stim[1] == 2:
                            sf = rbx_input[random_stim, 0]
                            ori = rbx_input[random_stim, 1]
                            normed_rbx_input = np.delete(normed_rbx_input, random_stim, 0)
                            rbx_input = np.delete(rbx_input, random_stim, 0)
                        elif disconfirming_stim[1] == 3:
                            sf = rby_input[random_stim, 0]
                            ori = rby_input[random_stim, 1]
                            normed_rby_input = np.delete(normed_rby_input, random_stim, 0)
                            rby_input = np.delete(rby_input, random_stim, 0)
                        break

                    elif label == 2 and b_stims_shown <= num_of_b_stims:
                        #print "Dist was: " + str(dist) + " this is a hard B " + str(norm_sf) + ", " + str(norm_ori)
                        hard_stims += 1
                        b_stims_shown += 1
                        if disconfirming_stim[1] == 2:
                            sf = rbx_input[random_stim, 0]
                            ori = rbx_input[random_stim, 1]
                            normed_rbx_input = np.delete(normed_rbx_input, random_stim, 0)
                            rbx_input = np.delete(rbx_input, random_stim, 0)
                        elif disconfirming_stim[1] == 3:
                            sf = rby_input[random_stim, 0]
                            ori = rby_input[random_stim, 1]
                            normed_rby_input = np.delete(normed_rby_input, random_stim, 0)
                            rby_input = np.delete(rby_input, random_stim, 0)
                        break

                    else:
                        #print "Not a valid stim. Dist was: " + str(dist) + " from the bound. Trying again."
                        #print('label: ' + str(label) + ' a_stims_shown: ' + str(a_stims_shown) + ' b_stims_shown: ' + str(
                        #    b_stims_shown))
                        disconfirming_stim[2] += 1

                else:
                    #print "Not a valid stim. Dist was: " + str(dist) + " from the bound. Trying again."
                    #print(disconfirming_stim[0], dist, easy_stims, hard_stims)
                    disconfirming_stim[2] += 1

    #print(sf, ori, label, norm_sf, norm_ori)
    return sf, ori, label, norm_sf, norm_ori

def stim_selection_dist_diff(stimCount, ps, db, prev_x, prev_y):
    global normed_rbx_input, normed_rby_input, easy_stims, hard_stims, a_stims_shown, b_stims_shown, disconfirming_stim, \
    rbx_input, rby_input, stim_select_tries, num_of_easy_stims, num_of_hard_stims, num_of_a_stims, num_of_b_stims, \
    optimizer_time_buffer, rbx_stim_location_threshold, rby_stim_location_threshold

    ii_dom_rbx_or_rby = 0
    rbx_stim_location_threshold = 0.1
    rby_stim_location_threshold = 0.05
    norm_sf = prev_x
    norm_ori = prev_y
    disconfirming_stim[2] = 0


    while True:  # Check to see that no new stims are needed.

        # disconfirming_stim is an array. index[0] is whether it disconfirms or not.
        # index[1] is which distribution the stim is from (2 is RBX, 3 is RBY)
        # index[2] is how many times it has tried to find a stim.
        disconfirming_stim[0], disconfirming_stim[1] = 0, 0

        if a_stims_shown == num_of_a_stims:
            a_stims_shown = 0
        if b_stims_shown == num_of_b_stims:
            b_stims_shown = 0
        if easy_stims == num_of_easy_stims:
            easy_stims = 0
        if hard_stims == num_of_hard_stims:
            hard_stims = 0

        #print(str(len(normed_rbx_input)) + ' rbx stims left. ' +  str(len(normed_rby_input)) + ' rby stims left.')
        random_stim = random.randint(0, min(len(normed_rbx_input) - 1, len(normed_rby_input) - 1))

        if stimCount <= 81:
            #print("trial < 81")
            disconfirming_stim[1] = 2
            disconfirming_stim[2] = stim_select_tries + 1

        if disconfirming_stim[2] >= stim_select_tries:
            if stimCount > 81:
                disconfirming_stim[1] = random.randint(2,3)
            #print("max attempts exceeded. Picking a stim")
            #print(disconfirming_stim)
            if disconfirming_stim[1] == 2:
                #print("picking RBX")
                norm_sf = normed_rbx_input[random_stim][0]
                norm_ori = normed_rbx_input[random_stim][1]
                label = normed_rbx_input[random_stim][2]
                sf = rbx_input[random_stim, 0]
                ori = rbx_input[random_stim, 1]
                normed_rbx_input = np.delete(normed_rbx_input, random_stim, 0)
                rbx_input = np.delete(rbx_input, random_stim, 0)
                #last_rbx = [norm_sf, norm_ori]
                disconfirming_stim = [1, 2, 0]
                if label == 4:
                    label -= 3
                elif label == 3:
                    label -= 1
                if label == 1:
                    a_stims_shown += 1
                elif label == 2:
                    b_stims_shown += 1

                break
            elif disconfirming_stim[1] == 3:
                #print("picking RBY")
                norm_sf = normed_rby_input[random_stim][0]
                norm_ori = normed_rby_input[random_stim][1]
                label = normed_rby_input[random_stim][2]
                sf = rby_input[random_stim, 0]
                ori = rby_input[random_stim, 1]
                normed_rby_input = np.delete(normed_rby_input, random_stim, 0)
                rby_input = np.delete(rby_input, random_stim, 0)
                #last_rby = [norm_sf, norm_ori]
                disconfirming_stim = [1, 2, 0]
                if label == 4:
                    label -= 3
                elif label == 3:
                    label -= 1
                if label == 1:
                    a_stims_shown += 1
                elif label == 2:
                    b_stims_shown += 1
                break

        elif stimCount > 81:
            ps_min = ps.index(min(ps)) + 1  # so that the index is either '1' '2' or '3'
            #print('PS values: ' + str(ps))

            if ps_min == 1:  # if we think they are using II, sample from the whole space

                while not math.hypot(norm_sf - prev_x, norm_ori - prev_y) > rbx_stim_location_threshold:
                    random_stim = random.randint(0, min(len(normed_rbx_input) - 1, len(normed_rby_input) - 1))
                    #print(random_stim)
                    #print('Dist was: ' + str(math.hypot(norm_sf - prev_x, norm_ori - prev_y)) + '. Not far enough from last stim, picking again')

                    if ii_dom_rbx_or_rby == 0:
                        ii_dom_rbx_or_rby = random.randint(2,3)

                    if ii_dom_rbx_or_rby == 2: #if II, pick
                        #print('II is most confident, picking RBX')
                        norm_sf = normed_rbx_input[random_stim][0]
                        norm_ori = normed_rbx_input[random_stim][1]
                        label = normed_rbx_input[random_stim][2]
                        disconfirming_stim[1] = 2
                        #last_rbx = [norm_sf, norm_ori]

                    elif ii_dom_rbx_or_rby == 3:
                        #print('II is most confident, picking RBY')
                        norm_sf = normed_rby_input[random_stim][0]
                        norm_ori = normed_rby_input[random_stim][1]
                        label = normed_rby_input[random_stim][2]
                        #last_rby = [norm_sf, norm_ori]
                        disconfirming_stim[1] = 3

                if disconfirming_stim[1] == 2:
                    1+1
                    #print('Far enough. Dist was: ' + str(math.hypot(norm_sf - prev_x, norm_ori - prev_y)) + ' from last stim')
                elif disconfirming_stim[1] == 3:
                    1+1
                    #print('Far enough. Dist was: ' + str(
                    #    math.hypot(norm_sf - prev_x, norm_ori - prev_y)) + ' from last stim')

                b = db[0]
                E_x = norm_ori - b
                ii_left_or_right = (norm_sf - E_x)
                dist_to_E = (abs(ii_left_or_right))
                dist = (dist_to_E * 0.7071067811865475)
                disconfirming_stim[0] = 1

            elif ps_min == 2:  # if we think they are using RB_X, sample from RB_Y
                #print('RBX is most confident')
                #print('previous RBY stim was: ' + str(prev_x) + ', ' + str(prev_y))
                while disconfirming_stim[0] == 0 and disconfirming_stim[2] < stim_select_tries:
                    #while not math.hypot(norm_sf - prev_x, norm_ori - prev_y) > stim_location_threshold:
                    random_stim = random.randint(0, min(len(normed_rbx_input) - 1, len(normed_rby_input) - 1))
                    #print(random_stim)
                    norm_sf = normed_rby_input[random_stim][0]
                    norm_ori = normed_rby_input[random_stim][1]
                    label = normed_rby_input[random_stim][2]
                    # normed_rby_input = np.delete(normed_rby_input, random_stim, 0)

                    x1 = db[1]
                    y1 = 20

                    x2 = db[1]
                    y2 = 80
                    dist = abs(((y2 - y1) * norm_sf) - ((x2 - x1) * norm_ori) + (x2 * y1) - (y2 * x1)) / math.sqrt(
                        ((y2 - y1) ** 2) + ((x2 - x1) ** 2))

                    rbx_left_or_right = ((norm_sf - x1) * (y2 - y1) - (norm_ori - y1) * (x2 - x1))

                    #print(rbx_left_or_right, label)

                    if math.hypot(norm_sf - prev_x, norm_ori - prev_y) > rby_stim_location_threshold:
#                    if math.hypot(norm_sf - prev_x, norm_ori - prev_y) > rby_stim_location_threshold:
                        #print(
                        #    'Far enough. New coords are: ' + str(norm_sf) + ', ' + str(norm_ori) + ' Dist was: ' + str(
                        #        math.hypot(norm_sf - prev_x, norm_ori - prev_y)) + ' from last stim')
                        if (rbx_left_or_right < 0 and label in [2, 3]) or (rbx_left_or_right > 0 and label in [1, 4]):
                            #print('disconfirms')
                            disconfirming_stim[0] = 1
                            disconfirming_stim[1] = 3
                        else:
                            #print("doesn't disconfirm")
                            disconfirming_stim[2] += 1
                            #print(disconfirming_stim)
                    else:
                        disconfirming_stim[2] += 1
                        #print('Dist was: ' + str(math.hypot(norm_sf - prev_x,
                        #                                    norm_ori - prev_y)) + '. Not far enough from last stim, picking again')
                        #print(disconfirming_stim)

            elif ps_min == 3:  # if we think they are using RB_Y, sample from RB_X
                #print('RBY is most confident')
                #print('previous RBX stim was: ' + str(prev_x) + ', ' + str(prev_y))
                while disconfirming_stim[0] == 0 and disconfirming_stim[2] < stim_select_tries:
                    random_stim = random.randint(0, min(len(normed_rbx_input) - 1, len(normed_rby_input) - 1))
                    #print(random_stim)
                    norm_sf = normed_rbx_input[random_stim][0]
                    norm_ori = normed_rbx_input[random_stim][1]
                    label = normed_rbx_input[random_stim][2]
                    # normed_rbx_input = np.delete(normed_rbx_input, random_stim, 0)

                    x1 = 20
                    y1 = db[2]

                    x2 = 80
                    y2 = db[2]

                    dist = abs(((y2 - y1) * norm_sf) - ((x2 - x1) * norm_ori) + (x2 * y1) - (y2 * x1)) / math.sqrt(
                        ((y2 - y1) ** 2) + ((x2 - x1) ** 2))

                    rby_left_or_right = ((norm_sf - x1) * (y2 - y1) - (norm_ori - y1) * (x2 - x1))

                    #print(rby_left_or_right, label)

                    if math.hypot(norm_sf - prev_x, norm_ori - prev_y) > rbx_stim_location_threshold:
                    #    print(
                    #        'Far enough. New coords are: ' + str(norm_sf) + ', ' + str(norm_ori) + ' Dist was: ' + str(
                    #            math.hypot(norm_sf - prev_x, norm_ori - prev_y)) + ' from last stim')
                        if (rby_left_or_right < 0 and label in [2, 3]) or (rby_left_or_right > 0 and label in [1, 4]):
                     #       print('disconfirms')
                            disconfirming_stim[0] = 1
                            disconfirming_stim[1] = 2

                        else:
                      #      print("doesn't disconfirm")
                            disconfirming_stim[2] += 1
                       #     print(disconfirming_stim)
                    else:
                        disconfirming_stim[2] += 1
                        #print('Dist was: ' + str(math.hypot(norm_sf - prev_x,
                        #                                    norm_ori - prev_y)) + '. Not far enough from last stim, picking again')
                        #print(disconfirming_stim)

            if disconfirming_stim[0] == 1:
                if label == 4:
                    label -= 3
                elif label == 3:
                    label -= 1
                #print label
                #print(easy_stims, hard_stims, a_stims_shown, b_stims_shown)
                #print(disconfirming_stim)

                if dist >= easy_thresh and easy_stims <= num_of_easy_stims:
                    #print('dist is > easy_thresh and easy_stims <= num_of_easy_stims')
                    if label == 1 and a_stims_shown <= num_of_a_stims:
                        #print "Dist was: " + str(dist) + " this is an easy A " + str(norm_sf) + ", " + str(norm_ori)
                        easy_stims += 1
                        a_stims_shown += 1
                        if disconfirming_stim[1] == 2:
                            sf = rbx_input[random_stim, 0]
                            ori = rbx_input[random_stim, 1]
                            normed_rbx_input = np.delete(normed_rbx_input, random_stim, 0)
                            rbx_input = np.delete(rbx_input, random_stim, 0)
                            #last_rbx = [norm_sf, norm_ori]
                        elif disconfirming_stim[1] == 3:
                            sf = rby_input[random_stim, 0]
                            ori = rby_input[random_stim, 1]
                            normed_rby_input = np.delete(normed_rby_input, random_stim, 0)
                            rby_input = np.delete(rby_input, random_stim, 0)
                            #last_rby = [norm_sf, norm_ori]
                        break

                    elif label == 2 and b_stims_shown <= num_of_b_stims:
                        #print "Dist was: " + str(dist) + " this is an easy B " + str(norm_sf) + ", " + str(norm_ori)
                        easy_stims += 1
                        b_stims_shown += 1
                        if disconfirming_stim[1] == 2:
                            sf = rbx_input[random_stim, 0]
                            ori = rbx_input[random_stim, 1]
                            normed_rbx_input = np.delete(normed_rbx_input, random_stim, 0)
                            rbx_input = np.delete(rbx_input, random_stim, 0)
                            #last_rbx = [norm_sf, norm_ori]
                        elif disconfirming_stim[1] == 3:
                            sf = rby_input[random_stim, 0]
                            ori = rby_input[random_stim, 1]
                            normed_rby_input = np.delete(normed_rby_input, random_stim, 0)
                            rby_input = np.delete(rby_input, random_stim, 0)
                            #last_rby = [norm_sf, norm_ori]
                        break

                    else:
                        #print "Not a valid stim. Dist was: " + str(dist) + " from the bound. Trying again."
                        #print('label: ' + str(label) + ' a_stims_shown: ' + str(a_stims_shown) + ' b_stims_shown: ' + str(b_stims_shown))
                        disconfirming_stim[2] += 1


                elif dist < hard_thresh and hard_stims <= num_of_hard_stims:
                    #print('dist is < hard_thresh and hard_stims <= num_of_hard_stims')
                    if label == 1 and a_stims_shown <= num_of_a_stims:
                        #print "Dist was: " + str(dist) + " this is a hard A " + str(norm_sf) + ", " + str(norm_ori)
                        hard_stims += 1
                        a_stims_shown += 1
                        if disconfirming_stim[1] == 2:
                            sf = rbx_input[random_stim, 0]
                            ori = rbx_input[random_stim, 1]
                            normed_rbx_input = np.delete(normed_rbx_input, random_stim, 0)
                            rbx_input = np.delete(rbx_input, random_stim, 0)
                            #last_rbx = [norm_sf, norm_ori]
                        elif disconfirming_stim[1] == 3:
                            sf = rby_input[random_stim, 0]
                            ori = rby_input[random_stim, 1]
                            normed_rby_input = np.delete(normed_rby_input, random_stim, 0)
                            rby_input = np.delete(rby_input, random_stim, 0)
                            #last_rby = [norm_sf, norm_ori]
                        break

                    elif label == 2 and b_stims_shown <= num_of_b_stims:
                        #print "Dist was: " + str(dist) + " this is a hard B " + str(norm_sf) + ", " + str(norm_ori)
                        hard_stims += 1
                        b_stims_shown += 1
                        if disconfirming_stim[1] == 2:
                            sf = rbx_input[random_stim, 0]
                            ori = rbx_input[random_stim, 1]
                            normed_rbx_input = np.delete(normed_rbx_input, random_stim, 0)
                            rbx_input = np.delete(rbx_input, random_stim, 0)
                            #last_rbx = [norm_sf, norm_ori]
                        elif disconfirming_stim[1] == 3:
                            sf = rby_input[random_stim, 0]
                            ori = rby_input[random_stim, 1]
                            normed_rby_input = np.delete(normed_rby_input, random_stim, 0)
                            rby_input = np.delete(rby_input, random_stim, 0)
                            #last_rby = [norm_sf, norm_ori]
                        break

                    else:
                        #print "Not a valid stim. Dist was: " + str(dist) + " from the bound. Trying again."
                        #print('label: ' + str(label) + ' a_stims_shown: ' + str(a_stims_shown) + ' b_stims_shown: ' + str(
                         #   b_stims_shown))
                        disconfirming_stim[2] += 1

                else:
                    #print "Not a valid stim. Dist was: " + str(dist) + " from the bound. Trying again."
                    #print(disconfirming_stim[0], dist, easy_stims, hard_stims)
                    disconfirming_stim[2] += 1

    #print(sf, ori, label, norm_sf, norm_ori)
    return sf, ori, label, norm_sf, norm_ori

def mainExperiment():

    global trialClock, stimCount, actualStim, textStim, jitter, jitter_text, block_clock, \
        instructions, intervention, time_to_start_trial, run, trial_terminated, block, \
        jitter_stim_count, block, result, par, trial_didnt_start_on_time#, TR, TR_array, TR_time, TR_trial_array

    trial_didnt_start_on_time = 0
    optim_has_run = 0
    phase = 1
    trialClock.reset()
    block_clock.reset()
    textStim.text = str(int(round(time_before_first_trial - block_clock.getTime(), 0)))
    ps = [0, 0, 0]
    db = [0, 0, 0]
    stim_has_been_selected = 0
    data_opened = 0
    norm_sf = 0
    norm_ori = 0

    trial_start_array = []

    if stimCount > 1:
        block_clock.add(-475)

    # uncomment this in order to start in the end of the last block.
    # stimCount = 479
    # block = 6
    # block_clock.add(-455)
    # print block_clock.getTime()

    #block before last
    # stimCount = 399
    # block = 5
    # block_clock.add(-475)
    # print block_clock.getTime()

    # end of first block
    #stimCount = 78
    #block = 1
    #print(int(jitter_input[78]))
    #block_clock.add(-1 * int(jitter_input[78]))

    time_to_start_trial = time_before_first_trial + int(jitter_input[stimCount])

    while(True):

        jitter = 0

        if stim_has_been_selected == 0:
            stim_has_been_selected = 1
            sf, ori, label, norm_sf, norm_ori = stim_selection_dist_diff(stimCount, ps, db, norm_sf, norm_ori)

        sfs.append(norm_sf)
        oris.append(norm_ori)
        labels.append(label)

        #actualStim.sf = sf
        #actualStim.ori = ori
        
        #print sf, ori, norm_sf, norm_ori

        actualStim.setImage("./Bait_Switch/split/Stims/%f_%f.png" %(sf, ori))

        # add a little countdown before the first trial
        if stimCount == 0 or (stimCount in trial_num_on_break):
            if instructions == 0 and block_clock.getTime() < time_to_start_trial:
                textStim.text = "Trial begins in: " + str(int(round(int(time_to_start_trial) - int(block_clock.getTime()), 0)))
                textStim.draw()
                win.flip()

        if block_clock.getTime() >= time_to_start_trial and (block_clock.getTime() + stimTimeout + feedbackTimeout + 0.1) <= total_block_time:

            #print "trial " + str(stimCount+1) + " should begin at: " + str(time_to_start_trial) + " and began at: " + str(block_clock.getTime()) + \
            #      " and should have sf: " + str(sf) + " and ori: " + str(ori) + ". Next trial starts at: " + str(int(jitter_input[stimCount + 1]))

            #print('------------' + str(block_clock.getTime() < (time_to_start_trial + 0.1)) + '------------' )
            if block_clock.getTime() > (time_to_start_trial + 0.1):
                trial_didnt_start_on_time += 1

            trial_terminated = 0 #allows jitters to happen.
            #print "current TTS: " + str(time_to_start_trial)

            if stimCount + 1 in trial_num_on_break:
                time_to_start_trial = total_block_time + 1
            else:
                time_to_start_trial = int(jitter_input[stimCount + 1])

            trial_start_time = block_clock.getTime()
            trial_start_array.append(trial_start_time)
            response = doStimulus(allowedKeys, stimTimeout)
            if (response["timedOut"]):
                response = doTooSlow(allowedKeys)
                textStim.pos = (0, 0)

            if block == 6: # no feedback on last block
                feedback = doFeedback(keyMap[response["firstKey"]], label, 0)
            else:
                feedback = doFeedback(keyMap[response["firstKey"]], label, 1)

            #print("before writing")
            #print(response["firstKey"])
            #print("translated")
            #print(keyMap[response["firstKey"]])

            dataFile = open(filename + '_Falling_Cat_Bait_n_Switch_no_jitter_task_fMRI_PINNACLE_actual_TARPON.txt', 'a')
            if response['timedOut']:
                dataFile.write('%i %f %f %f %i %s %s %f %i %f %f\n' % (stimCount + 1, trial_start_time, sf, ori, label, keyMap[response["firstKey"]], feedback, response["duration"], block, norm_sf, norm_ori))
            else:
                dataFile.write('%i %f %f %f %i %i %i %f %i %f %f\n' % (stimCount + 1, trial_start_time, sf, ori, label, actualkeyMap[response["firstKey"]], feedback, response["duration"], block, norm_sf, norm_ori))
             #   print('*** data written ***')
                #if block > 1:
                pinn_data = open('./pinn_files/subj_' + str(expInfo['Participant']) + '/pinn_data_' + str(
                    expInfo['Participant']) + '.txt', 'a')
                pinn_data.write('%f %f %i %i\n' % (norm_sf, norm_ori, label, keyMap[response["firstKey"]]))
                pinn_data.close()
            dataFile.close()
            #jitter

            jitter_stim_count += 1
            textStim.text = "+"
            textStim.height = 0.1
            textStim.color = "black"
            #print('ready to show fixation. still have: ' +str(time_to_start_trial - block_clock.getTime()))
            #print(stimCount % 80)
            #print(block_clock.getTime() <= (time_to_start_trial - optimizer_time_buffer))

            if (stimCount - 1) not in trial_num_on_break:

                while block_clock.getTime() <= (time_to_start_trial - optimizer_time_buffer):
                    #print('in the jitter while loop')
                    if event.getKeys(["escape"]):
                        dataFile.close()
#                        for t in range(len(TR_time)):
#                            scanner_TR_signal = open(filename + "_scanner_TR_timings.txt", "a")
#                            scanner_TR_signal.write('%i %i %f\n' %(TR_trial_array[t], TR_array[t], TR_time[t]))
#                            scanner_TR_signal.close()
                        core.quit()

#                    if event.getKeys(['5']):  # This is a "pause" button for the experiment
#                        TR_time.append(block_clock.getTime())
#                        TR += 1
#                        TR_array.append(TR)
#                        TR_trial_array.append(stimCount)
                        #print stimCount, TR, block_clock.getTime(), block
#                        scanner_TR_signal = open(filename + "_scanner_TR_timings.txt", "a")
#                        scanner_TR_signal.write('%i %i %f %i\n' %(stimCount, TR, TR_time, block))
#                        scanner_TR_signal.close()

                    jitter = 1
                    textStim.setAutoDraw(True)
                    win.flip()

                    if block > 1:
                        trial_num = stimCount
                        optimizing = 1
                        evaluating = 0
                        logging = 0

                        if data_opened == 0:
                            data = np.loadtxt('./pinn_files/subj_' + str(expInfo['Participant']) + '/pinn_data_' + str(expInfo['Participant']) + '.txt')
                            data_opened = 1
                        if optim_has_run == 0:
                            opt_count = 0
                            optim_has_run = 1
                            #print('starting 1st run of the optimizer')
                            start_t = block_clock.getTime()
                            a = minimize(do_bns, (par), method='L-BFGS-B', args=([trial_num, optimizing, evaluating, logging, str(expInfo['Participant']), trial_start_array, block], data),
                                         bounds=[(0.95, 1.5), (0.4, 0.85), (0.001, 0.1), (0.1, 0.4), (0.3, 1), (0.001, 0.1)],
                                         options={"disp": False, 'maxfun': 1}, callback=test)
                            end_t = block_clock.getTime()
                            optim_time = end_t - start_t
                            #print(end_t - start_t)
                            par = a['x']
                            opt_count += 1


                        elif optim_has_run == 1 and ((block_clock.getTime()) + optim_time + optimizer_time_buffer) < time_to_start_trial:
                            #print('we still have ' + str(time_to_start_trial - (block_clock.getTime())))
                            start_t = block_clock.getTime()
                            a = minimize(do_bns, (par), method='L-BFGS-B', args=([trial_num, optimizing, evaluating, logging, str(expInfo['Participant']), trial_start_array, block], data),
                                         bounds=[(0.95, 1.5), (0.4, 0.8), (0.001, 0.1), (0.1, 0.4), (0.3, 1), (0.001, 0.1)],
                                         options={"disp": False, 'maxfun': 1}, callback=test)
                            end_t = block_clock.getTime()
                            optim_time = end_t - start_t
                            par = a['x']
                            #print(end_t - start_t)
                            opt_count += 1

                textStim.color = "white"
                win.flip()
                while block_clock.getTime() <= (time_to_start_trial - 0.100):
                    if event.getKeys(["escape"]):
                        dataFile.close()
#                        for t in range(len(TR_time)):
#                            scanner_TR_signal = open(filename + "_scanner_TR_timings.txt", "a")
#                            scanner_TR_signal.write('%i %i %f\n' %(TR_trial_array[t], TR_array[t], TR_time[t]))
#                            scanner_TR_signal.close()
                        core.quit()

#            if event.getKeys(['5']):  # This is a "pause" button for the experiment
#                TR_time.append(block_clock.getTime())
#                TR += 1
#                TR_array.append(TR)
#                TR_trial_array.append(stimCount)
                #print stimCount, TR, block_clock.getTime(), block
#                scanner_TR_signal = open(filename + "_scanner_TR_timings.txt", "a")
#                scanner_TR_signal.write('%i %i %f %i\n' %(stimCount, TR, TR_time, block))
#                scanner_TR_signal.close()

                #if block_clock.getTime() >= (time_to_start_trial - 1) and block_clock.getTime() <= time_to_start_trial:
                    # turn the fixation cross green 1 second before the trial starts


            #print "done with jitter, moving on to next trial"
            stimCount += 1
            textStim.height = 0.07
            textStim.color = "white"
            textStim.setAutoDraw(False)
            win.flip()
            stim_has_been_selected = 0

            # pinnacle's guess.
            if block > 1:
                optimizing = 0
                evaluating = 1
                logging = 1
                ps, db = do_bns(par, [trial_num, optimizing, evaluating, logging, str(expInfo['Participant']), trial_start_array, block], data)
                optim_has_run = 0
                #print 'fit value is: ' + str(a['fun'])
                #print('PINN results are: ' + str(ps) + " " + str(db))
                #del data
                data_opened = 0
            if plotting == 5:
                #plt.plot([x_resp_a], [y_resp_a], "o", c='red', markersize=2)
                #plt.plot([x_resp_b], [y_resp_b], "o", c='blue', markersize=2)
                plt.plot([sfs], [oris], "o", c='black')
                if label == 1:
                    plt.plot([sf], [ori], "o", c='red')
                elif label == 2:
                    plt.plot([sf], [ori], "o", c='blue')
                # plt.plot([x_resp_b[t]], [y_resp_b[t]], "o", c='blue')


                # plt.plot([candidate_x_list_norm[s]], [candidate_y_list_norm[s]], "o", color='y')
                plt.plot([db[1], db[1]], [0, 1], 'b')
                plt.plot([0, 1], [db[2], db[2]], 'b')
                plt.plot([0, 1], [db[0], (1 + db[0])], 'b')

                # c1 = plt.Circle((candidate_x_list_norm[s], candidate_y_list_norm[s]), radius=sorted_ps_dict[0][1],
                #                    alpha=1, color='y', fill=False)
                ax = plt.axes()
                plt.axis([0, 1, 0, 1])

                # ax.set_aspect(1)
                # plt.gcf().gca().add_artist(c1)

                plt.ion()
                plt.pause(0.0005)
                plt.clf()

        ##print "checking to see if it's time for a break"
        if stimCount > 0:
            if block_clock.getTime() >= total_block_time:
                lever.setAutoDraw(False)
                if block == total_blocks:
                    # Wrap everything up before quitting.
                    dataFile = open(filename + '_Falling_Cat_Bait_n_Switch_no_jitter_task_fMRI_PINNACLE_actual_TARPON.txt', 'a')
                    dataFile.write(datetime.datetime.now().strftime("Experiment Ended: %H:%M:%S"))  # adds the final line to the dataFile with the experiment duration.
                    dataFile.close()

#                    for t in range(len(TR_time)):
#                        scanner_TR_signal = open(filename + "_scanner_TR_timings.txt", "a")
#                        scanner_TR_signal.write('%i %i %f\n' %(TR_trial_array[t], TR_array[t], TR_time[t]))
#                        scanner_TR_signal.close()

                    textStim.text = 'Thank you for participating in this study.\n\nPlease inform the researcher that you have finished.'  # sets some text
                    instructions = 1
                    #print "showing goodbye screen"
                    stimUntilAnyKey(textStim)
                    core.quit()
                if block == interventionBlock:
                    block += 1
                    intervention = 1
                    instructions = 1
                    doPause()
                else:
                    block += 1
                    instructions = 1
                    doPause()




#A few instruction screens before the experiment begins.
#plt.ion()
#plt.plot(normed_rbx_input[:,0], normed_rbx_input[:,1])
#plt.plot(normed_rby_input[:,0], normed_rby_input[:,1])
#plt.waitforbuttonpress()

imageStim.units = "pix"
imageStim.size = (1280, 768)
imageStim.setImage("Falling_Cat_No_Jitter_Task_Instructions_1.png")
stimUntilAnyKey(imageStim)
imageStim.setImage("Falling_Cat_No_Jitter_Task_Instructions_2.png")
instructions = 1
stimUntilAnyKey(imageStim)
imageStim.units = "norm"
imageStim.size = (0.7, 0.7)
textStim.text = " "
instructions = 1
doUserInteraction(textStim, ("5"), None, None)

instructions = 0
if stimCount < 2:
    dataFile.write('\nDate: ' + str(expInfo['date']) + '\n\ntrial block_time sf ori label response feedback RT block norm_sf norm_ori\n')
dataFile.close()
mainExperiment()

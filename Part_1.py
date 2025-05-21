#!/usr/bin/python3
#importing packages
from datetime import datetime   
from psychopy import core, gui, visual, event  
from collections import defaultdict
from psychopy.hardware import keyboard
import csv
import random


#Creating a string version of the current year/month/day hour/minute
date = datetime.now().strftime('%Y%m%d_%H%M%S')

#Setting up input dialog box
dlg = gui.Dlg(title='Input Participant data') 
dlg.addFixedField('expname', label='Experiment Name', initial='My test experiment')
dlg.addFixedField('expdate', label='Date', initial=date)
dlg.addField('ID', label = 'Participant ID') 
dlg.show()

#Checking if the user pressed Cancel
if not dlg.OK:
    print("User cancelled the experiment")
    core.quit()

#Extracting participant data
data = dlg.data
p_id = data['ID']
expdate = data['expdate']

#Generating a filename using participant ID and experiment date and time
filename = f"{p_id}_{expdate}.csv"
datafile = open(filename,'w')
print("File created:",filename) 
datafile.write('Condition, Target, Word1, Word2, Word3, Answer, CorrectAnswer,RT, IsCorrect, Time\n') 

#Experiment START

#Create the window and set the color to grey
win = visual.Window([1024, 768], units="pix",
                    color=(0, 0, 0))

#Setup for keyboard functions 
kb = keyboard.Keyboard()
exp_clock = core.Clock()

#Create welcome message
welcomestim = visual.TextStim(win, 'Welcome to our experiment!\n\n\n You will see a target word and three choices.\n\n Choose the word closest to the meaning or to a specific feature of the target word as fast as possible.\n\n Left Answer: Keypress "1". Middle Answer: Keypress "2". Right Answer: Keypress "3".\n\n Press "space to start', height = 25) 
welcomestim.draw()
win.flip()
keys = kb.waitKeys(keyList = ['space', 'escape'])
exp_clock.reset()
if keys == 'escape':
    win.close()
    core.quit()
    

#Drawing fixation cross
cross = visual.TextStim(win, '+', height = 60)
cross.draw()
win.flip()
core.wait(5.0)

#Creating the introuction screen
ins = visual.TextStim(win,'The experiment is about to begin.\n\n GET READY!', height = 50)
ins.draw()
win.flip()
core.wait(5.0)

#reading the stimuli/trials.csv file and grouping trials by condition 
conditions = defaultdict(list)
with open('stimuli/trials.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cond = row['Condition'].strip().lower()
        conditions[cond].append(row)

#setting text stimuli to be edited later
cond = visual.TextStim(win, '', height = 40, pos = (0, 0))
target = visual.TextStim(win, '', height = 60, pos = (0, 200))
word1 = visual.TextStim(win, '', height = 60, pos = (-300, -200))
word2 = visual.TextStim(win, '', height = 60, pos = (0, -200))
word3 = visual.TextStim(win, '', height = 60, pos = (300, -200))
ins = visual.TextStim(win,'', height = 30) 

#shuffling condition block order
block_order = ['low', 'high', 'shape', 'size', 'colour', 'texture']
random.shuffle(block_order)

for block_index, cond_name in enumerate(block_order):
    trials = conditions[cond_name]
    
    #changing the condition name from high/low to meaning for reading purposes
    display_name = 'meaning' if cond_name in ['high', 'low'] else cond_name
    random.shuffle(trials)
    
    #setting instruction screen text to be edited for each block
    ins.setText(f"In the next block, choose the word that is a similar {display_name.upper()} to the target word.\n\n GET READY!")
    ins.draw()
    win.flip()
    core.wait(5.0)
    
    for stim in trials:
        
        #drawing fixation cross to show between trials
        cross.draw()
        win.flip()
        core.wait(random.choice([0.5,2.5]))
        
        #Setting and drawing stimuli
        label = 'meaning' if stim['Condition'].lower() in ['high', 'low'] else stim['Condition']
        cond.setText(label)
        target.setText(stim['Target'])
        word1.setText(stim['Word1'])
        word2.setText(stim['Word2'])
        word3.setText(stim['Word3'])
        cond.draw()
        target.draw()
        word1.draw()
        word2.draw()
        word3.draw()
        win.flip()
        
        #Resetting clock to record reaction times
        kb.clock.reset()
        kb.clearEvents()
        
        #Recording keypresses and reaction times, including NA if a trial is missed
        keys = kb.waitKeys(maxWait = 10.0,keyList=['1', '2', '3', 'escape'], waitRelease = False)
        if keys: 
            key = keys[0].name
            rt = round(keys[0].rt, 3)
        else: 
            key = 'none'
            rt  = 'NA'
        
        #Setting experiment clock for final Time column in datafile
        secs = exp_clock.getTime()
        minutes = int(secs// 60)
        sec = round(secs% 60, 1)
        time = f"{minutes:02d} : {sec: 04.1f}" 
        
        #Setting correct answers to add to IsCorrect colum in datafile
        correct = stim['Correct']
        is_correct = int(str(key) == str(correct)) if key != 'escape' else 'NA'
        
        #Writing in datafile
        datafile.write(f"{stim['Condition']}, {stim['Target']}, {stim['Word1']},{stim['Word2']},{stim['Word3']},{key},{correct},{rt},{is_correct},{time}\n")
        
        #Ensuring participants can exit the experiment
        if key == 'escape':
            datafile.close()
            win.close()
            core.quit()
        
    #adding fixation cross between blocks
    if cond_name != block_order[-1]:
        cross.draw()
        win.flip()
        core.wait(random.choice([7.5,12.5]))
        
    #adding a break halfway between condition blocks
    if block_index ==2:
        ins.setText(f"Take a short break, but please pay attention to the screen.\n\n The experiment is going to start again in a few seconds.")
        ins.draw()
        win.flip()
        core.wait(10.0)

cross.draw()
win.flip()
core.wait(5.0)

ins.setText(f"You have completed this experiment!\n\n Your responses have been recorded.\n\n Thank you for taking part!\n\n This screen will close in a few seconds.")
ins.draw()
win.flip()
core.wait(7.0)

win.close()
core.quit()




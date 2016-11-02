"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template,request
from WordGame import app
from operator import itemgetter
import random
import pickle 

startTime = datetime
sourceWord = ''
wrongWords = {'duplicate':'', 'noMatch':'','tooShort':'','notRealWord':'','matchesSource':''}
time = datetime



@app.route('/')
@app.route('/home', methods=['POST'])
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/gamePage',  methods=['POST'])
def gamePage():
    #renders opening game page
    lotsOfWords = []
    with open("words.txt", "r") as words:
        for line in words:
            temp = line[0:len(line)-1]
            lotsOfWords.append(temp)
        charWords = []
        for word in lotsOfWords:
              if len(word) >= 7:
                charWords.append(word)

        global sourceWord
        sourceWord = random.choice(charWords) 
        sourceWord = sourceWord.lower()
        global startTime
        startTime = datetime.now()
                    
        return render_template('gamePage.html', title='Word Game',year=datetime.now().year,word = sourceWord) 

@app.route('/results', methods=['POST'])
def results():
    endTime = datetime.now()
    global time
    time = (endTime - startTime).total_seconds()
    time = datetime.fromtimestamp(time).strftime('%M:%S')
    print(str(time))
    words = []
    global wrongWords  
    wrongWords = {key: '' for key in wrongWords}

    for k,v in request.form.items():
        if v in words:
            wrongWords['duplicate'] = wrongWords['duplicate'] + ", " + v
        else:
            words.append(v.lower())    
 
    

    #check characters match source word
    checkChars(words)
    #check for length
    threeChars(words)
    #check word is not source word
    checkSource(words)
    #check if the word is a real word
    isRealWord(words)
    
    correct = areWrongWords() 

    if not correct:
        return render_template('Incorrect.html', year = datetime.now().year, sourceWord=sourceWord, duplicates=wrongWords['duplicate'][2:], tooShort=wrongWords['tooShort'][2: ], isSource=wrongWords['matchesSource'][2: ], notRealWords=wrongWords['notRealWord'][2: ], noMatch=wrongWords['noMatch'][2: ])
    else:
       return winner(str(time))
    
        

@app.route('/winner', methods = ['POST'])
def winner(time):
        
    return render_template('winner.html', year = datetime.now().year, time = time)

@app.route('/leaderboard', methods = ['POST'])
def leaderboard():
    name = request.form['name']
    board = [{}]
    with open('leaderboard.pickle', 'rb') as lb:
        board = pickle.load(lb)
    
    board.append({'Name':name , 'Time':str(time)})
    board = sorted(board,key=itemgetter('Time'))   
    with open('leaderboard.pickle', 'wb') as l:
        pickle.dump(board, l)

    topTen = []
    for i in range(0,10):
        topTen.append(board[i])

    for i, dict in enumerate(board):
        if dict['Name'] == name and dict['Time'] == time:
            pos = i
        
    return render_template('leaderboard.html', year = datetime.now().year, board = topTen, position = pos)

def checkChars(words):
   global wrongWords

   for word in words:
        for char in word:
            if word.count(char) > sourceWord.count(char):
                wrongWords['noMatch'] = wrongWords['noMatch'] + ', ' + word
                break 

def threeChars(words):
    global wrongWords

    for word in words:
        if len(word) < 3:
            wrongWords['tooShort'] = wrongWords['tooShort'] + ', ' + word

def checkSource(words):
    global wrongWords

    for word in words:
        if word == sourceWord:
            wrongWords['matchesSource'] = wrongWords['matchesSource'] + ', ' + word

def isRealWord(words):
    global wrongWords
    lotsOfWords = []

    with open("words.txt", "r") as dictWords:
        for line in dictWords:
            temp = line[0:len(line)-1]
            lotsOfWords.append(temp)

        for word in words:
            if word not in lotsOfWords:
                wrongWords['notRealWord'] = wrongWords['notRealWord'] + ', ' + word

def areWrongWords():
    global wrongWords
    correct = True

    for key in wrongWords:
        if wrongWords[key] != '':
            correct = False

    return correct

       
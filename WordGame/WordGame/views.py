"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template,request,Flask,session
from operator import itemgetter
import random
import pickle 

app = Flask(__name__)
app.config['SECRET_KEY'] = "YOUWILLNEVERGUESSMYSECRETKEY"

#startTime = datetime
#sourceWord = ''
#wrongWords = {'duplicate':'', 'noMatch':'','tooShort':'','notRealWord':'','matchesSource':''}
#time = datetime



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

        session['sourceWord'] = random.choice(charWords).lower() 
        session['startTime'] = datetime.now()
                    
        return render_template('gamePage.html', title='Word Game',year=datetime.now().year,word = session['sourceWord']) 

@app.route('/results', methods=['POST'])
def results():
    endTime = datetime.now()
    session['time'] = (endTime - session['startTime']).total_seconds()
    session['time'] = datetime.fromtimestamp(session['time']).strftime('%M:%S')
    words = []
    session['wrongWords'] = {'duplicate':'', 'noMatch':'','tooShort':'','notRealWord':'','matchesSource':''}

    for k,v in request.form.items():
        if v in words:
           session['wrongWords']['duplicate'] = session['wrongWords']['duplicate'] + ", " + v
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
        return render_template('Incorrect.html', year = datetime.now().year, sourceWord=session['sourceWord'], duplicates=session['wrongWords']['duplicate'][2:], tooShort=session['wrongWords']['tooShort'][2: ], isSource=session['wrongWords']['matchesSource'][2: ], notRealWords=session['wrongWords']['notRealWord'][2: ], noMatch=session['wrongWords']['noMatch'][2: ])
    else:
       return winner()
    
        

@app.route('/winner', methods = ['POST'])
def winner():
        
    return render_template('winner.html', year = datetime.now().year, time = session['time'])

@app.route('/leaderboard', methods = ['POST'])
def leaderboard():
    name = request.form['name']
    board = [{}]
    with open('leaderboard.pickle', 'rb') as lb:
        board = pickle.load(lb)
    
    board.append({'Name':name , 'Time':str(session['time'])})
    board = sorted(board,key=itemgetter('Time'))   
    with open('leaderboard.pickle', 'wb') as l:
        pickle.dump(board, l)

    topTen = []
    for i in range(0,10):
        topTen.append(board[i])

    for i, dict in enumerate(board):
        if dict['Name'] == name and dict['Time'] == session['time']:
            pos = i
        
    return render_template('leaderboard.html', year = datetime.now().year, board = topTen, position = pos)

def checkChars(words):
   
   for word in words:
        for char in word:
            if word.count(char) > session['sourceWord'].count(char):
                session['wrongWords']['noMatch'] = session['wrongWords']['noMatch'] + ', ' + word
                break 

def threeChars(words):
    for word in words:
        if len(word) < 3:
            session['wrongWords']['tooShort'] = session['wrongWords']['tooShort'] + ', ' + word

def checkSource(words):
    
    for word in words:
        if word == session['sourceWord']:
            session['wrongWords']['matchesSource'] = session['wrongWords']['matchesSource'] + ', ' + word

def isRealWord(words):
    lotsOfWords = []

    with open("words.txt", "r") as dictWords:
        for line in dictWords:
            temp = line[0:len(line)-1]
            lotsOfWords.append(temp)

        for word in words:
            if word not in lotsOfWords:
                session['wrongWords']['notRealWord'] = session['wrongWords']['notRealWord'] + ', ' + word

def areWrongWords():

    correct = True

    for key in session['wrongWords']:
        if session['wrongWords'][key] != '':
            correct = False

    return correct
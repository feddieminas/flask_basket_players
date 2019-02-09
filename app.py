import os
import json
from flask import Flask, render_template, redirect, request, url_for, session
from flask_pymongo import PyMongo

app = Flask(__name__)
#app.secret_key = "fmd270584" 

app.config["MONGO_DBNAME"] = 'dcd_basketball'
app.config["MONGO_URI"] = 'mongodb://root:dcd_basketball1234@ds119049.mlab.com:19049/dcd_basketball'

mongo = PyMongo(app) 

@app.route('/')
@app.route('/login')
def get_username():
    return render_template("index.html")


@app.route('/insert_login', methods=['POST'])
def insert_login():
    user = request.form["username"].lower()
    passwd = request.form["password"].lower()
    
    fileExists = os.path.isfile('static/logins.txt')
    userId = 0
    
    if fileExists == False:
        with open('static/logins.txt', 'w') as f:
            f.write('{0},{1}&{2}'.format(userId, user,passwd))
            f.close()
    else:
        with open('static/logins.txt', 'r') as f:
            lines = f.read().splitlines()
            f.close()
            
        for i, text in enumerate(lines):
            if (text.split(',')[1] == user + "&" + passwd):
                userId=i
        
        if userId == 0: #new Id 
            userId = i+1 
            with open('static/logins.txt', 'a') as f:
                f.write('\n{0},{1}&{2}'.format(userId,user,passwd))
                f.close()
        #else:
            #mongodb find records before redirecting to list summary and parameter the records
    
    return redirect(url_for('get_username'))


@app.route('/list_summary')
def get_list():
    return render_template("listsummary.html")


@app.route('/add_player')
def add_player():
    #userId=1 #we take it then from session variable, might make it global var
    return render_template("addplayer.html")


@app.route('/insert_player', methods=['POST'])
def insert_player(): #need to pass UserId
    mydictReq={'userId': 1, 'position': request.form["optPosition"], 'name': request.form["player_name"], 
    'gender': request.form["optGender"], 'birth_region': request.form["optBirthRegion"], 
    'discipline': {'disc1':[request.form["disc1"],request.form["disc1_rate"]], 
    'disc2':[request.form["disc2"],request.form["disc2_rate"]],
    'disc3':[request.form["disc3"],request.form["disc3_rate"]]},
    'virtual_meet': {'times_see':3, 'go_for':'coffee'}}
    print('mydictReq',mydictReq)
    print('json', json.dumps(mydictReq, ensure_ascii=False))
    
    ubp = mongo.db.users_basket_players
    ubp.insert_one(mydictReq)
    
    return redirect(url_for('add_player'))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
    port=os.environ.get('PORT'),
    debug=True)
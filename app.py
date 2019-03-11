import os
from flask_bcrypt import Bcrypt
from collections import Counter
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.json_util import dumps
import re
from difflib import ndiff

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = "fmd270584" 

app.config["MONGO_DBNAME"] = 'dcd_basketball'
app.config["MONGO_URI"] = 'mongodb://root:dcd_basketball1234@ds119049.mlab.com:19049/dcd_basketball'

'''global player variables'''
disciplines=["points","rebounds","assists","steals","blocks","field_goals","three_points","free_throws"]
virtuals=["coffee", "brunch", "street","na"]

mongo = PyMongo(app) 


''' LOGIN / LOGOUT '''

@app.route('/')
@app.route('/login')
def get_username():
    ''' Login Page... userId number of Guest credentials and store in sessions '''
    if "userID" not in session: session["userID"] = None
    return render_template("index.html", userId=session["userID"])

@app.route('/insert_login', methods=['POST'])
def insert_login():
    ''' Logout and else Login actions taken '''
    if request.form['action'] == 'logout_action': 
        '''if logout clear the session'''
        #app.secret_key = os.urandom(8)
        session["userID"] = None
        session["msg"] = ""
        return redirect(url_for('get_username'))
    elif request.form['action'] == 'login_action': 
        ''' if login, I/O txt file operations for credentials '''
        try:
            user = request.form["username"].strip().lower()
            passwd = request.form["password"].strip().lower()
            hpasswd = bcrypt.generate_password_hash(passwd).decode('utf-8') 
            
            fileLogs = 'static/logs.txt' 
            fileExists = os.path.isfile(fileLogs)
            userId = -1
            
            if fileExists == False:
                with open(fileLogs, 'w') as f: 
                    ''' first ever Guest logsIn '''
                    f.write('{0},{1},{2}'.format(userId+1, user,hpasswd))
                    f.close()
            else:
                with open(fileLogs, 'r') as f: 
                    ''' read existing file created '''
                    lines = f.read().splitlines()
                    f.close()
                
                if lines: 
                    for i, text in enumerate(lines):
                        ''' Check username and password and retrieve the userID '''
                        if (text.split(',')[1] == user and bcrypt.check_password_hash(text.split(',')[2], passwd)):
                            userId=i
                
                if userId == -1: 
                    ''' if no existing userID retrieved, open the file and store a new userID '''  
                    with open(fileLogs, 'a') as f:
                        if not lines:
                            ''' file created isEmpty and first Guest enters '''
                            f.write('{0},{1},{2}'.format(userId+1,user,hpasswd)) 
                        else:
                            userId = i+1 
                            ''' file created not isEmpty and append to last stored userID '''
                            f.write('\n{0},{1},{2}'.format(userId,user,hpasswd))  
                        f.close()
            
            ''' init your session variables '''        
            session["userID"] = userId
            session["msg"] = ""
        except:
            ''' ex. error can occur if one not enters username and password 
            and press login button, then reload the login page '''
            return redirect(url_for('get_username'))
    
        ''' login success with userID not null '''
        return redirect(url_for('get_list'))


''' LIST SUMMARY '''

@app.route('/list_summary')
def get_list():
    ''' Not enter to users List Page if not userID exist and with value '''
    if "userID" not in session or session["userID"] is None:  
        return redirect(url_for("get_username"))

    ''' Guest player records retrieve '''
    _ubp=mongo.db.users_basket_players.find({'userId':int(session["userID"])})
    
    ''' Guest player records retrieve birth region, store it as JSON to move into JS script  '''
    _ubpCopy = mongo.db.users_basket_players.find({'userId':int(session["userID"]) }, {"birth_region": 1,"_id":0 })
    ubpCopyForJS = dumps(_ubpCopy)
    
    ''' flask string messages for add/edit/delete and already exists player '''
    if session["msg"]!="":
        category, message = session["msg"]
        flash(message, category)
        session["msg"] = ""
    
    return render_template("listsummary.html", user_id=session["userID"], ubp=_ubp, ubpJS=ubpCopyForJS)

@app.context_processor
def utility_processor():
    ''' calc individual player's disciplines average on runtime '''
    def format_avg(val1,val2,val3):
        sum = 0
        list=[val1,val2,val3]
        for num in list:
            num=0 if num=="" else float(num)
            sum = sum +num
        avg  = sum / len(list)
        return u'{0:.1f}'.format(avg)
    ''' calc individual player's virtual expenses for guest on runtime '''    
    def format_vp(times,gofor):
        dictGoforRate = {"brunch": 0.60, "coffee": 0.28, "street": 0.11, "na": 0.01}
        goforResRate = dictGoforRate["na"] if gofor=="" else dictGoforRate[gofor]
        vpCalc = (((goforResRate * times) * 100)/2.5) #3
        return u'{0:.1f}'.format(vpCalc)
    return dict(format_avg=format_avg, format_vp=format_vp)


''' PLAYERS ADD/EDIT/DEL '''

''' seven functions below for cross-checking and adjusting inputs if err types or range of values'''

'''
sub-function of checkVals 
replace is defined in case one use comma in decimals (ex. 9,2) 
'''
def adjNums(key,val,adjval):
    if val[-1]=='0' and len(val)>2:
        adjval=int(int(adjval.replace(',','.'))/10) 
    elif len(val)<=2:
        adjval=int(adjval)
    else:
        adjval=float(adjval.replace(',','.'))/10
        if key[:2]=="vp" and val[1]==".": adjval=round(float(adjval)/10,1)
    return adjval    

''' 
check and adjust if necessary the three disciplines and virtual times values.
extract special chars (+,-) and digits as a string and convert to a whole number
or with one decimal if a guest has inserted any.
'''
def checkVals(disc1_rate,disc2_rate,disc3_rate,vp_time):  # Check Values
    dictCheckVal = { "disc1_rate":disc1_rate, "disc2_rate":disc2_rate, 
    "disc3_rate":disc3_rate, "vp_time":vp_time}
    
    for key, val in dictCheckVal.items():
        try:
            if val=="":
                adjval = ""
            else:
                adjval = val[0] if val[0] in ['+','-'] else ''
                adjval = "".join([adjval] + [v for v in val if v.isdigit()])
                
                adjvalLen = len(adjval)
                if (key[:2]=="vp" and adjvalLen>3):
                    adjval=adjval[:3] 
                elif (key[:2]=="di" and adjvalLen>2):
                    adjval=adjval[:2]
                else:
                    pass
                
                if adjval!="": 
                    adjval= adjNums(key,val,adjval)    
                
                #final touch
                if key[:2]=="vp":
                    adjval = 0 if adjval=="" else adjval if adjval<0 else adjval
                    if adjval>20: adjval=20 # max value to be inserted
                else:
                    adjval = 5 if adjval=="" else adjval if adjval<0 else adjval
                    if adjval>10: adjval=10 # max value to be inserted
        finally:
            dictCheckVal[key]=adjval
        
    return dictCheckVal 

'''
Check Disciplines Select form for any duplicates. 
For ex. disc1 and disc3 both not to include points. Only the first served input. 
'''
def checkSelects(disc1,disc2,disc3):
    listCheckDisc = [disc1,disc2,disc3]
    myduplis = [item for item, count in Counter(listCheckDisc).items() if count > 1]
    for itemdp in myduplis:
        counter=0
        for idx,item in enumerate(listCheckDisc):
            if itemdp==item:
                listCheckDisc[idx]=""
                while counter==0:
                    listCheckDisc[idx]=item
                    counter+=1

    dictCheckSel = {"disc1": listCheckDisc[0], "disc2": listCheckDisc[1],"disc3": listCheckDisc[2]}
    return dictCheckSel

'''
virtual place vs virtual times interactivity
show a min value or a place if its counter option is not empty
'''
def vpStandalone(vp,dictCheckVal):
    if (vp!="" and vp!="na") and dictCheckVal["vp_time"]==0:
        dictCheckVal["vp_time"]=1
    elif vp=="" and dictCheckVal["vp_time"]=="":    
        dictCheckVal["vp_time"]=0
    elif vp=="" and dictCheckVal["vp_time"]>0:
        vp="street"
    else:
        pass
    return vp,dictCheckVal 

'''
As a single input of Name is provided, need to check whether a guest will insert both name or surname
or only the surname. Apart from a whitespace or a tab, we include the possibility of separate them with dot and comma 
(ex. michael jordan - michael.jordan - michael,jordan). 
'''
def playerHypothSurname(formName):
    return re.split('. |, |' ' |\t |'' ',formName)[-1]

'''
sub-function of CheckPlayerInDB
use a custom algorithm to retrieve part of player's surname, which we will then use it to retrieve data from db
using regex and wildcards before and after
'''
def LongestSubstring(Surname,wordLen):
    mid = (wordLen-1) // 2
    left = mid // 2
    right = min(wordLen, max((mid+wordLen) // 2,5))
    return Surname[left:mid] + Surname[mid:right]

'''
check if already the same player exists in the database  
'''
def CheckPlayerInDB(ubp,formName):
    #split name and surname to take the surname
    SurnameTake = playerHypothSurname(formName)
    #custom function for a distinct search of substring of the surname
    LongSubstr = LongestSubstring(SurnameTake,len(SurnameTake))
    #find regex of a name in database and retrieve
    playerIfExists = ubp.find_one({'userId':int(session["userID"]), 'name':{'$regex':'.*' + LongSubstr + '.*'}},{ "name": 1,"_id":1 })
    #use ndiff py function to find differences
    playerNotExists = True
    if (playerIfExists is not None):
        countDiffs = sum([i[0] != ' ' for i in ndiff(playerIfExists['name'],formName)]) #if same name and surname it exists so no new insert
        if int(countDiffs/2) <= 1: #assume max one "spelling" error
            playerNotExists = False
    return playerNotExists         


'''''' 
@app.route('/add_player')
def add_player():
    return render_template("addplayer.html", disciplines=disciplines, virtuals=virtuals)
''''''  

@app.route('/insert_player', methods=['POST'])
def insert_player():
    # Check Values
    dictCheckVal = checkVals(request.form["disc1_rate"], request.form["disc2_rate"], request.form["disc3_rate"], request.form["vp_time"])
        
    # Check Select
    dictCheckSel = checkSelects(request.form.get("disc1", ""),request.form.get("disc2", ""),request.form.get("disc3", ""))
 
    # Final touches
    for key, val in dictCheckSel.items():
        if dictCheckSel[key]=="": dictCheckVal[key+"_rate"]=""

    vp=request.form.get("virtualplace", "")
    vp, dictCheckVal = vpStandalone(vp,dictCheckVal)

    formName = request.form["player_name"].lower()

    mydictReq={'userId': int(session["userID"]), 'position': request.form["optPosition"], 'name': formName, 
    'gender': request.form["optGender"], 'birth_region': request.form["optBirthRegion"], 
    'discipline': {'disc1':[dictCheckSel["disc1"],dictCheckVal["disc1_rate"]], 
    'disc2':[dictCheckSel["disc2"],dictCheckVal["disc2_rate"]],
    'disc3':[dictCheckSel["disc3"],dictCheckVal["disc3_rate"]]},
    'virtual_meet': {'times_see':dictCheckVal["vp_time"], 'go_for':vp}}
    
    ubp = mongo.db.users_basket_players
    
    playerNotExists = CheckPlayerInDB(ubp,formName)
    
    if playerNotExists == True:
        ubp.insert_one(mydictReq)
        session["msg"] = ("success", "New " + formName.title() + " Succesfully Inserted")
    else:
        session["msg"] = ("error", "Player " + formName.title() + " Already Exists. No Inserts Occured")
    
    return redirect(url_for('get_list'))


''''''
@app.route('/edit_del_player/<player_id>')
def edit_del_player(player_id):
    the_player = mongo.db.users_basket_players.find_one({"_id": ObjectId(player_id),'userId':int(session["userID"])})
    return render_template("editDelplayer.html", player=the_player, disciplines=disciplines, virtuals=virtuals, player_db=the_player["name"])
''''''

@app.route('/update_del_player/<player_id>/<player_db>', methods=["POST"])
def update_del_player(player_id, player_db):
    if request.form['action'] == 'edit_action':
        # Check Values
        dictCheckVal = checkVals(request.form["disc1_rate"], request.form["disc2_rate"], request.form["disc3_rate"], request.form["vp_time"])
        
        # Check Select
        dictCheckSel = checkSelects(request.form.get("disc1", ""),request.form.get("disc2", ""),request.form.get("disc3", ""))
        
        # Final touches
        for key, val in dictCheckSel.items():
            if dictCheckSel[key]=="": dictCheckVal[key+"_rate"]=""
    
        vp=request.form.get("virtualplace", "")
        vp, dictCheckVal = vpStandalone(vp,dictCheckVal)
        
        formName = request.form["player_name"].lower()
    
        mydictReq={'userId': int(session["userID"]), 'position': request.form["optPosition"], 'name': formName, 
        'gender': request.form["optGender"], 'birth_region': request.form["optBirthRegion"], 
        'discipline': {'disc1':[dictCheckSel["disc1"],dictCheckVal["disc1_rate"]], 
        'disc2':[dictCheckSel["disc2"],dictCheckVal["disc2_rate"]],
        'disc3':[dictCheckSel["disc3"],dictCheckVal["disc3_rate"]]},
        'virtual_meet': {'times_see':dictCheckVal["vp_time"], 'go_for':vp}}        

        ubp = mongo.db.users_basket_players
        
        playerNotExists = None
        if player_db!=formName:
            playerNotExists = CheckPlayerInDB(ubp,formName)
        
        if playerNotExists != False:
            ubp.update({'_id': ObjectId(player_id), 'userId': int(session["userID"])},mydictReq)
            session["msg"] = ("success", "Edit " + formName.title() + " Succesfully Updated")
        else:
            session["msg"] = ("alert", "Player Name changed to " + formName.title() + " exists. Current Player " + player_db + " not updated")
        
    elif request.form['action'] == 'dele_action':
        mongo.db.users_basket_players.remove({'_id': ObjectId(player_id), 'userId': int(session["userID"])}, {"justOne":True})
        session["msg"] = ("error", request.form["player_name"].lower().title() + " Succesfully Deleted")
        
    return redirect(url_for('get_list'))

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
    port=os.environ.get('PORT'),
    debug=True)
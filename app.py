import os
from flask_bcrypt import Bcrypt
from collections import Counter
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.json_util import dumps
import re
from difflib import ndiff
from functools import wraps

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = os.urandom(8)

app.config["MONGO_DBNAME"] = 'dcd_basketball'
app.config["MONGO_URI"] = 'mongodb://root:dcd_basketball1234@ds119049.mlab.com:19049/dcd_basketball'

'''global player variables'''
disciplines=["points","rebounds","assists","steals","blocks","3-points_%","2-points_%","free_throws", "fouls_drawn"]
virtuals=["coffee", "brunch", "street","na"]

mongo = PyMongo(app) 


''' LOGIN / LOGOUT '''

@app.route('/')
@app.route('/login')
def get_username():
    ''' Login Page... userID number of Guest credentials and store in sessions '''
    if "userID" not in session: session["userID"] = None
    return render_template("index.html", userID=session["userID"])

class MyUnSuccess(Exception): 
    def __init__(self, value): 
        self.value = value 
  
    def __str__(self): 
        return self.value 

@app.route('/insert_login', methods=['POST'])
def insert_login():
    ''' 
    SignUp Plus Logout and else Login actions taken 
    '''
    if request.form['action'] == 'signup_action':
        try:
            user = request.form["username"].strip().lower()
            passwd = request.form["password"].strip().lower()
            
            LogOutFirst = False
            ''' if logged in before, sessionID num exists, then need to logout first '''
            if session["userID"] is not None: 
                LogOutFirst = True
                raise(MyUnSuccess("Need to Logout First"))
            
            ''' if usename and/or password are not inserted '''
            if(any(x in ["",None] for x in [user, passwd])): 
                raise(MyUnSuccess("Insert both Username and Password"))
            
            _userPass = mongo.db.user_pass
            
            ''' retrieve usernames found if any with inserted username input form '''
            userPassOther = _userPass.find({'user': user})
            for up in userPassOther:
                ''' check if any username already exists to prevent two separate guests having same username '''
                if up['user'] == user:
                    raise(MyUnSuccess("Username already exists. Please choose a different one"))
            else:
                pass
            
            hpasswd = bcrypt.generate_password_hash(passwd).decode('utf-8')
            ''' if a new distinct username is about to sign up, find the maximum ID that exists in db '''
            maxUserID = _userPass.find_one(sort=[("userID", -1)]) 
            
            if maxUserID is None:
                ''' first ever guest '''
                userID = 0
            else: 
                ''' add a new guest ''' 
                userID = int(maxUserID['userID']) + 1 
                
            _userPass.insert_one({'userID':userID, 'user': user, 'pass': hpasswd}) 
            ''' init session variables '''
            session["userID"], session["msg"] = userID, "" 
            
        except MyUnSuccess as msg: # Not Signed Up for reasons. Please try again
            session["msg"] = ("alert", msg.value)
            category, message = session["msg"]
            flash(message, category)
            session["msg"] = ""
        finally:
            if session["userID"] is not None and LogOutFirst == False:
                ''' SignUp success with userID not null '''
                return redirect(url_for('get_list'))
            else:
                ''' Not Signed Up '''
                return redirect(url_for('get_username'))
    
    elif request.form['action'] == 'logout_action': 
        '''if logout clear the session'''
        session.pop("userID", None)
        session.pop("msg", "")
        return redirect(url_for('get_username'))
        
    elif request.form['action'] == 'login_action':
        try:
            user = request.form["username"].strip().lower()
            passwd = request.form["password"].strip().lower() 
            
            ''' if usename and/or password are not inserted '''
            if(any(x in ["",None] for x in [user, passwd])): 
                raise(MyUnSuccess("Insert both Username and Password"))
            
            ''' 
            sort ascending the UserIDs in case there is a duplication username for some unexpected reason
            and retrieve the minimum UserID number for that username and password
            '''
            _userPass = mongo.db.user_pass.find({'user': user}).sort([("userID", 1)]) 

            userID = -1
            for up in _userPass:
                ''' check matched username and password '''
                if up['user'] == user and bcrypt.check_password_hash(up['pass'].encode('utf-8'), passwd):
                    userID = int(up['userID'])
                    session["userID"], session["msg"] = userID, ""
                    break
            else:
                ''' if no documents found or match '''
                if _userPass.count() == 0:
                    ''' no documents means not Username is inserted as presumed '''
                    raise(MyUnSuccess("Username inserted not match"))
                else:
                    ''' if documents inserted there is no password match on a matched username '''
                    raise(MyUnSuccess("Password inserted not match"))
        
        except MyUnSuccess as msg: # Not Logged for reasons. Please try again
            session["msg"] = ("alert", msg.value)
            category, message = session["msg"]
            flash(message, category)
            session["msg"] = ""
        finally:
            if session["userID"] is not None:
                ''' Logged success with userID not null '''
                return redirect(url_for('get_list'))
            else:
                ''' Not Logged In '''
                return redirect(url_for('get_username'))


''' LIST SUMMARY '''

''' Not enter to user Pages if not userID exist and with value '''
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "userID" not in session or session["userID"] is None:
            return redirect(url_for("get_username"))
        else:
            return f(*args, **kwargs)
    return wrap

@app.route('/list_summary')
@login_required
def get_list():
    ''' Guest player records retrieve '''
    _ubp=mongo.db.users_basket_players.find({'userID':int(session["userID"])})
    
    ''' Guest player records retrieve birth region, disciplines and virtual place, store it as JSON to move into JS script  '''
    _ubpCopy = mongo.db.users_basket_players.find({'userID':int(session["userID"]) }, {"birth_region": 1,"discipline": 1,"virtual_meet.go_for": 1,"_id":0 })
    ubpCopyForJS = dumps(_ubpCopy)
    
    ''' flask string messages for add/edit/delete and already exists player '''
    if session["msg"]!="":
        category, message = session["msg"]
        flash(message, category)
        session["msg"] = ""
    
    return render_template("listsummary.html", ubp=_ubp, ubpJS=ubpCopyForJS)

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
        if times == "": times = 0
        dictGoforRate = {"brunch": 0.60, "coffee": 0.28, "street": 0.11, "na": 0.01}
        goforResRate = dictGoforRate["na"] if gofor=="" else dictGoforRate[gofor]
        vpCalc = (((goforResRate * times) * 100)/2.5) #3
        return u'{0:.1f}'.format(vpCalc)
    return dict(format_avg=format_avg, format_vp=format_vp)


''' PLAYERS ADD/EDIT/DEL '''

''' seven functions below for cross-checking and adjusting inputs if err types or range of values'''

'''
sub-function of checkVals 
reassign your string based on replaced value 
'''
def change_char(s, p, r):
    return s[:p]+r+s[p+1:]

''' 
check and adjust if necessary the three disciplines and virtual times values.
round to one decimal, check if any str inserted or special chars, produce a number
'''
def checkVals(disc1_rate,disc2_rate,disc3_rate,vp_time):
    dictCheckVal = { "disc1_rate":disc1_rate, "disc2_rate":disc2_rate, 
    "disc3_rate":disc3_rate, "vp_time":vp_time}
    
    for key, val in dictCheckVal.items():
        val = val.replace(',','.')
        
        PointCount = val.count(".")
        idx = -1
        while PointCount>1:
            idx+= 1
            PointFounder = val.find(".", idx+1)
            if PointFounder!=-1: val = change_char(val, int(PointFounder), "a")
            PointCount-=1
        
        adjval = "".join([s for s in re.findall(r'-?\d*\.?\d*', val)])
        
        adjvalLen = len(adjval)
        adjNums = bool(adjvalLen>0)
        if adjNums:
            adjval = adjval[:-1] if adjval[-1] =="." else adjval
        
        if not val == "":   
            if key[:2]=="vp":
                if adjNums:
                    adjval= round(float(adjval[:min(adjvalLen,5)]),1)
                adjval = 0.0 if adjval=="" else adjval if adjval<0.0 else adjval
                if adjval>20.0: adjval=20.0 # max value to be inserted
            else:
                if adjNums:
                    adjval= round(float(adjval[:min(adjvalLen,4)]),1)
                adjval = 5.0 if adjval=="" else adjval if adjval<0.0 else adjval
                if adjval>10.0: adjval=10.0 # max value to be inserted        
        
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
    if (vp!="" and vp!="na") and dictCheckVal["vp_time"] in ["",0]:
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
    return re.sub(r'([\s,.]+)',r' \1 ',formName).split()[-1]

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
    playerIfExists = ubp.find_one({'userID':int(session["userID"]), 'name':{'$regex':'.*' + LongSubstr + '.*'}},{ "name": 1,"_id":1 })
    #use ndiff py function to find differences
    playerNotExists = True
    if (playerIfExists is not None):
        countDiffs = sum([i[0] != ' ' for i in ndiff(playerIfExists['name'],formName)]) #if same name and surname it exists so no new insert
        if int(countDiffs/2) <= 1: #assume max one "spelling" error
            playerNotExists = False
    return playerNotExists         


'''''' 
@app.route('/add_player')
@login_required
def add_player():
    return render_template("addplayer.html", disciplines=disciplines, virtuals=virtuals)
''''''  

@app.route('/insert_player', methods=['POST'])
@login_required
def insert_player():
    try:
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
        if formName=="": raise(MyUnSuccess("Input not an Empty Name. Player " + formName.title() + " Not Added. Please Try Again"))
    
        mydictReq={'userID': int(session["userID"]), 'position': request.form["optPosition"], 'name': formName, 
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
    except MyUnSuccess as msg: # Player not entered
        session["msg"] = ("error", msg.value)
    finally:
        return redirect(url_for('get_list'))


''''''
@app.route('/edit_del_player/<player_id>')
@login_required
def edit_del_player(player_id):
    the_player = mongo.db.users_basket_players.find_one({"_id": ObjectId(player_id),'userID':int(session["userID"])})
    return render_template("editDelplayer.html", player=the_player, disciplines=disciplines, virtuals=virtuals, player_db=the_player["name"])
''''''

@app.route('/update_del_player/<player_id>/<player_db>', methods=["POST"])
@login_required
def update_del_player(player_id, player_db):
    if request.form['action'] == 'edit_action':
        try:
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
            if formName=="": raise(MyUnSuccess("Input not an Empty Name. Player " + formName.title() + " Not Modified. Please Try Again"))
        
            mydictReq={'userID': int(session["userID"]), 'position': request.form["optPosition"], 'name': formName, 
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
                ubp.update({'_id': ObjectId(player_id), 'userID': int(session["userID"])},mydictReq)
                session["msg"] = ("success", "Edit " + formName.title() + " Succesfully Updated")
            else:
                session["msg"] = ("alert", "Player Name changed to " + formName.title() + " exists. Current Player " + player_db + " not updated")
        except MyUnSuccess as msg: # Player not modified
            session["msg"] = ("error", msg.value)
        finally:
            return redirect(url_for('get_list'))
        
    elif request.form['action'] == 'dele_action':
        try:
            mongo.db.users_basket_players.remove({'_id': ObjectId(player_id), 'userID': int(session["userID"])}, {"justOne":True})
            session["msg"] = ("error", request.form["player_name"].lower().title() + " Succesfully Deleted")
        except:
            session["msg"] = ("error", request.form["player_name"].lower().title() + " NOT Deleted")
        finally:
            return redirect(url_for('get_list'))

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
    port=os.environ.get('PORT'))
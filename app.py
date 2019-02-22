import os
from flask_bcrypt import Bcrypt
from collections import Counter
from flask import Flask, render_template, redirect, request, url_for, session, json
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = "fmd270584" 

app.config["MONGO_DBNAME"] = 'dcd_basketball'
app.config["MONGO_URI"] = 'mongodb://root:dcd_basketball1234@ds119049.mlab.com:19049/dcd_basketball'

disciplines=["points","rebounds","assists","steals","blocks","field_goals","three_points","free_throws"]
virtuals=["coffee", "brunch", "street","na"]

mongo = PyMongo(app) 

@app.route('/')
@app.route('/login')
def get_username():
    return render_template("index.html")


@app.route('/insert_login', methods=['POST'])
def insert_login():
    user = request.form["username"].strip().lower()
    passwd = request.form["password"].strip().lower()
    hpasswd = bcrypt.generate_password_hash(passwd).decode('utf-8')
    
    fileExists = os.path.isfile('static/logs.txt')
    userId = -1
    
    if fileExists == False:
        with open('static/logs.txt', 'w') as f:
            f.write('{0},{1},{2}'.format(userId+1, user,hpasswd))
            f.close()
    else:
        with open('static/logs.txt', 'r') as f:
            lines = f.read().splitlines()
            f.close()
        
        if lines: 
            for i, text in enumerate(lines):
                if (text.split(',')[1] == user and bcrypt.check_password_hash(text.split(',')[2], passwd)):
                    userId=i
        
        if userId == -1: #new Id 
            with open('static/logs.txt', 'a') as f:
                if not lines:
                    f.write('{0},{1},{2}'.format(userId+1,user,hpasswd))
                else:
                    userId = i+1 
                    f.write('\n{0},{1},{2}'.format(userId,user,hpasswd))
                f.close()
            
    session["userID"] = userId    
    
    return redirect(url_for('get_list'))


@app.route('/list_summary')
def get_list():
    if "userID" not in session: 
        return redirect(url_for("get_username"))

    _ubp=mongo.db.users_basket_players.find({}, {'userId':int(session["userID"])})
    #player_list = [player for player in _ubp]
    
    #json file to create and retrieve in js with queue js.. if needed. will check with pagination
    
    return render_template("listsummary.html", user_id=session["userID"], ubp=_ubp)

@app.context_processor
def utility_processor():
    def format_avg(val1,val2,val3):
        sum = 0
        list=[val1,val2,val3]
        for num in list:
            num=0 if num=="" else float(num)
            sum = sum +num
        avg  = sum / len(list)
        return u'{0:.2f}'.format(avg)
    def format_vp(times,gofor):
        dictGoforRate = {"brunch": 0.60, "coffee": 0.28, "street": 0.11, "na": 0.01}
        goforResRate = dictGoforRate["na"] if gofor=="" else dictGoforRate[gofor]
        vpCalc = (((goforResRate * times) * 100)/2.5) #3
        return u'{0:.2f}'.format(vpCalc)
    return dict(format_avg=format_avg, format_vp=format_vp)


@app.route('/add_player')
def add_player():
    return render_template("addplayer.html", disciplines=disciplines, virtuals=virtuals)

def adjNums(val,adjval):
    if val[-1]=='0' and len(val)>2:
        adjval=int(int(adjval.replace(',','.'))/10)
    elif len(val)<=2:
        adjval=int(adjval)
    else:
        adjval=float(adjval.replace(',','.'))/10
    return adjval    

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
                if (key[:2]=="vp" and adjvalLen>3) or (key[:2]=="di" and adjvalLen>2):
                    adjval=adjval[:adjvalLen-1] 
                
                if adjval!="": 
                    adjval= adjNums(val,adjval)    
                
                #final touch
                if key[:2]=="vp":
                    adjval = 0 if adjval=="" else adjval if adjval<0 else adjval
                    if adjval>20: adjval=20 
                else:
                    adjval = 5 if adjval=="" else adjval if adjval<0 else adjval
                    if adjval>10: adjval=10
        finally:
            dictCheckVal[key]=adjval
        
    return dictCheckVal 
    
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

@app.route('/insert_player', methods=['POST'])
def insert_player():
    
    # Check Values
    dictCheckVal = checkVals(request.form["disc1_rate"], request.form["disc2_rate"], request.form["disc3_rate"], request.form["vp_time"])
        
    # Check Select
    dictCheckSel = checkSelects(request.form.get("disc1", ""),request.form.get("disc2", ""),request.form.get("disc3", ""))

    #Final touches
    for key, val in dictCheckSel.items():
        if dictCheckSel[key]=="": dictCheckVal[key+"_rate"]=""

    vp=request.form.get("virtualplace", "")
    if vp!="" and dictCheckVal["vp_time"]==0:
        dictCheckVal["vp_time"]=1
    elif vp=="" and dictCheckVal["vp_time"]>0:
        vp="street"
    else:
        pass

    mydictReq={'userId': int(session["userID"]), 'position': request.form["optPosition"], 'name': request.form["player_name"], 
    'gender': request.form["optGender"], 'birth_region': request.form["optBirthRegion"], 
    'discipline': {'disc1':[dictCheckSel["disc1"],dictCheckVal["disc1_rate"]], 
    'disc2':[dictCheckSel["disc2"],dictCheckVal["disc2_rate"]],
    'disc3':[dictCheckSel["disc3"],dictCheckVal["disc3_rate"]]},
    'virtual_meet': {'times_see':dictCheckVal["vp_time"], 'go_for':vp}}
    
    ubp = mongo.db.users_basket_players
    ubp.insert_one(mydictReq)
    
    return redirect(url_for('get_list'))


@app.route('/edit_del_player/<player_id>')
def edit_del_player(player_id):
    the_player = mongo.db.users_basket_players.find_one({"_id": ObjectId(player_id),'userId':int(session["userID"])})
    return render_template("editDelplayer.html", player=the_player, disciplines=disciplines, virtuals=virtuals)

@app.route('/update_del_player/<player_id>', methods=["POST"])
def update_del_player(player_id):
    if request.form['action'] == 'edit_action':
        dictCheckVal = checkVals(request.form["disc1_rate"], request.form["disc2_rate"], request.form["disc3_rate"], request.form["vp_time"])
        dictCheckSel = checkSelects(request.form.get("disc1", ""),request.form.get("disc2", ""),request.form.get("disc3", ""))
        
        #Final touches
        for key, val in dictCheckSel.items():
            if dictCheckSel[key]=="": dictCheckVal[key+"_rate"]=""
    
        vp=request.form.get("virtualplace", "")
        if vp!="" and dictCheckVal["vp_time"]==0:
            dictCheckVal["vp_time"]=1
        elif vp=="" and dictCheckVal["vp_time"]>0:
            vp="street"
        else:
            pass
    
        mydictReq={'userId': int(session["userID"]), 'position': request.form["optPosition"], 'name': request.form["player_name"], 
        'gender': request.form["optGender"], 'birth_region': request.form["optBirthRegion"], 
        'discipline': {'disc1':[dictCheckSel["disc1"],dictCheckVal["disc1_rate"]], 
        'disc2':[dictCheckSel["disc2"],dictCheckVal["disc2_rate"]],
        'disc3':[dictCheckSel["disc3"],dictCheckVal["disc3_rate"]]},
        'virtual_meet': {'times_see':dictCheckVal["vp_time"], 'go_for':vp}}        

        ubp = mongo.db.users_basket_players
        ubp.update({'_id': ObjectId(player_id), 'userId': int(session["userID"])},mydictReq)
        
    elif request.form['action'] == 'dele_action':
        mongo.db.users_basket_players.remove({'_id': ObjectId(player_id), 'userId': int(session["userID"])}, {"justOne":True})
    else:
        pass
    return redirect(url_for('get_list'))

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
    port=os.environ.get('PORT'),
    debug=True)
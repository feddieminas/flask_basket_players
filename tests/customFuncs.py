import os
import bcrypt
from collections import Counter
import pymongo
import re
from difflib import ndiff

class MyUnSuccess(Exception): 
    def __init__(self, value): 
        self.value = value 
  
    def __str__(self): 
        return self.value 

def insert_login(fileLogs,username,password,action, session_userID=None, LogOutFirst=False):
    ''' 
    SignUp Plus Logout and else Login actions taken
    
    For test purposes we use a text file instead of db 
    '''
    sessionMsg = ""
    if action == 'signup_action':
        try:
            user = username
            passwd = password
            
            LogOutFirst = False
            ''' if logged in before, sessionID num exists, then need to logout first '''
            if session_userID is not None:
                LogOutFirst = True
                raise(MyUnSuccess("Need to Logout First"))
            
            ''' if usename and/or password are not inserted '''
            if(any(x in ["",None] for x in [user, passwd])):
                raise(MyUnSuccess("Insert both Username and Password"))
            
            '''
            app.py
            
            _userPass = mongo.db.user_pass
            # retrieve usernames found if any with inserted username input form
            userPassOther = _userPass.find({'user': user})
            for up in userPassOther:
                # check if any username already exists to prevent two separate guests having same username
                if up['user'] == user: 
                    raise(MyUnSuccess("Username already exists. Please choose a different one"))
            else:
                pass
            '''
            ''' customFuncs.py ''' 
            with open(fileLogs, 'r') as f: 
                ''' read existing file created '''
                lines = f.read().splitlines()
                f.close()
                
            if lines: 
                for i, text in enumerate(lines):
                    if (text.split(',')[1] == user): 
                        raise(MyUnSuccess("Username already exists. Please choose a different one"))
            #####
            
            '''
            app.py
            
            bcrypt.generate_password_hash(passwd).decode('utf-8')
            '''
            ''' customFuncs.py '''             
            hpasswd = bcrypt.hashpw(passwd, bcrypt.gensalt()).decode('utf-8')
            #####
            
            '''
            app.py 
            
            # if a new distinct username is about to sign up, find the maximum ID that exists in db
            maxUserID = _userPass.find_one(sort=[("userID", -1)]) 
            
            if maxUserID is None:
                 # first ever guest
                userID = 0
            else: 
                # add a new guest
                userID = int(maxUserID['userID']) + 1            
            '''
            ''' customFuncs.py '''            
            with open(fileLogs, 'r') as f: 
                ''' read existing file created '''
                lines = f.read().splitlines()
                f.close()
            
            maxUserID = None    
            if lines: 
                for i, text in enumerate(lines):
                    maxUserID = i           
            
            if maxUserID is None:
                userID = 0
            else:
                userID = int(maxUserID) + 1 
            #####
            
            '''
            app.py  
            
            _userPass.insert_one({'userID':userID, 'user': user, 'pass': hpasswd})
            '''
            ''' customFuncs.py '''             
            with open(fileLogs, 'a') as f:
                if not lines:
                    ''' file created isEmpty and first Guest enters '''
                    f.write('{0},{1},{2}'.format(userID,user,hpasswd)) 
                else:
                    ''' file created not isEmpty and append to last stored userID '''
                    f.write('\n{0},{1},{2}'.format(userID,user,hpasswd))  
                    f.close()               
            #####
            
            ''' init session variables '''
            session_userID, sessionMsg = userID, ""
            
        except MyUnSuccess as msg: # Not Signed Up for reasons. Please try again
            sessionMsg = ("alert", msg.value)
            '''
            app.py 
            
            category, message = sessionMsg
            flash(message, category)
            sessionMsg = ""
            '''
            ''' customFuncs.py ''' 
            sessionMsg = "YES"
            #####
        finally:
            if session_userID is not None and LogOutFirst == False:
                # SignUp success with userID not null
                return "sessionMsg = " + sessionMsg + " and redirect(url_for('get_list'))"
            else:
                # Not Signed Up
                return "sessionMsg = " + sessionMsg + " and redirect(url_for('get_username'))"
    
    elif action == 'logout_action': 
        '''if logout clear the session'''
        '''
        app.py
        
        session.pop("userID", None)
        session.pop("msg", "")
        '''
        return "session clear and redirect(url_for('get_username'))"
        
    elif action == 'login_action':
        try:
            user = username
            passwd = password
            
            ''' if usename and/or password are not inserted '''
            if(any(x in ["",None] for x in [user, passwd])):
                raise(MyUnSuccess("Insert both Username and Password"))
            
            '''
            app.py
            
            # sort ascending the UserIDs in case there is a duplication username for some unexpected reason
            # and retrieve the minimum UserID number for that username and password
            _userPass = mongo.db.user_pass.find({'user': user}).sort([("userID", 1)])
            
            userID = -1
            for up in _userPass:
                # check matched username and password
                if up['user'] == user and bcrypt.check_password_hash(up['pass'].encode('utf-8'), passwd):
                    userID = int(up['userID'])
                    session_userID, sessionMsg = userID, ""
                    break
            else:
                # if no documents found or match
                if _userPass.count() == 0: 
                    # no documents means not Username is inserted as presumed
                    raise(MyUnSuccess("Username inserted not match"))
                else: 
                    # if documents inserted there is no password match on a matched username
                    raise(MyUnSuccess("Password inserted not match"))
            '''        
            ''' customFuncs.py ''' 
            with open(fileLogs, 'r') as f: 
                ''' read existing file created '''
                lines = f.read().splitlines()
                f.close()
                
            for i, text in enumerate(lines):
                if (text.split(',')[1] == user and bcrypt.checkpw(passwd, text.split(',')[2].encode('utf-8'))): 
                    userID = int(text.split(',')[0])
                    session_userID, sessionMsg = userID, ""
                    break
            else:
                if not lines:
                    raise(MyUnSuccess("Username inserted not match"))
                else:
                    raise(MyUnSuccess("Password inserted not match"))                    
            #####            
        
        except MyUnSuccess as msg: # Not Logged for reasons. Please try again
            sessionMsg = ("alert", msg.value)
            '''
            app.py
            
            category, message = sessionMsg
            flash(message, category)
            sessionMsg = ""
            '''
            ''' customFuncs.py '''            
            sessionMsg = "YES"
            #####
        finally:
            if session_userID is not None:
                ''' Logged success with userID not null '''
                return "sessionMsg = " + sessionMsg + " and redirect(url_for('get_list'))"
            else:
                ''' Not Logged In '''
                return "sessionMsg = " + sessionMsg + " and redirect(url_for('get_username'))"

'''
sub-function of checkVals 
replace is defined in case one use comma in decimals (ex. 9,2) 
'''
def adjNums(key,val,adjval):
    if any([len(val)<=2,val[-1]=='0' and len(val)-len(adjval)!=abs(1)]):
        adjval=int(adjval)    
    elif val[-1]=='0' and len(val)>2:
        adjval=round(int(adjval.replace(',','.'))/10,1)
    else:
        divideMe = 1 if key[:2]=="di" and val[2]=="." else 10 
        adjval=float(adjval.replace(',','.'))/divideMe
        if any([key[:2]=="vp" and val[1]=="." and val!=str(adjval),len(str(adjval))>4]): adjval=round(int(adjval)/10,1)
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
def CheckPlayerInDB(ubp,formName,userID):
    #split name and surname to take the surname
    SurnameTake = playerHypothSurname(formName)
    #custom function for a distinct search of substring of the surname
    LongSubstr = LongestSubstring(SurnameTake,len(SurnameTake))
    #find regex of a name in database and retrieve
    playerIfExists = ubp.find_one({'userID':int(userID), 'name':{'$regex':'.*' + LongSubstr + '.*'}},{ "name": 1,"_id":1 })
    #use ndiff py function to find differences
    playerNotExists = True
    if (playerIfExists is not None):
        countDiffs = sum([i[0] != ' ' for i in ndiff(playerIfExists['name'],formName)]) #if same name and surname it exists so no new insert
        if int(countDiffs/2) <= 1: #assume max one "spelling" error
            playerNotExists = False
    return playerNotExists 
import os
import bcrypt
from collections import Counter
import pymongo
import re
from difflib import ndiff

def insert_login(username,password,action):
    ''' Logout and else Login actions taken '''
    if action == 'logout_action': 
        '''if logout clear the session'''
        '''
        session.pop("userID", None)
        session.pop("msg", "")
        return redirect(url_for('get_username'))
        '''
        return "Session delete and redirect(url_for('get_username'))"
    elif action == 'login_action': 
        ''' if login, I/O txt file operations for credentials '''
        try:
            user = username.strip().lower()
            passwd = password.strip().lower()
            hpasswd = bcrypt.hashpw(passwd, bcrypt.gensalt()).decode('utf-8') # bcrypt.generate_password_hash(passwd).decode('utf-8') 
            
            fileLogs = 'logs.txt' 
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
                        if (text.split(',')[1] == user and bcrypt.checkpw(passwd, text.split(',')[2].encode('utf-8'))): # bcrypt.check_password_hash(text.split(',')[2], passwd))
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
            '''
            session["userID"] = userId
            session["msg"] = ""
            '''
        except:
            ''' ex. error can occur if one not enters username and password 
            and press login button, then reload the login page '''
            return "redirect(url_for('get_username'))"
    
        ''' login success with userID not null '''
        return "set session['userID'] and session['msg'] and redirect(url_for('get_list'))"

'''
sub-function of checkVals 
replace is defined in case one use comma in decimals (ex. 9,2) 
'''
def adjNums(key,val,adjval):
    if val[-1]=='0' and len(val)>2:
        adjval=round(int(adjval.replace(',','.'))/10,1) 
    elif len(val)<=2:
        adjval=int(adjval)
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
    playerIfExists = ubp.find_one({'userId':int(userID), 'name':{'$regex':'.*' + LongSubstr + '.*'}},{ "name": 1,"_id":1 })
    #use ndiff py function to find differences
    playerNotExists = True
    if (playerIfExists is not None):
        countDiffs = sum([i[0] != ' ' for i in ndiff(playerIfExists['name'],formName)]) #if same name and surname it exists so no new insert
        if int(countDiffs/2) <= 1: #assume max one "spelling" error
            playerNotExists = False
    return playerNotExists 
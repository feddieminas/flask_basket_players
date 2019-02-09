import os
from flask import Flask, render_template, redirect, request, url_for, session

app = Flask(__name__)
#app.secret_key = "fmd270584" 


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


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
    port=os.environ.get('PORT'),
    debug=True)
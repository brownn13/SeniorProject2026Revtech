from flask import Flask, render_template, request  # type: ignore[import-not-found]

app = Flask(__name__)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password1234':
            return render_template('dashboard.html')
        else:  
            return render_template("login.html", error="Invalid user or password")
    else:
        return render_template('login.html')
    
@app.route('/logout')
def logout():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
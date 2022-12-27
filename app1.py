
from flask import Flask, redirect, render_template, request, session, url_for , flash , get_flashed_messages , json , request
from flask_login import LoginManager , UserMixin , login_user , login_required , logout_user , current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash , check_password_hash
from sqlalchemy import exc
import os
import requests
from dotenv import load_dotenv
from flask_login import login_user, current_user, logout_user 

app = Flask(__name__)
load_dotenv()
global api_key
api_key=os.environ.get("api_key")
login_manager = LoginManager(app)
login_manager.init_app(app)
print(api_key)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
db = SQLAlchemy(app)


@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))

class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False , unique=True )
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/returnback')
def returnback():
    return render_template('home.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username,password)
        if current_user.is_authenticated:
         return redirect(url_for('home'))
        user = users.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
         flash("login successful")
         return render_template("index.html",username=username)
        else:
         flash("invalid username or password")
    return render_template("login.html")

@app.route('/register',methods=['GET', 'POST'])
def register():
    if request.method=="POST":
            username = request.form.get('username')
            Email = request.form.get('email')
            password = request.form.get('password')
            db.create_all()
            password_hash = generate_password_hash( password ,"pbkdf2:sha256" , salt_length=8)
            data = users(username=username, email=Email ,password= password_hash)
            try:
                db.session.add(data)
                db.session.commit()
                flash('Successfully registered user') 
            except exc.IntegrityError as e:
                flash('Username already exists')
                return render_template("register.html")
                
            return redirect(url_for("login"))
         
    else:
        return render_template("register.html") 
 
@app.route('/getWeather',methods=["POST","GET"])
def getWeather():
    cityy=request.form["city"]
    print(cityy)
    details={
        "q":  cityy,
        "aqi":"yes",
        "key":api_key
    }    
    
    global response
    response = requests.post(url="http://api.weatherapi.com/v1/current.json",data=details)
    
    if(response.status_code==200):
        location=response.json()['location']['name']
        state=response.json()['location']['region']
        country=response.json()['location']['country']
        temperature = response.json()['current']['temp_c'] 
        condition = response.json()['current']['condition']['text']
        icon=response.json()['current']['condition']['icon']
        return render_template("index.html",cityy=cityy,w_name=location,w_state=state,w_country=country,w_temp = temperature,symbol="° C",w_condition = condition,w_image=icon,isExist=0)

    else:
        return render_template("index.html",w_name="",w_state="",w_country="",w_temp="",w_condition="",w_image="",isExist=1)


def form():
    return render_template("index.html") 

@app.route("/logout")
def logout():
    logout_user()
    return render_template("home.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0' , port="5000" , debug=True)

    

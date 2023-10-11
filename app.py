import json
import datetime
from flask import Flask, jsonify, redirect, request,session , render_template, url_for
from flask_login import LoginManager, UserMixin, login_required,login_user,current_user
from flask_bcrypt import Bcrypt

from pymongo import DESCENDING, MongoClient
from bson import json_util,ObjectId
import os
mongo_user=os.getenv('MONGO_USER')
mongo_password=os.getenv('MONGO_PASSWORD')
mongo_address=os.getenv('MONGO_ADDRESS')

db= MongoClient(f'mongodb://{mongo_user}:{mongo_password}@{mongo_address}:27017')

class User(UserMixin):
    def __init__(self,id,username,pic):
        
        self.id = id
        self.username = username
        self.pic = pic
        self.roles=["reader"]

class Post():
    def __init__(self,title,game,message,poster_id,gamer_tag, posted_date,expiry_date=None):
        self.title = title
        self.game = game 
        self.message = message 
        self.poster_id=poster_id
        self.gamer_tag = gamer_tag
        self.posted_date = posted_date
        self.expiry_date = expiry_date

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

login_manager = LoginManager()

@login_manager.unauthorized_handler
def unauthenticated():
        
        return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    print(f"user_id {user_id}")
    #client=db
    #userdb=client.UserDB.users
    userdb = db.userProfiles.userProfiles
    
    u= userdb.find_one({'_id':ObjectId(user_id)})
    print(u)
    
    

    return User(id=u['_id'],username=u['username'],pic=u['profilePic'])

login_manager.init_app(app)

def parse_json(data):
    return json.loads(json_util.dumps(data))

@app.route('/')
def index():
    games_list=[]
    games=db.Games_list.games.find()
    for g in games:
        games_list.append(g)
    return render_template ("index.html", games_list=games_list)

@app.route('/api/postgame', methods=['POST'])
@login_required
def post_game():
    title= request.form.get('title')
    game =request.form.get('game')
    message = request.form.get('message')
    poster_id = current_user.id
    gamer_tag = request.form.get('gamer_tag')
    posted_date = datetime.datetime.now()
    expiry_date = None
    game = Post(title,game,message,poster_id,gamer_tag,posted_date,expiry_date)
    post_to_db={"title":game.title,"game":game.game,"message":game.message,"poster_id":game.poster_id,"gamer_tag":game.gamer_tag,'posted_date':game.posted_date}
    db.gamepost.game_post.insert_one(post_to_db)
    return "200"
    


@app.route('/protected')
@login_required
def protected():
    return "you are loged in"

@app.route('/api/data_test')    
def test_data():
    users=[]
    #data= db.loginUsers.created_users.find()
    data=db.gamepost.game_post.find().sort('posted_date',DESCENDING)
    for u in data:
        
        users.append(u)
    clean_data = parse_json(users) 
    return jsonify(clean_data)


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        #user=request.json["email"]
        #pw=request.json["password"]
        email= request.form ['email']
        user = request.form ['username']
        pw= request.form ['pwd']
        print(user)
        #user_exists = db.loginUsers.created_users.find_one({"email":user})
        if db.authDb.users.find_one({"email":email}):
            return "user in db"
        elif db.authDb.users.find_one({"username":user}):    
            return "username exists"
        else: 
            hashed_pw = bcrypt.generate_password_hash(pw)
            db.authDb.users.insert_one({"email":email,"password":hashed_pw,'username':user})
            requested_user = db.authDb.users.find_one({"email":email})
            print(requested_user)
            user_uid = requested_user["_id"]
            #add user to profile db
            db.userProfiles.userProfiles.insert_one({'auth_id':user_uid,'username':user,"profilePic":None})

            return "user Not in DB"
    else: return render_template("register.html")            

@app.route('/login',methods=['POST','GET'] )
def login():
    if request.method == 'POST':
        user = request.form ['username']
        pw= request.form ['pwd']
        query= db.authDb.users.find_one({"email":user})

        if db.authDb.users.find_one({"email":user}):
            print('user in db')
            
            
            if bcrypt.check_password_hash(query['password'],pw):
                
                user_name=db.userProfiles.userProfiles.find_one({"auth_id":ObjectId(query['_id'])})
                user_id = user_name['_id']
                print(user_id)
                user = User(user_id,user_name['username'],None)
                
                login_user(user)
                return redirect('/')
            else: return jsonify({"error":"unauthorized"}),401

        else: return jsonify({"error":"unauthorized"}),401
    else: return render_template("login.html")
@app.route('/logout')
def logout():
    session.pop('user')
    return "loged out"

@app.route('/api/register', methods=['GET','POST'])
def api_register():
    if request.method == 'POST':
        user=request.json["email"]
        pw=request.json["password"]
        #user = request.form ['username']
        #pw= request.form ['pwd']
        print(user)
        #user_exists = db.loginUsers.created_users.find_one({"email":user})
        if db.loginUsers.created_users.find_one({"email":user}):
            return "user in db"
        else: 
            hashed_pw = bcrypt.generate_password_hash(pw)
            db.loginUsers.created_users.insert_one({"email":user,"password":hashed_pw})
            requested_user = db.loginUsers.created_users.find_one({"email":user})
            user_uid = requested_user["_id"]
            print(user_uid)
            return "user Not in DB"
    else: return render_template("register.html")       

@app.route('/api/login',methods=['POST','GET'] )
def api_login():
    if request.method == 'POST':
        user=request.json["email"]
        pw=request.json["password"]
        #user = request.form ['username']
        #pw= request.form ['pwd']
        query= db.loginUsers.created_users.find_one({"email":user})

        if db.loginUsers.created_users.find_one({"email":user}):
            print('user in db')
            
            
            if bcrypt.check_password_hash(query['password'],pw):
                
                user_name=db.loginUsers.created_users.find_one({"email":user})
                user_id = user_name['_id']
                print(user_id)
                user = User(user_id,user_name['email'],None)
                
                login_user(user)
                return "200"
            else: return jsonify({"error":"unauthorized"}),401

        else: return jsonify({"error":"unauthorized"}),401
    else: return render_template("login.html")    

if __name__=="__main__":
    app.run(debug=True)
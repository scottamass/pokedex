import json
import datetime
from flask import Flask, Response, jsonify, redirect, request,session , render_template, url_for
from flask_login import LoginManager, UserMixin, login_required,login_user,current_user, logout_user
from flask_bcrypt import Bcrypt
import requests
from data.data import _pokeradar
from pymongo import DESCENDING, MongoClient
from bson import json_util,ObjectId
import os
from data.pokedex.gen1 import _gen1Dex
from data.pokedex.gen2 import _gen2pokedex

mongo_connect=os.getenv('M_CONNECTION_STRING')
print(f'connection--{mongo_connect}')
db= MongoClient(mongo_connect)
print(db)


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
    #print(f"user_id {user_id}")
    #client=db
    #userdb=client.UserDB.users
    userdb = db.userProfiles.userProfiles
    
    u= userdb.find_one({'_id':ObjectId(user_id)})
    #print(u)
    
    

    return User(id=u['_id'],username=u['username'],pic=u['profilePic'])

login_manager.init_app(app)

def parse_json(data):
    return json.loads(json_util.dumps(data))

@app.route('/')
@login_required
def index():
    games_list=[]
    games=db.gamepost.game_post.find({"poster_id": current_user.id}).sort('posted_date',DESCENDING)
    for g in games:
        print(current_user.id)
        game_data = db.Games.games_list.find_one({'gid':g['game']})
        print(game_data)
        post_id_str = str(g['_id']) 
        games={'postid':post_id_str,"title":g['title'],'gid':game_data['gid'],'gname':game_data['name'],'imgurl':game_data['image']}
        print(games)
        games_list.append(games)

    return render_template ("index.html", games_list=games_list)

@app.route('/api/postgame', methods=['POST'])
@login_required
def post_game():
    title= request.form.get('title')
    game = request.form.get('options')
    print(game)
    message = request.form.get('message')
    poster_id = current_user.id
    gamer_tag = request.form.get('gamer_tag')
    posted_date = datetime.datetime.now()
    expiry_date = None
    game = Post(title,game,message,poster_id,gamer_tag,posted_date,expiry_date)
    post_to_db={"title":game.title,"game":game.game,"poster_id":game.poster_id,'posted_date':game.posted_date,"caught":[]}
    db.gamepost.game_post.insert_one(post_to_db)
    return redirect(url_for('index'))
    
@app.route('/games/<id>')
@login_required
def game(id):
    games=db.gamepost.game_post.find_one({"_id": ObjectId(id)})

    #print(games)
    clean_data_progess = games 
    print(clean_data_progess)
    game_info= db.Games.games_list.find_one({'gid':clean_data_progess['game']})
    print(game_info)
    if game_info['gen'] == 'gen1':
        print('yes')
        dex = _gen1Dex
    else:
        print('no')
        dex = _gen2pokedex
    return render_template('pokedexsummary.html',clean_data_progess=clean_data_progess,game_info=game_info, pokedex=dex)

@app.route('/protected')
@login_required
def protected():
    return "you are loged in"

@app.route('/pokemon/<id>')
def pokemon(id):
    pokeapi_url = f"https://pokeapi.co/api/v2/pokemon/{id}/"
    response = requests.get(pokeapi_url)
    if response.status_code == 200:
        pokemon_data = response.json()
        print(pokemon_data)
        sprite_url = pokemon_data["sprites"]["front_default"]
        print(f"Sprite URL for {id.capitalize()}: {sprite_url}")
    else:
        print(f"Failed to retrieve data for {id.capitalize()}.")

    return sprite_url

@app.route('/caught/<gid>/<pid>',methods=['POST'])
def caught(gid,pid):
    referring_url = request.headers.get('Referer')
    print(gid)
    pid=int(pid)
    print(pid)
    db.gamepost.game_post.update_one({"_id": ObjectId(gid)},{'$push': {'caught': pid}})
    return redirect(referring_url)

@app.route('/api/caught/<gid>/<pid>',methods=['POST'])
def api_caught(gid,pid):
    print(gid)
    pid=int(pid)
    print(pid)
    db.gamepost.game_post.update_one({"_id": ObjectId(gid)},{'$push': {'caught': pid}})
    return "ok"

@app.route('/uncaught/<gid>/<pid>',methods=['POST'])
def uncaught(gid,pid):
    referring_url = request.headers.get('Referer')
    print(gid)
    pid=int(pid)
    print(pid)
    db.gamepost.game_post.update_one({"_id": ObjectId(gid)},{'$pull': {'caught': pid}})
    
    #return "200"
    return redirect(referring_url)

@app.route('/api/data_test')    
def test_data():
    users=[]
    #data= db.loginUsers.created_users.find()
    data=db.gamepost.game_post.find().sort('posted_date',DESCENDING)
    for u in data:
        
        users.append(u)
        #print(u)
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
    logout_user()
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
            return redirect(url_for('login'))
    else: return render_template("register.html")       
@app.route('/pokeradar/<id>/<gen>/<route>/<game>')
def pokeradar(id,gen,route,game):
    games=db.gamepost.game_post.find_one({"_id": ObjectId(id)})
  
    caught_array =games['caught']
    gid= games['_id']
    print(gid)
    game=str(game)
    route=str(route)
    gen=str(gen)
    data = _pokeradar['games']['gen'][gen]["routes"][route]
    if gen =="gen1":
        return render_template('pokeradar/gen1.html',data =data ,game=game ,ca=caught_array ,gid=gid)

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
    app.run(debug=True ,host='0.0.0.0' ,port='80')
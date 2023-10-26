import json
import datetime
from flask import Flask, Response, jsonify, redirect, request,session , render_template, url_for
from flask_login import LoginManager, UserMixin, login_required,login_user,current_user, logout_user
from flask_bcrypt import Bcrypt
from data.data import _pokeradar
from pymongo import DESCENDING, MongoClient
from bson import json_util,ObjectId
import os
from data.pokedex.gen1 import _gen1Dex
from data.pokedex.gen2 import _gen2pokedex
from functions.dbfunc import catch_or_uncatch_poke, get_game_from_db, get_games_from_db, post_game_to_db


mongo_connect=os.getenv('M_CONNECTION_STRING')
db= MongoClient(mongo_connect)

VERSION='0.5'

class User(UserMixin):
    def __init__(self,id,username,pic):
        
        self.id = id
        self.username = username
        self.pic = pic
        self.roles=["reader"]

class Post():
    def __init__(self,title,game,poster_id, posted_date):
        self.title = title
        self.game = game 
        self.poster_id=poster_id
        self.posted_date = posted_date
    

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

login_manager = LoginManager()

@login_manager.unauthorized_handler
def unauthenticated():
        
        return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    u= db.userProfiles.userProfiles.find_one({'_id':ObjectId(user_id)})
    if u is not None:
        return User(id=u['_id'],username=u['username'],pic=u['profilePic'])

login_manager.init_app(app)

def parse_json(data):
    return json.loads(json_util.dumps(data))

@app.route('/')
@login_required
def index():
    games_list=[]
    games=get_games_from_db(current_user.id)
    for g in games:
        game_data = db.Games.games_list.find_one({'gid':g['game']})
        post_id_str = str(g['_id']) 
        games={'postid':post_id_str,"title":g['title'],'gid':game_data['gid'],'gname':game_data['name'],'imgurl':game_data['image']}
        games_list.append(games)
    print(games_list)    
    return render_template ("index.html", games_list=games_list)

@app.route('/api/postgame', methods=['POST'])
@login_required
def post_game():
    title= request.form.get('title')
    game = request.form.get('options')
    poster_id = current_user.id
    posted_date = datetime.datetime.now()
    game = Post(title,game,poster_id,posted_date)
    post_game_to_db(game)
    return redirect(url_for('index'))
    
@app.route('/games/<id>')
@login_required
def game(id):
    games_list=get_games_from_db(current_user.id)
    clean_data_progess=get_game_from_db(id)
    game_info= db.Games.games_list.find_one({'gid':clean_data_progess['game']})
    if game_info['gen'] == 'gen1':
        dex = _gen1Dex
    else:
        dex = _gen2pokedex
    return render_template('pokedexsummary.html',clean_data_progess=clean_data_progess,game_info=game_info, pokedex=dex,games_list=games_list)

@app.route('/gamesummary/<id>')
@login_required
def game_summary(id):
    games_list=get_games_from_db(current_user.id)
    clean_data_progess=get_game_from_db(id)
    game_info= db.Games.games_list.find_one({'gid':clean_data_progess['game']})
    data = _pokeradar['games']['gen'][game_info['gen']]
    if game_info['gen'] == 'gen1':
        dex = _gen1Dex
    return render_template('pokeradar/gamesummary.html',games_list=games_list ,clean_data_progess=clean_data_progess,game_info=game_info, pokedex=dex,data=data)


@app.route('/caught/<gid>/<pid>',methods=['POST'])
def caught(gid,pid):
    referring_url = request.headers.get('Referer')
    pid=int(pid)
    catch_or_uncatch_poke(gid,pid,'$push')
    return redirect(referring_url)

@app.route('/api/caught/<gid>/<pid>',methods=['POST'])
def api_caught(gid,pid):
    pid=int(pid)
    catch_or_uncatch_poke(gid,pid,'$push')
    return "ok"

@app.route('/uncaught/<gid>/<pid>',methods=['POST'])
def uncaught(gid,pid):
    referring_url = request.headers.get('Referer')
    pid=int(pid)
    catch_or_uncatch_poke(gid,pid,'$pull')
    return redirect(referring_url)

@app.route('/pokeradar/<id>/<gen>/<route>/<game>')
def pokeradar(id,gen,route,game):
    games=get_game_from_db(id)
    caught_array =games['caught']
    gid= games['_id']
    game_info= db.Games.games_list.find_one({'gid':games['game']})
    print(gid)
    game=str(game)
    route=str(route)
    gen=str(gen)
    data = _pokeradar['games']['gen'][gen]["routes"][route]
    games_list=get_games_from_db(current_user.id)
    if gen =="gen1":
        return render_template('pokeradar/gen1.html',data =data ,game=game,clean_data_progess=games ,ca=caught_array,game_info=game_info ,gid=gid,games_list=games_list)
    if gen =="gen2":
        return render_template('pokeradar/gen1.html',data =data ,game=game,clean_data_progess=games ,ca=caught_array ,gid=gid,game_info=game_info,games_list=games_list)
    

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email= request.form ['email']
        user = request.form ['username']
        pw= request.form ['pwd']
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
            return redirect(url_for('login'))
    else: return render_template("register.html")            

@app.route('/login',methods=['POST','GET'] )
def login():
    if request.method == 'POST':
        user = request.form ['username']
        pw= request.form ['pwd']
        query= db.authDb.users.find_one({"email":user})
        if db.authDb.users.find_one({"email":user}):
            if bcrypt.check_password_hash(query['password'],pw):                
                user_name=db.userProfiles.userProfiles.find_one({"auth_id":ObjectId(query['_id'])})
                user_id = user_name['_id']
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


@app.route('/api/login',methods=['POST','GET'] )
def api_login():
    if request.method == 'POST':
        user=request.json["email"]
        pw=request.json["password"]
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
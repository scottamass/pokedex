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
mongo_user=os.getenv('MONGO_USER')
mongo_password=os.getenv('MONGO_PASSWORD')
mongo_address=os.getenv('MONGO_ADDRESS')

db= MongoClient(f'mongodb://{mongo_user}:{mongo_password}@{mongo_address}:27017')
pokedex = [
    { "id": 152, "name": "Chikorita" },
    { "id": 153, "name": "Bayleef" },
    { "id": 154, "name": "Meganium" },
    { "id": 155, "name": "Cyndaquil" },
    { "id": 156, "name": "Quilava" },
    { "id": 157, "name": "Typhlosion" },
    { "id": 158, "name": "Totodile" },
    { "id": 159, "name": "Croconaw" },
    { "id": 160, "name": "Feraligatr" },
    { "id": 161, "name": "Sentret" },
    { "id": 162, "name": "Furret" },
    { "id": 163, "name": "Hoothoot" },
    { "id": 164, "name": "Noctowl" },
    { "id": 165, "name": "Ledyba" },
    { "id": 166, "name": "Ledian" },
    { "id": 167, "name": "Spinarak" },
    { "id": 168, "name": "Ariados" },
    { "id": 169, "name": "Crobat" },
    { "id": 170, "name": "Chinchou" },
    { "id": 171, "name": "Lanturn" },
    { "id": 172, "name": "Pichu" },
    { "id": 173, "name": "Cleffa" },
    { "id": 174, "name": "Igglybuff" },
    { "id": 175, "name": "Togepi" },
    { "id": 176, "name": "Togetic" },
    { "id": 177, "name": "Natu" },
    { "id": 178, "name": "Xatu" },
    { "id": 179, "name": "Mareep" },
    { "id": 180, "name": "Flaaffy" },
    { "id": 181, "name": "Ampharos" },
    { "id": 182, "name": "Bellossom" },
    { "id": 183, "name": "Marill" },
    { "id": 184, "name": "Azumarill" },
    { "id": 185, "name": "Sudowoodo" },
    { "id": 186, "name": "Politoed" },
    { "id": 187, "name": "Hoppip" },
    { "id": 188, "name": "Skiploom" },
    { "id": 189, "name": "Jumpluff" },
    { "id": 190, "name": "Aipom" },
    { "id": 191, "name": "Sunkern" },
    { "id": 192, "name": "Sunflora" },
    { "id": 193, "name": "Yanma" },
    { "id": 194, "name": "Wooper" },
    { "id": 195, "name": "Quagsire" },
    { "id": 196, "name": "Espeon" },
    { "id": 197, "name": "Umbreon" },
    { "id": 198, "name": "Murkrow" },
    { "id": 199, "name": "Slowking" },
    { "id": 200, "name": "Misdreavous" },
    { "id": 201, "name": "Unown" },
    { "id": 202, "name": "Wobbuffet" },
    { "id": 203, "name": "Girafarig" },
    { "id": 204, "name": "Pineco" },
    { "id": 205, "name": "Forretress" },
    { "id": 206, "name": "Dunsparce" },
    { "id": 207, "name": "Gligar" },
    { "id": 208, "name": "Steelix" },
    { "id": 209, "name": "Snubbull" },
    { "id": 210, "name": "Granbull" },
    { "id": 211, "name": "Qwilfish" },
    { "id": 212, "name": "Scizor" },
    { "id": 213, "name": "Shuckle" },
    { "id": 214, "name": "Heracross" },
    { "id": 215, "name": "Sneasel" },
    { "id": 216, "name": "Teddiursa" },
    { "id": 217, "name": "Ursaring" },
    { "id": 218, "name": "Slugma" },
    { "id": 219, "name": "Magcargo" },
    { "id": 220, "name": "Swinub" },
    { "id": 221, "name": "Piloswine" },
    { "id": 222, "name": "Corsola" },
    { "id": 223, "name": "Remoraid" },
    { "id": 224, "name": "Octillery" },
    { "id": 225, "name": "Delibird" },
    { "id": 226, "name": "Mantine" },
    { "id": 227, "name": "Skarmory" },
    { "id": 228, "name": "Houndour" },
    { "id": 229, "name": "Houndoom" },
    { "id": 230, "name": "Kingdra" },
    { "id": 231, "name": "Phanpy" },
    { "id": 232, "name": "Donphan" },
    { "id": 233, "name": "Porygon2" },
    { "id": 234, "name": "Stantler" },
    { "id": 235, "name": "Smeargle" },
    { "id": 236, "name": "Tyrogue" },
    { "id": 237, "name": "Hitmontop" },
    { "id": 238, "name": "Smoochum" },
    { "id": 239, "name": "Elekid" },
    { "id": 240, "name": "Magby" },
    { "id": 241, "name": "Miltank" },
    { "id": 242, "name": "Blissey" },
    { "id": 243, "name": "Raikou" },
    { "id": 244, "name": "Entei" },
    { "id": 245, "name": "Suicune" },
    { "id": 246, "name": "Larvitar" },
    { "id": 247, "name": "Pupitar" },
    { "id": 248, "name": "Tyranitar" },
    { "id": 249, "name": "Lugia" },
    { "id": 250, "name": "Ho-Oh" },
    { "id": 251, "name": "Celebi" },
    { "id": 1, "name": "Bulbasaur" },
    { "id": 2, "name": "Ivysaur" },
    { "id": 3, "name": "Venusaur" },
    { "id": 4, "name": "Charmander" },
    { "id": 5, "name": "Charmeleon" },
    { "id": 6, "name": "Charizard" },
    { "id": 7, "name": "Squirtle" },
    { "id": 8, "name": "Wartortle" },
    { "id": 9, "name": "Blastoise" },
    { "id": 10, "name": "Caterpie" },
    { "id": 11, "name": "Metapod" },
    { "id": 12, "name": "Butterfree" },
    { "id": 13, "name": "Weedle" },
    { "id": 14, "name": "Kakuna" },
    { "id": 15, "name": "Beedrill" },
    { "id": 16, "name": "Pidgey" },
    { "id": 17, "name": "Pidgeotto" },
    { "id": 18, "name": "Pidgeot" },
    { "id": 19, "name": "Rattata" },
    { "id": 20, "name": "Raticate" },
    { "id": 21, "name": "Spearow" },
    { "id": 22, "name": "Fearow" },
    { "id": 23, "name": "Ekans" },
    { "id": 24, "name": "Arbok" },
    { "id": 25, "name": "Pikachu" },
    { "id": 26, "name": "Raichu" },
    { "id": 27, "name": "Sandshrew" },
    { "id": 28, "name": "Sandslash" },
    { "id": 29, "name": "Nidoran♀" },
    { "id": 30, "name": "Nidorina" },
    { "id": 31, "name": "Nidoqueen" },
    { "id": 32, "name": "Nidoran♂" },
    { "id": 33, "name": "Nidorino" },
    { "id": 34, "name": "Nidoking" },
    { "id": 35, "name": "Clefairy" },
    { "id": 36, "name": "Clefable" },
    { "id": 37, "name": "Vulpix" },
    { "id": 38, "name": "Ninetales" },
    { "id": 39, "name": "Jigglypuff" },
    { "id": 40, "name": "Wigglytuff" },
    { "id": 41, "name": "Zubat" },
    { "id": 42, "name": "Golbat" },
    { "id": 43, "name": "Oddish" },
    { "id": 44, "name": "Gloom" },
    { "id": 45, "name": "Vileplume" },
    { "id": 46, "name": "Paras" },
    { "id": 47, "name": "Parasect" },
    { "id": 48, "name": "Venonat" },
    { "id": 49, "name": "Venomoth" },
    { "id": 50, "name": "Digglet" },
    { "id": 51, "name": "Dugtrio" },
    { "id": 52, "name": "Meowth" },
    { "id": 53, "name": "Persian" },
    { "id": 54, "name": "Psyduck" },
    { "id": 55, "name": "Golduck" },
    { "id": 56, "name": "Mankey" },
    { "id": 57, "name": "Primeape" },
    { "id": 58, "name": "Growlithe" },
    { "id": 59, "name": "Arcanine" },
    { "id": 60, "name": "Poliwag" },
    { "id": 61, "name": "Poliwhirl" },
    { "id": 62, "name": "Poliwrath" },
    { "id": 63, "name": "Abra" },
    { "id": 64, "name": "Kadabra" },
    { "id": 65, "name": "Alakazam" },
    { "id": 66, "name": "Machop" },
    { "id": 67, "name": "Machoke" },
    { "id": 68, "name": "Machamp" },
    { "id": 69, "name": "Bellsprout" },
    { "id": 70, "name": "Weepinbell" },
    { "id": 71, "name": "Victreebel" },
    { "id": 72, "name": "Tentacool" },
    { "id": 73, "name": "Tentacruel" },
    { "id": 74, "name": "Geodude" },
    { "id": 75, "name": "Graveler" },
    { "id": 76, "name": "Golem" },
    { "id": 77, "name": "Ponyta" },
    { "id": 78, "name": "Rapidash" },
    { "id": 79, "name": "Slowpoke" },
    { "id": 80, "name": "Slowbro" },
    { "id": 81, "name": "Magnemite" },
    { "id": 82, "name": "Magneton" },
    { "id": 83, "name": "Farfetch'd" },
    { "id": 84, "name": "Doduo" },
    { "id": 85, "name": "Dodrio" },
    { "id": 86, "name": "Seel" },
    { "id": 87, "name": "Dewgong" },
    { "id": 88, "name": "Grimer" },
    { "id": 89, "name": "Muk" },
    { "id": 90, "name": "Shellder" },
    { "id": 91, "name": "Cloyster" },
    { "id": 92, "name": "Gastly" },
    { "id": 93, "name": "Haunter" },
    { "id": 94, "name": "Gengar" },
    { "id": 95, "name": "Onix" },
    { "id": 96, "name": "Drowzee" },
    { "id": 97, "name": "Hypno" },
    { "id": 98, "name": "Krabby" },
    { "id": 99, "name": "Kingler" },
    { "id": 100, "name": "Voltorb" },
    { "id": 101, "name": "Electrode" },
    { "id": 102, "name": "Exeggcute" },
    { "id": 103, "name": "Exeggutor" },
    { "id": 104, "name": "Cubone" },
    { "id": 105, "name": "Marowak" },
    { "id": 106, "name": "Hitmonlee" },
    { "id": 107, "name": "Hitmonchan" },
    { "id": 108, "name": "Lickitung" },
    { "id": 109, "name": "Koffing" },
    { "id": 110, "name": "Weezing" },
    { "id": 111, "name": "Rhyhorn" },
    { "id": 112, "name": "Rhydon" },
    { "id": 113, "name": "Chansey" },
    { "id": 114, "name": "Tangela" },
    { "id": 115, "name": "Kangaskhan" },
    { "id": 116, "name": "Horsea" },
    { "id": 117, "name": "Seadra" },
    { "id": 118, "name": "Goldeen" },
    { "id": 119, "name": "Seaking" },
    { "id": 120, "name": "Staryu" },
    { "id": 121, "name": "Starmie" },
    { "id": 122, "name": "Mr. Mime" },
    { "id": 123, "name": "Scyther" },
    { "id": 124, "name": "Jynx" },
    { "id": 125, "name": "Electabuzz" },
    { "id": 126, "name": "Magmar" },
    { "id": 127, "name": "Pinsir" },
    { "id": 128, "name": "Tauros" },
    { "id": 129, "name": "Magikarp" },
    { "id": 130, "name": "Gyarados" },
    { "id": 131, "name": "Lapras" },
    { "id": 132, "name": "Ditto" },
    { "id": 133, "name": "Eevee" },
    { "id": 134, "name": "Vaporeon" },
    { "id": 135, "name": "Jolteon" },
    { "id": 136, "name": "Flareon" },
    { "id": 137, "name": "Porygon" },
    { "id": 138, "name": "Omanyte" },
    { "id": 139, "name": "Omastar" },
    { "id": 140, "name": "Kabuto" },
    { "id": 141, "name": "Kabutops" },
    { "id": 142, "name": "Aerodactyl" },
    { "id": 143, "name": "Snorlax" },
    { "id": 144, "name": "Articuno" },
    { "id": 145, "name": "Zapdos" },
    { "id": 146, "name": "Moltres" },
    { "id": 147, "name": "Dratini" },
    { "id": 148, "name": "Dragonair" },
    { "id": 149, "name": "Dragonite" },
    { "id": 150, "name": "Mewtwo" },
    { "id": 151, "name": "Mew" }
]


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
        
        game_data = db.Games.games_list.find_one({'gid':g['game']})
        #print(game_data)
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
    return "200"
    
@app.route('/games/<id>')
@login_required
def game(id):
    games=db.gamepost.game_post.find_one({"_id": ObjectId(id)})

    #print(games)
    clean_data_progess = games 
    print(clean_data_progess)
    game_info= db.Games.games_list.find_one({'gid':clean_data_progess['game']})
    print(game_info)

    return render_template('pokedexsummary.html',clean_data_progess=clean_data_progess,game_info=game_info, pokedex=pokedex)

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
            return "user Not in DB"
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
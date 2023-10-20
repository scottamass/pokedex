from bson import ObjectId
from pymongo import DESCENDING, MongoClient
import os
mongo_connect=os.getenv('M_CONNECTION_STRING')
db= MongoClient(mongo_connect)

def post_game_to_db(game):
        post_to_db={"title":game.title,"game":game.game,"poster_id":game.poster_id,'posted_date':game.posted_date,"caught":[]}
        db.gamepost.game_post.insert_one(post_to_db)

def get_games_from_db(gameId):
        data=db.gamepost.game_post.find({"poster_id": gameId}).sort('posted_date',DESCENDING)
        return data

def get_game_from_db(id):
        data=db.gamepost.game_post.find_one({"_id": ObjectId(id)})
        return data    


def catch_or_uncatch_poke(gid,pid,caught):
        db.gamepost.game_post.update_one({"_id": ObjectId(gid)},{caught: {'caught': pid}})
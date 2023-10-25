from pymongo import DESCENDING, MongoClient
import os
mongo_connect=os.getenv('M_CONNECTION_STRING')
db= MongoClient(mongo_connect)

print(mongo_connect)
#query=db.Games.games_list.find({})
db.Games.games_list.insert_many([{
 
  "name": "crystal",
  "image": "https://assets-prd.ignimgs.com/2021/12/14/pokemoncrystal-1639519080473.jpg",
  "gid": "1",
  "gen": "gen2",
  "max": 251
},
{
  
  "name": "red",
  "image": "https://m.media-amazon.com/images/M/MV5BYTRlNjQ1NGMtNmU1Ny00MmRkLWE2NzQtMWUzNDc2ZWI2YWE2XkEyXkFqcGdeQXVyMzM4MjM0Nzg@._V1_.jpg",
  "gid": "2",
  "gen": "gen1",
  "max": 151
},
{
  
  "name": "yellow",
  "image": "https://m.media-amazon.com/images/M/MV5BYTQ2ZDkyYTMtMDVjYy00OGI2LTkxZTYtN2UzYjk3YmVkZGUxXkEyXkFqcGdeQXVyMzM4MjM0Nzg@._V1_.jpg",
  "gid": "3",
  "gen": "gen1",
  "max": 151
}])
query = db.Games.games_list.find({})
print(query)
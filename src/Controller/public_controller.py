from fastapi import HTTPException
from src.Config.db import publicCollection, postCollection
from src.Auths.auth import hashingPassword,verifyPassword,create_token
from datetime import datetime 
from fastapi.encoders import jsonable_encoder
from bson import ObjectId

# ==== Register User =====
async def register_user(user):
    existUser = await publicCollection.find_one({
        "email":user.email
    })
    if existUser:
        raise HTTPException(404,detail="User already exist!")
    
    hashPassword = hashingPassword(user.password)
    createUser = {
        "name" : user.name,
        "email" : user.email,
        "mobile" : user.mobile,
        "createdAt" : datetime.utcnow(),
        "password" : hashPassword,
        "followings":[],
        "followers":[],
        "numOfFollowers":0,
        "numOfFollowings":0,
        "username":user.username,
        "savedPosts":[]
    }

    publicCollection.insert_one(createUser)
    return {
        "message":"Registraion Successfull",
    }

# ==== Login User =====
async def loginUser(data):
    user = await publicCollection.find_one({
        "email":data.email
    })
    if not user:
        raise HTTPException(404,detail="User not Exist")
    isValidPassword = verifyPassword(data.password,user["password"])
    if not isValidPassword:
        raise HTTPException(401, detail="Invalid Password")
    token = create_token({
        "_id":str(user["_id"]),
        "email":user["email"]
    })
    print("Type of user id:- ",type(user["_id"]))

    return {
        "token":token
    }

# ====== Get Users ===
async def allUsers():
    users = await publicCollection.find().to_list(length=None)
    if not users:
        raise HTTPException(404, detail="User not available")
     
    return jsonable_encoder(
        users,
        custom_encoder={ObjectId:str}
    )

# ====== all posts =====
async def allposts():
    # posts = await postCollection.find().sort("createdAt",-1).to_list(length=None)
    posts = await postCollection.aggregate([
        {
            "$lookup":{
                "from":"users",
                "localField":"user_id",
                "foreignField":"_id",
                "as":"user"
            }
        },
        {
            "$unwind":"$user"
        }
    ]).to_list(length=None)
    if not posts:
        raise HTTPException(404,detail="Not Posts yet!")

    return jsonable_encoder(
        posts,
        custom_encoder={ObjectId:str}
    )

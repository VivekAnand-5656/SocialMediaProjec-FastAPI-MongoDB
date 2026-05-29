from fastapi import HTTPException,Depends
from src.Config.db import db, publicCollection
from src.Auths.auth import hashingPassword,verifyPassword,create_token
from datetime import datetime
from src.Dependencies.check import isLogin

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
        "password" : hashPassword
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

    return {
        "token":token
    }

# ====== Get Users ===
async def allUsers(user):
    users = await publicCollection.find().to_list(length=None)
    if not users:
        raise HTTPException(404, detail="User not available")
    for us in users:
        us["_id"] = str(us["_id"])
    return users


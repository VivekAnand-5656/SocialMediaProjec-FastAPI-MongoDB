from fastapi import HTTPException
from datetime import datetime
from src.Config.cloudinary_config import upload_image
from src.Config.db import postCollection, publicCollection
from bson import ObjectId
from fastapi.encoders import jsonable_encoder

# ==== Create Post ====
async def createPost(caption: str, file, user):
    try:
        image = upload_image(file.file)
        print("id type:- ",type(user["_id"]))

        newpost = {
            "caption": caption,
            "image_url": image["url"],
            "public_id": image["public_id"],
            "likes": [],
            "comments": [],
            "user_id": ObjectId(user["_id"]),  
            "createdAt": datetime.utcnow()
        }

        result = await postCollection.insert_one(newpost)

        post = await postCollection.find_one(
            {"_id": result.inserted_id}
        )

        post["_id"] = str(post["_id"])
        post["user_id"] = str(post["user_id"])

        return {
            "message": "Post Created Successfully",
            "post": post
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============== Edit Posts =======
async def editPost(postId:str,caption:str,user):
    post = await postCollection.find_one(
        {"_id":ObjectId(postId)}
    )
    if not post:
        raise HTTPException(404,detail="Post not found!")
    await postCollection.update_one(
        {"_id":post["_id"]},
        {
            "$set":{
                "caption":caption
            }
        }
    )
    updatedPost = await postCollection.find_one(
        {"_id":post["_id"]}
    )
    return jsonable_encoder(
        updatedPost,
        custom_encoder={ObjectId:str}
    )
# =============== Delete Post ===========
async def deletePost(postId:str,user):
    post = await postCollection.find_one(
        {"_id":ObjectId(postId)}
    )
    if not post:
        raise HTTPException(404,detail="Post not found")
    await postCollection.delete_one(
        {"_id":post["_id"]}
    )

    return {
        "message":"Post Deleted Successfully"
    }
# =============== Get Posts ========
async def getPosts():
    try:
        posts = await postCollection.aggregate([
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "_id",
                    "as": "user"
                }
            },
            {
                "$unwind": "$user"
            }
        ]).to_list(None)

        for post in posts:
            post["_id"] = str(post["_id"])
            post["user_id"] = str(post["user_id"])
            if "user" in post:
                post["user"]["_id"] = str(post["user"]["_id"])
            for like in post["likes"]:
                like["user_id"] = str(like["user_id"])


        return jsonable_encoder(
            posts,
            custom_encoder={ObjectId:str}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ======== Likes ======
async def likePost(postId:str,user):
    post = await postCollection.find_one({
        "_id":ObjectId(postId)
    })
    if not post:
        raise HTTPException(404,detail="Post not found")
    for like in post["likes"]:
        if like["user_id"] == user["_id"]:
            await postCollection.update_one(
                {"_id":ObjectId(postId)},
                {
                    "$pull":{
                        "likes":{
                            "user_id":like["user_id"]
                        }
                    }
                }
            )
            return {
                "message":"Unliked this post"
            }
    likedbyuser = await publicCollection.find_one(
        {"_id":ObjectId(user["_id"])}
    ) 
    
    postCollection.update_one(
        {"_id":ObjectId(postId)},
        {
            "$addToSet":{
                "likes":{
                    "user_id":user["_id"], 
                    "name":likedbyuser["name"]
                } 
            }
        }
    ) 
    return {
        "message":"Liked this post" 
    }

# === Comment ===
async def commentPost(postId:str,comment:str,user):
    post = postCollection.find_one(
        {"_id":ObjectId(postId)}
    )
    if not post:
        raise HTTPException(404,detail="Post not found!")
    
    commentByuser = await publicCollection.find_one(
        {"_id":ObjectId(user["_id"])}
    )
    newComment = {
        "user_id":user["_id"],
        "comment":comment,
        "user_id":user["_id"], 
        "name":commentByuser["name"]
    }
    postCollection.update_one(
        {"_id":ObjectId(postId)},
        {
            "$push":{
                "comments":newComment 
            }
        }
    )
    return {
        "message":"Comment on this post",
        "comment":newComment
    }
# =========== Follow =======
async def follow(userId:str,user):
    followingUser = await publicCollection.find_one(
        {"_id":ObjectId(userId)}
    ) 

    if not followingUser:
        raise HTTPException(404, detail="User not exist!")
    
    if ObjectId(userId) == ObjectId(user["_id"]):
        raise HTTPException(400,detail="You can't follow yourself!")
    
    for usr in followingUser["followers"]:
        if usr["user_id"] == user["_id"]:
            raise HTTPException(400,detail="Already followed this account!")
    
    await publicCollection.update_one(
        {"_id":ObjectId(user["_id"])},
        {
            "$addToSet":{
                "followings":{
                    "user_id":followingUser["_id"],
                    "username":followingUser["username"],
                    "name":followingUser["name"],
                    "image_url":followingUser["image_url"]
                }
            }
        }
    )
    await publicCollection.update_one(
        {"_id":ObjectId(userId)},
        {
            "$addToSet":{
                "followers":{
                    "user_id":user["_id"],
                    "username":user["username"],
                    "name":user["name"],
                    "image_url":user["image_url"]
                }
            }
        }
    )

    return {
        "message":"Follow Successfully" 
    }

# == Unfollow ==
async def unfollow(userId:str,user):
    followingUser = await publicCollection.find_one(
        {"_id":ObjectId(userId)}
    )
    if not followingUser:
        raise HTTPException(404,detail="User not found")
    
    isFollowing = False
    for follower in followingUser.get("followers",[]):
        if follower["user_id"] == user["_id"]:
            isFollowing = True
            break
    
    if not isFollowing:
        raise HTTPException(400,detail="You are not following this account!")
    
    await publicCollection.update_one(
        {"_id":ObjectId(user["_id"])},
        {
            "$pull":{
                "followings":{
                    "user_id":followingUser["_id"]
                }
            }
        }
    )

    await publicCollection.update_one(
        {"_id":ObjectId(userId)},
        {
            "$pull":{
                "followers":{
                    "user_id":user["_id"]
                }
            }
        }
    )

    return {
        "message":"Unfollow this account successfully!"
    }


# ================= Profile Features ================
# ------- View Profile -----
async def viewProfile(user):
    profile = await publicCollection.find_one(
        {"_id":ObjectId(user["_id"])}
    )
    if not profile:
        raise HTTPException(404,detail="User not found")
    # profile["_id"] = str(profile["_id"])
    return jsonable_encoder(
        profile,
        custom_encoder={ObjectId:str}
    )

# -------- Update Profile ---------
async def updateProfile(name:str,email:str,mobile:str,username:str, file, user):

    curentUser = await publicCollection.find_one(
        {"_id": ObjectId(user["_id"])}
    )

    if not curentUser:
        raise HTTPException(
            status_code=404,
            detail="User not exist!"
        )

    update_data = {
        "name": name,
        "email": email,
        "mobile": mobile,
        "username":username
    }

    if file:
        image = upload_image(file.file)
        update_data["image_url"] = image["url"]

    await publicCollection.update_one(
        {"_id": curentUser["_id"]},
        {
            "$set": update_data
        }
    )

    updatedUser = await publicCollection.find_one(
        {"_id": curentUser["_id"]}
    ) 

    return jsonable_encoder(
        {
            "message": "Profile Updated",
            "user": updatedUser
        },
        custom_encoder={ObjectId:str}
    )

# ========== Find Users ========
async def findusers(name:str,user):

    users = await publicCollection.find(
        {
            "$or": [
            {"name": {"$regex": name, "$options": "i"}},
            {"username": {"$regex": name, "$options": "i"}}
            ]
        }
    ).to_list(length=None) 
    return jsonable_encoder(
        users,
        custom_encoder={ObjectId:str}
    )

# =============== My Followers ============
async def myFollowers(user):
    userdata = await publicCollection.find_one(
        {"_id":ObjectId(user["_id"])}
    ) 
    followerIds = []
    for follower in userdata["followers"]:
        followerIds.append(ObjectId(follower["user_id"]))

    followers = await publicCollection.find(
        {
            "_id":{
                "$in":followerIds
            }
        }
    ).to_list(length=None)
    
    return jsonable_encoder(
        followers,
        custom_encoder={ObjectId:str}
    )
    
# ====== 
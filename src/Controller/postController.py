from fastapi import HTTPException
from datetime import datetime
from src.Config.cloudinary_config import upload_image
from src.Config.db import postCollection, publicCollection
from bson import ObjectId

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
    return {
        "message":"Post Updated Successfully"
    }
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


        return posts

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
    newlike = {
        "user_id":user["_id"]
    }
    postCollection.update_one(
        {"_id":ObjectId(postId)},
        {
            "$push":{
                "likes":newlike
            }
        }
    ) 
    return {
        "message":"Liked this post",
        "newlike":newlike
    }

# === Comment ===
async def commentPost(postId:str,comment:str,user):
    post = postCollection.find_one(
        {"_id":ObjectId(postId)}
    )
    if not post:
        raise HTTPException(404,detail="Post not found!")
        
    newComment = {
        "user_id":user["_id"],
        "comment":comment
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
            "$push":{
                "followings":{
                    "user_id":followingUser["_id"]
                }
            }
        }
    )
    await publicCollection.update_one(
        {"_id":ObjectId(userId)},
        {
            "$push":{
                "followers":{
                    "user_id":user["_id"]
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
    profile["_id"] = str(profile["_id"])
    return profile

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

    updatedUser["_id"] = str(updatedUser["_id"])

    return updatedUser
from fastapi import HTTPException
from datetime import datetime
from src.Schema.postSchema import CommentPost,CreatePost
from src.Config.cloudinary_config import upload_image, upload_reel
from src.Config.db import postCollection, publicCollection
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
import cloudinary

# ==== Create Post ====
async def createPost(body, file, user):
    try:
        image = upload_image(file.file)
        print("id type:- ",type(user["_id"]))

        newpost = {
            "caption": body.caption,
            "post_url": image["url"],
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
# ============== Upload Reel ===============
async def createReel(body,file,user):
    try:
        video = upload_reel(file.file)
        newpost = {
            "caption": body.caption,
            "post_url": video["url"],
            "public_id": video["public_id"],
            "likes": [],
            "comments": [],
            "user_id": ObjectId(user["_id"]),  
            "createdAt": datetime.utcnow()
        }
        result = await postCollection.insert_one(newpost)
        newreel = await postCollection.find_one(
            {"_id":result.inserted_id}
        )

        return jsonable_encoder(
            {
                "msg":"Reel Uploaded Successfully",
                "Reel":newreel
            },
            custom_encoder={ObjectId:str}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # ============ Find Reel ========
async def findReel(user):
    try:
        reels = await postCollection.find(
            {"post_url":{"$exists":True}}
        ).sort({"createdAt":1}).to_list(length=None)
        if not reels:
            raise HTTPException(404,detail="Reels not uploaded!")
        return jsonable_encoder(
            reels,
            custom_encoder={ObjectId:str}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

     
# =============== Edit Posts =======
async def editPost(postId:str,body,user):
    try:
        post = await postCollection.find_one(
            {"_id":ObjectId(postId)}
        )
        if not post:
            raise HTTPException(404,detail="Post not found!")
        await postCollection.update_one(
            {"_id":post["_id"]},
            {
                "$set":{
                    "caption":body.caption
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# =============== Delete Post ===========
async def deletePost(postId:str,user):
    try:
        post = await postCollection.find_one(
            {"_id":ObjectId(postId)}
        )
        if not post:
            raise HTTPException(404,detail="Post not found")
        
        if "public_id" in post:
            cloudinary.uploader.destroy(
                post["public_id"],
                resource_type="video",

            )
        if "public_id" in post:
            cloudinary.uploader.destroy(
                post["public_id"],
                resource_type="image",

            )
            

        await postCollection.delete_one(
            {"_id":post["_id"]}
        )

        return {
            "message":"Post Deleted Successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============== Get Posts ========
async def getPosts(user):
    try:
        posts = await postCollection.aggregate([
            {
                "$match": {
                    "user_id": ObjectId(user["_id"])
                }
            },
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
        if not posts:
            raise HTTPException(404,detail="Empty Posts")

        return jsonable_encoder(
            posts,
            custom_encoder={ObjectId:str}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ==================== Saved Post =============
async def savePost(postId:str,user):
    try:
        post = await postCollection.find_one({
            "_id":ObjectId(postId)
        })
        if not post:
            raise HTTPException(404,detail="Post not found")
        
        isSavePost = await publicCollection.find_one(
            {
                "_id":ObjectId(user["_id"]),
                "savedPosts.post_id": {
                    "$in": [post["_id"]]
                }
            }
        )
        if isSavePost:
            raise HTTPException(401,detail="Post already saved !")

        await publicCollection.update_one(
            {"_id": ObjectId(user["_id"])},
            {
                "$addToSet":{
                    "savedPosts":{
                        "post_id":post["_id"]
                    }
                }
            }
        ) 
        return jsonable_encoder(
            {
                "msg":"Post Saved Successfully" 
            },
            custom_encoder={ObjectId:str}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ============== Saved Posts ==========
async def savedposts(userId:str,user):
    try:
        posts = await postCollection.find({"_id":ObjectId(userId)}).to_list(length=None)
        if not posts:
            raise HTTPException(404,detail="Not Posts Saved !")
        return jsonable_encoder(
            posts,
            custom_encoder={ObjectId:str}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ Unsave Post ==========
async def unSavePost(postId:str,user):
    try:
        isSavePost = await publicCollection.find_one(
            {
                "_id":ObjectId(user["_id"]),
                "savedPosts.post_id": {
                    "$in": [ObjectId(postId)]
                }
            }
        )
        if not isSavePost:
            raise HTTPException(401,detail="Post not saved !")
        await publicCollection.update_one(
            {"_id":ObjectId(user["_id"])},
            {
                "$pull":{
                    "savedPosts":{
                        "post_id":ObjectId(postId)
                    }
                },
            }
        )

        return jsonable_encoder(
            {
                "msg":"Post UnSaved Successfully" 
            },
            custom_encoder={ObjectId:str}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ======== Likes ======
async def likePost(postId:str,user):
    try:
        post = await postCollection.find_one({
            "_id":ObjectId(postId)
        })
        if not post:
            raise HTTPException(404,detail="Post not found")
         
        likedbyuser = await publicCollection.find_one(
            {"_id":ObjectId(user["_id"])}
        ) 
        likdeuserdata = {
            "user_id":user["_id"], 
            "name":likedbyuser["name"],
            "username":likedbyuser["username"],
        }
        if "image_url" in likedbyuser:
            likdeuserdata["image_url"]=likedbyuser["image_url"]
        postCollection.update_one(
            {"_id":ObjectId(postId)},
            {
                "$addToSet":{
                    "likes":likdeuserdata 
                }
            } 
        ) 
        return {
            "message":"Liked this post" 
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ------------- Unlike ----------
async def unlikepost(postId:str,user):
    try:
        isliked = await postCollection.find_one(
            {
                "_id":ObjectId(postId),
                "likes.user_id":{
                    "$in":[ObjectId(user["_id"])]
                }
            }
        )
        if isliked:
            raise HTTPException(401,detail="Post is also unliked!")
        likedbyuser = await publicCollection.find_one(
            {"_id":ObjectId(user["_id"])}
        ) 
        await postCollection.update_one(
            {"_id":ObjectId(postId)},
            {
                "$pull":{
                    "likes":{
                        "user_id":user["_id"], 
                        "name":likedbyuser["name"],
                        "username":likedbyuser["username"]
                    }
                }
            }
        )
        return jsonable_encoder(
            {
                "message":"Unliked this post"
            },
            custom_encoder={ObjectId:str}
        )
    

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Comment ===
async def commentPost(postId:str,body,user):
    try:
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
            "comment":body.comment,
            "user_id":user["_id"], 
            "name":commentByuser["name"]
        }
        if "image_url" in commentByuser:
            newComment["image_url"] = commentByuser["image_url"]
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =========== Follow =======
async def follow(userId:str,user):
    try:
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
        
        findFollower = await publicCollection.find_one(
            {"_id":ObjectId(user["_id"])}
        )

        await publicCollection.update_one(
            {"_id":ObjectId(user["_id"])},
            {
                "$addToSet": {
                    "followings":{
                        "user_id":followingUser["_id"],
                        "username":followingUser["username"],
                        "name":followingUser["name"], 
                    }
                },
                "$inc":{
                    "numOfFollowings":1
                }
            }
        ) 
        
        await publicCollection.update_one(
            {"_id":ObjectId(userId)},
            {
                "$addToSet":{
                    "followers":{
                        "user_id":user["_id"],
                        "username":findFollower["username"],
                        "name":findFollower["name"], 
                    }
                },
                "$inc":{
                    "numOfFollowers":1
                }
            }
        ) 
        return {
            "message":"Follow Successfully" 
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# == Unfollow ==
async def unfollow(userId:str,user):
    try:
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
        
        findFollower = await publicCollection.find_one(
            {"_id":ObjectId(user["_id"])}
        )

        await publicCollection.update_one(
            {"_id":ObjectId(user["_id"])},
            {
                "$pull":{
                    "followings":{
                        "user_id":followingUser["_id"]
                    }
                },
                "$inc":{
                    "numOfFollowings":-1
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
                },
                "$inc":{
                    "numOfFollowers":-1
                }
            }
        ) 
        

        return {
            "message":"Unfollow this account successfully!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================= Profile Features ================
# ------- View Profile -----
async def viewProfile(user):
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------- Update Profile ---------
async def updateProfile(name:str,email:str,mobile:str,username:str, file, user):
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== Find Users ========
async def findusers(name:str,user):
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============== My Followers ============
async def myFollowers(user):
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====== My Following ============
async def myFollowings(user):
    try:
        userData = await publicCollection.find_one(
            {"_id":ObjectId(user["_id"])}
        )
        followingIds = []
        for follwing in userData["followings"]:
            followingIds.append(ObjectId(follwing["user_id"]))
        follwings = await publicCollection.find(
            {
                "_id":{
                    "$in":followingIds
                }
            }
        ).to_list(length=None)

        return jsonable_encoder(
            follwings,
            custom_encoder={ObjectId:str}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Search user by id ================
async def userById(userId:str,user):
    try:
        userData = await publicCollection.find_one(
            {"_id":ObjectId(userId)}
        )

        if not userData:
            raise HTTPException(404,detail="User not found")
        
        return jsonable_encoder(
            userData,
            custom_encoder={ObjectId:str}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

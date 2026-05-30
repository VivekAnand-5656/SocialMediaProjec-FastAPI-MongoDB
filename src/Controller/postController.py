from fastapi import HTTPException
from datetime import datetime
from src.Config.cloudinary_config import upload_image
from src.Config.db import postCollection
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
            print("User id:- ",like["user_id"],"Type of := ",type(like["user_id"])," ",type(user["_id"]))
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
        "message":"Liked this post"
    }
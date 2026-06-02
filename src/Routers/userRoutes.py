from fastapi import APIRouter, Depends,File, UploadFile, Form
from src.Dependencies.check import isLogin 
from src.Controller import postController
from src.Schema.userSchema import UpdateProfile
userroutes = APIRouter(prefix="/user",tags=["User"])

@userroutes.post("/createpost")
async def postCreate(caption:str = Form(...),file: UploadFile= File(...),user=Depends(isLogin)):
    return await postController.createPost(caption,file,user)

@userroutes.post("/createreel")
async def reelcreate(caption:str = Form(...),file:UploadFile=File(...),user=Depends(isLogin)):
    return await postController.createReel(caption,file,user)

@userroutes.get("/reels")
async def reels(user=Depends(isLogin)):
    return await postController.findReel(user)

@userroutes.put("/updatepost/{postId}")
async def updatePost(postId:str,caption:str,user=Depends(isLogin)):
    return await postController.editPost(postId,caption,user)

@userroutes.delete("/deletepost/{postId}")
async def deletepost(postId:str,user=Depends(isLogin)):
    return await postController.deletePost(postId,user)

@userroutes.get("/posts")
async def allposts():
    return await postController.getPosts() 

@userroutes.put("/savepost/{postId}")
async def saveposts(postId:str,user=Depends(isLogin)):
    return await postController.savePost(postId,user)

@userroutes.put("/unsavepost/{postId}")
async def unsaveposts(postId:str,user=Depends(isLogin)):
    return await postController.unSavePost(postId,user)

@userroutes.put("/likepost/{postId}")
async def postlike(postId:str,user=Depends(isLogin)):
    return await postController.likePost(postId,user)

@userroutes.put("/commentpost/{postId}")
async def postComment(postId:str,comment:str,user=Depends(isLogin)):
    return await postController.commentPost(postId,comment,user)

@userroutes.put("/follow/{userId}")
async def followUser(userId:str,user=Depends(isLogin)):
    return await postController.follow(userId,user)

@userroutes.put("/unfollow/{userId}")
async def unfollow(userId:str,user=Depends(isLogin)):
    return await postController.unfollow(userId,user)

# ============== Profile Features ====
@userroutes.get("/profile")
async def profile(user=Depends(isLogin)):
    return await postController.viewProfile(user)

@userroutes.put("/updateprofile")
async def profileupdate(
    name:str = Form(...),
    email:str = Form(...),
    mobile:str = Form(...),
    username:str = Form(...),
    file:UploadFile=File(...),user=Depends(isLogin)):
    return await postController.updateProfile(
        name,
        email,
        mobile,
        username,
        file,
        user
    )

# ========== Find Users =============
@userroutes.get("/findusers")
async def allusers(name:str,user=Depends(isLogin)):
    return await postController.findusers(name,user)

# ========= My Followers =========
@userroutes.get("/myfollowers")
async def followers(user=Depends(isLogin)):
    return await postController.myFollowers(user)

# ========= My Followings =========
@userroutes.get("/myfollowings")
async def followings(user=Depends(isLogin)):
    return await postController.myFollowings(user)

# ====== Find User by id =========
@userroutes.get("/userbyid/{userId}")
async def findUserById(userId:str,user=Depends(isLogin)):
    return await postController.userById(userId,user)

from fastapi import APIRouter, Depends,File, UploadFile, Form
from src.Dependencies.check import isLogin 
from src.Controller import postController
from src.Schema.userSchema import UpdateProfile
userroutes = APIRouter(prefix="/user",tags=["User"])

@userroutes.post("/createpost")
async def postCreate(caption:str = Form(...),file: UploadFile= File(...),user=Depends(isLogin)):
    return await postController.createPost(caption,file,user)

@userroutes.put("/updatepost")
async def updatePost(postId:str,caption:str,user=Depends(isLogin)):
    return await postController.editPost(postId,caption,user)

@userroutes.delete("/deletepost")
async def deletepost(postId:str,user=Depends(isLogin)):
    return await postController.deletePost(postId,user)

@userroutes.get("/posts")
async def allposts():
    return await postController.getPosts() 

@userroutes.put("/likepost")
async def postlike(postId:str,user=Depends(isLogin)):
    return await postController.likePost(postId,user)

@userroutes.put("/commentpost")
async def postComment(postId:str,comment:str,user=Depends(isLogin)):
    return await postController.commentPost(postId,comment,user)

@userroutes.put("/follow")
async def followUser(userId:str,user=Depends(isLogin)):
    return await postController.follow(userId,user)

@userroutes.put("/unfollow")
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
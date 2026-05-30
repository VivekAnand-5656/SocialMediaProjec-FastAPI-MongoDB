from fastapi import APIRouter, Depends,File, UploadFile, Form
from src.Dependencies.check import isLogin 
from src.Controller import postController
userroutes = APIRouter(prefix="/user",tags=["User"])

@userroutes.post("/createpost")
async def postCreate(caption:str = Form(...),file: UploadFile= File(...),user=Depends(isLogin)):
    return await postController.createPost(caption,file,user)

@userroutes.get("/posts")
async def allposts():
    return await postController.getPosts() 

@userroutes.put("/likepost")
async def postlike(postId:str,user=Depends(isLogin)):
    return await postController.likePost(postId,user)
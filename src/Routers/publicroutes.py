from fastapi import APIRouter, Depends
from src.Controller import public_controller
from src.Schema.userSchema import CreateUser, LoginUser
from src.Dependencies.check import isLogin

publicroutes = APIRouter(prefix="/public",tags=["Public Routes"])

@publicroutes.get("/welcome")
async def welcome():
    return {
        "message":"Welcome to Social Medial Web Project"
    }
# ======== Register User ===========
@publicroutes.post("/createUser")
async def createUser(user:CreateUser):
    return await public_controller.register_user(user)

# ======== Login User ===========
@publicroutes.post("/login")
async def login(data:LoginUser):
    return await public_controller.loginUser(data)

# ====== ALl Users ===
@publicroutes.get("/users")
async def allusers(user = Depends(isLogin)):
    return await public_controller.allUsers(user)
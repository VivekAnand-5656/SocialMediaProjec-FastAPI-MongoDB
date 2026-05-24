from fastapi import APIRouter

publicroutes = APIRouter(prefix="/public",tags=["Public Routes"])

@publicroutes.get("/welcome")
async def welcome():
    return {
        "message":"Welcome to Social Medial Web Project"
    }
# ======== Register User ===========
# ======== Login User ===========
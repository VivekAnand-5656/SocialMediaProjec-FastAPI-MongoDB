from fastapi import FastAPI
import src.Config.cloudinary_config 
from src.Routers.publicroutes import publicroutes
from src.Routers.userRoutes import userroutes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Social Media Project"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(userroutes)
app.include_router(publicroutes)
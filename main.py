from fastapi import FastAPI
print("Main Started")
import src.Config.cloudinary_config
print("After Cloudinary importe") 
from src.Routers.publicroutes import publicroutes
from src.Routers.userRoutes import userroutes

app = FastAPI(
    title="Social Media Project"
)

app.include_router(userroutes)
app.include_router(publicroutes)
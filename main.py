from fastapi import FastAPI
from src.Routers.publicroutes import publicroutes
app = FastAPI(
    title="Social Media Project"
)

app.include_router(publicroutes)
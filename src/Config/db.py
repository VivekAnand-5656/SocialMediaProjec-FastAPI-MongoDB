from dotenv import load_dotenv
import os
from motor.motor_asyncio import AsyncIOMotorClient
load_dotenv()

MONGO_URL=os.getenv("MONGO_URL","")
MONGO_NAME=os.getenv("MONGO_NAME","")

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_NAME]

publicCollection = db["users"]

from dotenv import load_dotenv
import os
from motor.motor_asyncio import AsyncIOMotorClient
load_dotenv()

MONGO_URL=os.getenv("MONGO_URL","")
DB_NAME=os.getenv("DB_NAME","")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

publicCollection = db["users"]
postCollection = db["posts"]

import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

print("Before")
print("API_KEY =", os.getenv("API_KEY"))
print("CLOUD_NAME =", os.getenv("CLOUD_NAME"))
print("After")
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET") ,
    secure=True
)
 
print("API KEY =", cloudinary.config().api_key)
print("CLOUD NAME =", cloudinary.config().cloud_name)
def upload_image(file):
    result = cloudinary.uploader.upload(
        file,
        folder="posts"
    )

    return {
        "url":result["secure_url"],
        "public_id":result["public_id"]
    }

def upload_reel(file):
    result = cloudinary.uploader.upload(
        file,
        resource_type="video",
        folder="videos"
    )

    return {
        "url":result["secure_url"],
        "public_id":result["public_id"]
    }
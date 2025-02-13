from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import io
import os
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Twitter API credentials from .env file
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads/")

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Authenticate with Twitter API
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
twitter_api = tweepy.API(auth)

# Define image resize dimensions
RESIZE_SIZES = [(300, 250), (728, 90), (160, 600), (300, 600)]

app = FastAPI()

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        image_format = image.format

        resized_images = []
        for width, height in RESIZE_SIZES:
            img_resized = image.copy()
            img_resized.thumbnail((width, height))
            img_path = os.path.join(UPLOAD_FOLDER, f"{file.filename}_{width}x{height}.{image_format.lower()}")
            img_resized.save(img_path)
            resized_images.append(img_path)

        return JSONResponse({"message": "Images resized successfully", "files": resized_images})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/post-twitter/")
async def post_to_twitter(images: list[str], token: str = Form(...)):
    try:
        if not images:
            raise HTTPException(status_code=400, detail="No images provided")

        media_ids = []
        for img_path in images:
            media = twitter_api.media_upload(img_path)
            media_ids.append(media.media_id_string)

        twitter_api.update_status(status="Here are the resized images!", media_ids=media_ids)
        return {"message": "Images posted to Twitter successfully"}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

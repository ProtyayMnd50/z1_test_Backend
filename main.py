# Step 1: Backend Setup (FastAPI)

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from PIL import Image
import io
import os

app = FastAPI()

# Define image resize dimensions
RESIZE_SIZES = [(300, 250), (728, 90), (160, 600), (300, 600)]
UPLOAD_FOLDER = "uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Read image from file
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        image_format = image.format  # Preserve image format (JPEG/PNG)

        # Resize image to predefined sizes
        resized_images = []
        for width, height in RESIZE_SIZES:
            img_resized = image.copy()
            img_resized.thumbnail((width, height))
            img_path = f"{UPLOAD_FOLDER}{file.filename}_{width}x{height}.{image_format.lower()}"
            img_resized.save(img_path)
            resized_images.append(img_path)

        return JSONResponse({"message": "Images resized successfully", "files": resized_images})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# Run the FastAPI server
# uvicorn main:app --reload
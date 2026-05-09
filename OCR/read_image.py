import cv2
import numpy as np
import pytesseract
import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI(title="Receipt OCR API")


def process_ocr(image_bytes):
    # Convert bytes to OpenCV format
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Preprocessing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # OCR
    text = pytesseract.image_to_string(processed_img)
    return text


@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()
    text = process_ocr(contents)

    return {"filename": file.filename, "extracted_text": text}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

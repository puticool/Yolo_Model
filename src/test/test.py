from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from ultralytics import YOLO
import cv2
import numpy as np
import uvicorn
from PIL import Image, ImageDraw, ImageFont
import json
import asyncio

app = FastAPI(
    title="YOLO WebSocket API",
    description="This API allows real-time object detection using YOLO models over WebSocket.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model paths
model_paths = {
    "v9": "yolov9t.pt",
    "v10": "yolov10n.pt",
    "v11": "yolo11n.pt",
    "v12": "yolo12n.pt"
}

class ErrorResponse(BaseModel):
    error: str

@app.get("/")
async def read_root():
    return {"message": "Welcome to the YOLO WebSocket API"}

@app.websocket("/ws/{model_type}")
async def websocket_endpoint(websocket: WebSocket, model_type: str):
    """
    WebSocket endpoint for real-time object detection.

    - **model_type**: The type of YOLO model to use (e.g., 'v9', 'v10', 'v11', 'v12').
    """
    await websocket.accept()

    if model_type not in model_paths:
        await websocket.send_text(json.dumps({"error": "Invalid model type"}))
        await websocket.close()
        return

    model = YOLO(model_paths[model_type])

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        await websocket.send_text(json.dumps({"error": "Could not open video capture"}))
        await websocket.close()
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame, verbose=False)
            detected_objects = []

            for result in results:
                if hasattr(result, 'boxes') and result.boxes is not None:
                    for box, cls, conf in zip(result.boxes.xyxy, result.boxes.cls, result.boxes.conf):
                        label = model.names[int(cls)]
                        x1, y1, x2, y2 = map(int, box)
                        detected_objects.append({"label": label, "x": x1, "y": y1})
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        frame = draw_text_on_frame(frame, x1, y1, label)

            # Convert frame to JPEG binary and send through WebSocket
            _, buffer = cv2.imencode('.jpg', frame)
            img_bytes = buffer.tobytes()

            # Send image + objects list
            response = json.dumps({"objects": detected_objects})
            await websocket.send_text(response)
            await websocket.send_bytes(img_bytes)

            # Thêm delay nhỏ để tránh overload CPU
            await asyncio.sleep(0.05)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cap.release()
        await websocket.close()

def draw_text_on_frame(frame, x1, y1, label):
    # """Vẽ thông tin lên khung hình"""
    # pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    # draw = ImageDraw.Draw(pil_img)

    # try:
    #     font = ImageFont.truetype("arial.ttf", 20)
    # except IOError:
    #     font = ImageFont.load_default()

    # text = f"{label}"
    # draw.text((x1,y1 - 20), text, font=font, fill=(255, 255, 255))
    # return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return frame

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
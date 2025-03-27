from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import json
import os
import base64
from src.core.models import YOLOModelManager
from src.utils.image_process import draw_bounding_boxes
from src.utils.label import get_label_translation
from gtts import gTTS

router = APIRouter()

AUDIO_DIR = "../assets/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Nhận file ảnh và trả về dự đoán dưới dạng JSON"""
    # Kiểm tra định dạng file
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File không phải là ảnh")

    # Đọc nội dung file ảnh
    contents = await file.read()
    np_img = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=500, detail="Không thể đọc file ảnh")

    # Dự đoán bằng YOLO
    results = YOLOModelManager.get_model("v11")(img)
    predictions = []

    for result in results:
        if hasattr(result, "boxes") and result.boxes is not None:
            for box, cls, conf in zip(result.boxes.xyxy, result.boxes.cls, result.boxes.conf):
                # Tính toán thông tin bounding box
                x1, y1, x2, y2 = map(int, box)
                width = x2 - x1
                height = y2 - y1
                x_center = x1 + width / 2
                y_center = y1 + height / 2

                # Nhãn đối tượng và độ tin cậy
                label = result.names[int(cls)]
                label_vi = get_label_translation(label)
                confidence = float(conf)

                # Tạo file âm thanh
                audio_path = os.path.join(AUDIO_DIR, f"{label}_en.mp3")
                if not os.path.exists(audio_path):
                    tts = gTTS(text=label, lang="en")
                    tts.save(audio_path)

                # Thêm vào danh sách dự đoán
                predictions.append({
                    "width": width,
                    "height": height,
                    "x": x_center,
                    "y": y_center,
                    "label": label,
                    "label_vi": label_vi,
                    "audio_path": audio_path,
                    "confidence": confidence,
                })

                # Vẽ bounding box
                draw_bounding_boxes(img, box, f"{label} {confidence:.2f}")

    # Mã hóa ảnh xử lý thành base64 (nếu muốn trả về ảnh trong JSON)
    _, img_encoded = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    img_base64 = base64.b64encode(img_encoded).decode("utf-8")

    # Tạo response JSON
    response_data = {
        "predictions": predictions,
        "image": img_base64  # Thêm ảnh đã xử lý dưới dạng base64
    }

    # Trả về JSONResponse
    return JSONResponse(content=response_data)
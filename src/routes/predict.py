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
    """Nhận file ảnh và trả về dự đoán dưới dạng JSON, chỉ giữ lại một dự đoán cho mỗi nhãn với confidence cao nhất"""
    try:
        # Kiểm tra định dạng file
        if not file.content_type.startswith("image/"):
            print(f"Error: File không phải là ảnh. Content-Type: {file.content_type}")
            raise HTTPException(status_code=400, detail="File không phải là ảnh")

        # Đọc nội dung file ảnh
        contents = await file.read()
        if not contents:
            print("Error: File ảnh rỗng")
            raise HTTPException(status_code=400, detail="File ảnh rỗng")

        np_img = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        if img is None:
            print("Error: Không thể đọc file ảnh")
            raise HTTPException(status_code=500, detail="Không thể đọc file ảnh")

        # Log kích thước ảnh gốc
        print(f"Kích thước ảnh gốc: {img.shape}")

        # Dự đoán bằng YOLO
        results = YOLOModelManager.get_model("v11")(img)
        predictions = []

        for result in results:
            if hasattr(result, "boxes") and result.boxes is not None:
                for box, cls, conf in zip(result.boxes.xyxy, result.boxes.cls, result.boxes.conf):
                    x1, y1, x2, y2 = map(int, box)
                    width = x2 - x1
                    height = y2 - y1
                    x_center = x1 + width / 2
                    y_center = y1 + height / 2

                    label = result.names[int(cls)]
                    label_vi = get_label_translation(label)
                    confidence = float(conf)

                    if confidence <= 0.45:  # Nếu độ tin cậy thấp hơn hoặc bằng 0.6 thì bỏ qua
                        continue

                    predictions.append({
                        "width": width,
                        "height": height,
                        "x": x_center,
                        "y": y_center,
                        "label": label,
                        "label_vi": label_vi,
                        "confidence": confidence,
                    })

                    draw_bounding_boxes(img, box, f"{label} {confidence:.2f}")

        # Lọc predictions để chỉ giữ lại một mục cho mỗi label, chọn confidence cao nhất
        filtered_predictions = {}
        for pred in predictions:
            label = pred["label"]
            if label not in filtered_predictions or pred["confidence"] > filtered_predictions[label]["confidence"]:
                filtered_predictions[label] = pred

        # Chuyển lại thành danh sách
        final_predictions = list(filtered_predictions.values())

        # Log kích thước ảnh sau khi xử lý
        print(f"Kích thước ảnh sau khi xử lý: {img.shape}")

        # Mã hóa ảnh xử lý thành base64
        _, img_encoded = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        img_base64 = base64.b64encode(img_encoded).decode("utf-8")

        # Tạo file âm thanh cho các nhãn duy nhất
        for pred in final_predictions:
            label = pred["label"]
            audio_path = os.path.join(AUDIO_DIR, f"{label}_en.mp3")
            if not os.path.exists(audio_path):
                tts = gTTS(text=label, lang="en")
                tts.save(audio_path)

        # Tạo response JSON
        response_data = {
            "predictions": final_predictions,
            "image": img_base64
        }

        return JSONResponse(content=response_data)

    except HTTPException as e:
        print(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi không xác định: {str(e)}")
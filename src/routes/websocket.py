from fastapi import WebSocket, APIRouter
import cv2
from src.core.models import YOLOModelManager
from src.utils.video_process import draw_text_on_frame, frame_to_base64, get_color_from_label
from src.utils.label import get_label_translation

router = APIRouter()

@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    """Xử lý kết nối WebSocket cho camera real-time"""
    try:
        model = YOLOModelManager.get_model("v11")
    except ValueError as e:
        await websocket.send_text(str(e))
        await websocket.close()
        return

    await websocket.accept()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        await websocket.send_text("Lỗi: Không thể mở camera")
        await websocket.close()
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Chạy YOLO
            results = model(frame)
            detected_objects = []
            
            # Vẽ kết quả nhận diện
            for result in results:
                if hasattr(result, 'boxes') and result.boxes is not None:
                    for box, cls in zip(result.boxes.xyxy, result.boxes.cls):
                        label = model.names[int(cls)]
                        label_vi = get_label_translation(label)
                        x1, y1, x2, y2 = map(int, box)
                        detected_objects.append({"label": label, "label_vi": label_vi, "x": x1, "y": y1})
                        
                        color = get_color_from_label(label)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 4)
                        frame = draw_text_on_frame(frame, x1, y1, label, label_vi, color)
                        
            # Gửi frame qua WebSocket
            await websocket.send_json(
                {
                    "image": frame_to_base64(frame),
                }
            )
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cap.release()
        await websocket.close()
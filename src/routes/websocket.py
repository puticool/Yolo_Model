from fastapi import WebSocket, APIRouter
import cv2
from src.core.models import YOLOModelManager
from src.utils.video_process import draw_text_on_frame, frame_to_base64, get_color_from_label
from src.utils.label import get_label_translation
import asyncio
import random

router = APIRouter()

# Tạo bảng ánh xạ màu cố định cho từng nhãn
color_map = {}

def get_color_for_label(label):
    """Trả về màu cố định cho một nhãn."""
    if label not in color_map:
        # Tạo màu ngẫu nhiên và lưu vào bảng ánh xạ
        color_map[label] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    return color_map[label]

@router.websocket("/ws/v11")
async def websocket_endpoint(websocket: WebSocket):
    """Xử lý kết nối WebSocket cho camera real-time"""
    model = YOLOModelManager.get_model(model_type="v11")
    await websocket.accept()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        await websocket.send_text("Lỗi: Không thể mở camera")
        await websocket.close()
        return

    running = True
    frame_skip = 5  # Chỉ xử lý mỗi 5 frame
    frame_count = 0

    try:
        while running:
            if websocket.client_state == 1:
                try:
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=0.01)
                    if data == "STOP":
                        running = False
                        break
                except asyncio.TimeoutError:
                    pass

            ret, frame = cap.read()
            if not ret:
                break

            # Giảm độ phân giải frame để tăng tốc độ xử lý
            frame = cv2.resize(frame, (640, 480))

            # Chỉ xử lý mỗi `frame_skip` frame
            if frame_count % frame_skip == 0:
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

                            # Lấy màu cố định cho nhãn
                            color = get_color_for_label(label)
                            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 4)
                            frame = draw_text_on_frame(frame, x1, y1, label, label_vi, color)

                # Gửi frame qua WebSocket
                await websocket.send_json(
                    {
                        "image": frame_to_base64(frame),
                        "objects": detected_objects,
                    }
                )

            frame_count += 1
            await asyncio.sleep(0.01)  # Giảm tải CPU

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cap.release()
        await websocket.close()
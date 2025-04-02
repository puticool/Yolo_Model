from fastapi import WebSocket, APIRouter ,WebSocketDisconnect
import cv2
from src.core.models import YOLOModelManager
from src.utils.video_process import draw_text_on_frame, frame_to_binary, get_color_from_label
from src.utils.label import get_label_translation
import asyncio

router = APIRouter()
active_connections = set()

@router.websocket("/ws/v11")
async def websocket_endpoint(websocket: WebSocket):
    """Kết nối WebSocket và tạo một task riêng cho mỗi thiết bị"""
    await handle_client(websocket)
    
async def handle_client(websocket: WebSocket):
    """Xử lý kết nối WebSocket cho camera real-time"""
    # try:
    #     model = YOLOModelManager.get_model(model_type="v11")
    # except ValueError as e:
    #     await websocket.send_text(str(e))
    #     await websocket.close()
    #     return
    
    await websocket.accept()
    active_connections.add(websocket)
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        await websocket.send_text("Lỗi: Không thể mở camera")
        await websocket.close()
        active_connections.remove(websocket)
        return
    
    try:
        model = YOLOModelManager.get_model(model_type="v11")
    except ValueError as e:
        await websocket.send_text(str(e))
        await websocket.close()
        active_connections.remove(websocket)
        return
    
    running = True
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
                except WebSocketDisconnect:
                    running = False
                    break
            
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            if frame_count % 3 != 0:  # Chỉ xử lý mỗi 3 khung hình
                    continue

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
                        # Thêm SVG icon vào detected_objects
                        audio_icon = '''<svg class="audio-icon" viewBox="0 0 24 24">
                            <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                        </svg>'''
                        detected_objects.append({
                            "label": label, 
                            "label_vi": label_vi, 
                            "box": {
                                "x": x1, 
                                "y": y1,
                            
                        },
                        "audio_icon": audio_icon })
                        
                        color = get_color_from_label(label)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 4)
                        frame = draw_text_on_frame(frame, x1, y1, label, label_vi, color)
                        
            # Gửi frame qua WebSocket
            frame_data = frame_to_binary(frame)
            await websocket.send_bytes(frame_data)
            
            # Gửi thông tin về các đối tượng đã phát hiện
            await websocket.send_json({
                "objects": detected_objects,
                "ping": "keep-alive"
            })
            
            await asyncio.sleep(0.1)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cap.release()
        active_connections.discard(websocket)
        if websocket.client_state == 1:  # Chỉ đóng nếu WebSocket còn mở
            await websocket.close()
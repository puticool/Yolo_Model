from fastapi import WebSocket
from gtts import gTTS
import io
import base64

async def audio_endpoint(websocket: WebSocket):
    """Gửi âm thanh qua WebSocket theo thời gian thực"""
    await websocket.accept()
    
    while True:
        text = await websocket.receive_text()  # Nhận văn bản từ client
        tts = gTTS(text, lang="vi")
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        # Chuyển âm thanh thành base64 và gửi qua WebSocket
        audio_base64 = base64.b64encode(audio_buffer.read()).decode("utf-8")
        await websocket.send_text(audio_base64)

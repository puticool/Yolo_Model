import os
import base64
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pyttsx3
from pydantic import BaseModel

# Khởi tạo ứng dụng FastAPI
app = FastAPI()

# Đường dẫn thư mục lưu file audio tạm thời
AUDIO_DIR = r"src\assets\audio"

# Đảm bảo thư mục tồn tại, nếu không thì tạo mới
os.makedirs(AUDIO_DIR, exist_ok=True)

# Định nghĩa model cho dữ liệu JSON đầu vào
class AudioRequest(BaseModel):
    word: str
    voice: str = "female"  # Giá trị mặc định là "female"

@app.post("/audio")
async def generate_audio_endpoint(request: AudioRequest):
    """
    Endpoint để tạo audio từ word và trả về dữ liệu Base64.
    
    Args:
        request (AudioRequest): Đối tượng chứa "word" và "voice" từ JSON
    
    Returns:
        JSONResponse: Chứa "word" và "audio_base64"
    """
    # Lấy word và voice từ request
    word = request.word
    voice = request.voice

    # Kiểm tra nếu không có word
    if not word:
        return JSONResponse({"error": "No word provided to generate audio"}, status_code=400)
   
    # Tạo tên file audio với đường dẫn đầy đủ
    audio_filename = f"output_{word}_{voice}.mp3"
    audio_path = os.path.join(AUDIO_DIR, audio_filename)
    
    # Gọi hàm text_to_speech để tạo file audio
    text_to_speech(word, audio_path, voice)
    
    # Đọc file audio và mã hóa thành Base64
    try:
        with open(audio_path, "rb") as audio_file:
            audio_base64 = base64.b64encode(audio_file.read()).decode("utf-8")
    except Exception as e:
        return JSONResponse({"error": f"Failed to read audio file: {str(e)}"}, status_code=500)
    
    # Xóa file tạm sau khi mã hóa (tùy chọn)
    # try:
    #     os.remove(audio_path)
    # except Exception as e:
    #     print(f"Warning: Could not delete temporary file {audio_path}: {str(e)}")
    
    # Trả về phản hồi JSON với word và Base64
    return JSONResponse({
        "word": word,
        "audio_base64": audio_base64
    })

def text_to_speech(text: str, filename: str, voice: str = "female"):
    """
    Chuyển văn bản thành file âm thanh bằng pyttsx3.
    
    Args:
        text (str): Văn bản cần chuyển thành âm thanh
        filename (str): Đường dẫn để lưu file âm thanh
        voice (str): Giọng nói ("female" hoặc "male")
    """
    # Khởi tạo engine pyttsx3
    engine = pyttsx3.init()
    
    # Lấy danh sách giọng nói có sẵn
    voices = engine.getProperty('voices')
    
    # Chọn giọng nói dựa trên tham số voice
    if voice.lower() == "male" and len(voices) > 0:
        engine.setProperty('voice', voices[0].id)  # Giọng nam (thường là index 0)
    else:
        # Giọng nữ (thường là index 1, nếu không có thì dùng giọng đầu tiên)
        engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
    
    # Cài đặt tốc độ và âm lượng
    engine.setProperty('rate', 120)  # Tốc độ nói
    engine.setProperty('volume', 1.0)  # Âm lượng tối đa
    
    # Lưu file âm thanh
    engine.save_to_file(text, filename)
    engine.runAndWait()
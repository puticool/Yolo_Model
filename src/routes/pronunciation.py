from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import base64
import os
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
from difflib import SequenceMatcher
from io import BytesIO
import random

router = APIRouter()

AUDIO_DIR = r"C:\quangkhai\Yolo_Model2\src\assets\audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Cấu hình FFmpeg
AudioSegment.converter = r"C:\ffmpeg\ffmpeg.exe"
AudioSegment.ffmpeg = r"C:\ffmpeg\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\ffmpeg\ffprobe.exe"

def convert_to_pcm_wav(input_path: str, output_path: str) -> str:
    try:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"File đầu vào không tồn tại: {input_path}")
        if not os.path.exists(AudioSegment.converter):
            raise FileNotFoundError(f"FFmpeg không tìm thấy tại: {AudioSegment.converter}")
        print(f"Converting {input_path} to {output_path}")
        sound = AudioSegment.from_file(input_path)
        sound.export(output_path, format="wav")
        print(f"Converted successfully to: {output_path}")
        return output_path
    except Exception as e:
        print(f"Lỗi chuyển đổi file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Không thể chuyển đổi file âm thanh: {str(e)}")

def speech_to_text(audio_path: str) -> str:
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)

    print("Audio file received for recognition")
    try:
        print("Starting speech recognition...")
        text = recognizer.recognize_google(audio)
        print("Recognition successful:", text)
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")
        return None
    except sr.RequestError as e:
        print(f"Google Speech Recognition service error: {e}")
        return None

def compare_text(original: str, recognized: str) -> list:
    original_words = original.split()
    recognized_words = recognized.split()
    matcher = SequenceMatcher(None, original_words, recognized_words)
    differences = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            differences.append({"type": "replace", "original": original_words[i1:i2], "recognized": recognized_words[j1:j2]})
        elif tag == 'delete':
            differences.append({"type": "delete", "original": original_words[i1:i2], "recognized": []})
        elif tag == 'insert':
            differences.append({"type": "insert", "original": [], "recognized": recognized_words[j1:j2]})
    return differences

def compare_pronunciation(recognized_text: str, sample_sentence: str) -> float:
    recognized_words = recognized_text.lower().split()
    sample_words = sample_sentence.lower().split()

    if not sample_words:
        return 0.0

    total_score = 0.0
    for r, s in zip(recognized_words, sample_words):
        matcher = SequenceMatcher(None, r, s)
        similarity = matcher.ratio()
        if r == s:
            total_score += 1.0
        elif similarity > 0.7:
            total_score += similarity * 0.8
        else:
            total_score += 0.0

    accuracy = total_score / len(sample_words)
    return min(1.0, accuracy)

def generate_pronunciation_feedback(accuracy: float, differences: list, sample_sentence: str, recognized_text: str) -> str:
    """
    Tạo phản hồi ngẫu nhiên: chọn một câu khen nếu đúng, hoặc một câu động viên nếu sai.
    """
    praise_messages = [
        "Phát âm của bạn thật tuyệt vời! Tiếp tục phát huy nhé!",
        "Bạn đã làm rất tốt! Hãy thử với những câu khó hơn nào!",
        "Giỏi lắm! Phát âm của bạn rất chính xác!",
        "Xuất sắc! Bạn đã phát âm đúng hoàn toàn!"
    ]

    encouragement_messages = [
        "Đừng lo, hãy thử lại lần nữa nhé! Bạn sẽ làm tốt hơn!",
        "Không sao đâu, hãy luyện tập thêm một chút nào!",
        "Bạn đang tiến bộ đấy! Cố gắng thêm lần nữa nhé!",
        "Phát âm chưa đúng lắm, nhưng đừng bỏ cuộc! Hãy thử lại nào!"
    ]

    if accuracy >= 0.8:
        return random.choice(praise_messages)
    else:
        return random.choice(encouragement_messages)

def text_to_speech(text: str, lang: str = "en") -> tuple[str, str]:
    try:
        tts = gTTS(text=text if text else "No text recognized", lang=lang)
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        audio_path = os.path.join(AUDIO_DIR, "recognized_text_en.mp3")
        with open(audio_path, "wb") as f:
            f.write(audio_buffer.getvalue())

        audio_base64 = base64.b64encode(audio_buffer.getvalue()).decode("utf-8")
        return audio_path, audio_base64
    except Exception as e:
        print(f"Lỗi Text-to-Speech: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Không thể tạo âm thanh từ văn bản: {str(e)}")

@router.post("/pronunciation")
async def pronunciation_check(
    file: UploadFile = File(...),
    sample_sentence: str = Form(...)
):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File không phải là âm thanh")
    if not sample_sentence:
        raise HTTPException(status_code=400, detail="Thiếu câu mẫu")
    print("Received sample_sentence:", sample_sentence)

    contents = await file.read()
    file_extension = file.filename.split(".")[-1].lower()
    # Thêm hỗ trợ cho định dạng .webm
    if file_extension not in ["mp3", "m4a", "wav", "webm"]:
        raise HTTPException(status_code=400, detail="Định dạng file không được hỗ trợ. Chỉ hỗ trợ .mp3, .m4a, .wav, .webm")

    audio_filename = f"uploaded_audio_{file.filename}"
    audio_path = os.path.join(AUDIO_DIR, audio_filename)
    with open(audio_path, "wb") as audio_file:
        audio_file.write(contents)
    print(f"File saved at: {audio_path}")

    wav_path = os.path.join(AUDIO_DIR, f"converted_{file.filename.split('.')[0]}.wav")
    converted_audio_path = convert_to_pcm_wav(audio_path, wav_path)
    if not converted_audio_path:
        raise HTTPException(status_code=500, detail="Không thể chuyển đổi file âm thanh")

    print("Recognizing speech...")
    recognized_text = speech_to_text(converted_audio_path)
    if not recognized_text:
        raise HTTPException(status_code=500, detail="Không thể nhận dạng giọng nói")

    audio_base64 = base64.b64encode(contents).decode("utf-8")
    accuracy = compare_pronunciation(recognized_text, sample_sentence)
    differences = compare_text(sample_sentence, recognized_text)
    pronunciation_feedback = generate_pronunciation_feedback(accuracy, differences, sample_sentence, recognized_text)

    # Tạo âm thanh từ recognized_text
    tts_audio_path, tts_audio_base64 = text_to_speech(recognized_text)

    response_data = {
        "recognized_text": recognized_text,
        "sample_sentence": sample_sentence,
        "accuracy": accuracy,
        "pronunciation_feedback": pronunciation_feedback,
        "differences": differences,
        "audio_path": audio_path,
        "audio_base64": audio_base64,
        "tts_audio_path": tts_audio_path,
        "tts_audio_base64": tts_audio_base64
    }
    return JSONResponse(content=response_data)
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import google.generativeai as genai
from dotenv import load_dotenv
from googletrans import Translator
from pydantic import BaseModel

app = FastAPI()
 
# Load environment variables
load_dotenv()
 
# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 200,
    "response_mime_type": "text/plain",
}
class WordRequest(BaseModel):
    word: str
    

def translate_text(text, target_language="vi"):  # Remove async
    translator = Translator()
    translated = translator.translate(text, dest=target_language)
    return translated

async def generate_sentence(request: WordRequest):
    word = request.word
    if not word:
        return "I could not recognize any object clearly."
   
    prompt = (
        f"Explain the word '{word}' to a 10-year-old child using 25 to 30 simple English words. "
        f"Then, translate that explanation into Vietnamese so that a 10-year-old Vietnamese child can understand. "
        f"Keep both versions fun, imaginative, clear, and age-appropriate. "
        f"Avoid using sound effects, contractions, or special characters. "
        f"Format the response like this:\n\n"
        f"English: <your English explanation>\n"
        f"Vietnamese: <your Vietnamese translation>"
    )

    try:
        gen_model = genai.GenerativeModel("gemini-2.0-flash", generation_config=generation_config)
        response = gen_model.generate_content(prompt)
        text = response.text.strip()

        # Tách hai phần từ kết quả
        english_sentence = ""
        vietnamese_sentence = ""

        if "English:" in text and "Vietnamese:" in text:
            parts = text.split("Vietnamese:")
            english_sentence = parts[0].replace("English:", "").strip()
            vietnamese_sentence = parts[1].strip()
        else:
            # fallback nếu định dạng không đúng
            english_sentence = text
            vietnamese_sentence = "Không thể tách phần dịch tự động. Vui lòng kiểm tra lại kết quả."

        return JSONResponse({
            "sentence": english_sentence,
            "translated_sentence": vietnamese_sentence
        })
    except Exception as e:
        return JSONResponse({"error": f"Error generating sentence: {str(e)}"})
 


@app.post("/generate")
async def generate_sentence_endpoint(word):
       
    english_sentence = generate_sentence(word)
    translated_sentence = await translate_text(english_sentence, target_language="vi")
   
    return JSONResponse({
        "detected_word": word,
        "sentence": english_sentence,
        "translated_sentence": translated_sentence,
    })
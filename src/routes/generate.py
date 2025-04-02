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
    
async def generate_sentence(request: WordRequest):
    word = request.word
    if not word:
        return "I could not recognize any object clearly."
   
    prompt = (
        f"Describe {word} to a 10-year-old in a fun, exciting way using 25-30 words. "
        f"Use a playful, kid-friendly tone matching {word}'s personality. "
        "Avoid contractions like 'I'm' or 'it's', and keep it simple with no special characters."
    )
   
    try:
        gen_model = genai.GenerativeModel("gemini-2.0-flash", generation_config=generation_config)
        response = gen_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating sentence: {str(e)}"
 
async def translate_text(text, target_language="vi"):
    translator = Translator()
    translated = await translator.translate(text, dest=target_language)
    return translated.text


@app.post("/generate")
async def generate_sentence_endpoint(word):
       
    english_sentence = generate_sentence(word)
    translated_sentence = await translate_text(english_sentence, target_language="vi")
   
    return JSONResponse({
        "detected_word": word,
        "sentence": english_sentence,
        "translated_sentence": translated_sentence,
    })
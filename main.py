from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pyngrok import ngrok
from src.routes.websocket import websocket_endpoint
from src.routes.predict import predict
from src.routes.hello import read_root
from src.routes.pronunciation import pronunciation_check
from src.routes.audio import generate_audio_endpoint
from src.routes.generate import generate_sentence
#from src.routes.chatbot import chat_with_user

src = FastAPI()

src.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Định nghĩa WebSocket route
src.add_api_websocket_route("/ws/{model_type}", websocket_endpoint)
src.add_api_route("/predict", predict, methods=["POST"])
src.add_api_route("/pronunciation", pronunciation_check, methods=["POST"])
src.add_api_route("/generate", generate_sentence, methods=["POST"])
src.add_api_route("/audio", generate_audio_endpoint, methods=["POST"])
#src.add_api_route("/chat", chat_with_user, methods=["POST"])
src.add_api_route("/", read_root)

if __name__ == "__main__":
    # Mở đường hầm Ngrok
    public_url = ngrok.connect(7000).public_url
    print(f"🚀 Ngrok tunnel: {public_url}")

    uvicorn.run("main:src", host="0.0.0.0", port=7000, reload=True)
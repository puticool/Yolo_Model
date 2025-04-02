from fastapi import FastAPI
import uvicorn
from src.routes.websocket import websocket_endpoint
from src.routes.predict import predict
from src.routes.hello import read_root
from src.routes.pronunciation import pronunciation_check
from src.routes.audio import generate_audio_endpoint
from src.routes.generate import generate_sentence

src = FastAPI()

# Định nghĩa WebSocket route
src.add_api_websocket_route("/ws/{model_type}", websocket_endpoint)
src.add_api_route("/predict", predict, methods=["POST"])
src.add_api_route("/pronunciation", pronunciation_check, methods=["POST"])
src.add_api_route("/generate", generate_sentence, methods=["POST"])
src.add_api_route("/audio",generate_audio_endpoint , methods=["POST"])
src.add_api_route("/", read_root)

if __name__ == "__main__":
    uvicorn.run("main:src", host="127.0.0.1", port=7000, reload=True)

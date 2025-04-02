from fastapi import FastAPI
import uvicorn
from src.routes.websocket import websocket_endpoint
from src.routes.predict import predict
from src.routes.hello import read_root

src = FastAPI()

# Định nghĩa WebSocket route
src.add_api_websocket_route("/ws/v11", websocket_endpoint)
src.add_api_route("/predict", predict, methods=["POST"])
src.add_api_route("/", read_root)

if __name__ == "__main__":
    uvicorn.run("main:src", host="127.0.0.1", port=8000, reload=True)

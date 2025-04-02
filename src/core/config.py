import os

# Đường dẫn tới thư mục models
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")

# Đường dẫn tới model YOLO
MODEL_PATHS = {
    "v9": os.path.join(MODELS_DIR, "yolov9t.pt"),
    "v10": os.path.join(MODELS_DIR, "yolov10n.pt"),
    "v11": os.path.join(MODELS_DIR, "yolo11n.pt")
}
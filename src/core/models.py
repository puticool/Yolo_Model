from ultralytics import YOLO
from src.core.config import MODEL_PATHS

class YOLOModelManager:
    _models = {}
    @classmethod
    def get_model(cls, model_type: str):
        """Lấy model tương ứng với model_type"""
        if model_type not in cls._models:
            if model_type in MODEL_PATHS:
                cls._models[model_type] = YOLO(MODEL_PATHS[model_type])
            else:
                raise ValueError(f"Model {model_type} không tồn tại.")
        return cls._models[model_type]

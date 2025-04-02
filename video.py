from flask import Flask, request, jsonify
from ultralytics import YOLO
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import base64
 
app = Flask(__name__)
 
# Khởi tạo mô hình YOLO
model = YOLO('yolov10n.pt')
 
# Từ điển dịch thủ công các nhãn đối tượng
labels_dict = {
    "person": "người",
    "bicycle": "xe đạp",
    "car": "ô tô",
    "motorcycle": "xe máy",
    "airplane": "máy bay",
    "bus": "xe buýt",
    "train": "tàu",
    "truck": "xe tải",
    "boat": "thuyền",
    "traffic light": "đèn giao thông",
    "fire hydrant": "cột chữa cháy",
    "stop sign": "biển dừng",
    "parking meter": "máy tính tiền đỗ xe",
    "bench": "ghế băng",
    "bird": "con chim",
    "cat": "con mèo",
    "dog": "con chó",
    "horse": "con ngựa",
    "sheep": "con cừu",
    "cow": "con bò",
    "elephant": "con voi",
    "bear": "con gấu",
    "zebra": "ngựa vằn",
    "giraffe": "hươu cao cổ",
    "backpack": "ba lô",
    "umbrella": "ô",
    "handbag": "túi xách",
    "tie": "cà vạt",
    "suitcase": "vali",
    "frisbee": "đĩa bay",
    "skis": "ván trượt",
    "snowboard": "ván trượt tuyết",
    "sports ball": "quả bóng thể thao",
    "kite": "diều",
    "baseball bat": "gậy bóng chày",
    "baseball glove": "găng tay bóng chày",
    "skateboard": "ván trượt",
    "surfboard": "ván lướt sóng",
    "tennis racket": "vợt tennis",
    "bottle": "chai nước",
    "wine glass": "ly rượu",
    "cup": "cốc",
    "fork": "dĩa",
    "knife": "dao",
    "spoon": "muỗng",
    "bowl": "bát",
    "banana": "chuối",
    "apple": "táo",
    "sandwich": "bánh mì kẹp",
    "orange": "cam",
    "broccoli": "bông cải xanh",
    "carrot": "cà rốt",
    "hot dog": "xúc xích",
    "pizza": "pizza",
    "donut": "bánh donut",
    "cake": "bánh kem",
    "chair": "ghế",
    "couch": "ghế sofa",
    "potted plant": "cây trong chậu",
    "bed": "giường",
    "dining table": "bàn ăn",
    "toilet": "bồn cầu",
    "tv": "tivi",
    "laptop": "máy tính xách tay",
    "mouse": "chuột máy tính",
    "remote": "remote điều khiển",
    "keyboard": "bàn phím",
    "cell phone": "điện thoại di động",
    "microwave": "lò vi sóng",
    "oven": "lò nướng",
    "toaster": "máy nướng bánh",
    "sink": "bồn rửa",
    "refrigerator": "tủ lạnh",
    "book": "sách",
    "clock": "đồng hồ",
    "vase": "bình hoa",
    "scissors": "kéo",
    "teddy bear": "gấu bông",
    "hair drier": "máy sấy tóc",
    "toothbrush": "bàn chải đánh răng"
}
 
@app.route('/detect', methods=['POST'])
def detect_objects():
    try:
        data = request.json
        if 'image' not in data:
            return jsonify({'success': False, 'message': 'No image provided'}), 400
 
        # Chuyển base64 thành ảnh
        image_data = base64.b64decode(data['image'])
        image = Image.open(BytesIO(image_data))
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
 
        # Dự đoán với YOLO
        results = model(frame)
        detected_objects = []
 
        for result in results:
            if hasattr(result, 'boxes') and result.boxes is not None:
                for box, cls in zip(result.boxes.xyxy, result.boxes.cls):
                    label = model.names[int(cls)]
                    label_vi = labels_dict.get(label, "Không có nghĩa")
                    x1, y1, x2, y2 = map(int, box)
 
                    detected_objects.append({
                        'name': label,
                        'translation': label_vi,
                        'position': {
                            'top': float(y1),
                            'left': float(x1),
                            'width': float(x2 - x1),
                            'height': float(y2 - y1),
                        }
                    })
 
        return jsonify({'success': True, 'objects': detected_objects})
 
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
 
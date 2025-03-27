import cv2
import numpy as np
import base64
from PIL import Image, ImageDraw, ImageFont

def get_color_from_label(label):
    hash_code = hash(label)
    r = (hash_code & 255)
    g = ((hash_code >> 8) & 255)
    b = ((hash_code >> 16) & 255)
    return (r, g, b)

def draw_text_on_frame(frame, x1, y1, label, label_vi=None , color=None):
    """Vẽ thông tin lên khung hình"""
    if label_vi is None:
        label_vi = label
    if color is None:
        color = (255, 255, 255)
        
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()

    text = f"{label} {label_vi}"
    draw.text((x1, y1 - 20), text, font=font, fill=color)
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def frame_to_base64(frame):
    """Chuyển đổi frame thành base64 để gửi qua WebSocket"""
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]  # Set JPEG quality to 90
    _, buffer = cv2.imencode(".jpg", frame, encode_param)
    return base64.b64encode(buffer).decode("utf-8")



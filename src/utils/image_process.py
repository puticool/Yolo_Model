import cv2

def draw_bounding_boxes(image, box, text):
    x1, y1, x2, y2 = map(int, box)
    color = (0, 255, 0)
    thickness = 10

    # Vẽ bounding box
    cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)

    # Vẽ nhãn với độ tin cậy
    cv2.putText(image, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 4.5, color, thickness)
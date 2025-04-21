# face_capture.py
import cv2
from ultralytics import YOLO
from database import connect_db,insert_user, insert_face

def capture_face_data(user_name):
    cap = cv2.VideoCapture(0)
    model = YOLO("yolov8n.pt")
    face_data = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)

        for result in results:
            for *xyxy, conf, cls in result.boxes.data:
                if int(cls) == 0:  # 检测人脸（假设类别为0）
                    x1, y1, x2, y2 = map(int, xyxy)
                    face = frame[y1:y2, x1:x2]
                    face_data.append(face)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.imshow("Detected Face", face)

        if cv2.waitKey(1) & 0xFF == ord('q') or len(face_data) >= 5:
            break

    cap.release()
    cv2.destroyAllWindows()

    # 插入用户信息
    user_id = insert_user(user_name)
    if not user_id:
        print("[ERROR] 用户插入失败，可能用户名重复")
        return

    # 插入人脸图像
    for face in face_data:
        _, buffer = cv2.imencode('.jpg', face)
        face_bytes = buffer.tobytes()
        insert_face(user_id, face_bytes)
import cv2
import sqlite3
import numpy as np
from ultralytics import YOLO
from database import connect_db
from datetime import datetime
import os

def recognize_face():
    print("[INFO] 启动人脸识别...")

    # 初始化摄像头
    cap = cv2.VideoCapture(0)
    model = YOLO("yolov8n.pt")

    # 加载数据库中所有人脸图像数据
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_info.id, user_info.username, face_data.face_image 
            FROM user_info JOIN face_data ON user_info.id = face_data.user_id
        """)
        records = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        print(f"[ERROR] 数据库操作错误: {e}")
        return

    known_faces = []
    labels = []

    for user_id, username, face_blob in records:
        nparr = np.frombuffer(face_blob, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img_gray = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (100, 100))
        known_faces.append(img_gray)
        labels.append(username)

    print(f"[INFO] 已加载 {len(known_faces)} 张用户人脸")

    detected_username = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] 无法获取摄像头画面")
            break

        results = model(frame)

        for result in results:
            for *xyxy, conf, cls in result.boxes.data:
                if int(cls) == 0:  # 人脸
                    x1, y1, x2, y2 = map(int, xyxy)
                    face = frame[y1:y2, x1:x2]

                    # 预处理：转为灰度 + 缩放
                    face_gray = cv2.resize(cv2.cvtColor(face, cv2.COLOR_BGR2GRAY), (100, 100))

                    # 简单相似度比对（欧式距离）
                    min_dist = float("inf")
                    best_match = "Unknown"

                    for i, known in enumerate(known_faces):
                        dist = np.linalg.norm(face_gray - known)
                        if dist < min_dist:
                            min_dist = dist
                            best_match = labels[i]

                    if min_dist < 2000:  # 距离阈值
                        detected_username = best_match
                        status = "识别成功"
                        color = (0, 255, 0)
                    else:
                        detected_username = "陌生人"
                        status = "识别失败"
                        color = (0, 0, 255)

                    cv2.putText(frame, f"{status}: {detected_username}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                    # 记录日志
                    log_recognition(detected_username, status)
                    break

        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def log_recognition(name, status):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                timestamp TEXT,
                status TEXT
            )
        """)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO access_log (username, timestamp, status) VALUES (?, ?, ?)",
                       (name, timestamp, status))
        conn.commit()
        conn.close()
        print(f"[LOG] {name} @ {timestamp} - {status}")
    except sqlite3.Error as e:
        print(f"[ERROR] 写入日志失败: {e}")

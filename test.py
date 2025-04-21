import sys
import cv2
import sqlite3
from ultralytics import YOLO
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap


# 连接到 SQLite3 数据库
def connect_db():
    conn = sqlite3.connect("IgateDB.db")
    return conn


# 提取人脸并录入到数据库
def capture_face_data(user_id, name):
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
                if int(cls) == 0:  # 假设 0 类别为人脸
                    x1, y1, x2, y2 = map(int, xyxy)
                    face = frame[y1:y2, x1:x2]
                    face_data.append(face)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        if len(face_data) >= 50:  # 提取 50 张图像
            break

    cap.release()

    # 将人脸数据保存到数据库
    conn = connect_db()
    cursor = conn.cursor()
    for face in face_data:
        _, buffer = cv2.imencode('.jpg', face)
        face_image = buffer.tobytes()
        cursor.execute("INSERT INTO user_info (username, face_data) VALUES (?, ?)", (name, face_image))

    conn.commit()
    conn.close()


# 创建前端界面
class FaceCaptureApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("人脸录入系统")
        self.setGeometry(100, 100, 400, 300)

        # 布局
        layout = QVBoxLayout()

        self.username_label = QLabel("用户名:")
        layout.addWidget(self.username_label)

        self.username_input = QLineEdit(self)
        layout.addWidget(self.username_input)

        self.capture_button = QPushButton("录入人脸", self)
        self.capture_button.clicked.connect(self.capture_face)
        layout.addWidget(self.capture_button)

        self.query_button = QPushButton("查询信息", self)
        self.query_button.clicked.connect(self.query_info)
        layout.addWidget(self.query_button)

        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)

        self.setLayout(layout)

    def capture_face(self):
        username = self.username_input.text()
        if username:
            capture_face_data(1, username)  # 这里假设 user_id 为 1
            self.status_label.setText(f"用户 {username} 的人脸数据已录入")
        else:
            self.status_label.setText("请输入用户名")

    def query_info(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT username, face_data FROM user_info")
        rows = cursor.fetchall()
        for row in rows:
            print(f"用户名: {row[0]}")
            # 如果需要显示图片，可以用 QPixmap 显示 face_data
        conn.close()


# 启动 PyQt 应用
app = QApplication(sys.argv)
window = FaceCaptureApp()
window.show()
sys.exit(app.exec_())

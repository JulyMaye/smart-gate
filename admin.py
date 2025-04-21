from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, QMessageBox
import sqlite3

class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin 管理界面")
        self.setGeometry(300, 300, 500, 500)

        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)

        self.btn_user = QPushButton("查看用户信息")
        self.btn_log = QPushButton("查看访问日志")
        self.btn_user.clicked.connect(self.display_users)
        self.btn_log.clicked.connect(self.display_logs)

        layout = QVBoxLayout()
        layout.addWidget(self.btn_user)
        layout.addWidget(self.btn_log)
        layout.addWidget(self.text_display)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def display_users(self):
        conn = sqlite3.connect("IgateDB.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM user_info")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            self.text_display.setText("暂无用户。")
            return

        text = "\n".join([f"ID: {row[0]} | 用户名: {row[1]}" for row in rows])
        self.text_display.setText(text)

    def display_logs(self):
        conn = sqlite3.connect("IgateDB.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username, access_time, status FROM user_log ORDER BY access_time DESC LIMIT 50")
        logs = cursor.fetchall()
        conn.close()

        if not logs:
            self.text_display.setText("暂无日志。")
            return

        text = "\n".join([f"{log[1]} | {log[0]} | {log[2]}" for log in logs])
        self.text_display.setText(text)

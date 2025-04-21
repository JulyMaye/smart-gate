# main.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import uic, QtWidgets
from admin import AdminWindow
from recognizer import recognize_face
import resource_rc
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('frontpage.ui', self)

        self.pushButton_5.clicked.connect(self.show_admin)
        self.pushButton_6.clicked.connect(self.recognize)
        self.pushButton_7.clicked.connect(self.enroll_new_user)

    def show_admin(self):  #
        self.admin_window = AdminWindow()  # 建议使用 self.admin_window 避免全局变量
        self.admin_window.show()

    def recognize(self):
        result = recognize_face()
        QMessageBox.information(self, "识别结果", result)

    def enroll_new_user(self):
        try:
            name, ok = QtWidgets.QInputDialog.getText(self, "新用户注册", "请输入姓名：")
            if ok:
                from face_capture import capture_face_data
                capture_face_data(name)
                QMessageBox.information(self, "提示", "新用户录入完成")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"录入失败：{str(e)}")

if __name__ == '__main__':
    from database import init_db
    init_db()  # 初始化数据库
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

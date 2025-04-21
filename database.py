# database.py
import sqlite3
import os

DB_PATH = "Igate.db"

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    # 创建用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            gender TEXT,
            department TEXT
        )
    """)

    # 创建人脸数据表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS face_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            face_image BLOB,
            FOREIGN KEY(user_id) REFERENCES user_info(id)
        )
    """)

    # 创建访问日志表（如果识别器没创建）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            access_time TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("[INFO] 数据库初始化完成！")

# 添加新用户
def insert_user(username, gender="", department=""):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO user_info (username, gender, department) VALUES (?, ?, ?)",
                       (username, gender, department))
        conn.commit()
        user_id = cursor.lastrowid
        print(f"[INFO] 成功添加用户 {username} (ID: {user_id})")
        return user_id
    except sqlite3.IntegrityError:
        print("[ERROR] 用户名已存在")
        return None
    finally:
        conn.close()

# 存入人脸图像（face_blob 为二进制）
def insert_face(user_id, face_blob):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO face_data (user_id, face_image) VALUES (?, ?)", (user_id, face_blob))
    conn.commit()
    conn.close()
    print("[INFO] 人脸图像存储成功")

# 查询所有用户
def get_all_users():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_info")
    rows = cursor.fetchall()
    conn.close()
    return rows

# 删除用户（同时删除人脸）
def delete_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM face_data WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM user_info WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    print(f"[INFO] 已删除用户 ID: {user_id}")

# 修改用户信息
def update_user(user_id, new_name=None, gender=None, department=None):
    conn = connect_db()
    cursor = conn.cursor()
    if new_name:
        cursor.execute("UPDATE user_info SET username = ? WHERE id = ?", (new_name, user_id))
    if gender:
        cursor.execute("UPDATE user_info SET gender = ? WHERE id = ?", (gender, user_id))
    if department:
        cursor.execute("UPDATE user_info SET department = ? WHERE id = ?", (department, user_id))
    conn.commit()
    conn.close()
    print(f"[INFO] 已更新用户信息 ID: {user_id}")

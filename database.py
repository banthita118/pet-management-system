import sqlite3

# ตั้งค่าตัวแปรสำหรับชื่อไฟล์ฐานข้อมูล เพื่อง่ายต่อการแก้ไข
DB_FILE = "pets.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            gender TEXT,
            age TEXT,
            owner TEXT NOT NULL,
            phone TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_all_pets():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, type, gender, age, owner, phone FROM pets")
    rows = cursor.fetchall()
    conn.close()
    
    # แปลงข้อมูลให้อยู่ในรูป List ของ Dictionary 
    pets = []
    for row in rows:
        pets.append({
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "gender": row[3],
            "age": row[4],
            "owner": row[5],
            "phone": row[6]
        })
    return pets

def add_pet_db(name, p_type, gender, age, owner, phone):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pets (name, type, gender, age, owner, phone)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, p_type, gender, age, owner, phone))
    conn.commit()
    conn.close()

def update_pet_db(pet_id, name, p_type, gender, age, owner, phone):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE pets 
        SET name = ?, type = ?, gender = ?, age = ?, owner = ?, phone = ?
        WHERE id = ?
    """, (name, p_type, gender, age, owner, phone, pet_id))
    conn.commit()
    conn.close()

def delete_pet_db(pet_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pets WHERE id = ?", (pet_id,))
    conn.commit()
    conn.close()
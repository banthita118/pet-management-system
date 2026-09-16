from database import init_db, get_all_pets

# เริ่มต้นสร้างฐานข้อมูลถ้ายังไม่มี
init_db()

# ดึงข้อมูลจาก SQLite มาเก็บไว้ในตัวแปร pets_data
pets_data = get_all_pets()
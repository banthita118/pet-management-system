import flet as ft
from views.pet_manager import PetManager

import flet as ft
from views.pet_manager import PetManager

def main(page: ft.Page):
    # ================= ตั้งค่าหน้าจอ =================
    page.title = "Pet Management System"
    page.scroll = "adaptive"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#EBF4FA" 
    page.padding = 40
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # 🌟 โหลดฟอนต์ Sarabun (ไทยสารบัญ) จาก Google Fonts
    page.fonts = {
        "Sarabun": "https://raw.githubusercontent.com/google/fonts/main/ofl/sarabun/Sarabun-Regular.ttf",
        "Sarabun-Bold": "https://raw.githubusercontent.com/google/fonts/main/ofl/sarabun/Sarabun-Bold.ttf"
    }
    # 🌟 ตั้งค่าให้ทั้งโปรเจกต์ใช้ฟอนต์นี้เป็นค่าเริ่มต้น
    page.theme = ft.Theme(font_family="Sarabun")
    
    # ================= เรียกหน้า UI มาแสดง =================
    page.add(PetManager(page).build())

ft.run(main, view=ft.AppView.WEB_BROWSER, assets_dir="assets")
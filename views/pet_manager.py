import flet as ft
from models import pets_data 
from database import add_pet_db, update_pet_db, delete_pet_db, get_all_pets

class PetManager:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_filter = "ทั้งหมด" 
        self.editing_id = None 
        
        self.item_to_delete = None 
        self.delete_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("ยืนยันการลบ", weight="bold", size=20),
            content=ft.Text("คุณต้องการลบข้อมูลนี้ใช่หรือไม่?", size=18),
            actions=[
                ft.TextButton("ยกเลิก", on_click=self.close_delete_dlg), 
                ft.ElevatedButton("ลบข้อมูล", on_click=self.execute_delete, color="white", bgcolor="#EF4444")
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        # 🌟 ลงทะเบียน dialog ไว้ใน overlay ตั้งแต่ต้น (เหมือน dob_picker ข้างล่าง)
        # เพื่อให้ toggle .open = True/False + page.update() ใช้ได้แน่นอน ไม่ว่า Flet เวอร์ชันไหน
        self.page.overlay.append(self.delete_dialog)
        
        # Style สำหรับ TextField
        self.tf_style = {
            "border_color": "#CBD5E1",
            "focused_border_color": "#0F172A",
            "border_radius": 6,
            "text_size": 16,
            "bgcolor": "white",
            "height": 45,
        }

        # Style สำหรับ Dropdown แยกออกจาก TextField
        # Flet 0.28.3 ไม่รองรับพารามิเตอร์ height ใน ft.Dropdown
        self.dropdown_style = {
            "border_color": "#CBD5E1",
            "focused_border_color": "#0F172A",
            "border_radius": 6,
            "text_size": 16,
            "bgcolor": "white",
        }

        self.pet_name = ft.TextField(
            label="ชื่อสัตว์เลี้ยง",
            width=200,
            **self.tf_style
        )

        self.pet_type = ft.Dropdown(
            label="ประเภท",
            width=150,
            **self.dropdown_style,
            options=[
                ft.dropdown.Option("สุนัข"),
                ft.dropdown.Option("แมว"),
                ft.dropdown.Option("กระต่าย"),
                ft.dropdown.Option("นก"),
                ft.dropdown.Option("อื่นๆ"),
            ],
        )
        self.pet_type_other = ft.TextField(label="โปรดระบุ...", width=150, bgcolor="white", height=45, border_color="#CBD5E1", focused_border_color="#0F172A", border_radius=6, text_size=16)
        self.pet_breed = ft.TextField(label="สายพันธุ์", width=180, **self.tf_style)
        self.pet_gender = ft.RadioGroup(content=ft.Row([ft.Radio(value="ผู้", label="เพศผู้"), ft.Radio(value="เมีย", label="เพศเมีย")]))
        self.pet_age_years = ft.TextField(label="อายุ (ปี)", width=100, **self.tf_style)
        self.pet_age_months = ft.TextField(label="(เดือน)", width=100, **self.tf_style)
        self.pet_weight = ft.TextField(label="น้ำหนัก (กก.)", width=120, **self.tf_style)
        self.pet_color = ft.TextField(label="สี", width=120, **self.tf_style)
        self.dob_field = ft.TextField(label="วันเกิด", width=150, read_only=True, **self.tf_style)
        
        self.dob_picker = ft.DatePicker(on_change=self.update_date_field)
        self.page.overlay.append(self.dob_picker)
        self.dob_btn = ft.ElevatedButton("เลือกวัน", on_click=self.open_dob_picker, bgcolor="#F1F5F9", color="#334155")

        self.owner_name = ft.TextField(label="ชื่อ-นามสกุล", width=250, **self.tf_style)
        self.owner_phone = ft.TextField(label="เบอร์โทรศัพท์", width=200, **self.tf_style)
        
        self.owner_address = ft.TextField(label="ที่อยู่ / อีเมล", expand=True, **self.tf_style)
        
        self.vaccine_field = ft.TextField(label="วันที่ฉีดวัคซีนล่าสุด", width=250, **self.tf_style)
        self.is_spayed = ft.Checkbox(label="ทำหมันเรียบร้อยแล้ว", fill_color="#0F172A") 
        self.health_notes = ft.TextField(label="หมายเหตุเพิ่มเติม...", width=700, multiline=True, border_color="#CBD5E1", focused_border_color="#0F172A", border_radius=6, text_size=16)

        self.search_input = ft.TextField(label="ค้นหารายชื่อ...", width=300, **self.tf_style)
        self.data_table = ft.DataTable(
            heading_row_color="#F1F5F9",
            columns=[
                ft.DataColumn(ft.Text("ลำดับ", weight="bold", size=16)), ft.DataColumn(ft.Text("ชื่อ", weight="bold", size=16)),
                ft.DataColumn(ft.Text("ประเภท", weight="bold", size=16)), ft.DataColumn(ft.Text("เพศ", weight="bold", size=16)),
                ft.DataColumn(ft.Text("อายุ", weight="bold", size=16)), ft.DataColumn(ft.Text("เจ้าของ", weight="bold", size=16)),
                ft.DataColumn(ft.Text("เบอร์โทร", weight="bold", size=16)), ft.DataColumn(ft.Text("จัดการ", weight="bold", size=16)),
            ],
            rows=[]
        )
        
        self.txt_filter_all = ft.Text("ทั้งหมด (0)")
        self.txt_filter_dog = ft.Text("สุนัข (0)")
        self.txt_filter_cat = ft.Text("แมว (0)")
        self.txt_filter_other = ft.Text("อื่นๆ (0)")
        
        self.btn_filter_all = ft.ElevatedButton(content=self.txt_filter_all, on_click=lambda e: self.apply_filter("ทั้งหมด"), height=40)
        self.btn_filter_dog = ft.ElevatedButton(content=self.txt_filter_dog, on_click=lambda e: self.apply_filter("สุนัข"), height=40)
        self.btn_filter_cat = ft.ElevatedButton(content=self.txt_filter_cat, on_click=lambda e: self.apply_filter("แมว"), height=40)
        self.btn_filter_other = ft.ElevatedButton(content=self.txt_filter_other, on_click=lambda e: self.apply_filter("อื่นๆ"), height=40)
        
        self.txt_save = ft.Text("บันทึกข้อมูล")
        self.btn_save = ft.ElevatedButton(content=self.txt_save, on_click=self.save_pet, bgcolor="#0F172A", color="white", height=45, width=150)
        
        self.txt_menu_0 = ft.Text("ภาพรวมและฐานข้อมูล")
        self.txt_menu_1 = ft.Text("ลงทะเบียนสัตว์เลี้ยงใหม่")
        

        self.configure_responsive_controls()
        self.setup_layouts()

    def configure_responsive_controls(self):
        """กำหนดสัดส่วน control สำหรับมือถือ แท็บเล็ต และคอม"""
        controls = [
            self.pet_name, self.pet_type, self.pet_type_other, self.pet_breed,
            self.pet_age_years, self.pet_age_months, self.pet_weight, self.pet_color,
            self.dob_field, self.owner_name, self.owner_phone, self.owner_address,
            self.vaccine_field, self.health_notes, self.search_input,
        ]
        for control in controls:
            control.width = None

        self.pet_name.col = {"sm": 12, "md": 6, "lg": 3}
        self.pet_type.col = {"sm": 12, "md": 6, "lg": 3}
        self.pet_type_other.col = {"sm": 12, "md": 6, "lg": 3}
        self.pet_breed.col = {"sm": 12, "md": 6, "lg": 3}

        self.pet_age_years.col = {"sm": 6, "md": 3, "lg": 2}
        self.pet_age_months.col = {"sm": 6, "md": 3, "lg": 2}
        self.pet_weight.col = {"sm": 6, "md": 3, "lg": 2}
        self.pet_color.col = {"sm": 6, "md": 3, "lg": 2}
        self.dob_field.col = {"sm": 8, "md": 6, "lg": 2}
        self.dob_btn.col = {"sm": 4, "md": 6, "lg": 2}

        self.owner_name.col = {"sm": 12, "md": 6, "lg": 4}
        self.owner_phone.col = {"sm": 12, "md": 6, "lg": 3}
        self.owner_address.col = {"sm": 12, "md": 12, "lg": 5}

        self.vaccine_field.col = {"sm": 12, "md": 6, "lg": 4}
        self.is_spayed.col = {"sm": 12, "md": 6, "lg": 4}
        self.health_notes.col = {"sm": 12, "md": 12, "lg": 12}
        self.search_input.col = {"sm": 12, "md": 8, "lg": 6}

    def update_date_field(self, e):
        if self.dob_picker.value:
            self.dob_field.value = self.dob_picker.value.strftime("%Y-%m-%d")
            self.page.update()

    def open_dob_picker(self, e):
        self.dob_picker.open = True
        self.page.update()

    def show_snackbar(self, message, is_error=False):
        bg_color = "#EF4444" if is_error else "#10B981" 
        snack = ft.SnackBar(ft.Text(message, color="white", size=16), bgcolor=bg_color)
        
        if hasattr(self.page, "open"):
            self.page.open(snack)
        else:
            self.page.snack_bar = snack
            self.page.snack_bar.open = True
            self.page.update()

    def clear_inputs(self):
        self.pet_name.value = self.pet_type.value = self.pet_breed.value = self.pet_type_other.value = ""
        self.pet_age_years.value = self.pet_age_months.value = self.pet_weight.value = self.pet_color.value = self.dob_field.value = ""
        self.owner_name.value = self.owner_phone.value = self.owner_address.value = self.vaccine_field.value = self.health_notes.value = ""
        self.is_spayed.value = False
        self.pet_gender.value = None
        
        self.editing_id = None
        self.txt_save.value = "บันทึกข้อมูล"
        self.page.update()

    def apply_filter(self, filter_type):
        self.current_filter = filter_type
        self.refresh_table()

    def update_filter_buttons_style(self):
        buttons = [
            (self.btn_filter_all, self.txt_filter_all, "ทั้งหมด"),
            (self.btn_filter_dog, self.txt_filter_dog, "สุนัข"),
            (self.btn_filter_cat, self.txt_filter_cat, "แมว"),
            (self.btn_filter_other, self.txt_filter_other, "อื่นๆ")
        ]
        
        for btn, txt, f_type in buttons:
            if self.current_filter == f_type:
                btn.bgcolor = "#0F172A" 
                txt.color = "white"
            else:
                btn.bgcolor = "#F1F5F9" 
                txt.color = "#475569"

    def refresh_table(self, search_query=""):
        global pets_data
        pets_data = get_all_pets()
        
        total_pets = len(pets_data)
        dog_count = sum(1 for p in pets_data if p['type'] == 'สุนัข')
        cat_count = sum(1 for p in pets_data if p['type'] == 'แมว')
        other_count = total_pets - dog_count - cat_count
        
        self.txt_filter_all.value = f"ทั้งหมด ({total_pets})"
        self.txt_filter_dog.value = f"สุนัข ({dog_count})"
        self.txt_filter_cat.value = f"แมว ({cat_count})"
        self.txt_filter_other.value = f"อื่นๆ ({other_count})"
        
        self.update_filter_buttons_style()

        new_rows = []
        display_no = 1

        for pet in pets_data:
            match_search = search_query.lower() in pet['name'].lower() or search_query.lower() in pet['type'].lower()
            
            match_filter = True
            if self.current_filter == "สุนัข" and pet['type'] != "สุนัข": match_filter = False
            elif self.current_filter == "แมว" and pet['type'] != "แมว": match_filter = False
            elif self.current_filter == "อื่นๆ" and pet['type'] in ["สุนัข", "แมว"]: match_filter = False
            
            if match_search and match_filter:
                new_rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(display_no), size=16)), 
                            ft.DataCell(ft.Text(pet['name'], weight="bold", size=16)),
                            ft.DataCell(ft.Text(pet['type'], size=16)), 
                            ft.DataCell(ft.Text(pet['gender'], size=16)),
                            ft.DataCell(ft.Text(pet.get('age', '-'), size=16)), 
                            ft.DataCell(ft.Text(pet['owner'], size=16)),
                            ft.DataCell(ft.Text(pet['phone'], size=16)),
                            ft.DataCell(
                                ft.Row([
                                    # 🌟 ยกเลิกการใช้ lambda และฝาก ID ไว้ใน data แทน (ป้องกันบั๊ก 100%)
                                    ft.ElevatedButton("แก้ไข", color="#0D9488", bgcolor="#CCFBF1", height=32, data=pet['id'], on_click=self.edit_pet),
                                    ft.ElevatedButton("ลบ", color="#EF4444", bgcolor="#FEE2E2", height=32, data=pet['id'], on_click=self.confirm_delete)
                                ], spacing=8)
                            )
                        ]
                    )
                )
                display_no += 1
        
        self.data_table.rows = new_rows
        self.page.update()

    # 🌟 รับค่า event (e) จากปุ่ม แล้วดึง ID ออกมาจาก data
    def edit_pet(self, e):
        pet_id = e.control.data 
        pet = next((p for p in pets_data if p['id'] == pet_id), None)
        if pet:
            self.pet_name.value = pet['name']
            
            options = ["สุนัข", "แมว", "กระต่าย", "นก"]
            if pet['type'] in options:
                self.pet_type.value = pet['type']
                self.pet_type_other.value = ""
            else:
                self.pet_type.value = "อื่นๆ"
                self.pet_type_other.value = pet['type'] if pet['type'] != "-" else ""
            
            self.pet_gender.value = pet['gender'] if pet['gender'] != "-" else None
            
            age_str = pet.get('age', '')
            self.pet_age_years.value = ""
            self.pet_age_months.value = ""
            if "ปี" in age_str:
                self.pet_age_years.value = age_str.split("ปี")[0].strip()
            if "เดือน" in age_str:
                parts = age_str.split("เดือน")[0].split()
                self.pet_age_months.value = parts[-1].strip()

            self.owner_name.value = pet['owner']
            self.owner_phone.value = pet['phone']
            
            self.editing_id = pet_id
            self.txt_save.value = "อัปเดตข้อมูล"
            
            self.switch_tab(1) 
            self.page.update()

    def save_pet(self, e):
        self.btn_save.disabled = True
        self.page.update()

        if not self.pet_name.value or not self.owner_name.value:
            self.show_snackbar("กรุณากรอกข้อมูลให้ครบถ้วน", is_error=True)
            self.btn_save.disabled = False
            self.page.update()
            return

        final_type = self.pet_type.value
        if final_type == "อื่นๆ":
            final_type = self.pet_type_other.value if self.pet_type_other.value else "ไม่ได้ระบุ"
        elif not final_type:
            final_type = "-"

        age_str = f"{self.pet_age_years.value} ปี " if self.pet_age_years.value else ""
        age_str += f"{self.pet_age_months.value} เดือน" if self.pet_age_months.value else ""
        final_age = age_str.strip() if age_str else "-"
        final_gender = self.pet_gender.value if self.pet_gender.value else "-"

        if self.editing_id:
            update_pet_db(self.editing_id, self.pet_name.value, final_type, final_gender, final_age, self.owner_name.value, self.owner_phone.value)
            self.show_snackbar("อัปเดตข้อมูลเรียบร้อยแล้ว")
        else:
            add_pet_db(self.pet_name.value, final_type, final_gender, final_age, self.owner_name.value, self.owner_phone.value)
            self.show_snackbar("บันทึกข้อมูลเรียบร้อยแล้ว")
        
        self.clear_inputs()
        self.current_filter = "ทั้งหมด" 
        self.refresh_table()
        self.switch_tab(0)

        self.btn_save.disabled = False
        self.page.update()

    # 🌟 รับค่า event (e) จากปุ่ม แล้วดึง ID ออกมาจาก data เช่นเดียวกัน
    def confirm_delete(self, e):
        self.item_to_delete = e.control.data # อ่าน ID จากปุ่ม
        print(f"[DEBUG] confirm_delete: item_to_delete = {self.item_to_delete}")
        # dialog ถูกใส่ไว้ใน page.overlay ตั้งแต่ตอน __init__ แล้ว
        # แค่ toggle .open แล้ว update พอ ใช้ได้ทุกเวอร์ชันของ Flet
        self.delete_dialog.open = True
        self.page.update()

    def close_delete_dlg(self, e=None):
        self.item_to_delete = None 
        self.delete_dialog.open = False
        self.page.update()

    def execute_delete(self, e):
        print(f"[DEBUG] execute_delete called, item_to_delete = {self.item_to_delete}")
        try:
            if self.item_to_delete is not None:
                delete_pet_db(self.item_to_delete)
                self.delete_dialog.open = False
                self.refresh_table()
                self.show_snackbar("ลบข้อมูลสำเร็จ")
            else:
                self.delete_dialog.open = False
                self.page.update()
        except Exception as ex:
            import traceback
            traceback.print_exc()
            self.delete_dialog.open = False
            self.page.update()
            self.show_snackbar(f"เกิดข้อผิดพลาด: {ex}", is_error=True)
        finally:
            self.item_to_delete = None

    def search_pet(self, e):
        self.refresh_table(self.search_input.value)

    def switch_tab(self, index):
        menus = [(self.menu_buttons[0], self.txt_menu_0), (self.menu_buttons[1], self.txt_menu_1)]
        for i, (btn, txt) in enumerate(menus):
            if i == index:
                btn.bgcolor = "#0F172A"
                txt.color = "white"
            else:
                btn.bgcolor = "white"
                txt.color = "#64748B"
        self.main_container.content = self.tab_contents[index]
        self.page.update()

    def setup_layouts(self):
        self.header_image = ft.Image(
            src="animal.jpg",
            fit=ft.ImageFit.COVER,
            border_radius=12,
        )
        self.header_title = ft.Text(
            "PET REGISTRATION",
            size=50,
            font_family="Sarabun-Bold",
            color="black",
            text_align=ft.TextAlign.CENTER,
            style=ft.TextStyle(
                shadow=ft.BoxShadow(
                    color="white",
                    blur_radius=15,
                    offset=ft.Offset(0, 0),
                )
            ),
        )
        self.header_overlay = ft.Column(
            [
                ft.Container(height=15),
                ft.Row([self.header_title], alignment=ft.MainAxisAlignment.CENTER),
            ]
        )
        self.header_stack = ft.Stack(
            controls=[self.header_image, self.header_overlay]
        )

        for btn in [
            self.btn_filter_all,
            self.btn_filter_dog,
            self.btn_filter_cat,
            self.btn_filter_other,
        ]:
            btn.width = None
            btn.col = {"sm": 6, "md": 3, "lg": 3}

        filter_row = ft.ResponsiveRow(
            [
                self.btn_filter_all,
                self.btn_filter_dog,
                self.btn_filter_cat,
                self.btn_filter_other,
            ],
            spacing=8,
            run_spacing=8,
        )

        self.search_button = ft.ElevatedButton(
            "ค้นหา",
            on_click=self.search_pet,
            bgcolor="#F1F5F9",
            height=45,
        )
        self.search_button.col = {"sm": 12, "md": 4, "lg": 2}

        search_row = ft.ResponsiveRow(
            [self.search_input, self.search_button],
            spacing=10,
            run_spacing=10,
        )

        table_scroll = ft.Row(
            [self.data_table],
            scroll=ft.ScrollMode.AUTO,
        )

        self.overview_and_table_card = ft.Container(
            bgcolor="white",
            padding=30,
            border_radius=12,
            content=ft.Column(
                [
                    ft.Text("ภาพรวมฐานข้อมูล", weight="bold", size=22, color="#0F172A"),
                    filter_row,
                    ft.Divider(height=30, color="#F1F5F9"),
                    ft.Text("รายชื่อในระบบ", weight="bold", size=20),
                    search_row,
                    ft.Divider(height=12, color="transparent"),
                    table_scroll,
                ],
                spacing=12,
            ),
        )

        pet_basic_row = ft.ResponsiveRow(
            [self.pet_name, self.pet_type, self.pet_type_other, self.pet_breed],
            spacing=15,
            run_spacing=15,
        )

        pet_detail_row = ft.ResponsiveRow(
            [
                self.pet_age_years,
                self.pet_age_months,
                self.pet_weight,
                self.pet_color,
                self.dob_field,
                self.dob_btn,
            ],
            spacing=15,
            run_spacing=15,
        )

        owner_row = ft.ResponsiveRow(
            [self.owner_name, self.owner_phone, self.owner_address],
            spacing=15,
            run_spacing=15,
        )

        health_row = ft.ResponsiveRow(
            [self.vaccine_field, self.is_spayed],
            spacing=15,
            run_spacing=15,
        )

        notes_row = ft.ResponsiveRow(
            [self.health_notes],
            spacing=15,
            run_spacing=15,
        )

        self.form_card = ft.Container(
            bgcolor="white",
            padding=30,
            border_radius=12,
            content=ft.Column(
                [
                    ft.Text("ข้อมูลสัตว์เลี้ยง", weight="bold", size=20),
                    pet_basic_row,
                    pet_detail_row,
                    self.pet_gender,
                    ft.Divider(height=30, color="#F1F5F9"),
                    ft.Text("ข้อมูลเจ้าของ", weight="bold", size=20),
                    owner_row,
                    ft.Divider(height=30, color="#F1F5F9"),
                    ft.Text("ข้อมูลสุขภาพ", weight="bold", size=20),
                    health_row,
                    notes_row,
                    ft.Container(height=10),
                    ft.Row([self.btn_save], alignment=ft.MainAxisAlignment.END),
                ],
                spacing=12,
            ),
        )

        btn_style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8)
        )
        self.menu_buttons = [
            ft.ElevatedButton(
                content=self.txt_menu_0,
                on_click=lambda e: self.switch_tab(0),
                height=55,
                style=btn_style,
            ),
            ft.ElevatedButton(
                content=self.txt_menu_1,
                on_click=lambda e: self.switch_tab(1),
                height=55,
                style=btn_style,
            ),
        ]

        for btn in self.menu_buttons:
            btn.width = None
            btn.col = {"sm": 12, "md": 6, "lg": 6}

        self.menu_buttons[0].bgcolor = "#0F172A"
        self.txt_menu_0.color = "white"
        self.menu_buttons[1].bgcolor = "white"
        self.txt_menu_1.color = "#64748B"

        menu_row = ft.ResponsiveRow(
            self.menu_buttons,
            spacing=12,
            run_spacing=12,
        )

        self.tab_contents = [self.overview_and_table_card, self.form_card]
        self.main_container = ft.Container(content=self.tab_contents[0])

        self.app_layout = ft.Column(
            [
                self.header_stack,
                ft.Container(height=4),
                menu_row,
                ft.Divider(height=4, color="transparent"),
                self.main_container,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=8,
        )

        self.root_container = ft.Container(content=self.app_layout)

        self.page.on_resized = self.handle_resize
        self.handle_resize()

    def handle_resize(self, e=None):
        page_width = self.page.width or 1000

        if page_width < 600:
            page_padding = 8
            card_padding = 16
            title_size = 28
        elif page_width < 900:
            page_padding = 16
            card_padding = 24
            title_size = 38
        else:
            page_padding = 40
            card_padding = 40
            title_size = 50

        self.page.padding = page_padding
        available_width = max(280, page_width - (page_padding * 2))
        content_width = min(900, available_width)

        self.root_container.width = content_width
        self.header_stack.width = content_width
        self.header_image.width = content_width
        self.header_overlay.width = content_width
        self.header_title.size = title_size

        self.overview_and_table_card.padding = card_padding
        self.form_card.padding = card_padding

        if e is not None:
            self.page.update()

    def build(self):
        self.refresh_table()
        return self.root_container
    

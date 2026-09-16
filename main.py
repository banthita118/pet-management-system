import flet as ft
from views.pet_manager import PetManager


def main(page: ft.Page):
    page.title = "Pet Management System"
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#EBF4FA"
    page.padding = 8
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.fonts = {
        "Sarabun": "https://raw.githubusercontent.com/google/fonts/main/ofl/sarabun/Sarabun-Regular.ttf",
        "Sarabun-Bold": "https://raw.githubusercontent.com/google/fonts/main/ofl/sarabun/Sarabun-Bold.ttf",
    }

    page.theme = ft.Theme(font_family="Sarabun")

    manager = PetManager(page)
    page.add(manager.build())


if __name__ == "__main__":
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        assets_dir="assets",
    )

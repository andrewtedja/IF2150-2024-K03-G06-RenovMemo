import flet as ft

class RenovMemoNavbar(ft.Row):
    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page

        self.controls = [
            # Logo on the left
            ft.Text("RenovMemo", size=24, weight=ft.FontWeight.BOLD, expand=1),

            ft.Row(
                [
                    ft.ElevatedButton(
                        text="Proyek",
                        on_click=lambda e: self.page.go("/proyek"),
                        style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_100),
                    ),
                    ft.ElevatedButton(
                        text="Inspirasi",
                        on_click=lambda e: self.page.go("/inspirasi"),
                        style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_100),
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,  
                expand=2,  
            ),
        ]

        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN
        self.padding = ft.padding.only(top=16, bottom=16)
        self.bgcolor = ft.colors.GREY_800
        self.text_color = ft.colors.WHITE

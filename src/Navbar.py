import flet as ft

class RenovMemoNavbar(ft.Row):
    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page

        self.controls = [
            ft.Container(
                content=ft.Text(
                    "RenovMemo", 
                    size=24, 
                    weight=ft.FontWeight.W_800, 
                    color=ft.colors.WHITE
                ),
                padding=10,
            ),

            ft.Row(
                [
                    ft.FilledButton(
                        content=ft.Text("Proyek", weight=ft.FontWeight.W_500),
                        on_click=lambda e: self.page.go("/proyek"),
                        style=ft.ButtonStyle(
                            bgcolor={
                                ft.MaterialState.DEFAULT: ft.colors.BLUE_600,
                                ft.MaterialState.HOVERED: ft.colors.BLUE_700,
                            },
                            color=ft.colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        height=35,
                    ),
                    ft.FilledButton(
                        content=ft.Text("Inspirasi", weight=ft.FontWeight.W_500),
                        on_click=lambda e: self.page.go("/inspirasi"),
                        style=ft.ButtonStyle(
                            bgcolor={
                                ft.MaterialState.DEFAULT: ft.colors.BLUE_600,
                                ft.MaterialState.HOVERED: ft.colors.BLUE_700,
                            },
                            color=ft.colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        height=35,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15,
            )
        ]

        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN
        self.vertical_alignment = ft.CrossAxisAlignment.CENTER
        self.padding = ft.padding.only(left=20, right=20, top=10, bottom=10)
        self.bgcolor = ft.colors.BLUE_GREY_900
        self.height = 50
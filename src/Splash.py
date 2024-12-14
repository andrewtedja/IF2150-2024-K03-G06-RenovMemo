import flet as ft

def splash_page(page: ft.Page):
    page.title = "RenovMemo"
    page.bgcolor = ft.colors.BLUE_GREY_900
    page.padding = 0

    def go_to_main_page(e):
        page.go("/main")

    logo = ft.Text(
        "RenovMemo",
        size=80,
        color=ft.colors.WHITE,
        weight=ft.FontWeight.BOLD,
    )

    button = ft.ElevatedButton(
        content=ft.Text("Enter", size=18),
        on_click=go_to_main_page,
        style=ft.ButtonStyle(
            color={
                ft.MaterialState.HOVERED: ft.colors.WHITE,
                ft.MaterialState.DEFAULT: ft.colors.BLUE_GREY_500,
            },
            bgcolor={
                ft.MaterialState.HOVERED: ft.colors.BLUE_500,
                ft.MaterialState.DEFAULT: ft.colors.WHITE,
            },
            padding=20,
            animation_duration=500,
            side={
                ft.MaterialState.DEFAULT: ft.BorderSide(2, ft.colors.BLUE_200),
                ft.MaterialState.HOVERED: ft.BorderSide(2, ft.colors.WHITE),
            },
        ),
    )

    content = ft.Column(
        [
            logo,
            ft.Container(height=40),  
            button
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    return ft.Container(
        content=content,
        alignment=ft.alignment.center,
        expand=True,
    )
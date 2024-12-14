from database import initializeDatabase, closeDatabase
import flet as ft
from Proyek import ProyekManager
from Tugas import TugasManager
from Inspirasi import InspirasiProyekManager
from Navbar import RenovMemoNavbar


def main(page: ft.Page):
    page.title = "RenovMemo"
    navbar = RenovMemoNavbar(page)  

    # Initialize FilePicker
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    def route_change(e):
        page.views.clear()

        # PROYEK
        if page.route == "/" or page.route.startswith("/proyek"):
            manager = ProyekManager(page)
            page.views.append(
                ft.View(
                    "/proyek",
                    controls=[
                        navbar,
                        manager.build()
                    ],
                )
            )
        # TUGAS
        elif page.route.startswith("/tugas"):
            query_str = page.route.replace("/tugas?", "")
            query_params = dict(pair.split('=') for pair in query_str.split('&') if '=' in pair)
            proyek_id = int(query_params.get("proyek_id", 1))

            tugas_manager = TugasManager(page, proyek_id)
            page.views.append(
                ft.View(
                    "/tugas",
                    controls=[
                        navbar,
                        tugas_manager.build()
                    ],
                )
            )
        # INSPIRASI
        elif page.route.startswith("/inspirasi"):
            inspirasi_manager = InspirasiProyekManager(page, file_picker)
            page.views.append(
                ft.View(
                    "/inspirasi",
                    controls=[
                        navbar,
                        inspirasi_manager.build()
                    ],
                )
            )

        page.update()

    def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            page.go(page.views[-1].route)
        else:
            page.window_close()

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Set the default route
    page.go("/proyek")

ft.app(target=main)

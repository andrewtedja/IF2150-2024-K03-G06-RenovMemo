import flet as ft
import database

STATUS_OPTIONS = ["Belum Dimulai", "Sedang Berjalan", "Selesai"]

import flet as ft

class RenovMemoNavbar(ft.Row):
    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page

        self.controls = [
            ft.Text("RenovMemo", size=24, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                text="Proyek",
                on_click=lambda e: self.page.views[0].show(),
                style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_100)
            ),
            ft.ElevatedButton(
                text="Inspirasi",
                on_click=lambda e: self.page.views[1].show(),
                style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_100)
            )
        ]

        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN
        self.padding = ft.padding.only(top=16, bottom=16)
        self.bgcolor = ft.colors.GREY_800
        self.text_color = ft.colors.WHITE

class ProyekManager:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.database = database
        self.database.initializeDatabase()
        self.proyek_list = []


        # Proyek View Components
        self.filter_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option("All")] + [ft.dropdown.Option(status) for status in STATUS_OPTIONS],
            value="All",
            on_change=self.load_proyek,
            width=200,
        )

        self.proyek_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nama")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Budget")),
                ft.DataColumn(ft.Text("Tanggal Mulai")),
                ft.DataColumn(ft.Text("Tanggal Selesai")),
                ft.DataColumn(ft.Text("Rincian")),
                ft.DataColumn(ft.Text("Action")),
            ]
        )

        self.add_proyek_button = ft.ElevatedButton(
            text="Tambah Proyek",
            on_click=self.open_add_proyek_dialog,
        )

        # Inspirasi View (placeholder)
        self.inspirasi_view = ft.Column([
            ft.Text("Inspirasi View - Coming Soon!", size=24),
            ft.Text("Here you can add your inspiration and project ideas.")
        ], visible=False)

        # Main Layout
        self.page.add(
            ft.Column(
                [
                    ft.Row([
                        ft.Text("Filter by Status:"),
                        self.filter_dropdown,
                    ]),
                    self.proyek_table,
                    self.add_proyek_button,
                    self.inspirasi_view
                ]
            )
        )

        self.load_proyek(None)

    def show_proyek_view(self, e):
        self.proyek_table.visible = True
        self.filter_dropdown.parent.parent.visible = True
        self.add_proyek_button.visible = True
        self.inspirasi_view.visible = False
        self.page.update()

    def show_inspirasi_view(self, e):
        self.proyek_table.visible = False
        self.filter_dropdown.parent.parent.visible = False
        self.add_proyek_button.visible = False
        self.inspirasi_view.visible = True
        self.page.update()

    def load_proyek(self, e):
        self.proyek_table.rows.clear()

        filter_status = self.filter_dropdown.value
        if filter_status == "All":
            self.proyek_list = self.database.getAllProyek()
        else:
            self.proyek_list = self.database.getProyekWithStatus(filter_status)

        for proyek in self.proyek_list:
            self.proyek_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(proyek[1])),  # Nama
                        ft.DataCell(ft.Text(proyek[2])),  # Status
                        ft.DataCell(ft.Text(f"Rp. {proyek[6]}")),  # Budget
                        ft.DataCell(ft.Text(proyek[4])),  # Tanggal Mulai
                        ft.DataCell(ft.Text(proyek[5])),  # Tanggal Selesai
                        ft.DataCell(ft.Text(proyek[3])),  # Rincian
                        ft.DataCell(
                            ft.ElevatedButton(
                                text="Delete",
                                on_click=lambda e, pid=proyek[0]: self.delete_proyek(pid),
                            )
                        ),
                    ]
                )
            )

        self.page.update()

    def delete_proyek(self, proyek_id):
        confirm = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text("Are you sure you want to delete this project?"),
            actions=[
                ft.TextButton("Yes", on_click=lambda e: self.confirm_delete(proyek_id)),
                ft.TextButton("No", on_click=lambda e: self.page.dialog.close()),
            ],
        )
        self.page.dialog = confirm
        confirm.open = True
        self.page.update()

    def confirm_delete(self, proyek_id):
        self.database.deleteProyek(proyek_id)
        self.page.dialog.open = False
        self.load_proyek(None)

    def open_add_proyek_dialog(self, e):
        self.add_dialog = ft.AlertDialog()

        self.nama_input = ft.TextField(label="Nama Proyek")
        self.deskripsi_input = ft.TextField(label="Deskripsi Proyek")
        self.status_input = ft.Dropdown(
            options=[ft.dropdown.Option(status) for status in STATUS_OPTIONS]
        )
        self.tanggal_mulai_input = ft.TextField(label="Tanggal Mulai (YYYY-MM-DD)")
        self.tanggal_selesai_input = ft.TextField(label="Tanggal Selesai (YYYY-MM-DD)")
        self.budget_input = ft.TextField(label="Budget (Rupiah)")

        self.add_dialog.content = ft.Column([
            self.nama_input,
            self.deskripsi_input,
            self.status_input,
            self.tanggal_mulai_input,
            self.tanggal_selesai_input,
            self.budget_input,
        ])
        self.add_dialog.actions = [
            ft.TextButton("Tambah", on_click=self.add_proyek),
            ft.TextButton("Batal", on_click=self.close_add_dialog),
        ]

        self.page.dialog = self.add_dialog
        self.add_dialog.open = True
        self.page.update()

    def close_add_dialog(self, e):
        # Clear all input fields
        self.nama_input.value = ""
        self.deskripsi_input.value = ""
        self.status_input.value = None
        self.tanggal_mulai_input.value = ""
        self.tanggal_selesai_input.value = ""
        self.budget_input.value = ""

        # Close the dialog
        self.page.dialog.open = False
        self.page.update()

    def add_proyek(self, e):
        nama = self.nama_input.value.strip()
        deskripsi = self.deskripsi_input.value.strip()
        status = self.status_input.value
        tanggal_mulai = self.tanggal_mulai_input.value.strip()
        tanggal_selesai = self.tanggal_selesai_input.value.strip()
        budget = self.budget_input.value.strip()

        if nama and deskripsi and status and tanggal_mulai and tanggal_selesai and budget:
            try:
                self.database.addProyek(
                    nama, status, deskripsi, tanggal_mulai, tanggal_selesai, int(budget)
                )
                self.page.dialog.open = False
                self.load_proyek(None)
                self.page.snack_bar = ft.SnackBar(ft.Text("Proyek berhasil ditambahkan"))
                self.page.snack_bar.open = True
            except ValueError:
                self.page.snack_bar = ft.SnackBar(ft.Text("Budget harus berupa angka"))
                self.page.snack_bar.open = True
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("Mohon isi semua field"))
            self.page.snack_bar.open = True

        self.page.update()


def main(page: ft.Page):
    page.title = "Proyek Manager"
    page.add(RenovMemoNavbar(page))
    page.window_width = 800
    page.window_height = 600
    page.padding = 20
    ProyekManager(page)

ft.app(target=main)
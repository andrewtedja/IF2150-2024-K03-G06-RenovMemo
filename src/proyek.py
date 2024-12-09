import flet as ft
import database
from datetime import datetime

STATUS_OPTIONS = ["Belum Dimulai", "Sedang Berjalan", "Selesai"]

def show_snackbar(page: ft.Page, message: str):
    snack_bar = ft.SnackBar(content=ft.Text(message))
    page.overlay.append(snack_bar)
    snack_bar.open = True
    page.update()

class AddProyekDialog(ft.AlertDialog):
    def __init__(self, page, on_add_callback):
        super().__init__()
        self.page = page
        self.on_add_callback = on_add_callback

        self.nama_label = ft.Text("Nama Proyek", size=14)
        self.nama_input = ft.TextField(label="Masukkan nama proyek", expand=1, width=600)

        self.deskripsi_label = ft.Text("Deskripsi Proyek", size=14)
        self.deskripsi_input = ft.TextField(label="Masukkan deskripsi proyek", multiline=True, min_lines=3, expand=1, width=600)

        self.status_label = ft.Text("Status Proyek", size=14)
        self.status_input = ft.Dropdown(
            options=[ft.dropdown.Option(status) for status in STATUS_OPTIONS],
            width=600
        )

        self.tanggal_mulai_label = ft.Text("Tanggal Mulai (YYYY-MM-DD)", size=14)
        self.tanggal_mulai_input = ft.TextField(label="Contoh: 2024-01-01", width=600)

        self.tanggal_selesai_label = ft.Text("Tanggal Selesai (YYYY-MM-DD)", size=14)
        self.tanggal_selesai_input = ft.TextField(label="Contoh: 2024-12-31", width=600)

        self.budget_label = ft.Text("Budget (Rupiah)", size=14)
        self.budget_input = ft.TextField(label="Contoh: 100000", width=600)

        self.content = ft.Column(
            [
                self.nama_label,
                self.nama_input,
                self.deskripsi_label,
                self.deskripsi_input,
                self.status_label,
                self.status_input,
                self.tanggal_mulai_label,
                self.tanggal_mulai_input,
                self.tanggal_selesai_label,
                self.tanggal_selesai_input,
                self.budget_label,
                self.budget_input,
            ],
            spacing=10
        )
        self.actions = [
            ft.ElevatedButton(text="Tambah", on_click=self.add_proyek),
            ft.TextButton(text="Batal", on_click=self.close_dialog),
        ]

    def add_proyek(self, e):
        nama = self.nama_input.value.strip()
        deskripsi = self.deskripsi_input.value.strip()
        status = self.status_input.value
        tanggal_mulai = self.tanggal_mulai_input.value.strip()
        tanggal_selesai = self.tanggal_selesai_input.value.strip()
        budget = self.budget_input.value.strip()
        # VALIDASI

        if not (nama and deskripsi and status and tanggal_mulai and tanggal_selesai and budget):
            show_snackbar(self.page, "Mohon isi semua field")
            return

        if not self.validate_date(tanggal_mulai) or not self.validate_date(tanggal_selesai):
            show_snackbar(self.page, "Format tanggal tidak valid. Gunakan YYYY-MM-DD.")
            return

        try:
            budget_value = int(budget)
            if len(budget) > 15:
                show_snackbar(self.page, "Budget terlalu mahal!")
                return
        except ValueError:
            show_snackbar(self.page, "Budget harus berupa angka")
            return

        self.on_add_callback(nama, status, deskripsi, tanggal_mulai, tanggal_selesai, budget_value)
        self.close_dialog(e)

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def close_dialog(self, e):
        self.page.overlay.remove(self)
        self.page.update()

class DetailProyekDialog(ft.AlertDialog):
    def __init__(self, page, proyek_data, on_update_callback):
        super().__init__()
        self.page = page
        self.proyek_data = proyek_data
        self.on_update_callback = on_update_callback

        self.content = ft.Container(
            width=600,
            height=1000,
            content=ft.Column(
                [
                    ft.Text(f"Proyek: {self.proyek_data['nama']}", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text(f"Deskripsi: {self.proyek_data['deskripsi']}", size=16, min_lines=3),
                    ft.Text(f"Status: {self.proyek_data['status']}", size=16),
                    ft.Text(f"Tanggal Mulai: {self.proyek_data['tanggal_mulai']}", size=16),
                    ft.Text(f"Tanggal Selesai: {self.proyek_data['tanggal_selesai']}", size=16),
                    ft.Text(f"Budget: Rp. {self.proyek_data['budget']}", size=16),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.START,
            ),
            alignment=ft.alignment.center,
            padding=20,
        )
        self.actions = [
            ft.ElevatedButton(text="Edit"),  
            ft.ElevatedButton(text="Hapus", on_click=self.delete_proyek),
            ft.TextButton(text="Tutup", on_click=self.close_dialog),
        ]

    def delete_proyek(self, e):
        confirm = ft.AlertDialog(
            title=ft.Text("Konfirmasi Hapus"),
            content=ft.Text("Apakah Anda yakin ingin menghapus proyek ini?"),
            actions=[
                ft.TextButton("Ya", on_click=lambda e: self.confirm_delete()),
                ft.TextButton("Tidak", on_click=lambda e: self.close_dialog(e)),
            ],
        )
        self.page.overlay.append(confirm)
        confirm.open = True
        self.page.update()

    def confirm_delete(self):
        database.deleteProyek(self.proyek_data["proyek_id"])
        show_snackbar(self.page, "Proyek berhasil dihapus.")
        self.on_update_callback()
        self.close_dialog(None)

    def close_dialog(self, e):
        self.page.overlay.remove(self)
        self.page.update()

class ProyekManager:
    def __init__(self, page: ft.Page):
        self.page = page
        self.database = database
        self.database.initializeDatabase()

        self.current_page = 1
        self.items_per_page = 5
        self.total_pages = 1
        self.proyek_list = []

        self.title = ft.Container(
            content=ft.Text("Daftar Proyek", size=28, weight=ft.FontWeight.BOLD),
            alignment=ft.alignment.center,
            padding=ft.padding.all(20),
        )

        self.filter_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option("All")] + [ft.dropdown.Option(status) for status in STATUS_OPTIONS],
            value="All",
            on_change=self.load_proyek,
            width=200,
        )

        self.add_proyek_button = ft.ElevatedButton(
            text="Tambah Proyek",
            style=ft.ButtonStyle(
                color="white",
                bgcolor="blue",
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
            ),
            on_click=self.open_add_proyek_dialog,
        )

        self.proyek_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nama", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Budget", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Mulai", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Selesai", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Rincian", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(2, "lightgray"),
            border_radius=10,
            horizontal_margin=20,
            column_spacing=100,
        )

        self.prev_button = ft.ElevatedButton(
            text="Sebelum",
            on_click=self.prev_page,
            disabled=True,
        )
        self.next_button = ft.ElevatedButton(
            text="Lanjut",
            on_click=self.next_page,
            disabled=True,
        )
        self.page_label = ft.Text("Page 1 of 1")

        self.pagination = ft.Row(
            controls=[self.prev_button, self.page_label, self.next_button],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        self.main_column = ft.Column(
            controls=[
                self.title,
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Text("Filter Status:"),
                                    self.filter_dropdown,
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                spacing=10,
                            ),
                            self.add_proyek_button,  
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        expand=True,
                    ),
                    padding=ft.padding.symmetric(horizontal=20),
                ),
                self.proyek_table,
                self.pagination,
            ]
        )

        self.load_proyek(None)

    def load_proyek(self, e):
        filter_status = self.filter_dropdown.value
        if filter_status == "All":
            proyek_list = self.database.getAllProyek()
        else:
            proyek_list = self.database.getProyekWithStatus(filter_status)

        self.proyek_list = proyek_list
        total_items = len(self.proyek_list)
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)

        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        elif self.current_page < 1:
            self.current_page = 1

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        paginated_proyek = self.proyek_list[start_idx:end_idx]

        self.proyek_table.rows.clear()
        if not paginated_proyek:
            self.page_label.value = f"Page {self.current_page} of {self.total_pages}"
            self.prev_button.disabled = self.current_page <= 1
            self.next_button.disabled = self.current_page >= self.total_pages
            self.page.update()
            return

        for proyek in paginated_proyek:
            # proyek = [id, nama, status, deskripsi, tgl_mulai, tgl_selesai, budget]
            view_handler = lambda e, pid=proyek[0]: self.view_rincian(pid)
            self.proyek_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(proyek[1], size=16)),
                        ft.DataCell(ft.Text(proyek[2], size=16)),
                        ft.DataCell(ft.Text(f"Rp. {proyek[6]}", size=16)),
                        ft.DataCell(ft.Text(proyek[4], size=16)),
                        ft.DataCell(ft.Text(proyek[5], size=16)),
                        ft.DataCell(
                            ft.ElevatedButton(
                                text="Lihat",
                                style=ft.ButtonStyle(
                                    color="white",
                                    bgcolor="green",
                                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                ),
                                on_click=view_handler,
                            )
                        ),
                    ]
                )
            )

        self.page_label.value = f"Page {self.current_page} of {self.total_pages}"
        self.prev_button.disabled = self.current_page <= 1
        self.next_button.disabled = self.current_page >= self.total_pages
        self.page.update()

    def view_rincian(self, proyek_id):
        self.page.go(f"/tugas?proyek_id={proyek_id}")

    def open_add_proyek_dialog(self, e):
        add_dialog = AddProyekDialog(self.page, self.add_proyek_to_database)
        self.page.overlay.append(add_dialog)
        add_dialog.open = True
        self.page.update()

    def add_proyek_to_database(self, nama, status, deskripsi, tanggal_mulai, tanggal_selesai, budget):
        self.database.addProyek(nama, status, deskripsi, tanggal_mulai, tanggal_selesai, budget)
        show_snackbar(self.page, "Proyek berhasil ditambahkan")
        self.refresh_data()

    def refresh_data(self):
        self.load_proyek(None)

    def prev_page(self, e):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_proyek(None)

    def next_page(self, e):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_proyek(None)

    def build(self):
        return self.main_column

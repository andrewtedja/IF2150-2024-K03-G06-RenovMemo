import flet as ft
import database
import base64
import os
from datetime import datetime

STATUS_OPTIONS = ["Belum Dimulai", "Sedang Berjalan", "Selesai"]

def show_snackbar(page: ft.Page, message: str):
    snack_bar = ft.SnackBar(content=ft.Text(message))
    page.overlay.append(snack_bar)
    snack_bar.open = True
    page.update()

class AddInspirasiDialog(ft.AlertDialog):
    def __init__(self, page, on_add_callback, file_picker):
        super().__init__()
        self.page = page
        self.on_add_callback = on_add_callback
        self.file_picker = file_picker
        self.chosen_image_data = None
        self.chosen_image_name = ft.Text("Belum ada gambar yang dipilih.")

        self.nama_label = ft.Text("Nama Inspirasi", size=14)
        self.nama_input = ft.TextField(
            label="Masukkan nama inspirasi",
            expand=1,
            width=600,
        )

        self.deskripsi_label = ft.Text("Deskripsi Inspirasi", size=14)
        self.deskripsi_input = ft.TextField(
            label="Masukkan deskripsi inspirasi",
            multiline=True,
            min_lines=2,
            expand=1,
            width=600,
        )

        self.referensi_label = ft.Text("Referensi Inspirasi (opsional)", size=14)
        self.referensi_input = ft.TextField(
            label="Masukkan referensi inspirasi",
            expand=1,
            width=600,
        )

        self.gambar_button = ft.ElevatedButton(
            "Pilih Gambar",
            on_click=lambda e: self.file_picker.pick_files(allow_multiple=False)
        )

        self.content = ft.Container(
            height=500,  
            content=ft.Column(
                [
                    self.nama_label,
                    self.nama_input,
                    ft.Container(height=10),  
                    self.deskripsi_label,
                    self.deskripsi_input,
                    ft.Container(height=10),
                    self.referensi_label,
                    self.referensi_input,
                    ft.Container(height=10),
                    self.gambar_button,
                    self.chosen_image_name,
                ],
                spacing=5 
            ),
            alignment=ft.alignment.center,
            padding=ft.padding.all(20),
        )
        self.actions = [
            ft.ElevatedButton(text="Tambah", on_click=self.add_inspirasi),
            ft.TextButton(text="Batal", on_click=self.close_dialog),
        ]

    def on_file_picker_result(self, e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            file_path = e.files[0].path
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        self.chosen_image_data = f.read()
                    self.chosen_image_name.value = f"Gambar dipilih: {os.path.basename(file_path)}"
                    show_snackbar(self.page, "Gambar dipilih.")
                except Exception as ex:
                    show_snackbar(self.page, f"Gagal membaca gambar: {ex}")
            else:
                self.chosen_image_data = None
                self.chosen_image_name.value = "Belum ada gambar yang dipilih."
        else:
            self.chosen_image_data = None
            self.chosen_image_name.value = "Belum ada gambar yang dipilih."
        self.page.update()

    def add_inspirasi(self, e):
        nama = self.nama_input.value.strip()
        deskripsi = self.deskripsi_input.value.strip()
        referensi = self.referensi_input.value.strip()

        if nama and deskripsi:
            self.on_add_callback(nama, deskripsi, self.chosen_image_data, referensi)
            self.close_dialog(e)
        else:
            show_snackbar(self.page, "Mohon isi semua field")
            self.page.update()

    def close_dialog(self, e):
        self.open = False
        self.page.dialog = None
        self.page.update()

class EditInspirasiDialog(ft.AlertDialog):
    def __init__(self, page, inspirasi_data, on_update_callback, file_picker):
        super().__init__()
        self.page = page
        self.inspirasi_id = inspirasi_data["inspirasi_id"]
        self.on_update_callback = on_update_callback
        self.chosen_image_data = None
        self.chosen_image_name = ft.Text("Belum ada gambar baru yang dipilih.")
        self.file_picker = file_picker

        self.nama_label = ft.Text("Nama Inspirasi", size=14)
        self.nama_input = ft.TextField(
            value=inspirasi_data["inspirasi_nama"],
            label="Masukkan nama inspirasi",
            expand=1,
            width=600,
        )

        self.deskripsi_label = ft.Text("Deskripsi Inspirasi", size=14)
        self.deskripsi_input = ft.TextField(
            value=inspirasi_data["inspirasi_deskripsi"],
            label="Masukkan deskripsi inspirasi",
            multiline=True,
            min_lines=3,
            expand=1,
            width=600,
        )

        self.referensi_label = ft.Text("Referensi Inspirasi (opsional)", size=14)
        self.referensi_input = ft.TextField(
            value=inspirasi_data["inspirasi_referensi"],
            label="Masukkan referensi inspirasi",
            expand=1,
            width=600,
        )

        self.gambar_button = ft.ElevatedButton(
            text="Pilih Gambar (opsional)",
            on_click=lambda e: self.file_picker.pick_files(allow_multiple=False)
        )

        self.content = ft.Container(
            height=500,  
            content=ft.Column(
                [
                    self.nama_label,
                    self.nama_input,
                    ft.Container(height=10),
                    self.deskripsi_label,
                    self.deskripsi_input,
                    ft.Container(height=10),
                    self.referensi_label,
                    self.referensi_input,
                    ft.Container(height=10),
                    self.gambar_button,
                    self.chosen_image_name,
                ],
                spacing=5
            ),
            alignment=ft.alignment.center,
            padding=ft.padding.all(20),
        )
        self.actions = [
            ft.ElevatedButton(text="Simpan", on_click=self.save_changes),
            ft.TextButton(text="Batal", on_click=self.close_dialog),
        ]

    def on_file_picker_result(self, e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            file_path = e.files[0].path
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        self.chosen_image_data = f.read()
                    self.chosen_image_name.value = f"Gambar baru dipilih: {os.path.basename(file_path)}"
                    show_snackbar(self.page, "Gambar baru dipilih.")
                except Exception as ex:
                    show_snackbar(self.page, f"Gagal membaca gambar: {ex}")
            else:
                self.chosen_image_data = None
                self.chosen_image_name.value = "Belum ada gambar baru yang dipilih."
        else:
            self.chosen_image_data = None
            self.chosen_image_name.value = "Belum ada gambar baru yang dipilih."
        self.page.update()

    def save_changes(self, e):
        nama = self.nama_input.value.strip()
        deskripsi = self.deskripsi_input.value.strip()
        referensi = self.referensi_input.value.strip()

        if not (nama and deskripsi):
            show_snackbar(self.page, "Mohon isi semua field")
            self.page.update()
            return

        database.editInspirasi(
            inspirasi_id=self.inspirasi_id,
            inspirasi_nama=nama,
            inspirasi_deskripsi=deskripsi,
            inspirasi_gambar_blob=self.chosen_image_data,
            inspirasi_referensi=referensi,
        )
        show_snackbar(self.page, "Inspirasi berhasil diperbarui.")
        self.on_update_callback()
        self.close_dialog(e)

    def close_dialog(self, e):
        self.open = False
        self.page.dialog = None
        self.page.update()

class DetailInspirasiDialog(ft.AlertDialog):
    def __init__(self, page, inspirasi_data, on_update_callback, file_picker):
        super().__init__()
        self.page = page
        self.inspirasi_data = inspirasi_data
        self.on_update_callback = on_update_callback
        self.file_picker = file_picker

        self.content = ft.Container(
            width=600,
            height=500,
            content=ft.Column(
                [
                    ft.Text(f"Inspirasi Proyek: {self.inspirasi_data['inspirasi_nama']}", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text(f"Deskripsi: {self.inspirasi_data['inspirasi_deskripsi']}", size=16),
                    ft.Text(
                        f"Referensi: {self.inspirasi_data['inspirasi_referensi']}",
                        size=16
                    ) if self.inspirasi_data["inspirasi_referensi"] else ft.Text("Referensi: Tidak ada referensi.", size=16),
                    ft.Container(
                        content=ft.Image(
                            src_base64=self.inspirasi_data["inspirasi_gambar"],
                            fit="contain",
                            width=500, 
                            height=250,  
                        ) if self.inspirasi_data["inspirasi_gambar"] else ft.Text("No image provided", size=16),
                        padding=ft.padding.only(top=10),
                    ),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.START,
            ),
            alignment=ft.alignment.center,
            padding=20,
        )
        self.actions = [
            ft.ElevatedButton(text="Edit", on_click=self.open_edit_dialog),
            ft.ElevatedButton(text="Hapus", on_click=self.delete_inspirasi),
            ft.TextButton(text="Tutup", on_click=self.close_dialog),
        ]

    def open_edit_dialog(self, e):
        edit_dialog = EditInspirasiDialog(self.page, self.inspirasi_data, self.on_update_callback, self.file_picker)
        self.file_picker.on_result = edit_dialog.on_file_picker_result
        self.page.dialog = edit_dialog
        edit_dialog.open = True
        self.page.update()

    def delete_inspirasi(self, e):
        confirm = ft.AlertDialog(
            title=ft.Text("Konfirmasi Hapus"),
            content=ft.Text("Apakah Anda yakin ingin menghapus inspirasi ini?"),
            actions=[
                ft.TextButton("Ya", on_click=lambda e: self.confirm_delete()),
                ft.TextButton("Tidak", on_click=lambda e: self.close_dialog(e)),
            ],
        )
        self.page.overlay.append(confirm)
        confirm.open = True
        self.page.update()

    def confirm_delete(self):
        database.deleteInspirasi(self.inspirasi_data["inspirasi_id"])
        show_snackbar(self.page, "Inspirasi berhasil dihapus.")
        self.on_update_callback()
        self.close_dialog(None)

    def close_dialog(self, e):
        self.open = False
        self.page.dialog = None
        self.page.update()

class InspirasiProyekManager:
    def __init__(self, page: ft.Page, file_picker: ft.FilePicker):
        self.page = page
        self.database = database
        self.file_picker = file_picker
        self.database.initializeDatabase()
        self.current_page = 1
        self.items_per_page = 5
        self.total_pages = 1
        self.inspirasi_list = []
        self.title = ft.Container(
            content=ft.Text("Daftar Inspirasi Proyek", size=28, weight=ft.FontWeight.BOLD),
            alignment=ft.alignment.center,
            padding=ft.padding.all(20),
        )
        self.add_inspirasi_button = ft.Container(
            content=ft.Row(
                controls=[
                    ft.ElevatedButton(
                        text="Tambah Inspirasi",
                        style=ft.ButtonStyle(
                            color="white",
                            bgcolor="blue",
                            padding=ft.padding.symmetric(horizontal=20, vertical=10),
                        ),
                        on_click=self.open_add_inspirasi_dialog,
                    )
                ],
                alignment=ft.MainAxisAlignment.END,
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
        )

        # Inspirasi Table
        self.inspirasi_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nama", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Deskripsi", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Rincian", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(2, "lightgray"),
            border_radius=10,
            horizontal_margin=20,
            column_spacing=100,
        )

        self.inspirasi_table_container = ft.Container(
            content=self.inspirasi_table,
            alignment=ft.alignment.center,
            padding=ft.padding.symmetric(vertical=20),
            width=1200,  
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
            spacing=20,
        )

        self.main_column = ft.Column(
            controls=[
                self.title,
                self.add_inspirasi_button,
                self.inspirasi_table_container,
                self.pagination,
            ],
            spacing=20, 
        )

        self.load_inspirasi()

    def load_inspirasi(self):
        self.inspirasi_list = self.database.getAllInspirasi()
        total_items = len(self.inspirasi_list)
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)

        # Pagination
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        elif self.current_page < 1:
            self.current_page = 1

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        paginated_inspirasi = self.inspirasi_list[start_idx:end_idx]

        self.inspirasi_table.rows.clear()
        if not paginated_inspirasi:
            self.page_label.value = f"Page {self.current_page} of {self.total_pages}"
            self.prev_button.disabled = self.current_page <= 1
            self.next_button.disabled = self.current_page >= self.total_pages
            self.page.update()
            return

        for insp in paginated_inspirasi:
            view_handler = lambda e, insp_id=insp[0]: self.view_rincian(e, insp_id)
            self.inspirasi_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(insp[1], size=16)),
                        ft.DataCell(ft.Text(insp[2], size=16, overflow="ellipsis")),
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

    def open_add_inspirasi_dialog(self, e):
        add_dialog = AddInspirasiDialog(self.page, self.add_inspirasi_to_database, self.file_picker)
        self.file_picker.on_result = add_dialog.on_file_picker_result
        self.page.dialog = add_dialog
        add_dialog.open = True
        self.page.update()

    def add_inspirasi_to_database(self, nama, deskripsi, gambar_data, referensi):
        self.database.addInspirasi(nama, deskripsi, gambar_data, referensi)
        show_snackbar(self.page, "Inspirasi berhasil ditambahkan.")
        self.refresh_data()

    def refresh_data(self):
        self.current_page = 1
        self.load_inspirasi()

    def view_rincian(self, e, insp_id):
        inspirasi = self.database.getInspirasiById(insp_id)
        if inspirasi:
            image_base64 = base64.b64encode(inspirasi[3]).decode("utf-8") if inspirasi[3] else None
            inspirasi_data = {
                "inspirasi_id": inspirasi[0],
                "inspirasi_nama": inspirasi[1],
                "inspirasi_deskripsi": inspirasi[2],
                "inspirasi_gambar": image_base64,
                "inspirasi_referensi": inspirasi[4],
            }

            detail_dialog = DetailInspirasiDialog(self.page, inspirasi_data, self.refresh_data, self.file_picker)
            self.file_picker.on_result = detail_dialog.on_file_picker_result  
            self.page.dialog = detail_dialog
            detail_dialog.open = True
            self.page.update()
        else:
            show_snackbar(self.page, "Inspirasi tidak ditemukan.")

    def prev_page(self, e):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_inspirasi()

    def next_page(self, e):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_inspirasi()

    def build(self):
        return self.main_column

def main(page: ft.Page):
    page.title = "Inspirasi Proyek Manager"
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    manager = InspirasiProyekManager(page, file_picker)
    page.add(manager.build())
    page.update()


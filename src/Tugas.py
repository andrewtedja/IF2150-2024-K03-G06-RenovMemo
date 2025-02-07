import flet as ft
import database
from datetime import datetime

STATUS_OPTIONS = ["Belum Dimulai", "Sedang Berjalan", "Selesai"]

def show_snackbar(page: ft.Page, message: str):
    snack_bar = ft.SnackBar(content=ft.Text(message))
    page.overlay.append(snack_bar)
    snack_bar.open = True
    page.update()

class AddTugasDialog(ft.AlertDialog):
    def __init__(self, page, proyek_id, on_add_callback):
        super().__init__()
        self.page = page
        self.proyek_id = proyek_id
        self.on_add_callback = on_add_callback

        self.nama_input = ft.TextField(label="Nama Tugas", width=400)
        self.deskripsi_input = ft.TextField(label="Deskripsi Tugas", multiline=True, min_lines=3, width=400)
        self.status_input = ft.Dropdown(
            options=[ft.dropdown.Option(status) for status in STATUS_OPTIONS],
            label="Status Tugas",
            width=400
        )
        self.estimasi_input = ft.TextField(label="Estimasi Biaya (Rupiah)", width=400)
        self.biaya_aktual_input = ft.TextField(label="Biaya Aktual (Rupiah)", width=400)

        self.content = ft.Column([
            self.nama_input,
            self.deskripsi_input,
            self.status_input,
            self.estimasi_input,
            self.biaya_aktual_input,
        ], spacing=10)
        self.actions = [
            ft.ElevatedButton(text="Tambah", on_click=self.add_tugas),
            ft.TextButton(text="Batal", on_click=self.close_dialog),
        ]

    def add_tugas(self, e):
        nama = self.nama_input.value.strip()
        deskripsi = self.deskripsi_input.value.strip()
        status = self.status_input.value
        estimasi = self.estimasi_input.value.strip()
        biaya_aktual = self.biaya_aktual_input.value.strip()

        if not (nama and status and estimasi and biaya_aktual):
            show_snackbar(self.page, "Mohon isi semua field")
            return

        if not estimasi.isdigit() or not biaya_aktual.isdigit():
            show_snackbar(self.page, "Estimasi dan Biaya Aktual harus berupa angka")
            return

        estimasi_value = int(estimasi)
        biaya_aktual_value = int(biaya_aktual)

        self.on_add_callback(nama, status, deskripsi, self.proyek_id, estimasi_value, biaya_aktual_value)
        show_snackbar(self.page, "Tugas berhasil ditambahkan.")
        self.close_dialog(e)

    def close_dialog(self, e):
        self.open = False
        if self.page:
            self.page.dialog = None
            self.page.update()

class EditTugasDialog(ft.AlertDialog):
    def __init__(self, page, tugas_data, on_update_callback):
        super().__init__()
        self.page = page
        self.tugas_data = tugas_data
        self.on_update_callback = on_update_callback

        self.nama_input = ft.TextField(value=tugas_data["tugas_nama"], label="Nama Tugas", width=400)
        self.deskripsi_input = ft.TextField(value=tugas_data["tugas_deskripsi"], label="Deskripsi Tugas", multiline=True, min_lines=3, width=400)
        self.status_input = ft.Dropdown(
            options=[ft.dropdown.Option(status) for status in STATUS_OPTIONS],
            value=tugas_data["tugas_status"],
            label="Status Tugas",
            width=400
        )

        self.content = ft.Column([
            self.nama_input,
            self.deskripsi_input,
            self.status_input,
        ], spacing=10)
        self.actions = [
            ft.ElevatedButton(text="Simpan", on_click=self.save_changes),
            ft.TextButton(text="Batal", on_click=self.close_dialog),
        ]

    def save_changes(self, e):
        nama = self.nama_input.value.strip()
        deskripsi = self.deskripsi_input.value.strip()
        status = self.status_input.value

        if not (nama and status):
            show_snackbar(self.page, "Mohon isi semua field")
            return

        database.editTugas(
            tugas_id=self.tugas_data["tugas_id"],
            tugas_nama=nama,
            tugas_status=status,
            tugas_deskripsi=deskripsi
        )
        show_snackbar(self.page, "Tugas berhasil diperbarui.")
        self.on_update_callback()
        self.close_dialog(e)

    def close_dialog(self, e):
        self.open = False
        if self.page:
            self.page.dialog = None
            self.page.update()

class ViewBiayaDialog(ft.AlertDialog):
    def __init__(self, page, tugas_data, on_update_callback):
        super().__init__()
        self.page = page
        self.tugas_data = tugas_data
        self.on_update_callback = on_update_callback
        self.is_editing = False

        self.estimasi_input = ft.TextField(
            value=f"Rp. {tugas_data['estimated']:,}",
            label="Estimasi Biaya (Rupiah)",
            width=400,
            read_only=True
        )
        self.biaya_aktual_input = ft.TextField(
            value=f"Rp. {tugas_data['budget']:,}",
            label="Biaya Aktual (Rupiah)",
            width=400,
            read_only=True
        )

        self.content = ft.Container(
            content=ft.Column([
                self.estimasi_input,
                self.biaya_aktual_input,
            ], spacing=10),
            width=450,
            padding=ft.padding.all(20),
        )
        self.edit_button = ft.ElevatedButton(text="Edit", on_click=self.toggle_edit)
        self.close_button = ft.TextButton(text="Tutup", on_click=self.close_dialog)
        self.actions = [
            self.edit_button,
            self.close_button,
        ]

    def toggle_edit(self, e):
        if not self.is_editing:
            self.is_editing = True
            self.estimasi_input.read_only = False
            self.biaya_aktual_input.read_only = False
            self.estimasi_input.value = str(self.tugas_data["estimated"])
            self.biaya_aktual_input.value = str(self.tugas_data["budget"])
            self.edit_button.text = "Simpan"
        else:
            estimasi = self.estimasi_input.value.strip().replace(",", "").replace("Rp.", "")
            biaya_aktual = self.biaya_aktual_input.value.strip().replace(",", "").replace("Rp.", "")

            if not (estimasi and biaya_aktual):
                show_snackbar(self.page, "Mohon isi semua field")
                return

            if not estimasi.isdigit() or not biaya_aktual.isdigit():
                show_snackbar(self.page, "Estimasi dan Biaya Aktual harus berupa angka")
                return

            estimasi_value = int(estimasi)
            biaya_aktual_value = int(biaya_aktual)

            database.editTugas(
                tugas_id=self.tugas_data["tugas_id"],
                estimated=estimasi_value,      
                budget=biaya_aktual_value     
            )
            show_snackbar(self.page, "Biaya berhasil diperbarui.")
            self.on_update_callback()

            self.is_editing = False
            self.estimasi_input.read_only = True
            self.biaya_aktual_input.read_only = True
            self.estimasi_input.value = f"Rp. {estimasi_value:,}"
            self.biaya_aktual_input.value = f"Rp. {biaya_aktual_value:,}"
            self.edit_button.text = "Edit"

        self.page.update()

    def close_dialog(self, e):
        self.open = False
        if self.page:
            self.page.dialog = None
            self.page.update()

class TugasManager:
    def __init__(self, page: ft.Page, proyek_id: int):
        self.page = page
        self.proyek_id = proyek_id
        database.initializeDatabase()

        self.current_page = 1
        self.items_per_page = 5
        self.total_pages = 1
        self.tugas_list = []

        proyek_data = database.getProyek(self.proyek_id)
        if proyek_data:
            proyek_name, proyek_status, proyek_deskripsi, proyek_mulai, proyek_selesai = proyek_data
            proyek_title = f"Proyek: {proyek_name}"
            proyek_info = f"Status: {proyek_status} | {proyek_mulai} - {proyek_selesai}"
            proyek_description = f"Deskripsi: {proyek_deskripsi}"

            self.tugas_list = database.getTugasWithProyek(self.proyek_id)

            completed_tasks = len([t for t in self.tugas_list if t[3] == "Selesai"])
            in_progress_tasks = len([t for t in self.tugas_list if t[3] == "Sedang Berjalan"])
            total_tasks = len(self.tugas_list)
            progress_value = (completed_tasks * 1 + in_progress_tasks * 0.5) / total_tasks if total_tasks > 0 else 0.0

            progress_percentage = int(progress_value * 100)
            self.progress_text = ft.Text(f"{progress_percentage}%", size=16, weight=ft.FontWeight.BOLD)
            self.progress_bar = ft.ProgressBar(value=progress_value, width=400)
            self.deskripsi_display = ft.Text(proyek_description, size=14)
            self.proyek_info_text = ft.Text(proyek_info, size=14)

            # Total Biaya
            self.total_biaya = sum(t[5] for t in self.tugas_list)
            self.total_biaya_text = ft.Text(f"Total Biaya: Rp. {self.total_biaya:,}", size=16, weight=ft.FontWeight.BOLD)
        else:
            proyek_title = "Proyek Tidak Ditemukan"
            proyek_info = ""
            proyek_description = "Deskripsi: -"
            self.progress_text = ft.Text("0%", size=16, weight=ft.FontWeight.BOLD)
            self.progress_bar = ft.ProgressBar(value=0.0, width=400)
            self.deskripsi_display = ft.Text(proyek_description, size=14)
            self.proyek_info_text = ft.Text("Proyek tidak ditemukan", size=16)
            self.total_biaya = 0
            self.total_biaya_text = ft.Text(f"Total Biaya: Rp. {self.total_biaya:,}", size=16, weight=ft.FontWeight.BOLD)

        self.title = ft.Container(
            content=ft.Text(proyek_title, size=28, weight=ft.FontWeight.BOLD),
            alignment=ft.alignment.center,
            padding=ft.padding.all(20),
        )

        self.proyek_info_text = ft.Text(proyek_info, size=14)
        self.deskripsi_display = ft.Text(proyek_description, size=14)
        self.total_biaya_text = ft.Text(f"Total Biaya: Rp. {self.total_biaya:,}", size=16, weight=ft.FontWeight.BOLD)

        self.add_tugas_button = ft.ElevatedButton(
            text="Tambah Tugas",
            style=ft.ButtonStyle(
                color="white",
                bgcolor="blue",
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
            ),
            on_click=self.open_add_tugas_dialog,
        )

        self.tugas_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nama", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Deskripsi", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Aksi", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(2, "lightgray"),
            border_radius=10,
            horizontal_margin=50,
            column_spacing=200,
            width=2000
        )

        self.prev_button = ft.ElevatedButton(
            text="Sebelum",
            on_click=self.prev_page,
            disabled=True,
            style=ft.ButtonStyle(
                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                text_style=ft.TextStyle(size=14),
            )
        )
        self.next_button = ft.ElevatedButton(
            text="Lanjut",
            on_click=self.next_page,
            disabled=True,
            style=ft.ButtonStyle(
                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                text_style=ft.TextStyle(size=14),
            )
        )
        self.page_label = ft.Text("Page 1 of 1", size=16, weight=ft.FontWeight.NORMAL)

        self.pagination = ft.Row(
            controls=[self.prev_button, self.page_label, self.next_button],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        self.progress_display = ft.Row(
            controls=[
                self.progress_bar,
                self.progress_text
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10
        )

        self.main_column = ft.Column(
            controls=[
                self.title,
                self.proyek_info_text,
                ft.Divider(),
                self.deskripsi_display,
                self.progress_display, 
                self.total_biaya_text,
                ft.Divider(),
                ft.Text("Daftar Tugas", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Row(
                        [
                            self.add_tugas_button,
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    padding=ft.padding.symmetric(horizontal=20),
                ),
                self.tugas_table,
                self.pagination,
            ],
            spacing=20,
        )

        self.load_tugas()

    def toggle_tugas_status(self, tugas_id, current_status):
        new_status = "Selesai" if current_status != "Selesai" else "Sedang Berjalan"
        database.editTugas(tugas_id=tugas_id, tugas_status=new_status)
        show_snackbar(self.page, f"Status tugas berhasil diubah menjadi {new_status}.")
        self.refresh_data()

    def load_tugas(self):
        self.tugas_list = database.getTugasWithProyek(self.proyek_id)
        completed_tasks = len([t for t in self.tugas_list if t[3] == "Selesai"])
        in_progress_tasks = len([t for t in self.tugas_list if t[3] == "Sedang Berjalan"])
        total_tasks = len(self.tugas_list)
        progress_value = (completed_tasks * 1 + in_progress_tasks * 0.5) / total_tasks if total_tasks > 0 else 0.0
        self.progress_bar.value = progress_value
        progress_percentage = int(progress_value * 100)
        self.progress_text.value = f"{progress_percentage}%"

        #Total Biaya
        self.total_biaya = sum(t[5] for t in self.tugas_list) 
        self.total_biaya_text.value = f"Total Biaya: Rp. {self.total_biaya:,}"

        self.total_pages = max(1, (total_tasks + self.items_per_page - 1) // self.items_per_page)

        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        elif self.current_page < 1:
            self.current_page = 1

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        paginated_tugas = self.tugas_list[start_idx:end_idx]

        self.tugas_table.rows.clear()
        if not paginated_tugas:
            self.page_label.value = f"Page {self.current_page} of {self.total_pages}"
            self.prev_button.disabled = self.current_page <= 1
            self.next_button.disabled = self.current_page >= self.total_pages
            self.page.update()
            return

        for tugas in paginated_tugas:
            delete_handler = lambda e, tid=tugas[0]: self.delete_tugas(e, tid)
            edit_handler = lambda e, tdata=tugas: self.open_edit_tugas_dialog(e, tdata)
            view_biaya_handler = lambda e, tdata=tugas: self.view_biaya(e, tdata)
            toggle_status_handler = lambda e, tid=tugas[0], status=tugas[3]: self.toggle_tugas_status(tid, status)

            text_color = (
                "gray" if tugas[3] == "Belum Dimulai" else
                "orange" if tugas[3] == "Sedang Berjalan" else
                "green"
            )

            self.tugas_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(tugas[1], size=16)),
                        ft.DataCell(ft.Text(tugas[3], size=16, color=text_color)),
                        ft.DataCell(ft.Text(tugas[2], size=16, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        text="Edit",
                                        style=ft.ButtonStyle(
                                            color="white",
                                            bgcolor="blue",
                                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                        ),
                                        on_click=edit_handler,
                                    ),
                                    ft.ElevatedButton(
                                        text="Hapus",
                                        style=ft.ButtonStyle(
                                            color="white",
                                            bgcolor="red",
                                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                        ),
                                        on_click=delete_handler,
                                    ),
                                    ft.ElevatedButton(
                                        text="Lihat Biaya",
                                        style=ft.ButtonStyle(
                                            color="white",
                                            bgcolor="purple",
                                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                        ),
                                        on_click=view_biaya_handler,
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DONE if tugas[3] != "Selesai" else ft.icons.CANCEL,
                                        tooltip="Tandai Selesai" if tugas[3] != "Selesai" else "Tandai Belum Selesai",
                                        on_click=toggle_status_handler,
                                    ),
                                ],
                                spacing=10,
                            )
                        ),
                    ]
                )
            )

        self.page_label.value = f"Page {self.current_page} of {self.total_pages}"
        self.prev_button.disabled = self.current_page <= 1
        self.next_button.disabled = self.current_page >= self.total_pages
        self.page.update()

    def view_biaya(self, e, tugas_data):
        biaya_dialog = ViewBiayaDialog(self.page, {
            "estimated": tugas_data[6], 
            "budget": tugas_data[5],     
            "tugas_id": tugas_data[0]
        }, self.refresh_data)
        self.page.dialog = biaya_dialog
        biaya_dialog.open = True
        self.page.update()

    def open_add_tugas_dialog(self, e):
        add_dialog = AddTugasDialog(self.page, self.proyek_id, self.add_tugas_to_database)
        self.page.dialog = add_dialog
        add_dialog.open = True
        self.page.update()

    def open_edit_tugas_dialog(self, e, tugas_data):
        tugas_data_dict = {
            "tugas_id": tugas_data[0],
            "tugas_nama": tugas_data[1],
            "tugas_deskripsi": tugas_data[2],
            "tugas_status": tugas_data[3],
        }
        edit_dialog = EditTugasDialog(self.page, tugas_data_dict, self.refresh_data)
        self.page.dialog = edit_dialog
        edit_dialog.open = True
        self.page.update()

    def add_tugas_to_database(self, nama, status, deskripsi, proyek_id, estimasi, biaya_aktual):
        database.addTugas(
            tugas_nama=nama,
            tugas_status=status,
            proyek_id=proyek_id,
            tugas_deskripsi=deskripsi,
            budget=biaya_aktual,     
            estimated=estimasi       
        )
        show_snackbar(self.page, "Tugas berhasil ditambahkan")
        self.refresh_data()

    def open_delete_tugas_dialog(self, e, tugas_id):
        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Konfirmasi Hapus"),
            content=ft.Text("Apakah Anda yakin ingin menghapus tugas ini?"),
            actions=[
                ft.TextButton("Ya", on_click=lambda e: self.confirm_delete(tugas_id)),
                ft.TextButton("Tidak", on_click=self.close_dialog),
            ],
        )
        self.page.dialog = confirm_dialog
        confirm_dialog.open = True
        self.page.update()

    def confirm_delete(self, tugas_id):
        database.deleteTugas(tugas_id)
        show_snackbar(self.page, "Tugas berhasil dihapus.")
        self.refresh_data()
        self.close_dialog(None)

    def delete_tugas(self, e, tugas_id):
        self.open_delete_tugas_dialog(e, tugas_id)

    def close_dialog(self, e):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.dialog = None
            self.page.update()

    def refresh_data(self):
        self.load_tugas()
        self.page.update()

    def prev_page(self, e):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_tugas()

    def next_page(self, e):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_tugas()

    def build(self):
        return self.main_column

def main(page: ft.Page):
    page.title = "Tugas Manager"
    proyek_id = 1  
    manager = TugasManager(page, proyek_id)
    page.add(manager.build())
    page.update()

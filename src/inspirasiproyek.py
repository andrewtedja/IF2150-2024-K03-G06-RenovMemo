from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QWidget, QDialog, QLabel,
    QTextEdit, QMessageBox, QHeaderView, QFileDialog,QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys
import database  
from detailinspirasiproyek import DetailInspirasiWindow  


class AddInspirasiDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Inspirasi Proyek")
        self.resize(600, 600)  

        layout = QVBoxLayout()

        # Input 
        self.namaInput = QLineEdit()
        self.namaInput.setPlaceholderText("Nama Inspirasi")
        self.deskripsiInput = QTextEdit()  
        self.deskripsiInput.setPlaceholderText("Deskripsi Inspirasi")
        self.deskripsiInput.setFixedHeight(150)  
        gambarLayout = QHBoxLayout()
        self.gambarInput = QLineEdit()
        self.gambarInput.setPlaceholderText("URL/Path Gambar")
        browseButton = QPushButton("Browse")
        browseButton.clicked.connect(self.browseImage)
        gambarLayout.addWidget(self.gambarInput)
        gambarLayout.addWidget(browseButton)
        self.referensiInput = QLineEdit()
        self.referensiInput.setPlaceholderText("Referensi Inspirasi")

        # Layout
        layout.addWidget(QLabel("Nama Inspirasi"))
        layout.addWidget(self.namaInput)
        layout.addWidget(QLabel("Deskripsi Inspirasi"))
        layout.addWidget(self.deskripsiInput)
        layout.addWidget(QLabel("Gambar"))
        layout.addLayout(gambarLayout)
        layout.addWidget(QLabel("Referensi"))
        layout.addWidget(self.referensiInput)

        # Add Button
        addButton = QPushButton("Tambah")
        addButton.setFixedHeight(50)  
        addButton.setStyleSheet("font-size: 18px;") 
        addButton.clicked.connect(self.addInspirasi)
        layout.addWidget(addButton)

        self.setLayout(layout)

    def browseImage(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        if filePath:
            self.gambarInput.setText(filePath)

    def addInspirasi(self):
        nama = self.namaInput.text().strip()
        deskripsi = self.deskripsiInput.toPlainText().strip()  
        gambar = self.gambarInput.text().strip()
        referensi = self.referensiInput.text().strip()

        if nama and deskripsi:
            self.parent().addInspirasiToDatabase(nama, deskripsi, gambar, referensi)
            self.accept()
            print(f"Added Inspirasi: {nama}")
        else:
            QMessageBox.warning(self, "Warning", "Mohon isi semua field")
            print("Failed to add Inspirasi: Missing fields")


class InspirasiProyekManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inspirasi Proyek Manager")
        self.resize(1200, 800) 
        self.database = database
        self.database.initializeDatabase()

        # Pagination 
        self.current_page = 1
        self.items_per_page = 5
        self.total_pages = 1

        # Main 
        mainLayout = QVBoxLayout()

        # Top layout 
        topLayout = QHBoxLayout()
        titleLabel = QLabel("Daftar Inspirasi Proyek")
        titleFont = QFont()
        titleFont.setPointSize(24)  
        titleFont.setBold(True)
        titleLabel.setFont(titleFont)
        topLayout.addWidget(titleLabel, alignment=Qt.AlignLeft)

        # Add Inspirasi Button
        addInspirasiButton = QPushButton("Tambah")
        addInspirasiButton.setFixedSize(250, 60)
        addInspirasiButton.setStyleSheet("font-size: 24px;")  
        addInspirasiButton.clicked.connect(self.openAddInspirasiDialog)
        topLayout.addWidget(addInspirasiButton, alignment=Qt.AlignRight)
        mainLayout.addLayout(topLayout)

        # Table
        self.inspirasiTable = QTableWidget(0, 3)  # kolom: Nama, Deskripsi, Rincian
        self.inspirasiTable.setHorizontalHeaderLabels(
            ["Nama", "Deskripsi", "Rincian"]
        )
        self.inspirasiTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.inspirasiTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.inspirasiTable.setSelectionBehavior(QTableWidget.SelectRows)
        mainLayout.addWidget(self.inspirasiTable)

        # Pagination buttons
        paginationLayout = QHBoxLayout()
        paginationLayout.addStretch()

        self.prevButton = QPushButton("Sebelum")
        self.prevButton.setFixedSize(200, 60)  
        self.prevButton.setStyleSheet("font-size: 24px;")  
        self.prevButton.clicked.connect(self.prevPage)
        paginationLayout.addWidget(self.prevButton)

        self.pageLabel = QLabel("Page 1 of 1")
        pageFont = QFont()
        pageFont.setPointSize(18)  
        self.pageLabel.setFont(pageFont)
        paginationLayout.addWidget(self.pageLabel)

        self.nextButton = QPushButton("Lanjut")
        self.nextButton.setFixedSize(200, 60) 
        self.nextButton.setStyleSheet("font-size: 24px;")  
        self.nextButton.clicked.connect(self.nextPage)
        paginationLayout.addWidget(self.nextButton)

        paginationLayout.addStretch()
        mainLayout.addLayout(paginationLayout)

        # Main Container
        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

        self.loadInspirasi()

    def loadInspirasi(self):
        all_inspirasi = self.database.getAllInspirasi()
        total_items = len(all_inspirasi)
        self.total_pages = (total_items + self.items_per_page - 1) // self.items_per_page or 1

        print(f"Total items: {total_items}, Total pages: {self.total_pages}")

        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        elif self.current_page < 1:
            self.current_page = 1

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        paginated_inspirasi = all_inspirasi[start_idx:end_idx]

        print(f"Loading page {self.current_page}: items {start_idx + 1} to {min(end_idx, total_items)}")

        # Update tabel
        self.inspirasiTable.setRowCount(0) 
        for inspirasi in paginated_inspirasi:
            row_position = self.inspirasiTable.rowCount()
            self.inspirasiTable.insertRow(row_position)

            self.inspirasiTable.setItem(row_position, 0, QTableWidgetItem(inspirasi[1]))  # Nama
            self.inspirasiTable.setItem(row_position, 1, QTableWidgetItem(inspirasi[2]))  # Deskripsi

            # Rincian 
            rincianBtn = QPushButton("Lihat")
            rincianBtn.setFixedSize(120, 50) 
            rincianBtn.setStyleSheet("font-size: 20px;")  
            rincianBtn.clicked.connect(lambda checked, insp_id=inspirasi[0]: self.viewRincian(insp_id))
            self.inspirasiTable.setCellWidget(row_position, 2, rincianBtn)

        self.pageLabel.setText(f"Page {self.current_page} of {self.total_pages}")
        self.prevButton.setEnabled(self.current_page > 1)
        self.nextButton.setEnabled(self.current_page < self.total_pages)

    def openAddInspirasiDialog(self):
        dialog = AddInspirasiDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.loadInspirasi()  

    def addInspirasiToDatabase(self, nama, deskripsi, gambar, referensi):
        self.database.addInspirasi(nama, deskripsi, gambar, referensi)
        self.loadInspirasi()

    def viewRincian(self, inspirasi_id):
        print(f"Attempting to view rincian for inspirasi_id: {inspirasi_id}")
        inspirasi = self.database.getInspirasiById(inspirasi_id)
        if inspirasi:
            inspirasi_data = {
                'inspirasi_id': inspirasi[0],
                'inspirasi_nama': inspirasi[1],
                'inspirasi_deskripsi': inspirasi[2],
                'inspirasi_gambar': inspirasi[3],
                'inspirasi_referensi': inspirasi[4]
            }
            print(f"Inspirasi data retrieved: {inspirasi_data}")
            self.openDetailWindow(inspirasi_data)
        else:
            QMessageBox.warning(self, "Warning", "Inspirasi not found.")
            print("Inspirasi not found.")

    def openDetailWindow(self, inspirasi_data):
        try:
            self.detailWindow = DetailInspirasiWindow(inspirasi_data, self)
            self.detailWindow.show()
            print("Detail window opened successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open detail window: {e}")
            print(f"Error opening detail window: {e}")

    def prevPage(self):
        if self.current_page > 1:
            self.current_page -= 1
            print(f"Navigating to previous page: {self.current_page}")
            self.loadInspirasi()

    def nextPage(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            print(f"Navigating to next page: {self.current_page}")
            self.loadInspirasi()

    def refreshTable(self):
        self.loadInspirasi()

    def closeEvent(self, event):
        self.database.closeDatabase()
        print("Application closed.")
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = InspirasiProyekManager()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

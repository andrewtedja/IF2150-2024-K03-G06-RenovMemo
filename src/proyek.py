from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QWidget, QDialog, QLabel, QLineEdit, QDateEdit, QSpinBox,
    QMessageBox
)
from PyQt5.QtCore import QDate
import sys
import database

STATUS_OPTIONS = ["Belum Dimulai", "Sedang Berjalan", "Selesai"]

class AddProyekDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Proyek")
        self.resize(800, 800)

        layout = QVBoxLayout()

        # Input fields
        self.namaInput = QLineEdit()
        self.namaInput.setPlaceholderText("Nama Proyek")
        self.deskripsiInput = QLineEdit()
        self.deskripsiInput.setPlaceholderText("Deskripsi Proyek")
        self.statusInput = QComboBox()
        self.statusInput.addItems(STATUS_OPTIONS)
        self.tanggalMulaiInput = QDateEdit()
        self.tanggalMulaiInput.setCalendarPopup(True)
        self.tanggalMulaiInput.setDate(QDate.currentDate())
        self.tanggalSelesaiInput = QDateEdit()
        self.tanggalSelesaiInput.setCalendarPopup(True)
        self.tanggalSelesaiInput.setDate(QDate.currentDate())
        self.budgetInput = QSpinBox()
        self.budgetInput.setRange(0, 1_000_000_000)
        self.budgetInput.setPrefix("Rp ")
        self.budgetInput.setSingleStep(10000)

        # Layout
        layout.addWidget(QLabel("Nama Proyek"))
        layout.addWidget(self.namaInput)
        layout.addWidget(QLabel("Deskripsi Proyek"))
        layout.addWidget(self.deskripsiInput)
        layout.addWidget(QLabel("Status"))
        layout.addWidget(self.statusInput)
        layout.addWidget(QLabel("Tanggal Mulai"))
        layout.addWidget(self.tanggalMulaiInput)
        layout.addWidget(QLabel("Tanggal Selesai"))
        layout.addWidget(self.tanggalSelesaiInput)
        layout.addWidget(QLabel("Budget (Rupiah)"))
        layout.addWidget(self.budgetInput)

        addButton = QPushButton("Tambah")
        addButton.clicked.connect(self.addProyek)
        layout.addWidget(addButton)

        self.setLayout(layout)

    def addProyek(self):
        nama = self.namaInput.text().strip()
        deskripsi = self.deskripsiInput.text().strip()
        status = self.statusInput.currentText()
        tanggal_mulai = self.tanggalMulaiInput.date().toString("yyyy-MM-dd")
        tanggal_selesai = self.tanggalSelesaiInput.date().toString("yyyy-MM-dd")
        budget = self.budgetInput.value()

        if nama and deskripsi:
            self.parent().addProyekToDatabase(
                nama, status, deskripsi, tanggal_mulai, tanggal_selesai, budget
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Warning", "Mohon isi semua field")

class ProyekManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proyek Manager")
        self.resize(1000, 1000)
        self.database = database
        self.database.initializeDatabase()

        mainLayout = QVBoxLayout()

        # Filter
        filterLayout = QHBoxLayout()
        filterLabel = QLabel("Filter by Status:")
        self.filterDropdown = QComboBox()
        self.filterDropdown.addItem("All")
        self.filterDropdown.addItems(STATUS_OPTIONS)
        self.filterDropdown.currentTextChanged.connect(self.loadProyek)
        filterLayout.addWidget(filterLabel)
        filterLayout.addWidget(self.filterDropdown)
        mainLayout.addLayout(filterLayout)

        # Table
        self.proyekTable = QTableWidget(0, 7)  # Added one column for delete button
        self.proyekTable.setHorizontalHeaderLabels(
            ["Nama", "Status", "Budget", "Tanggal mulai", "Tanggal selesai", "Rincian", "Action"]
        )
        mainLayout.addWidget(self.proyekTable)

        # Add Project Button
        addProyekButton = QPushButton("Tambah")
        addProyekButton.clicked.connect(self.openAddProyekDialog)
        mainLayout.addWidget(addProyekButton)

        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

        self.loadProyek()

    def loadProyek(self):
        self.proyekTable.setRowCount(0)
        
        filter_status = self.filterDropdown.currentText()
        if filter_status == "All":
            proyek_list = self.database.getAllProyek()
        else:
            proyek_list = self.database.getProyekWithStatus(filter_status)

        for row, proyek in enumerate(proyek_list):
            self.proyekTable.insertRow(row)
            
            # Add project data
            self.proyekTable.setItem(row, 0, QTableWidgetItem(str(proyek[1])))  # Nama
            self.proyekTable.setItem(row, 1, QTableWidgetItem(str(proyek[2])))  # Status
            self.proyekTable.setItem(row, 2, QTableWidgetItem(f"Rp. {proyek[6]}"))  # Budget
            self.proyekTable.setItem(row, 3, QTableWidgetItem(str(proyek[4])))  # Tanggal Mulai
            self.proyekTable.setItem(row, 4, QTableWidgetItem(str(proyek[5])))  # Tanggal Selesai
            self.proyekTable.setItem(row, 5, QTableWidgetItem(str(proyek[3])))  # Rincian

            # Add delete button
            deleteBtn = QPushButton("Delete")
            deleteBtn.clicked.connect(lambda checked, pid=proyek[0]: self.deleteProyek(pid))
            self.proyekTable.setCellWidget(row, 6, deleteBtn)

    def deleteProyek(self, proyek_id):
        reply = QMessageBox.question(self, 'Confirm Delete',
                                   'Are you sure you want to delete this project?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.database.deleteProyek(proyek_id)
            self.loadProyek()

    def openAddProyekDialog(self):
        dialog = AddProyekDialog(self)
        dialog.exec_()

    def addProyekToDatabase(self, nama, status, deskripsi, tanggal_mulai, tanggal_selesai, budget):
        self.database.addProyek(nama, status, deskripsi, tanggal_mulai, tanggal_selesai, budget)
        self.loadProyek()

    def closeEvent(self, event):
        self.database.closeDatabase()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProyekManager()
    window.show()
    sys.exit(app.exec_())

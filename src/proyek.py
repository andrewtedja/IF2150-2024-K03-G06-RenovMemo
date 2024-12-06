from PyQt5.QtWidgets import ( # type: ignore
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QWidget, QDialog, QLabel, QLineEdit, QDateEdit, QSpinBox
)
from PyQt5.QtCore import QDate # type: ignore
import sys
import database  # Replace with your database module


class AddProyekDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Proyek")
        self.resize(800, 800)

        layout = QVBoxLayout()

        # tempat input
        self.namaInput = QLineEdit()
        self.namaInput.setPlaceholderText("Enter Proyek Name")
        self.deskripsiInput = QLineEdit()
        self.deskripsiInput.setPlaceholderText("Enter Proyek Description")
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

        # layout tambah proyek
        layout.addWidget(QLabel("Nama Proyek"))
        layout.addWidget(self.namaInput)
        layout.addWidget(QLabel("Deskripsi Proyek"))
        layout.addWidget(self.deskripsiInput)
        layout.addWidget(QLabel("Tanggal Mulai"))
        layout.addWidget(self.tanggalMulaiInput)
        layout.addWidget(QLabel("Tanggal Selesai"))
        layout.addWidget(self.tanggalSelesaiInput)
        layout.addWidget(QLabel("Budget (Rupiah)"))
        layout.addWidget(self.budgetInput)

        # tombol tambah proyek
        addButton = QPushButton("Tambah")
        addButton.clicked.connect(self.addProyek)
        layout.addWidget(addButton)

        self.setLayout(layout)

    def addProyek(self):
        """Collect data and pass it to the main window."""
        nama = self.namaInput.text().strip()
        deskripsi = self.deskripsiInput.text().strip()
        tanggal_mulai = self.tanggalMulaiInput.date().toString("yyyy-MM-dd")
        tanggal_selesai = self.tanggalSelesaiInput.date().toString("yyyy-MM-dd")
        budget = self.budgetInput.value()
        status = "Belum Dimulai"  # Automatically set

        if nama and deskripsi:
            self.parent().addProyekToDatabase(
                nama, status, deskripsi, tanggal_mulai, tanggal_selesai, budget
            )
            self.accept()
        else:
            print("Please fill all fields.")


class ProyekManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proyek Manager")
        self.resize(1000, 1000)
        self.database = database
        self.database.initializeDatabase()

        mainLayout = QVBoxLayout()

        # Dropdown untuk filter
        filterLayout = QHBoxLayout()
        filterLabel = QLabel("Filter by Status:")
        self.filterDropdown = QComboBox()
        self.filterDropdown.addItems(
            ["All", "Selesai", "Sedang Berjalan", "Belum Dimulai"])
        self.filterDropdown.currentTextChanged.connect(self.loadProyek)
        filterLayout.addWidget(filterLabel)
        filterLayout.addWidget(self.filterDropdown)
        mainLayout.addLayout(filterLayout)

        # Tabel Proyek
        self.proyekTable = QTableWidget(0, 6)
        mainLayout.addWidget(self.proyekTable)

        # Tombol Tambah Proyek
        addProyekButton = QPushButton("Tambah")
        addProyekButton.clicked.connect(self.openAddProyekDialog)
        mainLayout.addWidget(addProyekButton)

        # Main Container
        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

        self.loadProyek()

    def loadProyek(self):
        """Load projects from the database into the table."""
        self.proyekTable.setRowCount(0)
        self.proyekTable.setColumnCount(6)
        self.proyekTable.setHorizontalHeaderLabels(
            ["Nama", "Status", "Budget", "Tanggal mulai", "Tanggal selesai", "Rincian"])

        filter_status = self.filterDropdown.currentText()

        if filter_status == "All":
            proyek_list = self.database.getAllProyek()
        else:
            proyek_list = self.database.getProyekWithStatus(filter_status)

        columns_to_display = [1, 2, 6, 4, 5]
        for row, proyek in enumerate(proyek_list):
            self.proyekTable.insertRow(row)
            for col_idx, col in enumerate(columns_to_display):
                data = proyek[col]
                if col == 6:
                    data = f"Rp. {data}"
                self.proyekTable.setItem(
                    row, col_idx, QTableWidgetItem(str(data)))

    def openAddProyekDialog(self):
        """Open a dialog to add a new project."""
        dialog = AddProyekDialog(self)
        dialog.exec_()

    def addProyekToDatabase(self, nama, status, deskripsi, tanggal_mulai, tanggal_selesai, budget):
        """Add a new project to the database."""
        self.database.addProyek(nama, status, deskripsi,
                                tanggal_mulai, tanggal_selesai, budget)
        self.loadProyek()

    def closeEvent(self, event):
        """Close the database connection on exit."""
        self.database.closeDatabase()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProyekManager()
    window.show()
    sys.exit(app.exec_())
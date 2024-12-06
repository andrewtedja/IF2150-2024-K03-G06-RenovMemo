from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QPushButton, QLabel, QWidget, QMessageBox, QHBoxLayout, QLineEdit, QDialog, QFileDialog, QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QFont
import sys
import database 


class EditInspirasiDialog(QDialog):
    def __init__(self, inspirasi_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Inspirasi Proyek")
        self.resize(600, 600)  
        self.inspirasi_id = inspirasi_data['inspirasi_id']

        layout = QVBoxLayout()

        # Input 
        self.namaInput = QLineEdit(inspirasi_data['inspirasi_nama'])
        self.deskripsiInput = QTextEdit(inspirasi_data['inspirasi_deskripsi']) 
        self.deskripsiInput.setFixedHeight(150)  

        gambarLayout = QHBoxLayout()
        self.gambarInput = QLineEdit()
        self.gambarInput.setPlaceholderText("Select new image or leave blank to keep current")
        browseButton = QPushButton("Browse")
        browseButton.clicked.connect(self.browseImage)
        gambarLayout.addWidget(self.gambarInput)
        gambarLayout.addWidget(browseButton)

        self.referensiInput = QLineEdit(inspirasi_data['inspirasi_referensi'])

        # Layout
        layout.addWidget(QLabel("Nama Inspirasi"))
        layout.addWidget(self.namaInput)
        layout.addWidget(QLabel("Deskripsi Inspirasi"))
        layout.addWidget(self.deskripsiInput)
        layout.addWidget(QLabel("Gambar"))
        layout.addLayout(gambarLayout)
        layout.addWidget(QLabel("Referensi"))
        layout.addWidget(self.referensiInput)

        # Save 
        saveButton = QPushButton("Simpan")
        saveButton.setFixedHeight(50)  
        saveButton.setStyleSheet("font-size: 18px;")  
        saveButton.clicked.connect(self.saveChanges)
        layout.addWidget(saveButton)

        self.setLayout(layout)

    def browseImage(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        if filePath:
            self.gambarInput.setText(filePath)

    def saveChanges(self):
        nama = self.namaInput.text().strip()
        deskripsi = self.deskripsiInput.toPlainText().strip() 
        gambar_path = self.gambarInput.text().strip()
        referensi = self.referensiInput.text().strip()

        if nama and deskripsi:
            if gambar_path:
                try:
                    with open(gambar_path, 'rb') as f:
                        gambar_blob = f.read()
                except Exception as e:
                    QMessageBox.warning(self, "Warning", f"Gagal membaca gambar: {e}")
                    print(f"Failed to read image: {e}")
                    return
            else:
                gambar_blob = None

            try:
                database.editInspirasi(
                    inspirasi_id=self.inspirasi_id,
                    inspirasi_nama=nama,
                    inspirasi_deskripsi=deskripsi,
                    inspirasi_gambar_blob=gambar_blob,
                    inspirasi_referensi=referensi
                )
                self.accept()
                QMessageBox.information(self, "Success", "Inspirasi Proyek berhasil diperbarui.")
                print(f"Inspirasi ID {self.inspirasi_id} updated.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal memperbarui Inspirasi: {e}")
                print(f"Failed to update Inspirasi: {e}")
        else:
            QMessageBox.warning(self, "Warning", "Mohon isi semua field.")
            print("Failed to update Inspirasi: Missing fields.")


class DetailInspirasiWindow(QMainWindow):
    def __init__(self, inspirasi_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Inspirasi Proyek {inspirasi_data['inspirasi_id']}")
        self.resize(1000, 800)  
        self.inspirasi_data = inspirasi_data
        self.parent = parent  

        #layout
        mainLayout = QVBoxLayout()
        headerLayout = QHBoxLayout()

        # Title
        self.titleLabel = QLabel(f"Inspirasi Proyek {self.inspirasi_data['inspirasi_id']}")
        titleFont = QFont()
        titleFont.setPointSize(24)  
        titleFont.setBold(True)
        self.titleLabel.setFont(titleFont)
        headerLayout.addWidget(self.titleLabel, alignment=Qt.AlignLeft)

        # Tombol
        actionLayout = QHBoxLayout()

        # Edit 
        editButton = QPushButton("Ubah Inspirasi")
        editButton.setFixedSize(200, 60)  
        editButton.setStyleSheet("font-size: 20px;")  
        editButton.clicked.connect(self.editInspirasi)
        actionLayout.addWidget(editButton)

        # Delete Tombol
        deleteButton = QPushButton("Hapus Inspirasi")
        deleteButton.setFixedSize(200, 60)  
        deleteButton.setStyleSheet("font-size: 20px;")  
        deleteButton.clicked.connect(self.deleteInspirasi)
        actionLayout.addWidget(deleteButton)

        headerLayout.addLayout(actionLayout)
        mainLayout.addLayout(headerLayout)

        # Description
        self.deskripsiLabel = QLabel(self.inspirasi_data['inspirasi_deskripsi'])
        self.deskripsiLabel.setWordWrap(True)
        self.deskripsiLabel.setFont(QFont("Arial", 16))  
        mainLayout.addWidget(self.deskripsiLabel)

        mainLayout.addSpacing(30)

        # Image
        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        mainLayout.addWidget(self.imageLabel)

        self.loadImage()

        mainLayout.addSpacing(30)

        if self.inspirasi_data['inspirasi_referensi']:
            self.referensiLabel = QLabel(f"Referensi: {self.inspirasi_data['inspirasi_referensi']}")
            self.referensiLabel.setWordWrap(True)
            self.referensiLabel.setFont(QFont("Arial", 16))  
            mainLayout.addWidget(self.referensiLabel)
            print("Reference displayed in detail window.")
        else:
            self.referensiLabel = QLabel("Tidak ada referensi.")
            self.referensiLabel.setAlignment(Qt.AlignLeft)
            self.referensiLabel.setFont(QFont("Arial", 16))  
            mainLayout.addWidget(self.referensiLabel)
            print("No reference provided in detail window.")

        mainLayout.addStretch()

        # Container
        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    def loadImage(self):
        try:
            if self.inspirasi_data['inspirasi_gambar']:
                image_data = self.inspirasi_data['inspirasi_gambar']
                if image_data:
                    image = QImage.fromData(image_data)
                    if not image.isNull():
                        pixmap = QPixmap.fromImage(image)
                        self.imageLabel.setPixmap(pixmap.scaled(500, 500, Qt.KeepAspectRatio))  
                        print("Image loaded successfully in detail window.")
                    else:
                        self.imageLabel.setText("Gambar tidak dapat ditampilkan.")
                        print("Failed to load image: Corrupted image data.")
                else:
                    self.imageLabel.setText("Gambar tidak dapat ditampilkan.")
                    print("Failed to load image: No image data.")
            else:
                self.imageLabel.setText("Tidak ada gambar.")
                print("No image data provided.")
        except Exception as e:
            self.imageLabel.setText("Gambar tidak dapat ditampilkan.")
            print(f"Error loading image: {e}")

    def editInspirasi(self):
        dialog = EditInspirasiDialog(self.inspirasi_data, self)
        if dialog.exec_() == QDialog.Accepted:
            updated_inspirasi = database.getInspirasiById(self.inspirasi_data['inspirasi_id'])
            if updated_inspirasi:
                self.inspirasi_data = {
                    'inspirasi_id': updated_inspirasi[0],
                    'inspirasi_nama': updated_inspirasi[1],
                    'inspirasi_deskripsi': updated_inspirasi[2],
                    'inspirasi_gambar': updated_inspirasi[3],
                    'inspirasi_referensi': updated_inspirasi[4]
                }
                self.refreshUI()
                self.parent.refreshTable()  
                print("Inspirasi Proyek details updated and UI refreshed.")
            else:
                QMessageBox.warning(self, "Warning", "Failed to retrieve updated data.")
                print("Failed to retrieve updated Inspirasi Proyek data.")

    def deleteInspirasi(self):
        reply = QMessageBox.question(
            self, 'Konfirmasi Hapus',
            f"Apakah Anda yakin ingin menghapus Inspirasi Proyek ID {self.inspirasi_data['inspirasi_id']}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                database.deleteInspirasi(self.inspirasi_data['inspirasi_id'])
                QMessageBox.information(self, "Deleted", "Inspirasi Proyek telah dihapus.")
                self.parent.refreshTable() 
                self.close()
                print(f"Inspirasi Proyek ID {self.inspirasi_data['inspirasi_id']} deleted.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menghapus Inspirasi: {e}")
                print(f"Failed to delete Inspirasi Proyek ID {self.inspirasi_id}: {e}")

    def refreshUI(self):
        self.setWindowTitle(f"Inspirasi Proyek {self.inspirasi_data['inspirasi_id']}")
        self.titleLabel.setText(f"Inspirasi Proyek {self.inspirasi_data['inspirasi_id']}")
        self.deskripsiLabel.setText(self.inspirasi_data['inspirasi_deskripsi'])
        self.loadImage()

        if self.inspirasi_data['inspirasi_referensi']:
            self.referensiLabel.setText(f"Referensi: {self.inspirasi_data['inspirasi_referensi']}")
            print("Reference updated in detail window.")
        else:
            self.referensiLabel.setText("Tidak ada referensi.")
            print("No reference provided for update.")

    def closeEvent(self, event):
        print("Closing DetailInspirasiWindow")
        if self.parent:
            self.parent.show()
        event.accept()

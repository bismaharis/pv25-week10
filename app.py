import sys
import sqlite3
import csv
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidgetItem,
    QMessageBox, QFileDialog
)

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("manajemenBuku.ui", self)
        self.setWindowTitle("Manajemen Buku")

        # Menampilkan Nama dan NIM
        self.labelNama.setText("Nama: Lalu Bisma Kurniawan Haris NIM: F1D022055")

        self.initDB()
        self.loadData()

        # Event
        self.btnSimpan.clicked.connect(self.simpanData)
        self.btnHapus.clicked.connect(self.hapusData)
        self.lineCari.textChanged.connect(self.cariData)
        self.tableWidget.itemDoubleClicked.connect(self.editData)

        # Menu
        self.actionSimpan.triggered.connect(self.simpanData)
        self.actionExport_CSV.triggered.connect(self.eksporCSV)  # Fixed action name
        self.actionKeluar.triggered.connect(self.close)
        self.actionHapus_Data.triggered.connect(self.hapusData)

    def initDB(self):
        self.conn = sqlite3.connect("database.db")
        self.c = self.conn.cursor()
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS buku (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT,
                pengarang TEXT,
                tahun INTEGER
            )
        """)
        self.conn.commit()

    def loadData(self):
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Judul", "Pengarang", "Tahun"])
        for row_index, row_data in enumerate(self.c.execute("SELECT * FROM buku")):
            self.tableWidget.insertRow(row_index)
            for col_index, col_data in enumerate(row_data):
                self.tableWidget.setItem(row_index, col_index, QTableWidgetItem(str(col_data)))

    def simpanData(self):
        judul = self.inputJudul.text()
        pengarang = self.inputPengarang.text()
        tahun = self.inputTahun.text()

        if not (judul and pengarang and tahun.isdigit()):
            QMessageBox.warning(self, "Error", "Harap isi semua field dengan benar.")
            return

        self.c.execute("INSERT INTO buku (judul, pengarang, tahun) VALUES (?, ?, ?)",
                       (judul, pengarang, int(tahun)))
        self.conn.commit()
        self.inputJudul.clear()
        self.inputPengarang.clear()
        self.inputTahun.clear()
        self.loadData()

    def hapusData(self):
        selected = self.tableWidget.currentRow()
        if selected < 0:
            return

        id_item = self.tableWidget.item(selected, 0).text()
        self.c.execute("DELETE FROM buku WHERE id = ?", (id_item,))
        self.conn.commit()
        self.loadData()

    def editData(self, item):
        row = item.row()
        id_data = self.tableWidget.item(row, 0).text()
        judul = self.tableWidget.item(row, 1).text()
        pengarang = self.tableWidget.item(row, 2).text()
        tahun = self.tableWidget.item(row, 3).text()

        self.inputJudul.setText(judul)
        self.inputPengarang.setText(pengarang)
        self.inputTahun.setText(tahun)

        self.c.execute("DELETE FROM buku WHERE id = ?", (id_data,))
        self.conn.commit()
        self.loadData()

    def cariData(self, text):
        for i in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(i, 1)  # Kolom Judul
            self.tableWidget.setRowHidden(i, text.lower() not in item.text().lower())

    def eksporCSV(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Simpan CSV", "", "CSV Files (*.csv)")
        if filename:
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                header = ["ID", "Judul", "Pengarang", "Tahun"]
                writer.writerow(header)

                for row in range(self.tableWidget.rowCount()):
                    rowdata = []
                    for col in range(self.tableWidget.columnCount()):
                        item = self.tableWidget.item(row, col)
                        rowdata.append(item.text() if item else "")
                    writer.writerow(rowdata)
            QMessageBox.information(self, "Sukses", "Data berhasil diekspor.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
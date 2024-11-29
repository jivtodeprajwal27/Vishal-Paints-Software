from PyQt5.QtWidgets import QDialog, QMessageBox, QVBoxLayout, QPushButton, QFileDialog, QLabel
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import sqlite3

class InvoicePopup(QDialog):
    def __init__(self, product_details):
        super().__init__()
        self.product_details = product_details
        self.invoice_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Invoice")
        layout = QVBoxLayout()

        # Add product details
        details_label = QLabel("Invoice Details:\n" + "\n".join([f"{k}: {v}" for k, v in self.product_details.items()]))
        layout.addWidget(details_label)

        # Add buttons
        set_path_button = QPushButton("Set Download Path")
        set_path_button.clicked.connect(self.set_download_path)
        layout.addWidget(set_path_button)

        download_button = QPushButton("Download Invoice")
        download_button.clicked.connect(self.download_invoice)
        layout.addWidget(download_button)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def set_download_path(self):
        """Opens a file dialog to set the download path for the invoice."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Set Invoice Download Path",
            "",
            "PDF Files (*.pdf);;All Files (*)",
            options=options
        )
        if file_path:
            self.invoice_path = file_path
            QMessageBox.information(self, "Path Set", f"Invoice will be saved at:\n{self.invoice_path}")

    def download_invoice(self):
        """Downloads the invoice to the set path."""
        if not self.invoice_path:
            QMessageBox.warning(self, "No Path Set", "Please set the download path first.")
            return

        try:
            self.generate_invoice_pdf(self.invoice_path)
            QMessageBox.information(self, "Success", f"Invoice successfully saved at:\n{self.invoice_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save invoice: {str(e)}")

    def generate_invoice_pdf(self, file_path):
        """Generates a PDF invoice and saves it to the specified path."""
        c = canvas.Canvas(file_path, pagesize=letter)
        c.drawString(100, 750, "Invoice")
        y = 700
        for key, value in self.product_details.items():
            c.drawString(100, y, f"{key}: {value}")
            y -= 20
        c.save()

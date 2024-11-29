from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton,
    QWidget, QFileDialog, QMessageBox, QHBoxLayout
)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class ProductHistoryScreen(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Product History")
        layout = QVBoxLayout()

        # Table for product history
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Product ID", "Product Name", "Description",
            "Yield", "Total Rate", "Date Created"
        ])
        layout.addWidget(self.table)

        # Fetch and display product history
        self.load_product_history()

        # Buttons layout
        buttons_layout = QHBoxLayout()

        # Download Invoice button
        download_invoice_button = QPushButton("Download Invoice")
        download_invoice_button.clicked.connect(self.download_invoice)
        buttons_layout.addWidget(download_invoice_button)

        # Back button
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.close)
        buttons_layout.addWidget(back_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def load_product_history(self):
        """
        Loads product history from the database and displays it in the table.
        """
        cursor = self.db_connection.cursor()
        cursor.execute("""
            SELECT id, product_name, description, yield_value, total_rate, date_created
            FROM product_details
            ORDER BY date_created DESC
        """)
        rows = cursor.fetchall()

        # Populate table
        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_data in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def download_invoice(self):
        """
        Downloads an invoice for the selected product.
        """
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a product to download the invoice.")
            return

        # Get selected product details
        row = selected_items[0].row()
        product_id = self.table.item(row, 0).text()
        product_name = self.table.item(row, 1).text()
        description = self.table.item(row, 2).text()
        yield_value = self.table.item(row, 3).text()
        total_rate = self.table.item(row, 4).text()
        date_created = self.table.item(row, 5).text()

        # Fetch materials for the selected product
        cursor = self.db_connection.cursor()
        cursor.execute("""
            SELECT material_name, material_quantity
            FROM product_materials
            WHERE product_id = ?
        """, (product_id,))
        materials = cursor.fetchall()

        # Open a file dialog to choose save location
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Invoice", f"{product_name}_invoice.pdf", "PDF Files (*.pdf);;All Files (*)", options=options
        )

        if not file_path:
            return  # User canceled the save dialog

        # Generate the PDF invoice
        try:
            self.generate_invoice_pdf(
                file_path, product_id, product_name, description, yield_value, total_rate, date_created, materials
            )
            QMessageBox.information(self, "Success", f"Invoice saved at: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save invoice: {str(e)}")

    def generate_invoice_pdf(self, file_path, product_id, product_name, description, yield_value, total_rate, date_created, materials):
        """
        Generates a PDF invoice and saves it to the specified path.
        """
        c = canvas.Canvas(file_path, pagesize=letter)
        c.drawString(100, 750, "Product Invoice")
        c.drawString(100, 720, f"Product ID: {product_id}")
        c.drawString(100, 700, f"Product Name: {product_name}")
        c.drawString(100, 680, f"Description: {description}")
        c.drawString(100, 660, f"Yield: {yield_value}")
        c.drawString(100, 640, f"Total Rate: {total_rate}")
        c.drawString(100, 620, f"Date Created: {date_created}")

        # Add materials
        c.drawString(100, 600, "Materials Used:")
        y_position = 580
        for material_name, material_quantity in materials:
            c.drawString(120, y_position, f"- {material_name}: {material_quantity}")
            y_position -= 20

        c.drawString(100, y_position - 20, "Thank you for your business!")
        c.save()

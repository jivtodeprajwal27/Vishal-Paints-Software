from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton,
    QWidget, QFileDialog, QMessageBox, QHBoxLayout
)


class ProductHistoryScreen(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Product History")
        layout = QVBoxLayout()
        self.setStyleSheet("background-color: #f4f6f9;")  # Light background color for the window

        # Table for product history
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(6)
        self.product_table.setHorizontalHeaderLabels([
            "Product ID", "Product Name", "Description",
            "Yield", "Total Rate", "Date Created"
        ])
        self.product_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ccc;
                background-color: #ffffff;
                font-size: 14px;
                color: #333;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #3a5a40;
                color: white;
                font-weight: bold;
                padding: 5px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #0066cc;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: #e6f7ff;
            }
        """)

        layout.addWidget(self.product_table)

        # Fetch and display product history
        self.load_product_history()

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        buttons_layout.setContentsMargins(0, 10, 0, 20)

        # Download Invoice button
        download_invoice_button = QPushButton("Download Invoice")
        download_invoice_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        download_invoice_button.clicked.connect(self.download_invoice)
        buttons_layout.addWidget(download_invoice_button)

        # Back button
        back_button = QPushButton("Back")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
        """)
        back_button.clicked.connect(self.close)
        buttons_layout.addWidget(back_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def load_product_history(self):
        """
        Loads product history from the database and displays it in the product history table.
        """
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT id, product_name, description, yield_value, total_rate, date_created
                FROM product_details
                ORDER BY date_created DESC
            """)
            rows = cursor.fetchall()

            # Populate product table
            self.product_table.setRowCount(len(rows))
            for row_idx, row_data in enumerate(rows):
                for col_idx, col_data in enumerate(row_data):
                    self.product_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load product history: {str(e)}")

    def download_invoice(self):
        """
        Downloads an invoice for the selected product from the product history table.
        """
        try:
            selected_items = self.product_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "No Selection", "Please select a product to download the invoice.")
                return

            # Get selected product name (instead of product_id)
            row = selected_items[0].row()
            product_name = self.product_table.item(row, 1).text()  # product_name is in the second column

            # Fetch the invoice BLOB for the selected product using product_name
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT invoice_pdf
                FROM invoices
                WHERE product_name = ?
            """, (product_name,))
            invoice_data = cursor.fetchone()

            if not invoice_data or invoice_data[0] is None:
                QMessageBox.warning(self, "No Invoice", "No invoice available for this product.")
                return

            # Get the invoice BLOB data
            invoice_blob = invoice_data[0]

            # Open a file dialog to choose save location
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Invoice", f"Invoice_{product_name}.pdf", "PDF Files (*.pdf);;All Files (*)", options=options
            )

            if not file_path:
                return  # User canceled the save dialog

            # Save the BLOB data to the chosen file
            with open(file_path, 'wb') as file:
                file.write(invoice_blob)

            QMessageBox.information(self, "Success", f"Invoice saved at: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download invoice: {str(e)}")
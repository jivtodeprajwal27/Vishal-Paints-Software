from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout, QGroupBox, QLineEdit, QPushButton, \
    QTableWidget, QTableWidgetItem, QLabel, QComboBox, QFileDialog, QHBoxLayout, QMenuBar, QMenu, QAction, QMessageBox
from PyQt5.QtWidgets import (
      QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy
     )
import sys
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import sqlite3
from PyQt5.QtWidgets import QDialog,QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel,QDoubleValidator
from PyQt5.QtWidgets import QAbstractItemView
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Table, TableStyle
from io import BytesIO
from datetime import datetime
from datetime import date
import os
from ProductHistoryScreen import ProductHistoryScreen

class ProductRateCalculatorApp(QWidget):  # Change to QMainWindow
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.initUI()

    def create_raw_material_history_table(self):
        """Create the raw_material_history table if it does not exist"""
        cursor = self.db_connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_material_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_material_id INTEGER NOT NULL,
            change_type TEXT NOT NULL,  -- e.g., 'added', 'updated', 'deleted'
            old_price REAL,
            new_price REAL,
            change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (raw_material_id) REFERENCES raw_materials (id)
        )
        ''')
        self.db_connection.commit()

    def initUI(self):
        self.setWindowTitle("Product Rate Calculator")
        self.setGeometry(100, 100, 600, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f4f4f9; /* Light pastel background for a clean look */
            }
            QGroupBox {
                font-size: 18px; /* Larger font size */
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif; /* Stylish font */
                color: #2c3e50; /* Deep gray for better visibility */
                border: 2px solid #bdc3c7; /* Subtle border */
                border-radius: 8px; /* Rounded edges */
                margin-top: 15px; /* Spacing above groups */
                padding: 10px; /* Internal padding for better readability */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 8px;
                font-size: 20px; /* Even larger font for titles */
                color: #34495e; /* Distinct title color */
            }
            QLabel {
                font-size: 16px; /* Slightly larger labels */
                font-family: 'Roboto', Arial, sans-serif; /* Modern font */
                color: #34495e; /* Distinct label color */
            }
            QLineEdit {
                border: 2px solid #95a5a6; /* Thicker border */
                border-radius: 5px; /* Rounded input boxes */
                padding: 10px;
                font-size: 16px; /* Larger text */
                font-family: 'Arial', sans-serif;
                background-color: #ffffff; /* White background */
                color: #2c3e50; /* Dark gray text */
            }
            QComboBox {
                border: 2px solid #95a5a6;
                border-radius: 5px;
                padding: 8px 10px;
                font-size: 16px;
                font-family: 'Arial', sans-serif;
                background-color: #ecf0f1; /* Light gray background */
                color: #2c3e50;
            }
            QPushButton {
                font-size: 16px; /* Larger button text */
                padding: 12px 20px; /* Larger buttons */
                background-color: #3498db; /* Blue for primary buttons */
                color: white; /* White text */
                border: none; /* No border for cleaner look */
                border-radius: 8px; /* Rounded buttons */
                font-family: 'Verdana', sans-serif;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9; /* Darker blue on hover */
            }
            QPushButton:pressed {
                background-color: #1c598a; /* Even darker on click */
            }
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                background-color: #ffffff;
                font-size: 14px;
                font-family: 'Arial', sans-serif;
                color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #34495e; /* Dark gray headers */
                color: white; /* White text for headers */
                font-weight: bold;
                font-size: 16px; /* Larger header font */
                border: none;
                padding: 8px;
            }
        """)

        
        layout = QVBoxLayout(self)

        # Product Details Form
        self.product_form = QFormLayout()
        self.product_form_group = QGroupBox("Product Details")
        layout.addWidget(self.product_form_group)

        self.operator_name = QLineEdit()
        self.product_form.addRow("Operator Name:", self.operator_name)
        self.product_name = QLineEdit()
        self.description = QLineEdit()
        self.yield_value = QLineEdit()
        self.viscosity = QLineEdit()
        self.weight_lit = QLineEdit()
        self.container_cost = QLineEdit()
        self.transport_cost = QLineEdit()
        self.sales_cost = QLineEdit()
        self.misc_cost = QLineEdit()
        self.total_rate = QLineEdit()
        self.total_rate.setReadOnly(True)

        self.product_form.addRow("Product Name:", self.product_name)
        self.product_form.addRow("Description:", self.description)
        self.product_form.addRow("Yield:", self.yield_value)
        self.product_form.addRow("Viscosity:", self.viscosity)
        self.product_form.addRow("Weight / Lit:", self.weight_lit)
        self.product_form.addRow("Container Cost:", self.container_cost)
        self.product_form.addRow("Transport Cost:", self.transport_cost)
        self.product_form.addRow("Sales Cost:", self.sales_cost)
        self.product_form.addRow("Miscellaneous Cost:", self.misc_cost)
        self.product_form.addRow("Total Rate:", self.total_rate)

        self.product_form_group.setLayout(self.product_form)

        # Dropdown for material type and name
        self.material_type_dropdown = QComboBox()
        self.material_type_label = QLabel("Select Material Type")
        self.material_type_dropdown.addItems(["Pigment", "Additive", "Resin", "Thinner"])
        self.material_type_dropdown.currentIndexChanged.connect(self.update_material_name_dropdown)

        self.material_name_dropdown = QComboBox()  # Material Name dropdown (empty at first)
        self.quantity_input = QLineEdit()  # Quantity input field
        self.rate_input = QLineEdit()  # Rate input field (auto-populated)

        # Button to Add Material to Table
        self.add_material_button = QPushButton("Add Material")
        self.add_material_button.clicked.connect(self.add_material_to_table)

        # Layout for adding material inputs and button
        material_input_layout = QHBoxLayout()
        material_input_layout.addWidget(self.material_type_dropdown)
        material_input_layout.addWidget(self.material_name_dropdown)
        material_input_layout.addWidget(self.quantity_input)
        material_input_layout.addWidget(self.rate_input)
        material_input_layout.addWidget(self.add_material_button)

        layout.addLayout(material_input_layout)

        # Add Materials Table
        self.material_table = QTableWidget(0, 4)
        self.material_table.setHorizontalHeaderLabels(
            ["Material Type", "Material Name", "Quantity", "Rate"]
        )
        layout.addWidget(QLabel("Materials:"))
        layout.addWidget(self.material_table)

        # Calculate Product Rate Button
        self.calculate_button = QPushButton("Calculate Product Rate")
        self.calculate_button.clicked.connect(self.calculate_product_rate)
        layout.addWidget(self.calculate_button)

        # Generate Invoice Button
        self.invoice_button = QPushButton("Generate Invoice")
        self.invoice_button.clicked.connect(self.generate_invoice)
        layout.addWidget(self.invoice_button)

        # Clear Form Button
        self.clear_button = QPushButton("Clear Form")
        self.clear_button.clicked.connect(self.clear_form)
        layout.addWidget(self.clear_button)

    
    def clear_form(self):
        """
        Clears all input fields in the form.
        """
        self.product_name.clear()
        self.description.clear()
        self.yield_value.clear()
        self.viscosity.clear()
        self.weight_lit.clear()
        self.container_cost.clear()
        self.transport_cost.clear()
        self.sales_cost.clear()
        self.misc_cost.clear()
        self.total_rate.clear()
        self.material_table.setRowCount(0)

    def generate_invoice(self):
        """Generate and save an invoice as a PDF."""
        # Step 1: Set download path
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Set Invoice Download Path",
            "",
            "PDF Files (*.pdf);;All Files (*)",
            options=options
        )
         

        if not file_path:
            QMessageBox.warning(self, "No Path Set", "No file path selected. Invoice generation aborted.")
            return
        if not file_path.lower().endswith('.pdf'):
            file_path += ".pdf"
        try:
            # Step 2: Generate the invoice PDF
            self.download_invoice(file_path)
            # Step 3: Read the PDF file as binary (BLOB)
            with open(file_path, 'rb') as pdf_file:
                pdf_data = pdf_file.read()
            
            # Step 4: Insert invoice data into the database
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO invoices (product_name, invoice_pdf)
                VALUES (?, ?)
            ''', (self.product_name.text(), pdf_data))
            self.db_connection.commit()
            QMessageBox.information(self, "Success", f"Invoice successfully saved at:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate invoice: {str(e)}")

    def download_invoice(self, file_path):
        """Generate and save the invoice as a PDF with a structured table."""
        operator_name = self.operator_name
        product_name = self.product_name.text()
        total_rate = self.total_rate.text()

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, "Vishal Paints, Inc")
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 70, f"Operator: {operator_name}")  # Add operator name
        p.drawString(50, height - 90, f"Date: {datetime.now().strftime('%Y-%m-%d')}")

        if not product_name or not total_rate:
            QMessageBox.warning(self, "Error", "Please fill in product details and calculate the rate first!")
            return

        yield_amount = float(self.yield_value.text() or 0)
        viscosity = self.viscosity.text()
        weight_lit = float(self.weight_lit.text() or 0)
        container_cost = float(self.container_cost.text() or 0)
        transport_cost = float(self.transport_cost.text() or 0)
        sales_cost = float(self.sales_cost.text() or 0)
        misc_cost = float(self.misc_cost.text() or 0)

        # desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        # file_name = f"{product_name}_invoice.pdf"
        # file_path = os.path.join(desktop_path, file_name)

        additive_cost, resin_cost, pigment_cost, thinner_cost = 0, 0, 0, 0
        invoice_items = []
        total_quantity = 0

        for row in range(self.material_table.rowCount()):
            material_type = self.material_table.item(row, 0).text().lower()
            material_name = self.material_table.item(row, 1).text()
            quantity = float(self.material_table.item(row, 2).text() or 0)
            rate_per_unit = float(self.material_table.item(row, 3).text() or 0)
            total_cost = quantity * rate_per_unit

            invoice_items.append((material_name, quantity, rate_per_unit, total_cost))
            total_quantity += quantity

            if material_type == 'additive':
                additive_cost += total_cost
            elif material_type == 'resin':
                resin_cost += total_cost
            elif material_type == 'pigment':
                pigment_cost += total_cost
            elif material_type == 'thinner':
                thinner_cost += total_cost

        rate_per_kg = float(total_rate) / total_quantity if total_quantity > 0 else 0
        rate_per_lit = float(total_rate) / yield_amount if yield_amount > 0 else 0
        cost_per_lit = rate_per_lit + container_cost + transport_cost + sales_cost + misc_cost

        additive_cost_per_lit = additive_cost / yield_amount if yield_amount > 0 else 0
        resin_cost_per_lit = resin_cost / yield_amount if yield_amount > 0 else 0
        pigment_cost_per_lit = pigment_cost / yield_amount if yield_amount > 0 else 0
        thinner_cost_per_lit = thinner_cost / yield_amount if yield_amount > 0 else 0

        pdf_canvas = canvas.Canvas(file_path, pagesize=A4)
        pdf_canvas.setTitle(f"Invoice - {product_name}")
        width, height = A4

        pdf_canvas.setFont("Helvetica-Bold", 16)
        pdf_canvas.drawString(50, height - 50, f"Vishal Paints, Inc - Invoice for {product_name}")

        pdf_canvas.setFont("Helvetica", 12)
        pdf_canvas.drawString(50, height - 90, f"Yield: {yield_amount}")
        pdf_canvas.drawString(50, height - 110, f"Viscosity: {viscosity}")
        pdf_canvas.drawString(50, height - 130, f"Weight/Lit: {weight_lit}")
        pdf_canvas.drawString(50, height - 150, f"Container Cost: Rs {container_cost}")
        pdf_canvas.drawString(50, height - 170, f"Transport Cost: Rs {transport_cost}")
        pdf_canvas.drawString(50, height - 190, f"Sales Cost: Rs {sales_cost}")
        pdf_canvas.drawString(50, height - 210, f"Misc. Cost: Rs {misc_cost}")

        pdf_canvas.drawString(50, height - 230, f"Total Quantity: {total_quantity}")
        pdf_canvas.drawString(50, height - 250, f"Total Rate: Rs {total_rate}")

        # Generate structured table for materials
        table_data = [["Material Name", "Quantity", "Rate/Unit (Rs)", "Total Cost (Rs)"]]
        for item in invoice_items:
            table_data.append([item[0], f"{item[1]:.2f}", f"{item[2]:.2f}", f"{item[3]:.2f}"])

        table = Table(table_data, colWidths=[7 * cm, 3 * cm, 5 * cm, 5 * cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        # Draw the table
        table.wrapOn(pdf_canvas, width - 100, height)
        table.drawOn(pdf_canvas, 50, height - 400)

        # Add summary
        y_position = height - 450
        pdf_canvas.setFont("Helvetica-Bold", 14)
        pdf_canvas.drawString(50, y_position, "Summary:")
        y_position -= 20

        pdf_canvas.setFont("Helvetica", 12)
        pdf_canvas.drawString(50, y_position, f"Additive Cost/Lit: Rs {additive_cost_per_lit:.2f}")
        y_position -= 20
        pdf_canvas.drawString(50, y_position, f"Resin Cost/Lit: Rs {resin_cost_per_lit:.2f}")
        y_position -= 20
        pdf_canvas.drawString(50, y_position, f"Pigment Cost/Lit: Rs {pigment_cost_per_lit:.2f}")
        y_position -= 20
        pdf_canvas.drawString(50, y_position, f"Thinner Cost/Lit: Rs {thinner_cost_per_lit:.2f}")
        y_position -= 20
        pdf_canvas.drawString(50, y_position, f"Rate/Kg: Rs {rate_per_kg:.2f}")
        y_position -= 20
        pdf_canvas.drawString(50, y_position, f"Rate/Lit: Rs {rate_per_lit:.2f}")
        y_position -= 20
        pdf_canvas.drawString(50, y_position, f"Cost/Lit: Rs {cost_per_lit:.2f}")

        pdf_canvas.save()

    def update_material_type_dropdown(self):
        """Populate the Material Type dropdown with available material types."""
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT DISTINCT mat_type FROM raw_materials")
        material_types = cursor.fetchall()

        self.material_type_dropdown.clear()

        # Add placeholder item
        self.material_type_dropdown.addItem("Select Material Type")
        for material_type in material_types:
            self.material_type_dropdown.addItem(material_type[0])

        # Connect to material name update function
        self.material_type_dropdown.currentIndexChanged.connect(self.update_material_name_dropdown)

    def update_material_name_dropdown(self):
        """Update the Material Name dropdown based on the selected material type."""
        selected_material_type = self.material_type_dropdown.currentText()

        # Skip if the placeholder is selected
        if selected_material_type == "Select Material Type":
            self.material_name_dropdown.clear()
            self.material_name_dropdown.addItem("Select Material")
            return

        cursor = self.db_connection.cursor()
        cursor.execute("""
            SELECT DISTINCT name FROM raw_materials WHERE mat_type = ?
        """, (selected_material_type,))
        material_names = cursor.fetchall()

        self.material_name_dropdown.clear()

        # Add placeholder item
        self.material_name_dropdown.addItem("Select Material")
        for material_name in material_names:
            self.material_name_dropdown.addItem(material_name[0])

        # Connect to rate update function
        self.material_name_dropdown.currentIndexChanged.connect(self.update_rate)

    def update_rate(self):
        """Fetch the rate from the database based on the selected material name"""
        selected_material_name = self.material_name_dropdown.currentText()
        if selected_material_name != "Select Material":
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT price FROM raw_materials WHERE name = ?
            """, (selected_material_name,))
            result = cursor.fetchone()
            if result:
                self.rate_input.setText(str(result[0]))

    def add_material_to_table(self):
        """Add material to the table and save to the database"""
        material_type = self.material_type_dropdown.currentText()
        material_name = self.material_name_dropdown.currentText()
        quantity = self.quantity_input.text()
        rate = self.rate_input.text()

       
        row_position = self.material_table.rowCount()
        self.material_table.insertRow(row_position)
        self.material_table.setItem(row_position, 0, QTableWidgetItem(material_type))
        self.material_table.setItem(row_position, 1, QTableWidgetItem(material_name))
        self.material_table.setItem(row_position, 2, QTableWidgetItem(quantity))
        self.material_table.setItem(row_position, 3, QTableWidgetItem(rate))

    def calculate_product_rate(self):
        """Calculate, display, and commit the total product rate to the database."""
        try:
            # Calculate total material cost from the table
            total_material_cost = 0
            for row in range(self.material_table.rowCount()):
                quantity = float(self.material_table.item(row, 2).text())
                rate = float(self.material_table.item(row, 3).text())
                total_material_cost += quantity * rate

            # Collect additional product costs
            container_cost = float(self.container_cost.text() or 0)
            transport_cost = float(self.transport_cost.text() or 0)
            sales_cost = float(self.sales_cost.text() or 0)
            misc_cost = float(self.misc_cost.text() or 0)

            # Calculate total rate
            total_cost = total_material_cost + container_cost + transport_cost + sales_cost + misc_cost
            self.total_rate_value = total_cost  # Store the total rate for later use

            # Display the total rate in a field
            self.total_rate.setText(f"{total_cost:.2f}")  # Update UI field

            # Gather product details
            product_name = self.product_name.text()
            description = self.description.text()
            yield_value = float(self.yield_value.text() or 0)
            viscosity = float(self.viscosity.text() or 0)
            weight_lit = float(self.weight_lit.text() or 0)
            date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Commit product details and calculated rate to the database
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO product_details (
                    product_name, yield_value, viscosity, weight_lit, container_cost,
                    transport_cost, sales_cost, misc_cost, total_rate, description, date_created
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_name, yield_value, viscosity, weight_lit, container_cost,
                transport_cost, sales_cost, misc_cost, total_cost, description, date_created
            ))
            self.db_connection.commit()

            # Show confirmation message
            QMessageBox.information(self, "Success", "Product rate calculated and saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while calculating the product rate:\n{str(e)}")

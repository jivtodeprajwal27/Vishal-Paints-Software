from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout, QGroupBox, QLineEdit, QPushButton, \
    QTableWidget, QTableWidgetItem, QLabel, QComboBox, QFileDialog, QHBoxLayout, QMenuBar, QMenu, QAction, QMessageBox
from PyQt5.QtWidgets import (
      QWidget, QVBoxLayout, QLabel,QInputDialog, QGridLayout,QFileDialog, QHBoxLayout, QScrollArea, QPushButton, QSpacerItem, QSizePolicy
     )
from PyQt5.QtGui import QPixmap, QColor,QFont
from PyQt5.QtCore import Qt
import sqlite3
from reportlab.platypus import Table, TableStyle
from PyQt5.QtWidgets import QDialog,QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel,QDoubleValidator
from PyQt5.QtWidgets import QAbstractItemView
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from ProductHistoryScreen import ProductHistoryScreen
from product_rate_calculator import ProductRateCalculatorApp 
from reportlab.pdfgen import canvas
from datetime import datetime
from PyQt5.QtCore import QDateTime


import os
class HomeScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.db_connection = self.create_db_connection()
        self.create_raw_materials_table()
        self.create_product_details_table()
        self.create_invoices_table()
        self.create_raw_material_history_table()
        self.stacked_widget = QStackedWidget()  # Add a QStackedWidget for navigation
        self.product_rate_calculator_widget = ProductRateCalculatorApp(self.db_connection)
        self.stacked_widget.addWidget(self.product_rate_calculator_widget)

    def create_db_connection(self):
        """Create a connection to SQLite database"""
        conn = sqlite3.connect("product_rate.db")
        return conn
  
    def create_invoices_table(self):
        """Create the invoices table to store PDFs."""
        cursor = self.db_connection.cursor()
        # cursor.execute('''DROP TABLE IF EXISTS invoices''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                invoice_pdf BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.db_connection.commit()

    def create_raw_materials_table(self):
        """Create the raw_materials table if it doesn't exist and insert initial data only once"""
        cursor = self.db_connection.cursor()
        
        # cursor.execute("DROP TABLE IF EXISTS raw_materials")
        # self.db_connection.commit()
        # print("The raw_materials table has been deleted.")

        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw_materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                mat_type TEXT NOT NULL
            )
        """)
        
        # Check if the table already has data
        cursor.execute("SELECT COUNT(*) FROM raw_materials")
        if cursor.fetchone()[0] == 0:  # Only insert data if table is empty
            cursor.execute("""
                INSERT INTO raw_materials (name, price, mat_type) VALUES
                ('P1', 227.00, 'Pigment'),
                ('P11', 109.00, 'Pigment'),
                ('P6', 170.00, 'Pigment'),
                ('P3', 560.00, 'Pigment'),
                ('P4', 158.00, 'Pigment'),
                ('P5', 109.00, 'Pigment'),
                ('P60', 59.00, 'Pigment'),
                ('P7', 115.00, 'Pigment'),
                ('P100', 35.00, 'Pigment'),
                ('P50', 125.00, 'Pigment'),
                ('P70', 130.00, 'Pigment'),
                ('Redoxide Powder', 15.00, 'Pigment'),
                ('White Whiting', 25.00, 'Pigment'),
                ('Talc', 104.00, 'Pigment'),
                ('A1', 162.00, 'Additive'),
                ('A2', 150.00, 'Additive'),
                ('HCO', 150.00, 'Additive'),
                ('ACE', 600.00, 'Additive'),
                ('PINCOIL', 150.00, 'Additive'),
                ('BRIGHT', 600.00, 'Additive'),
                ('CATALYST MATT', 225.00, 'Additive'),
                ('ICLAY', 308.00, 'Additive'),
                ('ICLAY JELLY 10%', 250.00, 'Additive'),
                ('LEAK 10%', 108.00, 'Additive'),
                ('OMEGA', 55.00, 'Additive'),
                ('DH', 134.00, 'Additive'),
                ('M1 50%', 125.00, 'Resin'),
                ('M1 70%', 124.00, 'Resin'),
                ('M6', 206.00, 'Resin'),
                ('Mo 70%', 220.00, 'Resin'),
                ('MD', 129.00, 'Resin'),
                ('MD 60%', 125.00, 'Resin'),
                ('R 920', 160.00, 'Resin'),
                ('DBTL', 40.00, 'Resin'),
                ('927', 109.00, 'Resin'),
                ('X1', 118.00, 'Thinner'),
                ('X2', 120.00, 'Thinner'),
                ('X3', 118.00, 'Thinner'),
                ('X5', 105.00, 'Thinner'),
                ('C9', 38.00, 'Thinner'),
                ('C12', 25.00, 'Thinner');
            """)
            self.db_connection.commit()

    def create_raw_material_history_table(self):
            """Create the raw_material_history table if it does not exist"""
            cursor = self.db_connection.cursor()
            # cursor.execute('''Drop table if exists raw_material_history''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS raw_material_history (
                id INTEGER PRIMARY KEY,
                raw_material_id INTEGER,
                old_price DECIMAL(10, 2),
                new_price DECIMAL(10, 2),
                change_date TEXT,  -- Use a timestamp to store the date
                FOREIGN KEY (raw_material_id) REFERENCES raw_materials(id)
            )
            ''')
            self.db_connection.commit()

    def create_product_details_table(self):
        """Create the product_details table if it doesn't exist"""
        cursor = self.db_connection.cursor()
        # cursor.execute('''DROP TABLE IF EXISTS product_details''')
        cursor.execute("""  
            CREATE TABLE IF NOT EXISTS product_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                yield_value REAL NOT NULL,
                viscosity REAL NOT NULL,
                weight_lit REAL NOT NULL,
                container_cost REAL NOT NULL,
                transport_cost REAL NOT NULL,
                sales_cost REAL NOT NULL,
                misc_cost REAL NOT NULL,
                total_rate REAL NOT NULL,
                description TEXT,
                date_created TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                material_name TEXT NOT NULL,
                material_quantity REAL NOT NULL,
                FOREIGN KEY(product_id) REFERENCES product_details(id)
            );
        """)
        self.db_connection.commit()

    def init_ui(self):
        self.setWindowTitle("Home - Vishal Paints")
        self.setFixedSize(800, 600)

        # Define a central widget and set it
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Add Menu Bar
        self.createMenuBar()

        # Set the main style using QSS
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f4f4;
            }
            QLabel {
                font-size: 18px;
                color: #333;
                font-family: 'Calibri', sans-serif;
            }
            QLabel#company_name {
                font-size: 26px;
                font-weight: bold;
                color: #2F4F4F;
            }
            QLabel#company_desc {
                font-size: 16px;
                line-height: 1.5;
                color: #555;
            }
            QPushButton {
                font-size: 16px;
                padding: 12px 20px;
                background-color: #4CAF50;
                color: white;
                border-radius: 8px;
                font-family: 'Segoe UI', sans-serif;
                text-align: center;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel#developer_label {
                font-size: 12px;
                color: #777;
                font-family: 'Segoe UI', sans-serif;
                margin-top: 10px;
            }
        """)

        # --- Top Section: Company Info ---
        company_info_layout = QVBoxLayout()

        # Company Name
        company_name_label = QLabel("Vishal Paints, Inc")
        company_name_label.setObjectName("company_name")
        company_name_label.setAlignment(Qt.AlignCenter)

        # Company Description
        company_desc_label = QLabel(
            "Vishal Paints offers premium quality paints and coatings for both industrial and domestic applications. "
            "We specialize in custom color solutions and efficient delivery for your painting needs."
        )
        company_desc_label.setObjectName("company_desc")
        company_desc_label.setAlignment(Qt.AlignCenter)
        company_desc_label.setWordWrap(True)

        # Add to company info layout
        company_info_layout.addWidget(company_name_label)
        company_info_layout.addWidget(company_desc_label)

        # --- Bottom Section: Watermark & Developer Info ---
        bottom_section_layout = QVBoxLayout()

        # Developer Text
        developer_label = QLabel("Developed by CSE Dept. GHRCE")
        developer_label.setObjectName("developer_label")
        developer_label.setAlignment(Qt.AlignCenter)

        # Watermark Image
        picture_path = os.path.join("src", "watermark.png")
        picture_pixmap = QPixmap(picture_path)
        if picture_pixmap.isNull():
            print("Error loading picture! Make sure the path is correct.")
        else:
            picture_label = QLabel()
            picture_label.setPixmap(picture_pixmap.scaled(
                200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            picture_label.setAlignment(Qt.AlignCenter)
            bottom_section_layout.addWidget(picture_label)

        # Spacer between watermark and bottom
        bottom_spacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

        # Add components to bottom section
        bottom_section_layout.addWidget(developer_label)
        bottom_section_layout.addItem(bottom_spacer)

        # --- Assemble Layout ---
        layout.addLayout(company_info_layout)  # Top section
        layout.addStretch(1)  # Flexible space
        layout.addLayout(bottom_section_layout)  # Bottom section

    def createMenuBar(self):
            menu_bar = self.menuBar()
            # Create Menus
            home_menu = menu_bar.addMenu('Home')
            product_menu = menu_bar.addMenu('Product')
            raw_material_menu = menu_bar.addMenu('Raw Material')
            inventory_menu = menu_bar.addMenu('Inventory')

            # Actions for Home Menu
            home_action = QAction('Home', self)
            home_action.triggered.connect(self.show_home)
            home_menu.addAction(home_action)

            # Actions for Product Menu
            product_rate_action = QAction('Product Rate Calculator', self)
            product_history_action = QAction('Product History', self)
            product_rate_action.triggered.connect(self.show_product_rate_calculator)
            product_history_action.triggered.connect(self.show_product_history)

            product_menu.addAction(product_rate_action)
            product_menu.addAction(product_history_action)

            # Actions for Raw Material Menu
            raw_material_management_action = QAction('Raw Material Management', self)
            raw_material_history_action = QAction('Raw Material History', self)
            raw_material_management_action.triggered.connect(self.open_raw_material_management)
            raw_material_history_action.triggered.connect(self.show_raw_material_history)

            raw_material_menu.addAction(raw_material_management_action)
            raw_material_menu.addAction(raw_material_history_action)

            # Actions for Inventory Menu
            inventory_details_action = QAction('Inventory Details', self)
            inventory_details_action.triggered.connect(self.show_inventory_details)

            inventory_menu.addAction(inventory_details_action)
   
    def show_product_rate_calculator(self):
        self.product_rate_calculator = ProductRateCalculatorApp(self.db_connection)
        self.product_rate_calculator.show()

    def show_product_history(self):
        self.product_history_action = ProductHistoryScreen(self.db_connection)
        self.product_history_action.show()

    def open_raw_material_management(self):
        # QMessageBox.information(self, "Raw Material Management", "This feature will manage raw materials.")
        raw_material_screen = RawMaterialManagementScreen(self.db_connection)
        raw_material_screen.exec()

    def show_raw_material_history(self):
        history_dialog = RawMaterialHistoryDialog(self.db_connection)
        history_dialog.exec()

        # Create a layout for the dialog
        layout = QVBoxLayout()

        # Table to display raw material history
        raw_material_table = QTableWidget(0, 3)
        raw_material_table.setHorizontalHeaderLabels(["Name", "Type", "Price"])
        layout.addWidget(raw_material_table)

        # Fetch raw material data from the database
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT name, mat_type, price FROM raw_materials")
        raw_materials = cursor.fetchall()

        # Populate the table with raw material data
        for row_data in raw_materials:
            row = raw_material_table.rowCount()
            raw_material_table.insertRow(row)
            for column, data in enumerate(row_data):
                raw_material_table.setItem(row, column, QTableWidgetItem(str(data)))

        # Add a close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(history_dialog.close)
        layout.addWidget(close_button)

        history_dialog.setLayout(layout)
        history_dialog.exec()

    def show_inventory_details(self):

        invent= InventoryDetailsDialog(self.db_connection)
        invent.exec()

    def show_home(self):
        QMessageBox.information(self, "Home Screen", "You are already on the home screen.")

class RawMaterialHistoryDialog(QDialog):
    def __init__(self, db_connection):  
        super().__init__()
        self.db_connection = db_connection
        self.setWindowTitle("Raw Material History")
        self.setGeometry(150, 150, 1000, 600)  # Adjusted window size for more content

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a search bar at the top of the layout
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search by material name or type...")
        self.search_bar.textChanged.connect(self.filter_history)  # Connect to filter method
        layout.addWidget(self.search_bar)

        # Scrollable area for tables
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Initialize the dictionary to store tables by material type
        self.tables_by_type = {}
        self.scroll_layout = scroll_layout

        self.load_history()

    def load_history(self):
        """Load only raw materials with changes into separate tables by material type."""
        cursor = self.db_connection.cursor()
        cursor.execute("""
            SELECT rm.name, rm.mat_type, rh.old_price, rh.new_price, rh.change_date
            FROM raw_materials rm
            LEFT JOIN raw_material_history rh 
                ON rm.id = rh.raw_material_id
            WHERE rh.old_price IS NOT NULL OR rh.new_price IS NOT NULL
            ORDER BY rm.mat_type, rh.change_date DESC
        """)
        history = cursor.fetchall()

        # Organize history by material type
        history_by_type = {}
        for name, mat_type, old_price, new_price, change_date in history:
            if mat_type not in history_by_type:
                history_by_type[mat_type] = []

            # Format the price change details for each raw material
            change_date_formatted = QDateTime.fromString(change_date, "yyyy-MM-dd HH:mm:ss").toString("yyyy-MM-dd")
            history_by_type[mat_type].append((name, mat_type, old_price, new_price, change_date_formatted))

        # Create a layout to display tables side by side
        self.tables_layout = QHBoxLayout()
        self.scroll_layout.addLayout(self.tables_layout)

        # Create a table for each material type
        for mat_type, items in history_by_type.items():
            table_layout = QVBoxLayout()

            # Material Type label
            table_label = QLabel(f"Material Type: {mat_type}")
            table_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            table_layout.addWidget(table_label)

            # Create the table (5 columns: name, type, old price, new price, and date)
            table = QTableWidget(0, 5)  # 5 columns: material name, material type, old price, new price, date
            table.setHorizontalHeaderLabels(["Material Name", "Material Type", "Old Price", "New Price", "Date Changed"])
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            table.setSelectionMode(QAbstractItemView.NoSelection)

            # Increase the cell size
            table.horizontalHeader().setStretchLastSection(True)  # Stretch last column to fill space
            table.setColumnWidth(0, 200)  # Adjust width for Material Name
            table.setColumnWidth(1, 150)  # Adjust width for Material Type
            table.setColumnWidth(2, 100)  # Adjust width for Old Price
            table.setColumnWidth(3, 100)  # Adjust width for New Price
            table.setColumnWidth(4, 150)  # Adjust width for Date Changed

            # Insert history records into the table
            for name, mat_type, old_price, new_price, change_date in items:
                row_count = table.rowCount()
                table.insertRow(row_count)
                table.setItem(row_count, 0, QTableWidgetItem(name))
                table.setItem(row_count, 1, QTableWidgetItem(mat_type))
                table.setItem(row_count, 2, QTableWidgetItem(str(old_price) if old_price is not None else "N/A"))
                table.setItem(row_count, 3, QTableWidgetItem(str(new_price) if new_price is not None else "N/A"))
                table.setItem(row_count, 4, QTableWidgetItem(change_date))  # Display formatted date

            # Add the table to the layout
            table_layout.addWidget(table)

            # Add the table layout to the main layout
            self.tables_layout.addLayout(table_layout)
            self.tables_by_type[mat_type] = table

    def filter_history(self):
        """Filter the history displayed in the tables based on search query."""
        search_query = self.search_bar.text().lower()

        # Filter history by checking if the query matches the material name or type
        for mat_type, table in self.tables_by_type.items():
            # Clear existing rows
            table.setRowCount(0)

            # Fetch the relevant history from the database again
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT rm.name, rm.mat_type, rh.old_price, rh.new_price, rh.change_date
                FROM raw_materials rm
                LEFT JOIN raw_material_history rh 
                    ON rm.id = rh.raw_material_id
                WHERE (rh.old_price IS NOT NULL OR rh.new_price IS NOT NULL)
                AND (LOWER(rm.name) LIKE ? OR LOWER(rm.mat_type) LIKE ?)
                ORDER BY rm.mat_type, rh.change_date DESC
            """, (f"%{search_query}%", f"%{search_query}%"))
            filtered_history = cursor.fetchall()

            # Organize filtered history by material type
            history_by_type = {}
            for name, mat_type, old_price, new_price, change_date in filtered_history:
                if mat_type not in history_by_type:
                    history_by_type[mat_type] = []

                # Format the price change details for each raw material
                change_date_formatted = QDateTime.fromString(change_date, "yyyy-MM-dd HH:mm:ss").toString("yyyy-MM-dd")
                history_by_type[mat_type].append((name, mat_type, old_price, new_price, change_date_formatted))

            # Update the tables based on the filtered history
            for mat_type, items in history_by_type.items():
                table = self.tables_by_type.get(mat_type)
                if table:
                    # Clear the existing rows and insert the filtered rows
                    table.setRowCount(0)
                    for name, mat_type, old_price, new_price, change_date in items:
                        row_count = table.rowCount()
                        table.insertRow(row_count)
                        table.setItem(row_count, 0, QTableWidgetItem(name))
                        table.setItem(row_count, 1, QTableWidgetItem(mat_type))
                        table.setItem(row_count, 2, QTableWidgetItem(str(old_price) if old_price is not None else "N/A"))
                        table.setItem(row_count, 3, QTableWidgetItem(str(new_price) if new_price is not None else "N/A"))
                        table.setItem(row_count, 4, QTableWidgetItem(change_date))  # Display formatted date

class InventoryDetailsDialog(QDialog):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.setWindowTitle("Inventory Details")
        self.setGeometry(150, 150, 800, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Search Bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search Materials...")
        self.search_bar.textChanged.connect(self.search_inventory)
        layout.addWidget(self.search_bar)

        # Scrollable area for tables
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        self.tables_by_type = {}
        self.scroll_layout = scroll_layout

        # Print Button
        print_button = QPushButton("Print Inventory Details")
        print_button.clicked.connect(self.print_inventory_pdf)
        layout.addWidget(print_button)

        self.load_inventory()

    def load_inventory(self):
        """Load inventory data into separate tables by product type."""
        cursor = self.db_connection.cursor()
        cursor.execute("""SELECT name, mat_type, price FROM raw_materials ORDER BY mat_type""")
        inventory = cursor.fetchall()

        # Organize inventory by type
        inventory_by_type = {}
        for name, mat_type, price in inventory:
            if mat_type not in inventory_by_type:
                inventory_by_type[mat_type] = []
            inventory_by_type[mat_type].append((name, price))

        # Create a layout to display tables side by side
        tables_layout = QHBoxLayout()  # This will allow side-by-side arrangement
        self.scroll_layout.addLayout(tables_layout)

        # Create a table for each product type
        for mat_type, items in inventory_by_type.items():
            # Vertical layout for each table (heading + table)
            table_layout = QVBoxLayout()

            # Table heading
            table_label = QLabel(f"{mat_type}")
            table_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            table_layout.addWidget(table_label)

            # Create the table
            table = QTableWidget(0, 2)
            table.setHorizontalHeaderLabels(["Material Name", "Price"])
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Make the table uneditable
            table.setSelectionMode(QAbstractItemView.NoSelection)

            for name, price in items:
                row_count = table.rowCount()
                table.insertRow(row_count)
                table.setItem(row_count, 0, QTableWidgetItem(name))
                table.setItem(row_count, 1, QTableWidgetItem(f"{price:.2f}"))

            # Add the table to the layout
            table_layout.addWidget(table)

            # Add the layout for this table to the main layout
            tables_layout.addLayout(table_layout)
            self.tables_by_type[mat_type] = table

    def search_inventory(self):
        """Search and filter the inventory based on the search query."""
        query = self.search_bar.text().lower()

        for mat_type, table in self.tables_by_type.items():
            for row in range(table.rowCount()):
                item_name = table.item(row, 0).text().lower()
                item_price = table.item(row, 1).text().lower()
                # Show or hide row based on the search query
                if query in item_name or query in item_price:
                    table.setRowHidden(row, False)
                else:
                    table.setRowHidden(row, True)

    def print_inventory_pdf(self):
        """Generate a PDF with inventory details in a tabular format and allow the user to choose the file path."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Inventory PDF", "Vishal_Paints_Inventory.pdf", "PDF Files (*.pdf)")

        if not file_path:  # User cancelled the dialog
            return

        pdf = canvas.Canvas(file_path, pagesize=A4)
        pdf.setTitle("Vishal Paints Inventory")

        width, height = A4
        y_position = height - 50

        # Title and Date
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, y_position, "Vishal Paints Inventory")
        y_position -= 20

        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, y_position, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        y_position -= 30

        # Iterate through each product type and create a table
        for mat_type, table in self.tables_by_type.items():
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(50, y_position, f"Material Type: {mat_type}")
            y_position -= 20

            # Table data: Header and rows
            table_data = [["Material Name", "Price (Rs)"]]
            for row in range(table.rowCount()):
                material_name = table.item(row, 0).text()
                price = table.item(row, 1).text()
                table_data.append([material_name, price])

            # Create the table
            data_table = Table(table_data, colWidths=[300, 100])
            data_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                            ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

            # Draw the table on the PDF
            data_table.wrapOn(pdf, width - 100, y_position)
            data_table.drawOn(pdf, 50, y_position - len(table_data) * 20 - 20)

            y_position -= (len(table_data) * 20 + 40)

            # Add a new page if needed
            if y_position < 100:
                pdf.showPage()
                y_position = height - 50

        pdf.save()
        QMessageBox.information(self, "PDF Generated", f"Inventory details saved to {file_path}")

class RawMaterialManagementScreen(QDialog):

    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Raw Material Management")

        # Allow the window to be resizable
        self.setMinimumSize(800, 600)  # Minimum size to prevent shrinking too small

        layout = QVBoxLayout()  # Main vertical layout for the dialog
        self.setLayout(layout)

        # Search bar for materials
        search_layout = QHBoxLayout()  # Horizontal layout for the search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search materials by name or type...")
        self.search_input.textChanged.connect(self.perform_search)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Material layout for side-by-side tables
        self.material_layout = QHBoxLayout()  # Horizontal layout for the tables
        self.material_group = QGroupBox("Materials by Type")
        self.material_group.setLayout(self.material_layout)
        layout.addWidget(self.material_group)

        # Load existing materials (e.g., from a database)
        self.load_materials()

        # Save and Delete Buttons
        button_layout = QHBoxLayout()  # Horizontal layout for the buttons

        # Add New Material Button
        self.add_button = QPushButton("Add New Material")
        self.add_button.clicked.connect(self.open_add_material_dialog)
        button_layout.addWidget(self.add_button)

        # Save Changes Button
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        button_layout.addWidget(self.save_button)

        # Delete Selected Button
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

    def load_materials(self):
        """Load all raw materials into a single table."""
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT id, name, mat_type, price FROM raw_materials ORDER BY name")
        materials = cursor.fetchall()

        # Clear existing layout in material group
        for i in reversed(range(self.material_layout.count())):
            widget = self.material_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Create a single table to display all materials
        table = QTableWidget(len(materials), 4)  # 4 columns: Name, Price, Material Type, ID
        table.setHorizontalHeaderLabels(["Material Name", "Price", "Material Type", "ID"])
        table.setEditTriggers(QTableWidget.DoubleClicked)
        table.setColumnHidden(3, True)  # Hide ID column

        # Insert material rows into the table
        for row, material in enumerate(materials):
            table.setItem(row, 0, QTableWidgetItem(material[1]))  # Name
            table.setItem(row, 1, QTableWidgetItem(str(material[3])))  # Price
            table.setItem(row, 2, QTableWidgetItem(material[2]))  # Material Type
            table.setItem(row, 3, QTableWidgetItem(str(material[0])))  # ID

        # Add the table to the layout
        self.material_layout.addWidget(table)

    def perform_search(self):
        """Search materials dynamically and allow editing of prices."""
        search_text = self.search_input.text().strip().lower()
        
        # Clear existing layout in material group
        for i in reversed(range(self.material_group.layout().count())):
            widget = self.material_group.layout().itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not search_text:  # Reload materials if search box is cleared
            self.load_materials()
            return

        cursor = self.db_connection.cursor()
        cursor.execute("""
            SELECT id, name, mat_type, price FROM raw_materials 
            WHERE LOWER(name) LIKE ? OR LOWER(mat_type) LIKE ?
        """, (f"%{search_text}%", f"%{search_text}%"))
        results = cursor.fetchall()

        if results:
            # Create a table for displaying search results
            table = QTableWidget(0, 4)
            table.setHorizontalHeaderLabels(["Material Name", "Material Type", "Price", "ID"])
            table.setEditTriggers(QTableWidget.DoubleClicked)
            table.setColumnHidden(3, True)  # Hide the ID column

            # Populate the table with search results
            for result in results:
                row_count = table.rowCount()
                table.insertRow(row_count)
                table.setItem(row_count, 0, QTableWidgetItem(result[1]))  # Name
                table.setItem(row_count, 1, QTableWidgetItem(result[2]))  # Material Type
                table.setItem(row_count, 2, QTableWidgetItem(str(result[3])))  # Price
                table.setItem(row_count, 3, QTableWidgetItem(str(result[0])))  # ID (hidden)

            # Connect to a method for tracking changes to prices
            # table.itemChanged.connect(self.track_price_change)

            # Add the table to the material group layout
            self.material_group.layout().addWidget(table)
            self.search_result_table = table  # Save reference to the search result table
        else:
            # Show "no results found" message if search yields no matches
            no_results_label = QLabel("No matching materials found.")
            self.material_group.layout().addWidget(no_results_label)

    # def track_price_change(self, item):
    #     """Track changes to the price and validate inputs."""
    #     try:
    #         if item.column() == 2:  # Price column
    #             new_price = float(item.text())  # Validate input as a float
    #             if new_price < 0:
    #                 raise ValueError("Price cannot be negative.")
    #             item.setBackground(QColor("lightgreen"))  # Highlight valid changes
    #     except ValueError:
    #         QMessageBox.warning(self, "Invalid Input", "Please enter a valid non-negative number for the price.")
    #         item.setText("0.0")  # Reset to a default valid value

    def save_changes(self):
        """Save edited prices to the database for search results."""
        cursor = self.db_connection.cursor()
        updated = False

        # Save changes for the displayed search results
        for row in range(self.search_result_table.rowCount()):
            try:
                material_id = int(self.search_result_table.item(row, 3).text())  # Hidden ID column
                new_price = float(self.search_result_table.item(row, 2).text())  # Price column
                
                # Fetch current price to check if it has changed
                cursor.execute("SELECT price FROM raw_materials WHERE id = ?", (material_id,))
                old_price = cursor.fetchone()[0]
                
                if old_price != new_price:
                    # Update price in the database
                    cursor.execute("UPDATE raw_materials SET price = ? WHERE id = ?", (new_price, material_id))
                    
                    # Log the price change in the history table
                    cursor.execute("""
                        INSERT INTO raw_material_history (raw_material_id, old_price, new_price, change_date)
                        VALUES (?, ?, ?, ?)
                    """, (material_id, old_price, new_price, QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")))
                    
                    updated = True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save changes: {str(e)}")
                self.db_connection.rollback()
                return

        if updated:
            try:
                self.db_connection.commit()
                QMessageBox.information(self, "Success", "Changes saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to commit changes: {str(e)}")
                self.db_connection.rollback()
        else:
            QMessageBox.information(self, "No Changes", "No changes were made to save.")

    def delete_selected(self):
        """Delete the selected raw material from the search result table and database."""
        selected_row = self.search_result_table.currentRow()
        
        if selected_row == -1:
            QMessageBox.warning(self, "No Selection", "Please select a raw material to delete.")
            return

        # Get the material ID from the hidden column (ID column)
        material_id = self.search_result_table.item(selected_row, 3).text()

        # Ask for confirmation before deleting
        reply = QMessageBox.question(self, 'Delete Material', f"Are you sure you want to delete the selected material?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                cursor = self.db_connection.cursor()
                # Delete the raw material from the database
                cursor.execute("DELETE FROM raw_materials WHERE id = ?", (material_id,))
                self.db_connection.commit()

                # Remove the row from the table view
                self.search_result_table.removeRow(selected_row)
                QMessageBox.information(self, "Success", "Material deleted successfully!")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete material: {str(e)}")
                self.db_connection.rollback()



    def open_add_material_dialog(self):
        """Open the dialog to add a new material."""
        dialog = AddMaterialDialog(self.db_connection, self)
        dialog.exec_()
        self.load_materials()

class AddMaterialDialog(QDialog):
    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Add New Material")
        self.setGeometry(300, 300, 400, 300)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Material Name Field
        self.name_label = QLabel("Material Name:")
        self.name_input = QLineEdit()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        # Material Type Field (Dropdown + Manual Input)
        self.type_label = QLabel("Type:")
        
        # Create a layout for the type input
        type_layout = QHBoxLayout()

        # Create the dropdown for material types
        self.type_input = QComboBox()
        self.populate_material_types()  # Populate the dropdown with material types
        type_layout.addWidget(self.type_input)

        # Create the manual input field
        self.manual_type_input = QLineEdit()
        self.manual_type_input.setPlaceholderText("Or enter a new material type")
        type_layout.addWidget(self.manual_type_input)

        layout.addWidget(self.type_label)
        layout.addLayout(type_layout)

        # "Add New Material Type" Button
        self.new_type_button = QPushButton("Add New Material Type")
        self.new_type_button.clicked.connect(self.add_new_material_type)
        layout.addWidget(self.new_type_button)

        # Price Field
        self.price_label = QLabel("Price:")
        self.price_input = QLineEdit()
        self.price_input.setValidator(QDoubleValidator(0.0, 999999.99, 2))
        layout.addWidget(self.price_label)
        layout.addWidget(self.price_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_material)
        button_layout.addWidget(self.add_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def populate_material_types(self):
        """Populate the dropdown list with material types from the database."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT DISTINCT mat_type FROM raw_materials")
            material_types = cursor.fetchall()

            self.type_input.clear()
            self.type_input.addItem("(Select a material)")  # Add placeholder text
            self.type_input.setCurrentIndex(0)  # Set placeholder as the default visible item

            for mat_type in material_types:
                self.type_input.addItem(mat_type[0])  # Add each material type to the dropdown
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load material types: {e}")

    def add_new_material_type(self):
        """Allow the user to enter a new material type."""
        new_type, ok = QInputDialog.getText(self, "New Material Type", "Enter the new material type:")
        if ok and new_type:
            try:
                # Insert the new material type into the raw_materials table
                cursor = self.db_connection.cursor()
                cursor.execute("INSERT INTO raw_materials (mat_type) VALUES (?)", (new_type,))
                self.db_connection.commit()

                # Refresh the material type dropdown to include the new material type
                self.populate_material_types()

                # Inform the user of the successful addition
                QMessageBox.information(self, "Success", f"Material type '{new_type}' added successfully.")
            except Exception as e:
                # If there's any error, rollback the changes
                self.db_connection.rollback()
                QMessageBox.critical(self, "Error", f"Failed to add material type: {e}")

    def add_material(self):
        """Insert new material into the database."""
        name = self.name_input.text().strip()
        mat_type = self.type_input.currentText()  # Get selected material type from dropdown
        manual_type = self.manual_type_input.text().strip()

        # If no material type is selected, use the manual input
        if mat_type == "(Select a material)" and manual_type:
            mat_type = manual_type

        price = self.price_input.text().strip()

        if not name or not mat_type or not price:
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "INSERT INTO raw_materials (name, mat_type, price) VALUES (?, ?, ?)",
                (name, mat_type, float(price)),
            )
            self.db_connection.commit()
            QMessageBox.information(self, "Success", "Material added successfully.")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add material: {e}")

if __name__ == "__main__":
    app = QApplication([])
    window = HomeScreen()
    window.show()
    app.exec_()
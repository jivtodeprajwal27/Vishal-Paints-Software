from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout, QGroupBox, QLineEdit, QPushButton, \
    QTableWidget, QTableWidgetItem, QLabel, QComboBox, QFileDialog, QHBoxLayout, QMenuBar, QMenu, QAction, QMessageBox
from PyQt5.QtWidgets import (
      QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy
     )
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import sqlite3
from PyQt5.QtWidgets import QDialog,QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel,QDoubleValidator
from PyQt5.QtWidgets import QAbstractItemView
from reportlab.lib.pagesizes import A4
from ProductHistoryScreen import ProductHistoryScreen
from product_rate_calculator import ProductRateCalculatorApp 
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
        #cursor.execute('''DROP TABLE IF EXISTS invoices''')
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

    def create_product_details_table(self):
        """Create the product_details table if it doesn't exist"""
        cursor = self.db_connection.cursor()
        #cursor.execute('''DROP TABLE IF EXISTS product_details''')
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
        raw_material_dialog = RawMaterialManagementScreen(self.db_connection)
        raw_material_dialog.exec()

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
    def __init__(self, db_connection):  # Corrected to __init__
        super().__init__()
        self.db_connection = db_connection
        self.setWindowTitle("Raw Material History")
        self.setGeometry(150, 150, 600, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Table to display raw material history
        self.history_table = QTableWidget(0, 5)
        self.history_table.setHorizontalHeaderLabels(["Material Name", "Material Type", "Old Price", "New Price", "Date"])
        layout.addWidget(self.history_table)

        self.load_history()

    def load_history(self):
        """Load raw material history into the table, showing all materials."""
        cursor = self.db_connection.cursor()
        cursor.execute("""
            SELECT rm.name, rm.mat_type, 
                rh.old_price, 
                rh.new_price, 
                rh.change_date
            FROM raw_materials rm
            LEFT JOIN raw_material_history rh 
                ON rm.id = rh.raw_material_id
            GROUP BY rm.id
            ORDER BY MAX(rh.change_date) DESC
        """)
        history = cursor.fetchall()

        self.history_table.setRowCount(0)  # Clear existing rows
        for record in history:
            row_count = self.history_table.rowCount()
            self.history_table.insertRow(row_count)

            # Insert Material Name and Material Type
            self.history_table.setItem(row_count, 0, QTableWidgetItem(record[0]))  # Material Name
            self.history_table.setItem(row_count, 1, QTableWidgetItem(record[1]))  # Material Type
            
            # If Old Price and New Price are the same, leave New Price and Date empty
            if record[2] == record[3]:  # No price change
                self.history_table.setItem(row_count, 2, QTableWidgetItem(str(record[2]) if record[2] is not None else "N/A"))  # Old Price
                self.history_table.setItem(row_count, 3, QTableWidgetItem(""))  # New Price empty
                self.history_table.setItem(row_count, 4, QTableWidgetItem(""))  # Date empty
            else:  # Price changed
                self.history_table.setItem(row_count, 2, QTableWidgetItem(str(record[2]) if record[2] is not None else "N/A"))  # Old Price
                self.history_table.setItem(row_count, 3, QTableWidgetItem(str(record[3])))  # New Price
                self.history_table.setItem(row_count, 4, QTableWidgetItem(str(record[4])))  # Change Date

class InventoryDetailsDialog(QDialog):
    def __init__(self, db_connection):  # Corrected to __init__
        super().__init__()
        self.db_connection = db_connection
        self.setWindowTitle("Inventory Details")
        self.setGeometry(150, 150, 600, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Table to display inventory details
        self.inventory_table = QTableWidget(0, 3)
        self.inventory_table.setHorizontalHeaderLabels(["Material Name", "Type", "Price"])
        self.inventory_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.inventory_table.setSelectionMode(QAbstractItemView.NoSelection)
        layout.addWidget(self.inventory_table)

        self.load_inventory()

    def load_inventory(self):
        """Load inventory data into the table."""
        cursor = self.db_connection.cursor()
        # Query to fetch material name, type, and price
        cursor.execute("""
            SELECT name, mat_type, price
            FROM raw_materials
        """)
        inventory = cursor.fetchall()

        self.inventory_table.setRowCount(0)  # Clear existing rows
        for record in inventory:
            row_count = self.inventory_table.rowCount()
            self.inventory_table.insertRow(row_count)
            self.inventory_table.setItem(row_count, 0, QTableWidgetItem(record[0]))  # Material Name
            self.inventory_table.setItem(row_count, 1, QTableWidgetItem(record[1]))  # Material Type
            self.inventory_table.setItem(row_count, 2, QTableWidgetItem(f"{record[2]:.2f}"))  # Price

class RawMaterialManagementScreen(QDialog):  # Changed from QDialog to QWidget
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Raw Material Management")
        self.setGeometry(150, 150, 500, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Table to display raw materials
        self.material_table = QTableWidget(0, 3)
        self.material_table.setHorizontalHeaderLabels(["Material Name", "Type", "Price"])
        self.material_table.setEditTriggers(QTableWidget.DoubleClicked)  # Allow price editing
        layout.addWidget(self.material_table)

        # Save and Delete Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add New Material")
        self.add_button.clicked.connect(self.open_add_material_dialog)
        button_layout.addWidget(self.add_button)

        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        button_layout.addWidget(self.save_button)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

        self.load_materials()

    def load_materials(self):
        """Load raw materials into the table."""
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT id, name, mat_type, price FROM raw_materials")
        materials = cursor.fetchall()

        self.material_table.setRowCount(0)  # Clear existing rows
        for material in materials:
            row_count = self.material_table.rowCount()
            self.material_table.insertRow(row_count)
            self.material_table.setItem(row_count, 0, QTableWidgetItem(material[1]))  # Name
            self.material_table.setItem(row_count, 1, QTableWidgetItem(material[2]))  # Type
            self.material_table.setItem(row_count, 2, QTableWidgetItem(str(material[3])))  # Price
            self.material_table.item(row_count, 0).setData(Qt.UserRole, material[0])  # Store ID in row

    def save_changes(self):
        """Save edited prices to the database and log changes to history."""
        cursor = self.db_connection.cursor()
        for row in range(self.material_table.rowCount()):
            material_id = self.material_table.item(row, 0).data(Qt.UserRole)
            name = self.material_table.item(row, 0).text()
            mat_type = self.material_table.item(row, 1).text()
            new_price = float(self.material_table.item(row, 2).text())

            # Get the old price from the database
            cursor.execute("SELECT price FROM raw_materials WHERE id = ?", (material_id,))
            old_price = cursor.fetchone()[0]

            # Update raw_materials table
            cursor.execute(
                "UPDATE raw_materials SET price = ? WHERE id = ?",
                (new_price, material_id)
            )

            # Insert into raw_material_history with old_price and new_price
            cursor.execute(
                "INSERT INTO raw_material_history (raw_material_id, change_type, old_price, new_price) "
                "VALUES (?, ?, ?, ?)",
                (material_id, 'updated', old_price, new_price)
            )

        self.db_connection.commit()
        QMessageBox.information(self, "Success", "Changes saved successfully!")

    def delete_selected(self):
        """Delete the selected raw material from the database."""
        selected_row = self.material_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select a row to delete.")
            return

        material_id = self.material_table.item(selected_row, 0).data(Qt.UserRole)
        cursor = self.db_connection.cursor()

        # Delete material from raw_materials table
        cursor.execute("DELETE FROM raw_materials WHERE id = ?", (material_id,))
        self.db_connection.commit()

        self.material_table.removeRow(selected_row)
        QMessageBox.information(self, "Success", "Material deleted successfully!")

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

        # Form Fields
        self.name_label = QLabel("Material Name:")
        self.name_input = QLineEdit()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        self.type_label = QLabel("Type:")
        self.type_input = QLineEdit()
        layout.addWidget(self.type_label)
        layout.addWidget(self.type_input)

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

    def add_material(self):
        """Insert new material into the database."""
        name = self.name_input.text().strip()
        mat_type = self.type_input.text().strip()
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
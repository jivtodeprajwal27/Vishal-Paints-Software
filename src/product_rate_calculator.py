from PyQt5.QtWidgets import QApplication,QFileDialog, QMainWindow, QWidget, QVBoxLayout, QFormLayout, QGroupBox, QLineEdit, QPushButton, \
    QTableWidget, QTableWidgetItem, QLabel, QComboBox, QHBoxLayout, QMenuBar, QMenu, QAction, QMessageBox
import sqlite3
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt
from datetime import datetime
from reportlab.pdfgen import canvas
from ProductHistoryScreen import ProductHistoryScreen

class ProductRateCalculatorApp(QMainWindow):  # Change to QMainWindow
    def __init__(self):
        super().__init__()
        self.initUI()
        self.db_connection = self.create_db_connection()
        self.create_raw_materials_table()
        self.create_product_details_table()
        self.create_raw_material_history_table()

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
                background-color: #f7f7f7;
            }
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #444;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 5px;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                font-size: 14px;
                background-color: #fff;
            }
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                font-size: 14px;
                background-color: #fff;
            }
            QPushButton {
                font-size: 14px;
                padding: 8px 15px;
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QTableWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #fff;
            }
            QHeaderView::section {
                background-color: #ddd;
                font-weight: bold;
                border: none;
            }
        """)
        # Create Menu Bar
        self.createMenuBar()

        # Central Widget and Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Product Details Form
        self.product_form = QFormLayout()
        self.product_form_group = QGroupBox("Product Details")
        layout.addWidget(self.product_form_group)

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

        # Set Main Layout
        central_widget.setLayout(layout)
    
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

        try:
            # Step 2: Generate the invoice PDF
            self.generate_invoice_pdf(file_path)
            QMessageBox.information(self, "Success", f"Invoice successfully saved at:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate invoice: {str(e)}")

    def generate_invoice_pdf(self, file_path):
        """Generate the invoice PDF and save it to the specified file path."""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter

        # Example product details
        product_details = {
            "Product Name": self.product_name.text(),
            "Description": self.description.text(),
            "Yield Value": self.yield_value.text(),
            "Viscosity": self.viscosity.text(),
            "Weight / Lit": self.weight_lit.text(),
            "Total Rate": self.total_rate.text(),
            "Date": datetime.now().strftime("%Y-%m-%d"),
        }

        c = canvas.Canvas(file_path, pagesize=letter)
        c.drawString(100, 750, "Invoice")
        c.drawString(100, 730, "=====================")
        y = 700

        for key, value in product_details.items():
            c.drawString(100, y, f"{key}: {value}")
            y -= 20

        c.save()


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

    def show_home(self):
        QMessageBox.information(self, "Home", "You are at the Home screen.")

    def show_product_rate_calculator(self):
        QMessageBox.information(self, "Product Rate Calculator", "You are already on the Product Rate Calculator screen.")

    def show_product_history(self):
        self.product_history_action = ProductHistoryScreen(self.db_connection)
        self.product_history_action.show()

    def open_raw_material_management(self):
        # QMessageBox.information(self, "Raw Material Management", "This feature will manage raw materials.")
        raw_material_dialog = RawMaterialManagementDialog(self.db_connection)
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
        QMessageBox.information(self, "Inventory Details", "This feature will show the inventory details.")

    def create_db_connection(self):
        """Create a connection to SQLite database"""
        conn = sqlite3.connect("product_rate.db")
        return conn

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

    def create_product_details_table(self):
        """Create the product_details table if it doesn't exist"""
        cursor = self.db_connection.cursor()

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

    def update_material_name_dropdown(self):
        """Update the Material Name dropdown based on the selected material type"""
        selected_material_type = self.material_type_dropdown.currentText()
        cursor = self.db_connection.cursor()
        cursor.execute("""
            SELECT DISTINCT name FROM raw_materials WHERE mat_type = ?
        """, (selected_material_type,))
        material_names = cursor.fetchall()

        self.material_name_dropdown.clear()

       
        self.material_name_dropdown.addItem("Select Material")
        for material_name in material_names:
            self.material_name_dropdown.addItem(material_name[0])

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

class RawMaterialManagementDialog(QDialog):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.setWindowTitle("Raw Material Management")
        self.setGeometry(150, 150, 500, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.material_table = QTableWidget(0, 3)
        self.material_table.setHorizontalHeaderLabels(["Material Name", "Type", "Price"])
        self.material_table.setEditTriggers(QTableWidget.DoubleClicked)  # Allow price editing
        layout.addWidget(self.material_table)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Changes")
        self.delete_button = QPushButton("Delete Selected")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)

        self.save_button.clicked.connect(self.save_changes)
        self.delete_button.clicked.connect(self.delete_selected)

        self.load_materials()

    def load_materials(self):
        """Load raw materials into the table."""
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT id, name, mat_type, price FROM raw_materials")
        materials = cursor.fetchall()

        self.material_table.setRowCount(0)
        for material in materials:
            row_count = self.material_table.rowCount()
            self.material_table.insertRow(row_count)
            self.material_table.setItem(row_count, 0, QTableWidgetItem(material[1]))  
            self.material_table.setItem(row_count, 1, QTableWidgetItem(material[2]))  
            self.material_table.setItem(row_count, 2, QTableWidgetItem(str(material[3])))
            self.material_table.item(row_count, 0).setData(Qt.UserRole, material[0]) 

    def save_changes(self):
        """Save edited prices to the database and log changes to history."""
        cursor = self.db_connection.cursor()
        for row in range(self.material_table.rowCount()):
            material_id = self.material_table.item(row, 0).data(Qt.UserRole)
            name = self.material_table.item(row, 0).text()
            mat_type = self.material_table.item(row, 1).text()
            new_price = float(self.material_table.item(row, 2).text())

            
            cursor.execute("""
                SELECT price FROM raw_materials WHERE id = ?
            """, (material_id,))
            old_price = cursor.fetchone()[0]

            
            cursor.execute("""
                UPDATE raw_materials
                SET price = ?
                WHERE id = ?
            """, (new_price, material_id))

            
            cursor.execute("""
                INSERT INTO raw_material_history (raw_material_id, change_type, old_price, new_price)
                VALUES (?, ?, ?, ?)
            """, (material_id,'updated', old_price, new_price))

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

       
        cursor.execute("DELETE FROM raw_materials WHERE id = ?", (material_id,))
        self.db_connection.commit()

        self.material_table.removeRow(selected_row)
        QMessageBox.information(self, "Success", "Material deleted successfully!")

class RawMaterialHistoryDialog(QDialog):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.setWindowTitle("Raw Material History")
        self.setGeometry(150, 150, 600, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

    
        self.history_table = QTableWidget(0, 5)
        # self.history_table.setHorizontalHeaderLabels(["Material Name", "Type", "Price", "Date"])
        self.history_table.setColumnCount(5) 
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

        self.history_table.setRowCount(0) 
        for record in history:
            row_count = self.history_table.rowCount()
            self.history_table.insertRow(row_count)

            self.history_table.setItem(row_count, 0, QTableWidgetItem(record[0])) 
            self.history_table.setItem(row_count, 1, QTableWidgetItem(record[1])) 
            
            if record[2] == record[3]:
                self.history_table.setItem(row_count, 2, QTableWidgetItem(str(record[2]) if record[2] is not None else "N/A"))  # Old Price
                self.history_table.setItem(row_count, 3, QTableWidgetItem("")) 
                self.history_table.setItem(row_count, 4, QTableWidgetItem("")) 
            else: 
                self.history_table.setItem(row_count, 2, QTableWidgetItem(str(record[2]) if record[2] is not None else "N/A"))  # Old Price
                self.history_table.setItem(row_count, 3, QTableWidgetItem(str(record[3])))  
                self.history_table.setItem(row_count, 4, QTableWidgetItem(str(record[4])))  

if __name__ == "__main__":
    app = QApplication([])
    window = ProductRateCalculatorApp()
    window.show()
    app.exec_()

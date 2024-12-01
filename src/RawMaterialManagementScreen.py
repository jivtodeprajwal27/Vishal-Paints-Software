from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QDialog, QTableWidgetItem, QLineEdit, QPushButton,
    QMessageBox, QLabel
)
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt



class RawMaterialManagementScreen(QWidget):  # Changed from QDialog to QWidget
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
